from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from copy import deepcopy
from board_components.go_players import GoPlayer, GoPlayerInterface
from board_components.rule_checker import RuleChecker
from board_components.board import Board
from board_components.point import Point
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, BLACK_STONE, \
    WHITE_STONE, PASS

###########################################
## This module implements the GO referee ##
###########################################

class GoRefereeInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='list(str)|None')
    def assign_player(self, player):
        """
            Only returns assigned stones after receiving name inputs for both players.
        """
        pass

    @abstractmethod
    @contract(act='str', returns='(list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH](list[$BOARD_SIZE_X](list[$BOARD_SIZE_Y](str)))|list[>=1,<=2](str))')
    def perform_action(self, act):
        """
            Given a point, the current player's stone (turn) will be placed on the recent board. If valid, the last three boards
            of the game’s state when the call takes place is returned.  Otherwise, if the action corresponds to an end of 
            the game or illegal move (auto lose), the names of the winner(s) are outputted in a list.
        """
        pass

    @abstractmethod
    @contract(b='$Board', returns='None')
    def update_history(self, b):
        """
            Given a new board, update the internal representation of the history for the game so far.
        """
        pass

###############################
## Go Referee Implementation ##
###############################

class GoReferee(GoRefereeInterface):
    def __init__(self):
        # slots for the two players
        self.player_1 = None
        self.player_2 = None
        # start out with empty board hist
        self.history = [Board()]
        self.rc = RuleChecker()
        # trackers for current player
        self.player_names = {'first': None, 'second': None}
        self.current_player = None
        self.current_stone = None
        ################
        ## Invariants ##
        ################
        # first and second player are assigned based on order
        # first player is always BLACK STONE
        # second player is always WHITE STONE

    def get_next_player_and_stone(self):
        if self.current_player == self.player_1:
            return (self.player_2, WHITE_STONE)
        else:
            return (self.player_1, BLACK_STONE)

    def assign_player(self, player):
        if self.player_1 is None:
            self.player_1 = player
            self.player_names['first'] = self.player_1.register()
            self.player_1.receive_stones(BLACK_STONE)
            return

        elif self.player_2 is None:
            self.player_2 = player
            self.player_names['second'] = self.player_2.register()
            self.player_2.receive_stones(WHITE_STONE)

            # both players assigned, init starting player
            self.current_player = self.player_1
            self.current_stone = BLACK_STONE
            return [BLACK_STONE, WHITE_STONE]

        raise AssertionError("Players are already set!")

    def perform_pass(self, hist):
        # check if last turn is also a pass
        if len(hist) > 1 and hist[0] == hist[1]:
            # game is over, get scores, find out the winner!
            scores = self.rc.count_score(hist[0])
            player_1_stone = BLACK_STONE
            player_2_stone = WHITE_STONE
            # evaluate the winner
            if scores[player_1_stone] == scores[player_2_stone]:
                return sorted([self.player_names['first'], self.player_names['second']])
            elif scores[player_1_stone] > scores[player_2_stone]:
                return [self.player_names['first']]
            else:
                return [self.player_names['second']]
        else:
            recent_board = deepcopy(hist[0])
            self.update_history(recent_board)
            (self.current_player, self.current_stone) = self.get_next_player_and_stone()
            return list(map(lambda b: b.get_board_repr(), hist))

    def perform_action(self, act):
        hist = deepcopy(self.history)
        stone = self.current_stone

        # check for double passing
        if act == PASS:
            return self.perform_pass(hist)

        # perform action (point)
        p = Point(act)

        try:
            new_board = self.attempt_move(stone, p, hist) ##
            self.update_history(new_board)
            (self.current_player, self.current_stone) = self.get_next_player_and_stone()
            return list(map(lambda b: b.get_board_repr(), hist))
        except ValueError:
            # illegal play has occurred, other player wins
            if self.current_player == self.player_1:
                return [self.player_names['second']]
            else:
                return [self.player_names['first']]

    def attempt_move(self, stone, p, hist):
        recent_board = hist[0]
        
        if self.rc.move_play(stone, p, hist):
            return self.rc.place_and_remove(stone, p, recent_board)
        else:
            raise ValueError("Illegal move has been performed!")

    def update_history(self, b):
        self.history = [b] + self.history
        # check if hist > 3, then chop off oldest board
        if len(self.history) > 3:
            self.history = self.history[:-1]

    def get_current_player(self):
        return self.current_player
    
    def get_history(self):
        return list(map(lambda b: b.get_board_repr(), self.history))
    
    def get_dict_names(self):
        return self.player_names