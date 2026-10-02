"""Tetromino shapes, rotation states and SRS wall-kick data."""
from dataclasses import dataclass

# Each shape is listed in spawn orientation (rotation 0) on its bounding box.
SHAPES = {
    "I": ["....", "IIII", "....", "...."],
    "O": ["OO", "OO"],
    "T": [".T.", "TTT", "..."],
    "S": [".SS", "SS.", "..."],
    "Z": ["ZZ.", ".ZZ", "..."],
    "J": ["J..", "JJJ", "..."],
    "L": ["..L", "LLL", "..."],
}

PIECE_TYPES = tuple(SHAPES)

# SRS wall kicks, (dx, dy) with +y pointing DOWN (screen coordinates).
_JLSTZ_KICKS = {
    (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
}
_I_KICKS = {
    (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (1, 0): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
    (2, 1): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (2, 3): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (3, 0): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
}


def _cells_from_rows(rows):
    return [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != "."]


def _rotate_cw(cells, size):
    return [(size - 1 - y, x) for x, y in cells]


def _build_rotations():
    table = {}
    for kind, rows in SHAPES.items():
        size = len(rows)
        states = [sorted(_cells_from_rows(rows))]
        for _ in range(3):
            states.append(sorted(_rotate_cw(states[-1], size)))
        table[kind] = states
    return table


ROTATIONS = _build_rotations()


def kick_offsets(kind: str, from_rot: int, to_rot: int):
    """Offsets to try, in order, when rotating from one state to another."""
    if kind == "O":
        return [(0, 0)]
    table = _I_KICKS if kind == "I" else _JLSTZ_KICKS
    return table[(from_rot, to_rot)]


@dataclass
class Piece:
    """A falling tetromino: type, rotation state and top-left position on the board."""

    kind: str
    x: int = 0
    y: int = 0
    rotation: int = 0

    def cells(self, x=None, y=None, rotation=None):
        """Absolute board cells occupied by the piece (optionally at a hypothetical pose)."""
        x = self.x if x is None else x
        y = self.y if y is None else y
        rotation = self.rotation if rotation is None else rotation
        return [(x + cx, y + cy) for cx, cy in ROTATIONS[self.kind][rotation % 4]]

    @property
    def size(self) -> int:
        return len(SHAPES[self.kind])
