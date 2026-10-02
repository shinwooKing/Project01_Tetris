"""7-bag random piece generator."""
import random

from .tetromino import PIECE_TYPES


class BagRandomizer:
    """Deals all seven pieces in a shuffled order before refilling the bag."""

    def __init__(self, seed=None):
        self._rng = random.Random(seed)
        self._bag = []

    def next(self) -> str:
        if not self._bag:
            self._bag = list(PIECE_TYPES)
            self._rng.shuffle(self._bag)
        return self._bag.pop()
