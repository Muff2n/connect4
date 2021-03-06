from oinkoink.board import Board

from oinkoink.neural.pytorch.data import Connect4Dataset, native_to_pytorch

import numpy as np
import pickle


def parse_line(line):
    x = line.split(',')
    if x[-1][0] == 'w':
        value = 1.0
    elif x[-1][0] == 'd':
        value = 0.5
    else:
        value = 0.0

    x = np.array([ord(i) for i in x[:-1]])
    x = np.flipud(np.transpose(x.reshape(7,6)))

    o_pieces = (x == 120)
    x_pieces = (x == 111)

    board = Board.from_pieces(o_pieces, x_pieces)
    return board, value


def read_8ply_data(add_fliplr: bool = False):
    with open('/home/richard/data/connect4/connect-4.data') as f:
        boards = []
        values = []
        for line in f:
            board, value = parse_line(line)
            boards.append(board)
            values.append(value)
            if add_fliplr and not board.symmetrical:
                boards.append(board.create_fliplr())
                values.append(value)
    return boards, values


boards, values = read_8ply_data()
with open('/home/richard/data/connect4/8ply_boards.pkl', 'wb') as f:
    pickle.dump(boards, f)
with open('/home/richard/data/connect4/8ply_values.pkl', 'wb') as f:
    pickle.dump(values, f)

board_t, value_t, _ = native_to_pytorch(boards, values)
data = Connect4Dataset(board_t, value_t, _)

data.save('/home/richard/data/connect4/connect4dataset_8ply.pth')
