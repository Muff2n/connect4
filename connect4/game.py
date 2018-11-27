from connect4 import board
from connect4 import player

import numpy as np


class Connect4():
    def __init__(self,
                 player_o_name,
                 player_x_name,
                 player_o_human=False,
                 player_x_human=False,
                 height=6,
                 width=7,
                 win_length=4):
        # Check inputs are sane
        assert width >= win_length and height >= win_length
        # my has function converts to a u64
        assert height * width <= 64
        self.hash_value = np.array([2**x for x in range(height * width)])

        self._board = board.Board(self.hash_value, height, width, win_length)
        self._player_o = player.HumanPlayer(player_o_name, 0, self._board) if player_o_human else player.ComputerPlayer(player_o_name, 0, self._board)
        self._player_x = player.HumanPlayer(player_x_name, 1, self._board) if player_x_human else player.ComputerPlayer(player_x_name, 1, self._board)

    def play(self):
        print("Match between", self._player_o, " and ", self._player_x)
        self._board.display()
        while not self._board.result:
            if self._board.player_to_move == 'o':
                self._player_o.make_move()
            else:
                self._player_x.make_move()
            self._board.display()

        if self._board.result == 1:
            result = "o wins"
        elif self._board.result == 2:
            result = "x wins"
        else:
            result = "draw"

        print("The result is: ", result)
