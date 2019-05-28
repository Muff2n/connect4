from connect4.board_c import Board
from connect4.player import BasePlayer

from copy import copy
from typing import List, Sequence


def training_game(player: BasePlayer):
    board = Board()
    game_data = GameData()
    while board.result is None:
        move, value, tree = player.make_move(board)
        prior = tree.get_policy()
        game_data.add_move(copy(board), move, value, prior)

    game_data.result = board.result

    return game_data


class TrainingData:
    def __init__(self,
                 boards: List[Board],
                 values: List[float],
                 priors: List[Sequence[float]]):
        self.boards = boards
        self.values = values
        self.priors = priors

    def __add__(self, other: 'TrainingData'):
        return TrainingData(self.boards + other.boards,
                            self.values + other.values,
                            self.priors + other.priors)
                            # self.values = np.concatenate((self.values, other.values), 0)

    def __repr__(self):
        return str([(b, v, p) for b, v, p in zip(self.boards,
                                                 self.values,
                                                 self.priors)])


class GameData():
    def __init__(self):
        self.result = None
        self.moves = []
        self.boards = []
        self.values = []
        self.priors = []
        self.result = None

    def add_move(self, board, move, value, prior):
        self.moves.append(move)
        self.boards.append(board)
        self.values.append(value)
        self.priors.append(prior)

    def create_training_values(self):
        assert self.result is not None
        # FIXME: TD(lambda) algorithm?
        # self.values = (np.array(self.values, dtype='float') + result.value) / 2.0
        return [self.result.value] * len(self.values)

    @property
    def data(self):
        assert self.result is not None
        return TrainingData(self.boards,
                            self.create_training_values(),
                            self.priors)

    def __str__(self):
        return "Result: {}, Game: {}, Data: {}".format(self.result,
                                                       self.game,
                                                       self.data)
