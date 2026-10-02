"""The playfield grid: collision checks, locking pieces and clearing lines."""
from . import config


class Board:
    """A grid of cells; each cell is None (empty) or a piece-type letter."""

    def __init__(self, width=config.BOARD_WIDTH, height=config.BOARD_HEIGHT):
        self.width = width
        self.height = height
        self.grid = [[None] * width for _ in range(height)]

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_free(self, x: int, y: int) -> bool:
        return self.inside(x, y) and self.grid[y][x] is None

    def fits(self, cells) -> bool:
        return all(self.is_free(x, y) for x, y in cells)

    def place(self, cells, kind: str) -> None:
        for x, y in cells:
            self.grid[y][x] = kind

    def full_rows(self):
        return [y for y, row in enumerate(self.grid) if all(row)]

    def clear_rows(self, rows) -> int:
        """Remove the given rows and shift everything above down. Returns rows removed."""
        rows = set(rows)
        kept = [row for y, row in enumerate(self.grid) if y not in rows]
        self.grid = [[None] * self.width for _ in rows] + kept
        return len(rows)

    def clear_full_rows(self) -> int:
        return self.clear_rows(self.full_rows())
