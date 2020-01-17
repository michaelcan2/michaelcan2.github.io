from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.strategies import DefaultStrategy, CaptureStrategy, RandomStrategy, PassStrategy
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, STONES, EMPTY_STONE, \
    GO_HAS_GONE_CRAZY, OK, PASS

import json
import socket
import requests

##############################################
## This module implements the players of GO ##
##############################################

class GoPlayerInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(returns='str')
    def register(self):
        """
            Should reply with the name, otherwise "no name" of the player.
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
    @contract(hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH](list[$BOARD_SIZE_X](list[$BOARD_SIZE_Y](str)))', returns='str')
    def make_a_move(self, hist):
        """
            If hist is valid, replies with Point that is a a legal placement for the player’s Stone taking into account Boards
            and selecting for smallest col index followed by row index (default strategy)
        """
        pass

    @abstractmethod
    @contract(returns='str')
    def end_game(self):
        """
            Notify player in a game that the game is over. Returns the string "OK".
        """
        pass

##############################
## Go Player Implementation ##
##############################

class GoPlayer(GoPlayerInterface):
    def __init__(self, name="no name", strategy=RandomStrategy()):
        self.name = name
        self.stone = None
        # services for validity and decision making
        self.strat = strategy

    def register(self):
        return self.name

    def receive_stones(self, s):
        self.stone = s

    def make_a_move(self, hist):
        hist_boards = list(map(lambda b: Board(b), hist))
        move = self.strat.make_a_move(self.stone, hist_boards)

        print(str(self.name) + ' made move ' + str(move))
        return move

    def end_game(self):
        self.stone = None
        return OK

##################################
## Go Player Gui Implementation ## TBD
##################################

class GoPlayerRemoteProxyGui(GoPlayerInterface):
    def __init__(self, socket):
        self.remote_player = GoPlayerRemoteProxy(socket)
        self.rc = RuleChecker()

    def register(self):
        return self.remote.register()

    def receive_stones(self, s):
        self.s = s
        return self.remote.receive_stones(s)
    
    def make_a_move(self, hist):
        self.rc.get_previous_player_move(hist, self.s)
        
        return self.remote.make_a_move(hist)

    def end_game(self):
        return self.remote.end_game()

############################
## Go Player Remote Proxy ##
############################     

class GoPlayerRemoteProxy(GoPlayerInterface):
    def __init__(self, socket):
        self.socket = socket
        conn, addr = self.socket.accept()
        self.conn = conn
        
    def register(self):
        command = json.dumps(['register'])
        self.conn.sendall(command.encode())
        data = self.conn.recv(32768)
        if not data:
            raise ConnectionResetError("Connection is gone!")
        
        result = json.loads(data.decode())

        print('remote player registered with name ' + str(result))

        self.name = result

        return result

    def receive_stones(self, s):
        command = json.dumps(['receive-stones', s])

        # print('remote player received command for stones ' + json.dumps(['receive-stones', s]))

        self.conn.sendall(command.encode())
        
        # no resp for receive_stones

    def make_a_move(self, hist):
        command = json.dumps(['make-a-move', hist])

        # print('remote player received command for move ' + json.dumps(['make-a-move', hist]))

        self.conn.sendall(command.encode())
        data = self.conn.recv(32768)
        if not data:
            raise ConnectionResetError("Connection is gone!")
        
        result = json.loads(data.decode())

        print(str(self.name) + ' made move ' + str(result))

        return result

    def end_game(self):
        command = json.dumps(['end-game'])

        self.conn.sendall(command.encode())
        data = self.conn.recv(32768)
        if not data:
            raise ConnectionResetError("Connection is gone!")
        
        result = json.loads(data.decode())

        print(str(self.name) + ' end game with reply ' + str(result))

        return result

#################################
## Go Player Contraint Proxies ##
#################################

class GoPlayerHandleExceptionProxy(GoPlayerInterface):
    def __init__(self, real_player):
        self.real_player = real_player

    def register(self):
        try:
            return self.real_player.register()
        except (ConnectionResetError, BrokenPipeError, AssertionError, contracts.interface.ContractNotRespected, socket.timeout) as e:
            raise AssertionError("[register] failed somehow, received the exception msg: " + str(e))

    def receive_stones(self, s):
        try:
            return self.real_player.receive_stones(s)
        except (ConnectionResetError, BrokenPipeError, AssertionError, contracts.interface.ContractNotRespected, socket.timeout) as e:
            raise AssertionError("[receive_stones] failed somehow, received the exception msg: " + str(e))

    def make_a_move(self, hist):
        try:
            return self.real_player.make_a_move(hist)
        except (ConnectionResetError, BrokenPipeError, AssertionError, contracts.interface.ContractNotRespected, socket.timeout) as e:
            raise AssertionError("[make_a_move] failed somehow, received the exception msg: " + str(e))

    def end_game(self):
        return self.real_player.end_game()

class GoPlayerOrderProxy(GoPlayerInterface):
    def __init__(self, real_player):
        self.real_player = real_player
        # subtle states of player
        self.registered = False
        self.received = False
    
    def register(self):
        assert self.registered == False, "Player is already registered!"
        self.registered = True
        return self.real_player.register()

    def receive_stones(self, s):
        assert self.registered == True, "Player haven't registered!"
        assert self.received == False, "Player is already received stones!"
        self.received = True
        return self.real_player.receive_stones(s)

    def make_a_move(self, hist):
        assert self.registered == True, "Player haven't registered!"
        assert self.received == True, "Player haven't received stones!"
        return self.real_player.make_a_move(hist)

    def end_game(self):
        # reset subtle states of player
        self.received = False
        return self.real_player.end_game()

class GoPlayerVerifyInputOutputProxy(GoPlayerInterface):
    def __init__(self, real_player):
        self.real_player = real_player
        # services for validity and decision making
        self.rc = RuleChecker()
        # keep track of stone for checking history when making moves
        self.stone = None

    def register(self):
        return self.real_player.register()

    def receive_stones(self, s):
        # check if s is a stone
        assert s in STONES, "Stone given is not valid!"
        self.stone = s
        return self.real_player.receive_stones(s)

    def make_a_move(self, hist):
        try:
            # if creating internal rep of board hist gives error, then there is an invalid board
            hist_boards = list(map(lambda b: Board(b), hist))
        except:
            raise AssertionError("Invalid board given!")

        # verify history
        if not self.rc.verify_history(hist_boards, self.stone):
            raise AssertionError("This history makes no sense!")

        move_point = self.real_player.make_a_move(hist)

        # check if pass first
        if move_point == PASS:
            return move_point

        try:
            # if creating internal rep of str point gives error, then it is an invalid move
            p = Point(move_point)
        except:
            raise AssertionError("Invalid point returned!: " + str(move_point))

        return move_point

    def end_game(self):
        msg = self.real_player.end_game()
        if msg != OK:
            raise AssertionError("Inproper reply when ending game for player!")

        return msg

######################################
## Go Player Remote Driver (Client) ##
######################################

class GoPlayerRemoteDriver(GoPlayerInterface):
    def __init__(self):
        self.remote_player = GoPlayer(name='not player one', strategy=RandomStrategy())

    def send(self, command):
        try:
            return self.read_command(command)
        except:
            # catch assertion and contract exceptions
            return GO_HAS_GONE_CRAZY
    
    def read_command(self, command):
        if command[0] == "register":
            return self.register()
        elif command[0] == "receive-stones":
            return self.receive_stones(command[1])
        elif command[0] == "make-a-move":
            return self.make_a_move(command[1])
        elif command[0] == "end-game":
            return self.end_game()
        else:
            raise AssertionError("Invalid command!")

    def register(self):
        return self.remote_player.register()

    def receive_stones(self, s):
        return self.remote_player.receive_stones(s)

    def make_a_move(self, hist):
        return self.remote_player.make_a_move(hist)

    def end_game(self):
        return self.remote_player.end_game()