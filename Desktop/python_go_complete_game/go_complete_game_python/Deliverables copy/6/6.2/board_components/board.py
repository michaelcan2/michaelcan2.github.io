from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.definitions import MAYBE_STONES, STONES, BLACK_STONE, WHITE_STONE, EMPTY_STONE, \
    BOARD_SIZE_X, BOARD_SIZE_Y, MAX_SCORE

import queue

class BoardInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(p='$Point', returns='bool')
    def occupied(self, p):
        """
            Check if board has a stone at the given Point. If so true otherwise false.
        """
        pass

    @abstractmethod
    @contract(s='str', p='$Point', returns='bool')
    def occupies(self, s, p):
        """
            Check if given Stone appears on the Board at the given Point. If so true otherwise false.
        """
        pass

    @abstractmethod
    @contract(p='$Point', s='str', returns='bool')
    def reachable(self, p, s):
        """
            Checks if (i) there is a path of (vertically or horizontally) adjacent points starting at the given Point 
            that have the same kind of Stone as the given Point and (ii) the path reaches a point of the Board with the 
            given MaybeStone. If so true otherwise false.
        """
        pass

    @abstractmethod
    @contract(pp='$Point', s='str', returns='list[< $MAX_SCORE]($Point)')
    def reachable_bfs(self, pp, s):
        """
            Checks if (i) there is a path of (vertically or horizontally) adjacent points starting at the given Point 
            that have the same kind of Stone as the given Point and (ii) the path reaches a point of the Board with the 
            given MaybeStone. If so, return all points that are s which is reachable from pp.
        """
        pass

    @abstractmethod
    @contract(s='str', p='$Point', returns='(list[$BOARD_SIZE_X](list[$BOARD_SIZE_Y](str))|str)')
    def place(self, s, p):
        """
            return a Board that reflects placing the given Stone on the given Point if it is possible to do so, 
            or it should return the JSON string "This seat is taken!" 
        """
        pass

    @abstractmethod
    @contract(s='str', p='$Point', returns='(list[$BOARD_SIZE_X](list[$BOARD_SIZE_Y](str))|str)')
    def remove(self, s, p):
        """
            return a Board that reflects removing Stone from the given Point on the Board if it is possible to do so, 
            or it should return the JSON string "I am just a board! I cannot remove what is not there!"
        """
        pass

    @abstractmethod
    @contract(s='str', returns='list(str)')
    def get_points(self, s):
        """
            return a JSON array of Points that collects all the Points on the Board that have the appropriate stone 
            or are empty depending on the given MaybeStone 
        """
        pass

    @abstractmethod
    @contract(s='str', returns='list(str)')
    def get_points_without_sort(self, s):
        """
            return a JSON array of Points that collects all the Points on the Board that have the appropriate stone 
            or are empty depending on the given MaybeStone with points with the smallest column index and (secondarily)
            the smallest row index
        """
        pass

    @abstractmethod
    @contract(returns='int,>=0,<=$MAX_SCORE')
    def get_num_black_stones(self):
        """
            Returns the number of black stones on the given board.
        """
        pass

    @abstractmethod
    @contract(returns='int,>=0,<=$MAX_SCORE')
    def get_num_white_stones(self):
        """
            Returns the number of white stones on the given board.
        """
        pass

    @abstractmethod
    @contract(returns='dict[2](str: int,>=0,<=$MAX_SCORE)')
    def get_players_stone_count(self):
        """
            Returns the number of stones for both players within a dict wheres keys are players and val is stone count.
        """
        pass

######## Implementation below ########

class Board(BoardInterface):
    def __init__(self, board):
        self.repr = board
        self.__verify_board()

    def __eq__(self, other):
        """
            Override the default Equals behavior
        """
        return self.repr == other.repr

    def __ne__(self, other):
        """
            Override the default Unequal behavior
        """
        return self.repr != other.repr

    def get_board_repr(self):
        return self.repr

    # private method
    def __verify_board(self):
        def is_valid_stone(s):
            assert s in MAYBE_STONES, "Stone value is not valid!"

        board = self.repr
        # check board length
        assert len(board) == BOARD_SIZE_Y, "Not a valid board, does not contain 19 rows!"
        for row in board:
            # check row lengths
            assert len(row) == BOARD_SIZE_X, "Not valid row, it is not length 19!"
            # check each stone is valid
            map(is_valid_stone, row)

    def __get_stone_value(self, p):
        return self.repr[p.x][p.y]

    def is_empty(self):
        for row in self.repr:
            for stone in row:
                if stone != EMPTY_STONE:
                    return False

        return True

    def get_num_black_stones(self):
        return len(self.get_points(BLACK_STONE))

    def get_num_white_stones(self):
        return len(self.get_points(WHITE_STONE))

    def get_players_stone_count(self):
        results = {
            BLACK_STONE: self.get_num_black_stones(),
            WHITE_STONE: self.get_num_white_stones()
        }
        return results

    def occupied(self, p):
        stone_val = self.__get_stone_value(p)
        return stone_val != EMPTY_STONE

    def occupies(self, s, p):
        assert s in STONES, "Not a valid stone!"
        stone_val = self.__get_stone_value(p)
        return stone_val == s

    def reachable(self, p, s):
        SIZE_X = BOARD_SIZE_X
        SIZE_Y = BOARD_SIZE_Y

        # check if given indexes are valid point

        def is_valid_pos(i, j):
            return 0 <= i < SIZE_X and 0 <= j < SIZE_Y

        # traverse board for paths using DFS

        def reachable_traverse(check_matrix, x, y, s, visited):  # s is MaybeStone
            if visited[x][y]:
                return False
            else:
                if is_valid_pos(x + 1, y) and check_matrix[x + 1][y] == s:
                    return True

                elif is_valid_pos(x - 1, y) and check_matrix[x - 1][y] == s:
                    return True

                elif is_valid_pos(x, y + 1) and check_matrix[x][y + 1] == s:
                    return True

                elif is_valid_pos(x, y - 1) and check_matrix[x][y - 1] == s:
                    return True

                else:
                    visited[x][y] = True
                    if is_valid_pos(x + 1, y) and check_matrix[x][y] == check_matrix[x + 1][y]:
                        right_bool = reachable_traverse(check_matrix, x + 1, y, s, visited)
                        if right_bool:
                            return True

                    if is_valid_pos(x - 1, y) and check_matrix[x][y] == check_matrix[x - 1][y]:
                        left_bool = reachable_traverse(check_matrix, x - 1, y, s, visited)
                        if left_bool:
                            return True

                    if is_valid_pos(x, y + 1) and check_matrix[x][y] == check_matrix[x][y + 1]:
                        down_bool = reachable_traverse(check_matrix, x, y + 1, s, visited)
                        if down_bool:
                            return True

                    if is_valid_pos(x, y - 1) and check_matrix[x][y] == check_matrix[x][y - 1]:
                        up_bool = reachable_traverse(check_matrix, x, y - 1, s, visited)
                        if up_bool:
                            return True

                    return False

        assert s in MAYBE_STONES, "Not a valid MaybeStone!"
        check_matrix = self.repr
        if check_matrix[p.x][p.y] == s:
            return True
        visited = [[False for i in range(SIZE_X)] for j in range(SIZE_Y)]
        return reachable_traverse(check_matrix, p.x, p.y, s, visited)

    def place(self, s, p):
        try:
            if self.occupied(p):
                raise AssertionError("This seat is taken!")
        except AssertionError as ex:
            # returns only str message
            return str(ex)
        assert s in STONES, "Not a valid stone!"
        self.repr[p.x][p.y] = s
        return self.repr

    def remove(self, s, p):
        try:
            # occupies already asserts if s is a STONE
            if not self.occupies(s, p):
                raise AssertionError("I am just a board! I cannot remove what is not there!")
        except AssertionError as ex:
            # returns only str message
            return str(ex)
        self.repr[p.x][p.y] = EMPTY_STONE
        return self.repr

    def get_points(self, s):
        assert s in MAYBE_STONES, "Not a valid MaybeStone!"
        results = []
        for i in range(BOARD_SIZE_X):
            for j in range(BOARD_SIZE_Y):
                if self.repr[i][j] == s:
                    results.append("{}-{}".format(j + 1, i + 1))
        results = sorted(results)
        return results

    def get_points_without_sort(self, s):
        assert s in MAYBE_STONES, "Not a valid MaybeStone!"
        results = []
        for i in range(BOARD_SIZE_Y):
            for j in range(BOARD_SIZE_X):
                if self.repr[j][i] == s:
                    results.append("{}-{}".format(i + 1, j + 1))
        return results

    def reachable_bfs(self, pp, s):
        SIZE_X = BOARD_SIZE_X
        SIZE_Y = BOARD_SIZE_Y
        res_list = []
        que = queue.Queue()

        # check if given indexes are valid point

        def is_valid_pos(i, j):
            return 0 <= i < SIZE_X and 0 <= j < SIZE_Y

        def reachable_bfs_helper(check_matrix, s, visited, que, result_list):  # s is MaybeStone
            if que.empty():
                return result_list
            else:
                p = que.get()
                if visited[p.x][p.y]:
                    reachable_bfs_helper(check_matrix,s,visited,que,result_list)
                visited[p.x][p.y] = True
                if is_valid_pos(p.x + 1, p.y) and check_matrix[p.x + 1][p.y] == s:
                    result_list.append(Point([p.x + 1, p.y]))

                if is_valid_pos(p.x - 1, p.y) and check_matrix[p.x - 1][p.y] == s:
                    result_list.append(Point([p.x-1, p.y]))

                if is_valid_pos(p.x, p.y + 1) and check_matrix[p.x][p.y + 1] == s:
                    result_list.append(Point([p.x, p.y + 1]))

                if is_valid_pos(p.x, p.y - 1) and check_matrix[p.x][p.y - 1] == s:
                    result_list.append(Point([p.x, p.y -1]))

                if is_valid_pos(p.x + 1, p.y) and not visited[p.x + 1][p.y] \
                        and check_matrix[p.x][p.y] == check_matrix[p.x + 1][p.y]:
                    que.put(Point([p.x+1, p.y]))

                if is_valid_pos(p.x - 1, p.y) and not visited[p.x-1][p.y] \
                        and check_matrix[p.x][p.y] == check_matrix[p.x - 1][p.y]:
                    que.put(Point([p.x-1, p.y]))

                if is_valid_pos(p.x, p.y + 1) and not visited[p.x][p.y+1] \
                        and check_matrix[p.x][p.y] == check_matrix[p.x][p.y + 1]:
                    que.put(Point([p.x, p.y+1]))

                if is_valid_pos(p.x, p.y - 1) and not visited[p.x][p.y-1] \
                        and check_matrix[p.x][p.y] == check_matrix[p.x][p.y - 1]:
                    que.put(Point([p.x, p.y-1]))

                return reachable_bfs_helper(check_matrix, s, visited, que,result_list)

        assert s in MAYBE_STONES, "Not a valid MaybeStone!"
        check_matrix = self.repr
        if check_matrix[pp.x][pp.y] == s:
            return res_list.append(s)
        visited = [[False for i in range(SIZE_X)] for j in range(SIZE_Y)]
        que.put(pp)
        res_list = reachable_bfs_helper(check_matrix, s, visited, que, [])
        return res_list
