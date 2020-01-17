from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, EMPTY_STONE, \
    WHITE_STONE, BLACK_STONE, PASS
import functools
import json

with open('go-player.config') as json_file:
    data = json.load(json_file)
    depth = data['depth']

#################################################
## This module implements GO player strategies ##
#################################################

class StrategyInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(stone='str', hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', rc='$RuleChecker', returns='str')
    def make_a_move(self, stone, hist, rc):
        """
            Depends on strategy, but returns a point that satisfies given strategy with min col followed by min row.
        """
        pass

class DefaultStrategy(StrategyInterface):
    def make_a_move(self, stone, hist, rc):
        recent_board = hist[0].get_board_repr()
        # loop boards by column then row
        for i in range(BOARD_SIZE_X):
            for j in range(BOARD_SIZE_Y):
                pos = Point("{}-{}".format(i+1, j+1))
                if recent_board[j][i] == EMPTY_STONE and rc.move_play(stone, pos, hist):
                    return pos.get_point_repr()

        return PASS

class CaptureStrategy(StrategyInterface):
    def __init__(self):
        self.ai_used_flag = False

    def __remove_duplicates(self, list_of_points):
        return list(dict.fromkeys(list_of_points))

    def move_sequence_possible(self, stone, hist, rc, n, other_player, other_player_move):
        if n == 0:
            return True
        # if the other_player can't move to the given point he will pass
        if rc.move_play(other_player, other_player_move, hist):
            temp_board = rc.place_and_remove(other_player, other_player_move, hist[0])
            hist[2] = hist[1]
            hist[1] = hist[0]
            hist[0] = temp_board
            # print("n in move_seq ",n)
            self.make_a_move(stone, hist, rc, n)
            if self.ai_used_flag:
                return True
        # print("return False")
        return False
        
    def make_a_move(self, stone, hist, rc, n=depth):
        if stone == BLACK_STONE:
            other_player = WHITE_STONE
        else:
            other_player = BLACK_STONE
            
        recent_board = hist[0].get_board_repr()
        other_player_points = hist[0].get_points_without_sort(other_player)
        # loop boards by column then row
        possible_move_list = []
        for p in other_player_points:
            pp = Point(p)
            liberty_list = hist[0].reachable_bfs(pp, EMPTY_STONE)
            liberty_list = self.__remove_duplicates(liberty_list)
            count = len(liberty_list)
            if count == n:
                for l in liberty_list:
                    if rc.move_play(stone, l, hist):
                        if n == 1:
                            possible_move_list.append(l)
                        else:
                            temp_board = rc.place_and_remove(self.stone, l, hist[0])
                            new_hist = [temp_board, hist[0], hist[1]]
                            temp_list = list(x for x in liberty_list if x != l)
                            #print("temp_list", list(map(lambda s: s.get_point_repr(), temp_list)))
                            if any(list(map(lambda other_player_move:
                                            self.move_sequence_possible(new_hist, n - 1, other_player_move),
                                            temp_list))):
                                possible_move_list.append(l)

        if not len(possible_move_list) == 0:
            def point_sort(p1, p2):
                if p1.y > p2.y:
                    return 1
                elif p1.y < p2.y:
                    return -1
                elif p1.y == p2.y:
                    if p1.x > p2.x:
                        return 1
                    elif p1.x < p2.x:
                        return -1
                    else:
                        return 0
            possible_move_list = sorted(possible_move_list, key=functools.cmp_to_key(point_sort))
            self.ai_used_flag = True
            #print(list(map(lambda s:s.get_point_repr(),possible_move_list)))
            #possible_move_list = remove_duplicates(possible_move_list)
            return possible_move_list[0].get_point_repr()

        self.ai_used_flag = False
        for i in range(BOARD_SIZE_X):
            for j in range(BOARD_SIZE_Y):
                pos = Point("{}-{}".format(i + 1, j + 1))
                if recent_board[j][i] == EMPTY_STONE and rc.move_play(stone, pos, hist):
                    return pos.get_point_repr()

        return PASS


class RandomStrategy(StrategyInterface):
    def make_a_move(self, stone, hist, rc):
        import random

        if random.random() > 0.9:
            return "invalid thing!"

        valid_moves = [PASS]

        recent_board = hist[0].get_board_repr()
        # loop boards by column then row
        for i in range(BOARD_SIZE_X):
            for j in range(BOARD_SIZE_Y):
                pos = Point("{}-{}".format(i+1, j+1))
                if recent_board[j][i] == EMPTY_STONE and rc.move_play(stone, pos, hist):
                    valid_moves.append(pos.get_point_repr())

        return random.choice(valid_moves)
