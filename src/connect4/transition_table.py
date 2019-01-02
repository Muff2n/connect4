from sortedcontainers import SortedSet


class Entry():
    def __init__(self, board, node_data):
        self.age = board.age
        self.table = dict()
        self.table[board] = node_data

    def __eq__(self, obj):
        return self.age == obj.age


class TransitionTable():
    def __init__(self):
        # table is a list of lists. The inner list is [age, dict()]
        # where the dict holds the board evaluations
        self.entries = SortedSet()

    def __contains__(self, board):
        age = board.age
        if age in self.entries:
            idx = self.entries.bisect_left(age)
            return board in self.entries[idx].table

        return False

    def __getitem__(self, board):
        age = board.age
        if age in self.entries:
            idx = self.entries.bisect_left(age)
            return self.entries[idx].table[board]

        raise KeyError("item not in TransitionTable")

    def __setitem__(self, board, node_data):
        age = board.age
        if age in self.entries:
            idx = self.entries.bisect_left(age)
            self.entries[idx].table[board] = node_data
        else:
            self.entries[age] = Entry(board, node_data)

    def age(self, num_moves):
        idx = self.entries.bisect_left(num_moves - 1)
        if idx > 0:
            for _ in range(idx):
                del self.entries[0]
