from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from copy import deepcopy
from board_components.go_player import GoPlayerInterface
from board_components.board import Board
from board_components.point import Point
from board_components.rule_checker import RuleChecker
from board_components.definitions import STONES, EMPTY_BOARD, PASS

class GoRefereeActionInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(player='$GoPlayerInterface', args='list')
    def act(self, player, args):
        """
            Implements functionality of next state and keeps track of next allowed action.
        """
        pass

class GoRefereeRegister(GoRefereeActionInterface):
    def act(self, player, args, container):
        assert len(args) == 0, "No args should be provided!"
        container.set_next(GoRefereeReceiveStones())
        return player.register()

class GoRefereeReceiveStones(GoRefereeActionInterface):
    def act(self, player, args, container):
        assert len(args) == 1, "One arg should be provided!"
        assert args[0] in STONES, "Arg0 is not a stone!"
        container.set_next(GoRefereeMakeMove())
        return player.receive_stones(*args)

class GoRefereeMakeMove(GoRefereeActionInterface):
    def act(self, player, args, container):
        assert len(args) == 2, "Two args should be provided!"
        assert isinstance(args[0], str), "Arg0 is not a string!"

        container.set_next(GoRefereeMakeMove())

        # track hist before move
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
                container.update_history(recent_board)
                self.current_player = self.get_next_player()

        # perform action (point)
        p = Point(act)

        try:
            new_board = self.current_player.try_move(p, hist)
            container.update_history(new_board)
            self.current_player = self.get_next_player()
            return list(map(lambda b: b.get_board_repr(), hist))
        except ValueError:
            # illegal play has occurred
            return [self.get_next_player().name]

class GoRefereeActionContainer(GoRefereeActionInterface):
    def __init__(self, player_1, player_2):
        self.next_action = GoRefereeRegister()
        self.history = [Board(EMPTY_BOARD)]
        self.rc = RuleChecker()
        self.player_1 = player_1
        self.player_2 = player_2
        self.current_player = None

    def set_first_player(self, player):
        self.current_player = player

    def update_history(self, b):
        self.history = [b] + self.history
        # check if hist > 3, then chop off oldest board
        if len(self.history) > 3:
            self.history = self.history[:-1]
    
    def set_next(self, act):
        self.next_action = act

    def act(self, player, args):
        self.next_action.act(player, args, self)