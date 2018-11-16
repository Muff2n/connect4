from src import game
import pytest

import numpy as np


# Board tests
pieces_1 = [
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [1, 1, 1, 1, 0, 0, 0]], dtype=np.bool_),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0, 0],
              [1, 1, 1, 0, 0, 0, 0]], dtype=np.bool_),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 1, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 1, 1, 1],
              [0, 0, 0, 1, 0, 1, 0]], dtype=np.bool_),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0, 0],
              [1, 1, 1, 0, 0, 0, 0]], dtype=np.bool_)


    ]
pieces_2 = [
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [1, 1, 1, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0]], dtype=np.bool_),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [1, 0, 1, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0]], dtype=np.bool_),
    np.array([[0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 0, 1, 1],
              [0, 0, 0, 0, 1, 1, 1],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 1, 0, 1]], dtype=np.bool_),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0, 0],
              [1, 1, 1, 0, 0, 0, 0]], dtype=np.bool_)
    ]
ans = [1, 1, 1, 1]


@pytest.mark.parametrize("n,pieces_1,pieces_2,ans",
                         [(n, p1, p2, a) for n, p1, p2, a in zip(range(len(ans)), pieces_1, pieces_2, ans)])
def test_check_valid(n, pieces_1, pieces_2, ans):
    print("test_check_valid", n)
    board = game.Board(white_pieces=pieces_1,
                       black_pieces=pieces_2)

    assert board.check_valid()
    assert board.check_terminal_position() == ans
    return
