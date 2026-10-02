"""Game state and rules. Pure logic: no pygame imports, time is injected via update(dt)."""
from collections import deque

from . import config
from .board import Board
from .randomizer import BagRandomizer
from .tetromino import Piece, kick_offsets


class Game:
    def __init__(self, seed=None):
        self.board = Board()
        self.randomizer = BagRandomizer(seed)
        self.queue = deque(self.randomizer.next() for _ in range(config.NEXT_QUEUE_SIZE))
        self.hold_kind = None
        self.hold_used = False
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.soft_dropping = False
        self.last_clear = 0          # rows cleared by the most recent lock
        self.cleared_rows = []       # row indices of the most recent clear (for effects)
        self._gravity_timer = 0.0
        self._lock_timer = 0.0
        self._lock_resets = 0
        self.current = None
        self._spawn()

    # ----- spawning ---------------------------------------------------------
    def _take_next(self) -> str:
        kind = self.queue.popleft()
        self.queue.append(self.randomizer.next())
        return kind

    def _spawn(self, kind=None) -> None:
        kind = kind or self._take_next()
        piece = Piece(kind)
        piece.x = (self.board.width - piece.size) // 2
        piece.y = 0
        self.current = piece
        self._gravity_timer = 0.0
        self._lock_timer = 0.0
        self._lock_resets = 0
        if not self.board.fits(piece.cells()):
            self.game_over = True
        elif self._fits(dy=1):
            # Guideline: drop one row right away so the piece enters the visible field.
            piece.y += 1

    # ----- queries ----------------------------------------------------------
    def _fits(self, dx=0, dy=0, rotation=None) -> bool:
        p = self.current
        return self.board.fits(p.cells(p.x + dx, p.y + dy, rotation))

    def on_ground(self) -> bool:
        return not self._fits(dy=1)

    def ghost_y(self) -> int:
        dy = 0
        while self._fits(dy=dy + 1):
            dy += 1
        return self.current.y + dy

    # ----- player actions ---------------------------------------------------
    def _after_successful_move(self) -> None:
        if self.on_ground() and self._lock_resets < config.MAX_LOCK_RESETS:
            self._lock_timer = 0.0
            self._lock_resets += 1

    def move(self, dx: int) -> bool:
        if self.game_over or not self._fits(dx=dx):
            return False
        self.current.x += dx
        self._after_successful_move()
        return True

    def rotate(self, direction: int) -> bool:
        """direction: +1 clockwise, -1 counter-clockwise."""
        if self.game_over:
            return False
        p = self.current
        old = p.rotation
        new = (old + direction) % 4
        for kx, ky in kick_offsets(p.kind, old, new):
            if self._fits(dx=kx, dy=ky, rotation=new):
                p.x += kx
                p.y += ky
                p.rotation = new
                self._after_successful_move()
                return True
        return False

    def soft_drop_step(self) -> bool:
        if self._fits(dy=1):
            self.current.y += 1
            self.score += config.SOFT_DROP_POINTS
            return True
        return False

    def hard_drop(self) -> None:
        if self.game_over:
            return
        distance = self.ghost_y() - self.current.y
        self.current.y += distance
        self.score += distance * config.HARD_DROP_POINTS
        self._lock()

    def hold(self) -> bool:
        if self.game_over or self.hold_used:
            return False
        kind = self.current.kind
        self._spawn(self.hold_kind)
        self.hold_kind = kind
        self.hold_used = True
        return True

    # ----- time -------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.game_over:
            return
        interval = config.gravity_interval(self.level)
        if self.soft_dropping:
            interval /= config.SOFT_DROP_FACTOR
        self._gravity_timer += dt
        while self._gravity_timer >= interval and not self.game_over:
            self._gravity_timer -= interval
            if self._fits(dy=1):
                self.current.y += 1
                if self.soft_dropping:
                    self.score += config.SOFT_DROP_POINTS
            else:
                self._gravity_timer = 0.0
                break

        if self.on_ground():
            self._lock_timer += dt
            if self._lock_timer >= config.LOCK_DELAY:
                self._lock()
        else:
            self._lock_timer = 0.0

    # ----- locking & scoring ------------------------------------------------
    def _lock(self) -> None:
        cells = self.current.cells()
        self.board.place(cells, self.current.kind)
        # Lock out: the whole piece came to rest above the visible field.
        if all(y < config.HIDDEN_ROWS for _, y in cells):
            self.game_over = True
            return
        self.cleared_rows = self.board.full_rows()
        cleared = self.board.clear_rows(self.cleared_rows)
        self.last_clear = cleared
        if cleared:
            self.score += config.LINE_SCORES[cleared] * self.level
            self.lines += cleared
            self.level = self.lines // config.LINES_PER_LEVEL + 1
        self.hold_used = False
        self._spawn()
