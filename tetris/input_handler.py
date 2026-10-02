"""Keyboard handling with DAS/ARR auto-repeat for horizontal movement."""
import pygame

from . import config

LEFT_KEYS = (pygame.K_LEFT,)
RIGHT_KEYS = (pygame.K_RIGHT,)
SOFT_DROP_KEYS = (pygame.K_DOWN,)
HARD_DROP_KEYS = (pygame.K_SPACE,)
ROTATE_CW_KEYS = (pygame.K_UP, pygame.K_x)
ROTATE_CCW_KEYS = (pygame.K_z, pygame.K_LCTRL, pygame.K_RCTRL)
HOLD_KEYS = (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT)
PAUSE_KEYS = (pygame.K_p, pygame.K_ESCAPE)


class InputHandler:
    """Translates pygame key events into Game actions."""

    def __init__(self):
        self._direction = 0      # -1 left, +1 right, 0 none
        self._das_timer = 0.0
        self._arr_timer = 0.0

    def reset(self):
        self._direction = 0
        self._das_timer = self._arr_timer = 0.0

    def handle_event(self, event, game) -> None:
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key in LEFT_KEYS or key in RIGHT_KEYS:
                self._direction = -1 if key in LEFT_KEYS else 1
                self._das_timer = self._arr_timer = 0.0
                game.move(self._direction)
            elif key in SOFT_DROP_KEYS:
                game.soft_dropping = True
            elif key in HARD_DROP_KEYS:
                game.hard_drop()
            elif key in ROTATE_CW_KEYS:
                game.rotate(1)
            elif key in ROTATE_CCW_KEYS:
                game.rotate(-1)
            elif key in HOLD_KEYS:
                game.hold()
        elif event.type == pygame.KEYUP:
            if event.key in SOFT_DROP_KEYS:
                game.soft_dropping = False
            elif (event.key in LEFT_KEYS and self._direction == -1) or (
                event.key in RIGHT_KEYS and self._direction == 1
            ):
                # Fall back to the other direction if it is still held.
                pressed = pygame.key.get_pressed()
                other = RIGHT_KEYS if self._direction == -1 else LEFT_KEYS
                self._direction = -self._direction if any(pressed[k] for k in other) else 0
                self._das_timer = self._arr_timer = 0.0

    def update(self, dt: float, game) -> None:
        if not self._direction:
            return
        self._das_timer += dt
        if self._das_timer < config.DAS:
            return
        self._arr_timer += dt
        while self._arr_timer >= config.ARR:
            self._arr_timer -= config.ARR
            if not game.move(self._direction):
                self._arr_timer = 0.0
                break
