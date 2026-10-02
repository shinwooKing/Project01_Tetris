"""Main loop and screen states (title, playing, paused, game over)."""
import pygame

from . import config
from .assets import Assets
from .game import Game
from .input_handler import PAUSE_KEYS, InputHandler
from .renderer import Renderer

TITLE, PLAYING, PAUSED, GAME_OVER = "title", "playing", "paused", "game_over"


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.assets = Assets()
        pygame.display.set_icon(self.assets.blocks["T"])
        self.renderer = Renderer(self.screen, self.assets)
        self.input = InputHandler()
        self.game = Game()
        self.state = TITLE
        self.high_score = 0
        self._flash_rows = []
        self._flash_timer = 0.0
        self.running = True

    def new_game(self):
        self.game = Game()
        self.input.reset()
        self._flash_rows = []
        self.state = PLAYING

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if self.state in (TITLE, GAME_OVER) and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.new_game()
                return
            if event.key in PAUSE_KEYS and self.state in (PLAYING, PAUSED):
                self.state = PAUSED if self.state == PLAYING else PLAYING
                self.input.reset()
                self.game.soft_dropping = False
                return
            if self.state == TITLE and event.key == pygame.K_ESCAPE:
                self.running = False
                return
        if self.state == PLAYING:
            self.input.handle_event(event, self.game)

    def update(self, dt):
        if self._flash_timer > 0:
            self._flash_timer -= dt
            if self._flash_timer <= 0:
                self._flash_rows = []
        if self.state != PLAYING:
            return
        self.input.update(dt, self.game)
        self.game.update(dt)
        self._check_lock_events()

    def _check_lock_events(self):
        if self.game.cleared_rows:
            # Rows above the cleared ones shift down; flash where the clear happened.
            self._flash_rows = self.game.cleared_rows
            self._flash_timer = config.LINE_CLEAR_FLASH
            self.game.cleared_rows = []
        if self.game.game_over:
            self.high_score = max(self.high_score, self.game.score)
            self.state = GAME_OVER

    def draw(self):
        overlay = None
        if self.state == TITLE:
            overlay = ("TETRIS", "Press ENTER to start")
        elif self.state == PAUSED:
            overlay = ("PAUSED", "Press P to resume")
        elif self.state == GAME_OVER:
            overlay = ("GAME OVER", f"Best {self.high_score:,}  -  ENTER")
        self.renderer.draw(self.game, self._flash_rows, overlay, show_piece=self.state != TITLE)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
                # Hard drop / hold happen inside event handling; react right away.
                if self.state == PLAYING:
                    self._check_lock_events()
            self.update(dt)
            self.draw()
        pygame.quit()
