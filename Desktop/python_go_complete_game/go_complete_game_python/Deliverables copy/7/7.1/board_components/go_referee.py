from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from copy import deepcopy
from board_components.go_player import GoPlayer
from board_components.rule_checker import RuleChecker
from board_components.board import Board
from board_components.point import Point
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, BLACK_STONE, \
    WHITE_STONE, EMPTY_BOARD, PASS

class GoRefereeInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(name='str', returns='list(str)|None')
    def assign_player(self, name):
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

######## Implementation below ########

class GoReferee(GoRefereeInterface):
    def __init__(self, player_1, player_2):
        self.player_1 = player_1
        self.player_2 = player_2
        self.history = [Board(EMPTY_BOARD)]
        self.rc = RuleChecker()
        self.current_player = None

    def get_next_player(self):
        if self.current_player == self.player_1:
            return self.player_2
        else:
            return self.player_1

    def assign_player(self, name):
        if self.player_1 is None:
            self.player_1 = GoPlayer(name)
            self.player_1.register()
            self.player_1.receive_stones(BLACK_STONE)
            return

        elif self.player_2 is None:
            self.player_2 = GoPlayer(name)
            self.player_2.register()
            self.player_2.receive_stones(WHITE_STONE)
            # both players assigned if here, init starting player
            self.current_player = self.player_1
            return [self.player_1.get_stone(), self.player_2.get_stone()]

        raise AssertionError("Players are already set!")

    def perform_action(self, act):
        hist = deepcopy(self.history)
        stone = self.current_player.get_stone()

        # check for double passing
        if act == PASS:
            # check if last turn is also a pass
            if len(hist) > 1 and hist[0] == hist[1]:
                # game is over, get scores, find out the winner!
                scores = self.rc.count_score(hist[0])
                player_1_stone = self.player_1.get_stone()
                player_2_stone = self.player_2.get_stone()
                if scores[player_1_stone] == scores[player_2_stone]:
                    return sorted([self.player_1.name, self.player_2.name])
                elif scores[player_1_stone] > scores[player_2_stone]:
                    return [self.player_1.name]
                else:
                    return [self.player_2.name]
            else:
                recent_board = deepcopy(hist[0])
                self.update_history(recent_board)
                self.current_player = self.get_next_player()

        # perform action (point)
        p = Point(act)

        try:
            new_board = self.current_player.try_move(p, hist)
            self.update_history(new_board)
            self.current_player = self.get_next_player()
            return list(map(lambda b: b.get_board_repr(), hist))
        except ValueError:
            # illegal play has occurred
            return [self.get_next_player().name]

    def update_history(self, b):
        self.history = [b] + self.history
        # check if hist > 3, then chop off oldest board
        if len(self.history) > 3:
            self.history = self.history[:-1]
