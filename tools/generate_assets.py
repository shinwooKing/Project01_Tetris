"""Regenerate all PNG assets under assets/images/.

Usage:  python tools/generate_assets.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from tetris.assets import generate_all  # noqa: E402


def main():
    pygame.init()
    for path in generate_all():
        print(f"wrote {path}")
    pygame.quit()


if __name__ == "__main__":
    main()
