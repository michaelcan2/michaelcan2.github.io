from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.strategies import DefaultStrategy, CaptureStrategy
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, STONES, EMPTY_STONE

class GoPlayerInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='str')
    def register(self):
        """
            Should reply with the name, otherwise "no name" of the player.
        """
        pass

    @abstractmethod
    @contract(returns='str')
    def get_stone(self):
        """
            Should reply with the set stone, otherwise raise error if not set.
        """
        pass

    @abstractmethod
    @contract(s='str', returns='None')
    def receive_stones(self, s):
        """
            Set the internal state of the registered player to start a game playing as the player with the given Stone
        """
        pass

    @abstractmethod
    @contract(p='$Point', hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', returns='$Board')
    def try_move(self, p, hist):
        """
            Attempts to place the given point onto the most recent board and returns the new board, otherwise raises an error.
        """
        pass

    @abstractmethod
    @contract(hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', returns='str')
    def make_a_move(self, hist):
        """
            If hist is valid, replies with Point that is a a legal placement for the player’s Stone taking into account Boards
            and selecting for smallest col index followed by row index (default strategy)
        """
        pass

######## Implementation below ########

class GoPlayer(GoPlayerInterface):
    def __init__(self, name="no name", strategy="default"):
        self.name = name
        # subtle states of player
        self.registered = False
        self.received = False
        self.stone = None
        # services for validity and decision making
        self.rc = RuleChecker()
        if strategy == "default":
            self.strat = DefaultStrategy()
        elif strategy == "capture":
            self.strat = CaptureStrategy()

    def register(self):
        assert self.registered == False, "Player is already registered!"
        self.registered = True
        return self.name

    def get_stone(self):
        assert self.stone != None, "Player stone is not set!"
        return self.stone

    def receive_stones(self, s):
        assert self.received == False, "Player is already received stones!"
        self.received = True
        # check if s is a stone
        assert s in STONES, "Stone given is not valid!"
        self.stone = s

    def try_move(self, p, hist):
        recent_board = hist[0]
        
        # print(self.rc.move_play(self.stone, p, hist), self.stone, p.get_point_repr())
        # print(list(map(lambda b: b.get_board_repr(), hist)))
        if self.rc.move_play(self.stone, p, hist):
            return self.rc.place_and_remove(self.stone, p, recent_board)
        else:
            # print("hello")
            raise ValueError("Illegal move has been performed!")
    
    def make_a_move(self, hist):
        assert self.stone != None, "Stone is not set yet!"

        if not self.rc.verify_history_jr(hist, self.stone):
            return "This history makes no sense!"

        return self.strat.make_a_move(self, self.stone, hist, self.rc)        
