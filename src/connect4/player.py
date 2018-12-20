from src.connect4 import tree

from src.connect4.utils import Connect4Stats as info

import numpy as np


class BasePlayer():
    def __init__(self, name, side):
        self.name = name
        self.side = side

    def __str__(self):
        return "Player: " + self.name


class HumanPlayer(BasePlayer):
    def __init__(self, name, side):
        super().__init__(name, side)

    def make_move(self, board):
        move = -1
        while move not in board.valid_moves():
            try:
                move = int(input("Enter player " + board.player_to_move + "'s move:"))
            except ValueError:
                pass
            print("Try again dipshit")
        board.make_move(int(move))
        return move

    def __str__(self):
        return super().__str__() + ", type: Human"


class ComputerPlayer(BasePlayer):
    def __init__(self, name, side, depth):
        super().__init__(name, side)
        self.tree = tree.Connect4Tree(self.evaluate_position)
        self.depth = depth
        # static member

    def make_move(self, board):
        self.tree.update_root(board)
        self.tree.expand_node(self.tree.root, self.depth)
        self.tree.nega_max(self.tree.root, self.depth, self.side)

        moves = np.array([(n.name) for n in self.tree.root.children])
        values = np.array([(n.data.node_eval.get_value()) for n in self.tree.root.children])
        idx = np.argmax(values * self.side)
        best_moves = moves[values == values[idx]]
        best_move_value = values[idx]

        best_move = moves[idx]
        #distance_to_middle = np.abs(best_moves - info.width / 2.0)
        #idx = np.argsort(distance_to_middle)
        #best_move = best_moves[idx[0]]

        if best_move_value == self.side:
            print("Trash! I will crush you.")
        elif best_move_value == -1 * self.side:
            print("Ah fuck you lucky shit")

        print("Best move selected: ", best_move)
        board.make_move(best_move)

        return best_move

    @staticmethod
    def evaluate_position(board):
        # return np.sum(np.multiply(board.o_pieces, info.value_grid) - np.multiply(board.x_pieces, info.value_grid)) / float(info.value_grid_sum)
        return (np.einsum('ij,ij', board.o_pieces, info.value_grid) - np.einsum('ij,ij', board.x_pieces, info.value_grid)) / float(info.value_grid_sum)

    def __str__(self):
        return super().__str__() + ", type: Computer"
