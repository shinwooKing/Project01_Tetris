from tetris import config
from tetris.game import Game
from tetris.randomizer import BagRandomizer
from tetris.tetromino import PIECE_TYPES


def test_bag_deals_each_piece_once_per_seven():
    r = BagRandomizer(seed=1)
    for _ in range(3):
        assert sorted(r.next() for _ in range(7)) == sorted(PIECE_TYPES)


def test_hard_drop_locks_and_scores():
    g = Game(seed=0)
    start_y = g.current.y
    distance = g.ghost_y() - start_y
    g.hard_drop()
    assert g.score == distance * config.HARD_DROP_POINTS
    assert any(any(row) for row in g.board.grid)


def test_move_blocked_by_wall():
    g = Game(seed=0)
    while g.move(-1):
        pass
    assert min(x for x, _ in g.current.cells()) == 0


def test_rotation_wall_kick_off_left_wall():
    g = Game(seed=0)
    g._spawn("T")
    g.rotate(-1)            # vertical, nub pointing left
    while g.move(-1):
        pass
    assert g.rotate(1)      # needs a kick to fit
    assert min(x for x, _ in g.current.cells()) >= 0


def test_hold_swaps_once_per_piece():
    g = Game(seed=0)
    first = g.current.kind
    next_kind = g.queue[0]
    assert g.hold()
    assert g.hold_kind == first and g.current.kind == next_kind
    assert not g.hold()
    g.hard_drop()
    assert g.hold()
    assert g.current.kind == first


def test_line_clear_scoring_and_level():
    g = Game(seed=0)
    bottom = config.BOARD_HEIGHT - 1
    # Fill the bottom 4 rows except column 0, then drop a vertical I there.
    for y in range(bottom - 3, bottom + 1):
        g.board.place([(x, y) for x in range(1, config.BOARD_WIDTH)], "J")
    g._spawn("I")
    g.rotate(1)
    while g.move(-1):
        pass
    g.score = 0
    distance = g.ghost_y() - g.current.y
    g.hard_drop()
    assert g.last_clear == 4
    assert g.lines == 4
    assert g.score == 800 + distance * config.HARD_DROP_POINTS
    assert not any(any(row) for row in g.board.grid)


def test_gravity_and_lock_delay():
    g = Game(seed=0)
    kind = g.current.kind
    y0 = g.current.y
    g.update(config.gravity_interval(1) + 0.001)
    assert g.current.y == y0 + 1
    # Fall to the floor, then wait out the lock delay.
    for _ in range(200):
        g.update(0.1)
        if g.current.kind != kind or g.current.y == y0:
            break
    assert any(any(row) for row in g.board.grid)


def test_game_over_when_spawn_blocked():
    g = Game(seed=0)
    for y in range(config.BOARD_HEIGHT):
        g.board.place([(x, y) for x in range(3, 7)], "Z")
    g._spawn()
    assert g.game_over
