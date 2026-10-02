from tetris.board import Board


def test_fits_and_bounds():
    b = Board(4, 4)
    assert b.fits([(0, 0), (3, 3)])
    assert not b.fits([(-1, 0)])
    assert not b.fits([(0, 4)])
    b.place([(1, 1)], "T")
    assert not b.fits([(1, 1)])


def test_clear_rows_shifts_down():
    b = Board(3, 4)
    b.place([(0, 3), (1, 3), (2, 3)], "I")  # full bottom row
    b.place([(1, 2)], "T")                  # block above it
    assert b.full_rows() == [3]
    assert b.clear_full_rows() == 1
    assert b.grid[3] == [None, "T", None]
    assert b.grid[0] == [None, None, None]
