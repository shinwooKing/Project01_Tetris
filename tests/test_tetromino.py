from tetris.tetromino import ROTATIONS, Piece, kick_offsets


def test_every_state_has_four_cells():
    for states in ROTATIONS.values():
        assert len(states) == 4
        assert all(len(cells) == 4 for cells in states)


def test_four_rotations_return_to_start():
    p = Piece("T", 3, 0)
    start = sorted(p.cells())
    for _ in range(4):
        p.rotation = (p.rotation + 1) % 4
    assert sorted(p.cells()) == start


def test_o_piece_does_not_change_shape():
    assert len({tuple(s) for s in ROTATIONS["O"]}) == 1
    assert kick_offsets("O", 0, 1) == [(0, 0)]


def test_kicks_start_with_no_offset():
    for kind in "IJLSTZ":
        for a in range(4):
            for b in ((a + 1) % 4, (a - 1) % 4):
                assert kick_offsets(kind, a, b)[0] == (0, 0)
