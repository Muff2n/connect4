from oinkoink.board import Board
from oinkoink.mcts import MCTSConfig, PositionEvaluation
from oinkoink.evaluators import Evaluator
from oinkoink.player import BasePlayer
from oinkoink.tree import BaseNodeData, Tree
from oinkoink.utils import Connect4Stats as info
from oinkoink.utils import (same_side,
                            Side,
                            value_to_side,
                            Result)

from anytree import Node
from collections import deque, namedtuple
import math
import numpy as np
from typing import (Callable,
                    Dict,
                    List,
                    Optional,
                    Set,
                    Tuple)

import os


class SearchEvaluation():
    def __init__(self):
        self.value_sum = 0.0
        self.visit_count = 0
        self.ghost_count = 0

    def add(self, value: float):
        self.value_sum += value
        self.visit_count += 1

    def add_ghost(self):
        self.ghost_count += 1

    def replace_ghost(self, value: float):
        assert self.ghost_count > 0
        self.ghost_count -= 1
        self.add(value)

    def __float__(self):
        assert (self.visit_count + self.ghost_count) != 0
        return float(self.value_sum / (self.visit_count + self.ghost_count))

    def __str__(self):
        return str(self.__float__())

    def __repr__(self):
        return "value: " + str(self.__float__()) + \
            ",  value_sum: " + str(self.value_sum) + \
            ",  visit_count: " + str(self.visit_count) + \
            ",  ghost_count: " + str(self.ghost_count)


TerminalResult = namedtuple('TerminalResult', ['result', 'age'])


class NodeData(BaseNodeData):
    def __init__(self, board: Board):
        super().__init__(board)
        self.terminal_result: Optional[TerminalResult] = None
        self.terminal_moves: Set[int] = set()
        self.search_value = SearchEvaluation()

    @property
    def search_value(self):
        if self._search_value.visit_count == 0:
            return None
        else:
            return self._search_value

    @search_value.setter
    def search_value(self, value):
        if isinstance(value, SearchEvaluation):
            self._search_value = value

    @property
    def non_terminal_moves(self):
        return self.valid_moves.difference(self.terminal_moves)

    def value(self, side: Side):
        if self.terminal_result is not None:
            return value_to_side(float(self.terminal_result.result.value),
                                 side)
        return super().value(side)

    def __str__(self):
        return "terminal_result: " + str(self.terminal_result) + \
            "  " + super().__str__()

    def __repr__(self):
        return super().__repr__() + \
            "   terminal_result: " + str(self.terminal_result) + \
            ",  terminal_moves: " + str(self.terminal_moves)


class MCTS_PARALLEL(BasePlayer):
    def __init__(self,
                 name: str,
                 config: MCTSConfig,
                 evaluator: Evaluator):
        super().__init__(name)
        self.config = config
        self.evaluator = evaluator

    def make_move(self, board):
        tree = Tree(board,
                    self.evaluator.result_table,
                    NodeData)

        search(self.config, tree, self.evaluator)

        if board.age >= self.config.num_sampling_moves:
            move, value = self.select_best_move(tree)
        else:
            move, value = tree.select_softmax_move()

        board.make_move(move)
        # Note that because we select the action greedily, the value of the root is equal to the perceived value of the 'best value' child
        # We need to return the value of the position to 'player_o'
        return move, value, tree

    def select_best_move(self, tree) -> Tuple[int, float]:
        if tree.root.data.terminal_result is None:
            move, value = tree.select_best_move()
        # choose shortest win
        elif same_side(tree.root.data.terminal_result.result, tree.side):
            _, _, move, value = max((tree.get_node_value(c),
                                     info.area - c.data.terminal_result.age,
                                     c.name,
                                     tree.get_node_value(c, Side.o))
                                    for c in tree.root.children
                                 if c.name in tree.root.data.terminal_moves)
        # else longest loss (or draw = 42)
        else:
            _, _, move, value = max((tree.get_node_value(c),
                                     c.data.terminal_result.age,
                                     c.name,
                                     tree.get_node_value(c, Side.o))
                                    for c in tree.root.children
                                    if c.name in tree.root.data.terminal_moves)

        return move, value

    def __str__(self):
        return super().__str__() + ", type: Computer"


def search(config: MCTSConfig,
           tree: Tree,
           evaluator: Callable[[Board],
                               Tuple[float, List[float]]]):
    ghost_nodes = deque()
    for _ in range(config.simulations):
        node = tree.root

        if not tree.root.data.non_terminal_moves:
            break

        while node.children:
            node = select_child(config, tree, node)

        # previously evaluated, so expand
        if node.data.position_value is not None:
            tree.expand_node(node, 1)
            node = select_child(config, tree, node)

        board = node.data.board
        # encountered a new terminal position
        if board.result is not None:
            node = backpropagate_terminal(node,
                                          board.result,
                                          board.age)
            value = board.result.value
        else:
            value, prior = evaluator(board)
            if value is None:
                ghost_nodes.append(node)
                # give it a loss and a flat prior
                node.data.position_value = PositionEvaluation(
                    value_to_side(0.0, board._player_to_move),
                    np.ones((info.width,)))
            else:
                node.data.position_value = PositionEvaluation(value, prior)

        if value is not None:
            backpropagate(node, lambda x: x.data._search_value.add(value))
        else:
            backpropagate(node, lambda x: x.data._search_value.add_ghost())

        if ghost_nodes and evaluator.has_update():
            while ghost_nodes and ghost_nodes[0].data.board in evaluator.position_table:
                node = ghost_nodes.popleft()
                value, prior = evaluator.position_table[node.data.board]
                node.data.position_value = PositionEvaluation(value, prior)
                backpropagate(node, lambda x: x.data._search_value.replace_ghost(value))

    while ghost_nodes:
        if evaluator.has_update():
            while ghost_nodes and ghost_nodes[0].data.board in evaluator.position_table:
                node = ghost_nodes.popleft()
                value, prior = evaluator.position_table[node.data.board]
                node.data.position_value = PositionEvaluation(value, prior)
                backpropagate(node, lambda x: x.data._search_value.replace_ghost(value))

    return


def select_child(config: MCTSConfig,
                 tree: Tree,
                 node: Node):
    non_terminal_children = [child for child in node.children if
                             child.name not in node.data.terminal_moves]
    _, child = max((ucb_score(config, tree, node, child), i)
                   for i, child in enumerate(non_terminal_children))

    return non_terminal_children[child]


def ucb_score(config: MCTSConfig,
              tree: Tree,
              node: Node,
              child: Node):
    pb_c = math.log((node.data._search_value.visit_count + config.pb_c_base + 1) /
                    config.pb_c_base) + config.pb_c_init
    pb_c *= math.sqrt(node.data._search_value.visit_count) / (child.data._search_value.visit_count + 1)

    pb_c = pb_c * (
        math.sqrt(node.data._search_value.visit_count)
        / (child.data._search_value.visit_count + 1))

    prior_score = pb_c * node.data.position_value.prior[child.name]
    value_score = tree.get_node_value(child)
    return prior_score + value_score


def backpropagate_terminal(node: Node,
                           result: Result,
                           age: int):
    node.data.terminal_result = TerminalResult(result, age)

    if node.is_root:
        return node

    node.parent.data.terminal_moves.add(node.name)
    node = node.parent

    # The side to move can choose a win - they choose the quickest forcing line
    if same_side(result, node.data.board._player_to_move):
        age = min((c.data.terminal_result.age
                   for c in node.children
                   if c.name in node.data.terminal_moves))
        return backpropagate_terminal(node, result, age)
    # The parent only has continuations that lead to terminal results
    # None of them can be winning for this node, because otherwise we would
    # have previously set the terminal value of this node, and never visited it
    # again in the mcts
    elif not node.data.non_terminal_moves:
        # the parent will now choose a draw if possible
        # if forced to choose a loss, will choose the longest one
        # N.B. in connect4 all draws have age 42
        _, age, idx = max((value_to_side(c.data.terminal_result.result.value,
                                         node.data.board._player_to_move),
                           c.data.terminal_result.age,
                           i)
                          for i, c in enumerate(node.children))
        result = node.children[idx].data.terminal_result.result
        return backpropagate_terminal(node, result, age)

    # nothing to do
    return node


def backpropagate(node: Node,
                  function: Callable):
    function(node)
    while not node.is_root:
        node = node.parent
        function(node)
# def backpropagate(node: Node,
#                   value: float):
#     node.data._search_value.add(value)
#     while not node.is_root:
#         node = node.parent
#         node.data._search_value.add(value)


def backpropagate_ghost(node: Node):
    node.data._search_value.add_ghost()
    while not node.is_root:
        node = node.parent
        node.data._search_value.add_ghost()


def backpropagate_replace_ghost(node: Node,
                                value: float):
    node.data._search_value.replace_ghost(value)
    while not node.is_root:
        node = node.parent
        node.data._search_value.replace_ghost(value)


def add_exploration_noise(config: MCTSConfig,
                          prior: np.ndarray,
                          valid_moves: Set):
    if config.root_dirichlet_alpha and config.root_exploration_fraction:
        noise = np.random.gamma(config.root_dirichlet_alpha,
                                1,
                                info.width)
        frac = config.root_exploration_fraction
        prior = prior * (1 - frac) + noise * frac
        prior = normalise_prior(valid_moves, prior)
    return prior


def normalise_prior(valid_moves: Set, prior: np.ndarray):
    invalid_moves = set(range(info.width)).difference(valid_moves)
    if invalid_moves:
        np.put(prior, list(invalid_moves), 0.0)
    prior = prior / np.sum(prior)
    return prior
