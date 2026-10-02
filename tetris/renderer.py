"""Draws the game state to a pygame surface."""
import pygame

from . import config
from .tetromino import ROTATIONS

LEFT_PANEL_X = 20
RIGHT_PANEL_X = config.BOARD_X + config.BOARD_WIDTH * config.CELL_SIZE + 20
PANEL_W = 140


class Renderer:
    def __init__(self, screen: pygame.Surface, assets):
        self.screen = screen
        self.assets = assets
        self.font_big = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 22)
        self.board_rect = pygame.Rect(
            config.BOARD_X,
            config.BOARD_Y,
            config.BOARD_WIDTH * config.CELL_SIZE,
            config.VISIBLE_HEIGHT * config.CELL_SIZE,
        )

    # ----- helpers ----------------------------------------------------------
    def _cell_pos(self, x, y):
        """Board cell -> screen pixel (hidden rows map above the visible board)."""
        return (
            config.BOARD_X + x * config.CELL_SIZE,
            config.BOARD_Y + (y - config.HIDDEN_ROWS) * config.CELL_SIZE,
        )

    def _text(self, text, font, color, pos, center=False):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
        self.screen.blit(surf, rect)

    def _panel(self, rect, title):
        pygame.draw.rect(self.screen, config.PANEL_COLOR, rect, border_radius=6)
        pygame.draw.rect(self.screen, config.BORDER_COLOR, rect, 2, border_radius=6)
        self._text(title, self.font_small, config.DIM_TEXT_COLOR, (rect.x + 10, rect.y + 8))

    def _mini_piece(self, kind, center):
        """Draw a small preview of a piece centered at `center`."""
        img = self.assets.small_blocks[kind]
        s = img.get_width()
        cells = ROTATIONS[kind][0]
        xs = [x for x, _ in cells]
        ys = [y for _, y in cells]
        w = (max(xs) - min(xs) + 1) * s
        h = (max(ys) - min(ys) + 1) * s
        ox = center[0] - w // 2 - min(xs) * s
        oy = center[1] - h // 2 - min(ys) * s
        for x, y in cells:
            self.screen.blit(img, (ox + x * s, oy + y * s))

    # ----- sections ---------------------------------------------------------
    def draw_board(self, game, flash_rows=(), show_piece=True):
        pygame.draw.rect(self.screen, (8, 8, 16), self.board_rect)
        # Faint grid inside the well.
        for x in range(config.BOARD_WIDTH + 1):
            px = config.BOARD_X + x * config.CELL_SIZE
            pygame.draw.line(self.screen, (30, 30, 50), (px, self.board_rect.top), (px, self.board_rect.bottom))
        for y in range(config.VISIBLE_HEIGHT + 1):
            py = config.BOARD_Y + y * config.CELL_SIZE
            pygame.draw.line(self.screen, (30, 30, 50), (self.board_rect.left, py), (self.board_rect.right, py))

        clip = self.screen.get_clip()
        self.screen.set_clip(self.board_rect)
        for y, row in enumerate(game.board.grid):
            for x, kind in enumerate(row):
                if kind:
                    self.screen.blit(self.assets.blocks[kind], self._cell_pos(x, y))

        if show_piece and not game.game_over:
            piece = game.current
            ghost_y = game.ghost_y()
            for x, y in piece.cells(y=ghost_y):
                self.screen.blit(self.assets.ghost, self._cell_pos(x, y))
            for x, y in piece.cells():
                self.screen.blit(self.assets.blocks[piece.kind], self._cell_pos(x, y))

        for y in flash_rows:
            _, py = self._cell_pos(0, y)
            flash = pygame.Surface((self.board_rect.width, config.CELL_SIZE), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 150))
            self.screen.blit(flash, (self.board_rect.left, py))
        self.screen.set_clip(clip)
        pygame.draw.rect(self.screen, config.BORDER_COLOR, self.board_rect.inflate(6, 6), 3, border_radius=4)

    def draw_side_panels(self, game):
        hold_rect = pygame.Rect(LEFT_PANEL_X, config.BOARD_Y, PANEL_W, 110)
        self._panel(hold_rect, "HOLD")
        if game.hold_kind:
            self._mini_piece(game.hold_kind, (hold_rect.centerx, hold_rect.centery + 10))
            if game.hold_used:
                veil = pygame.Surface(hold_rect.size, pygame.SRCALPHA)
                veil.fill((0, 0, 0, 120))
                self.screen.blit(veil, hold_rect)

        stats = [("SCORE", f"{game.score:,}"), ("LEVEL", str(game.level)), ("LINES", str(game.lines))]
        y = hold_rect.bottom + 20
        for label, value in stats:
            rect = pygame.Rect(LEFT_PANEL_X, y, PANEL_W, 70)
            self._panel(rect, label)
            self._text(value, self.font, config.TEXT_COLOR, (rect.centerx, rect.y + 45), center=True)
            y = rect.bottom + 12

        keys = ["<- -> move", "DOWN soft drop", "SPACE hard drop", "UP / X rotate", "Z rotate back", "C hold", "P pause"]
        y += 8
        for line in keys:
            self._text(line, self.font_small, config.DIM_TEXT_COLOR, (LEFT_PANEL_X + 4, y))
            y += 20

        next_rect = pygame.Rect(RIGHT_PANEL_X, config.BOARD_Y, PANEL_W, 60 + 70 * config.NEXT_QUEUE_SIZE)
        self._panel(next_rect, "NEXT")
        for i, kind in enumerate(game.queue):
            self._mini_piece(kind, (next_rect.centerx, next_rect.y + 65 + i * 70))

    def draw_overlay(self, title, subtitle=None):
        veil = pygame.Surface(self.board_rect.size, pygame.SRCALPHA)
        veil.fill(config.OVERLAY_COLOR)
        self.screen.blit(veil, self.board_rect)
        cx, cy = self.board_rect.center
        self._text(title, self.font_big, config.TEXT_COLOR, (cx, cy - 20), center=True)
        if subtitle:
            self._text(subtitle, self.font, config.DIM_TEXT_COLOR, (cx, cy + 25), center=True)

    def draw(self, game, flash_rows=(), overlay=None, show_piece=True):
        self.screen.blit(self.assets.background, (0, 0))
        self.draw_board(game, flash_rows, show_piece)
        self.draw_side_panels(game)
        if overlay:
            self.draw_overlay(*overlay)
