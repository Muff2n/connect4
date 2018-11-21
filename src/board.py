from src.utils import advance_player

import numpy as np


class Board():
    def __init__(self,
                 height=6,
                 width=7,
                 win_length=4,
                 white_pieces=None,
                 black_pieces=None):
        # Check inputs are sane
        assert width >= win_length and height >= win_length

        self._width = width
        self._height = height
        self._win_length = win_length
        self.white_pieces = np.zeros((self._height, self._width), dtype=np.bool_) if white_pieces is None else white_pieces
        self.black_pieces = np.zeros((self._height, self._width), dtype=np.bool_) if black_pieces is None else black_pieces

        self.player_to_move = np.count_nonzero(self.white_pieces) - np.count_nonzero(self.black_pieces)
        self.result = None

        self._check_valid()

    @property
    def player_to_move(self):
        return 'o' if self._player_to_move == 0 else 'x'

    @player_to_move.setter
    def player_to_move(self, player_to_move):
        assert player_to_move in [0, 1]
        self._player_to_move = player_to_move

    def display(self):
        display = np.chararray(self.white_pieces.shape)
        display[:] = ' '
        display[self.white_pieces] = 'o'
        display[self.black_pieces] = 'x'
        print(display.decode('utf-8'))

    def _get_pieces(self):
        return self.white_pieces + self.black_pieces

    def valid_moves(self):
        pieces = self._get_pieces()
        return [i for i in range(self._width) if not all(pieces[:,i])]

    def _check_straight(self, pieces):
        """Returns the number of horizontal wins"""
        count = 0
        for i in range(pieces.shape[1]):
            for j in range(pieces.shape[0] - self._win_length + 1):
                if np.all(pieces[j:j+self._win_length, i]):
                    count += 1
        return count

    def _check_diagonal(self, pieces):
        """Returns the number of diagonally down and right winners"""
        count = 0
        for i in range(pieces.shape[0] - self._win_length + 1):
            for j in range(pieces.shape[1] - self._win_length + 1):
                if np.count_nonzero([pieces[i+x, j+x] for x in range(self._win_length)]) == self._win_length:
                    count += 1
        return count

    def check_for_winner(self, pieces=None):
        if pieces is None:
            pieces = self.black_pieces if self._player_to_move else self.white_pieces

        return \
            self._check_straight(pieces) + \
            self._check_straight(np.transpose(pieces)) + \
            self._check_diagonal(pieces) + \
            self._check_diagonal(np.fliplr(pieces))

    def check_terminal_position(self):
        if self.check_for_winner(self.white_pieces):
            self.result = 0
        elif self.check_for_winner(self.black_pieces):
            self.result = 1
        elif np.all(self._get_pieces()):
            self.result = 2

    def make_move(self, move):
        board = self._get_pieces()
        idx = self._height - np.count_nonzero(board[:, move]) - 1
        if self._player_to_move:
            self.black_pieces[idx, move] = 1
        else:
            self.white_pieces[idx, move] = 1
        self.player_to_move = advance_player(self._player_to_move)
        # FIXME: remove when working
        self._check_valid()
        self.check_terminal_position()

    def _check_valid(self):
        no_gaps = True
        for col in range(self._width):
            board = self._get_pieces()
            if not np.array_equal(board[:, col], np.sort(board[:, col])):
                no_gaps = False

        assert no_gaps
        assert not np.any(np.logical_and(self.white_pieces, self.black_pieces))
        assert np.sum(self.white_pieces) - np.sum(self.black_pieces)  in [0, 1]
        #assert self.check_for_winner(self.white_pieces) + self.check_for_winner(self.black_pieces) in [0,1]
        assert (self.check_for_winner(self.white_pieces) == 0) or (self._player_to_move == 1)
        assert (self.check_for_winner(self.black_pieces) == 0) or (self._player_to_move == 0)
        assert self.white_pieces.shape == (self._height, self._width)
        assert self.black_pieces.shape == (self._height, self._width)
