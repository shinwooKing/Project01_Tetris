"""Procedurally generated image assets: block tiles, ghost tile and background.

Images are drawn with pygame and saved as PNG under assets/images/. When the game
starts, missing images are generated automatically.
"""
import pygame

from . import config

BLOCK_FILES = {kind: f"block_{kind}.png" for kind in config.PIECE_COLORS}
GHOST_FILE = "ghost.png"
BACKGROUND_FILE = "background.png"


def _shade(color, factor):
    """factor > 1 lightens toward white, factor < 1 darkens toward black."""
    if factor >= 1:
        return tuple(min(255, int(c + (255 - c) * (factor - 1))) for c in color)
    return tuple(int(c * factor) for c in color)


def draw_block(color, size=config.CELL_SIZE) -> pygame.Surface:
    """A beveled tile: light top/left edge, dark bottom/right edge and an inner gloss."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    bevel = max(3, size // 8)
    surf.fill(color)
    light, dark = _shade(color, 1.55), _shade(color, 0.55)
    pygame.draw.polygon(surf, light, [(0, 0), (size, 0), (size - bevel, bevel), (bevel, bevel), (bevel, size - bevel), (0, size)])
    pygame.draw.polygon(surf, dark, [(size, size), (0, size), (bevel, size - bevel), (size - bevel, size - bevel), (size - bevel, bevel), (size, 0)])
    # Inner face with a soft vertical gradient.
    inner = pygame.Rect(bevel, bevel, size - 2 * bevel, size - 2 * bevel)
    for i in range(inner.height):
        t = i / max(1, inner.height - 1)
        pygame.draw.line(surf, _shade(color, 1.15 - 0.3 * t), (inner.left, inner.top + i), (inner.right - 1, inner.top + i))
    # Gloss highlight.
    gloss = pygame.Surface((inner.width // 2, inner.height // 3), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, 70))
    surf.blit(gloss, (inner.left + 2, inner.top + 2))
    pygame.draw.rect(surf, (0, 0, 0, 120), surf.get_rect(), 1)
    return surf


def draw_ghost(size=config.CELL_SIZE) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((255, 255, 255, 35))
    pygame.draw.rect(surf, (255, 255, 255, 160), surf.get_rect(), 2)
    return surf


def draw_background(width=config.SCREEN_WIDTH, height=config.SCREEN_HEIGHT) -> pygame.Surface:
    surf = pygame.Surface((width, height))
    top, bottom = (18, 18, 38), (6, 6, 14)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
        pygame.draw.line(surf, color, (0, y), (width, y))
    grid = (28, 28, 52)
    step = config.CELL_SIZE
    for x in range(0, width, step):
        pygame.draw.line(surf, grid, (x, 0), (x, height))
    for y in range(0, height, step):
        pygame.draw.line(surf, grid, (0, y), (width, y))
    return surf


def generate_all(directory=config.IMAGE_DIR) -> list:
    """Draw every asset and save it as PNG. Returns the written paths."""
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    images = {name: draw_block(config.PIECE_COLORS[kind]) for kind, name in BLOCK_FILES.items()}
    images[GHOST_FILE] = draw_ghost()
    images[BACKGROUND_FILE] = draw_background()
    for name, surf in images.items():
        path = directory / name
        pygame.image.save(surf, str(path))
        written.append(path)
    return written


class Assets:
    """Loads images from disk (generating them first if any are missing)."""

    def __init__(self, directory=config.IMAGE_DIR):
        names = [*BLOCK_FILES.values(), GHOST_FILE, BACKGROUND_FILE]
        if not all((directory / n).exists() for n in names):
            generate_all(directory)
        self.blocks = {kind: self._load(directory / name) for kind, name in BLOCK_FILES.items()}
        self.ghost = self._load(directory / GHOST_FILE)
        self.background = self._load(directory / BACKGROUND_FILE, alpha=False)
        self.small_blocks = {
            kind: pygame.transform.smoothscale(img, (config.CELL_SIZE * 2 // 3,) * 2)
            for kind, img in self.blocks.items()
        }

    @staticmethod
    def _load(path, alpha=True):
        img = pygame.image.load(str(path))
        return img.convert_alpha() if alpha else img.convert()
