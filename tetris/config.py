"""Game-wide constants: sizes, colors, timings."""
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT_DIR / "assets" / "images"

# Board
BOARD_WIDTH = 10
VISIBLE_HEIGHT = 20
HIDDEN_ROWS = 2
BOARD_HEIGHT = VISIBLE_HEIGHT + HIDDEN_ROWS

# Layout (pixels)
CELL_SIZE = 30
BOARD_X = 180
BOARD_Y = 40
SIDE_PANEL_WIDTH = 160
SCREEN_WIDTH = BOARD_X + BOARD_WIDTH * CELL_SIZE + SIDE_PANEL_WIDTH + 20
SCREEN_HEIGHT = BOARD_Y + VISIBLE_HEIGHT * CELL_SIZE + 40
FPS = 60
TITLE = "Python Tetris"

# Colors (guideline palette)
PIECE_COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 220, 0),
    "Z": (240, 0, 0),
    "J": (0, 80, 240),
    "L": (240, 160, 0),
}
TEXT_COLOR = (230, 230, 240)
DIM_TEXT_COLOR = (140, 140, 160)
PANEL_COLOR = (25, 25, 40)
BORDER_COLOR = (90, 90, 130)
OVERLAY_COLOR = (0, 0, 0, 170)

# Timing (seconds)
LOCK_DELAY = 0.5
MAX_LOCK_RESETS = 15
SOFT_DROP_FACTOR = 20
DAS = 0.17
ARR = 0.05
LINE_CLEAR_FLASH = 0.15

# Scoring
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
SOFT_DROP_POINTS = 1
HARD_DROP_POINTS = 2
LINES_PER_LEVEL = 10
NEXT_QUEUE_SIZE = 5


def gravity_interval(level: int) -> float:
    """Seconds per row at the given level (Tetris Guideline formula)."""
    level = max(1, level)
    return (0.8 - (level - 1) * 0.007) ** (level - 1)
