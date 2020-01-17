from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from board_components.point import Point
from board_components.board import Board
from board_components.strategies import DefaultStrategy, CaptureStrategy
from board_components.rule_checker import RuleChecker
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, BOARD_SIZE_X, BOARD_SIZE_Y, STONES, EMPTY_STONE

import json
import socket

import queue
import threading

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

    @contract(returns='str')
    def get_stone(self):
        assert self.stone != None, "Player stone is not set!"
        return self.stone

    def receive_stones(self, s):
        assert self.registered == True, "Player is haven't registered!"
        assert self.received == False, "Player is already received stones!"
        self.received = True
        # check if s is a stone
        assert s in STONES, "Stone given is not valid!"
        self.stone = s

    @contract(p='$Point', hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', returns='$Board')
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
        hist_boards = list(map(lambda b: Board(b), hist))
        assert self.registered == True, "Player is haven't registered!"
        assert self.stone != None, "Stone is not set yet!"

        if not self.rc.verify_history_jr(hist_boards, self.stone):
            return "This history makes no sense!"

        return self.strat.make_a_move(self.stone, hist_boards, self.rc)        

class GoPlayerRemote(GoPlayerInterface):
    def __init__(self):
        self.remote_player = GoPlayer(strategy='capture')

    def send(self, command):
        try:
            return self.read_command(command)
        except:
            # catch assertion and contract exceptions
            return 'GO has gone crazy!'
    
    def read_command(self, command):
        if command[0] == "register":
            return self.register()
        elif command[0] == "receive-stones":
            return self.receive_stones(command[1])
        elif command[0] == "make-a-move":
            return self.make_a_move(command[1])
        else:
            raise AssertionError("Invalid command!")

    def register(self):
        return self.remote_player.register()

    def receive_stones(self, s):
        return self.remote_player.receive_stones(s)

    def make_a_move(self, hist):
        return self.remote_player.make_a_move(hist)

class ServerThread(threading.Thread):
    def __init__(self, arg_q, result_q, name='ServerThread'):
        """ constructor, setting initial variables """
        self.arg_q = arg_q
        self.result_q = result_q
        self.decoder = json.JSONDecoder()
        self._stopevent = threading.Event()

        threading.Thread.__init__(self, name=name)

    def run(self):
        """ main control loop """
        with open('go.config') as json_file:
            data = json.load(json_file)
            IP = data['IP']
            port = data['port']

        # print('starting server...')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((IP, port))
            s.listen()
            # print('waiting for connection')
            conn, addr = s.accept()
            with conn:
                while True:
                    while self.arg_q.empty() and not self._stopevent.isSet():
                        pass

                    if self._stopevent.isSet():
                        conn.sendall(bytes(json.dumps(['shutdown']), 'utf-8'))
                        break

                    command = self.arg_q.get()
                    # print(command)
                    conn.sendall(bytes(json.dumps(command), 'utf-8'))
                    try:
                        while True:
                            data = conn.recv(32768)
                            if data:
                                break
                    except ConnectionResetError:
                        break

                    result = self.decoder.raw_decode(data.decode('utf-8'))[0]
                    self.result_q.put(result)
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            s.close()

    def join(self, timeout=None):
        """ Stop the thread. """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class GoPlayerRemoteProxy(GoPlayerInterface):
    def __init__(self):
        self.arg_q = queue.Queue()
        self.result_q = queue.Queue()
        
        self.server_thread = ServerThread(self.arg_q, self.result_q)
        self.server_thread.start()

    def register(self):
        self.arg_q.put(['register'])
        while self.result_q.empty():
            pass
        return self.result_q.get()

    def receive_stones(self, s):
        self.arg_q.put(['receive-stones', s])
        while self.result_q.empty():
            pass
        return self.result_q.get()

    def make_a_move(self, hist):
        self.arg_q.put(['make-a-move', hist])
        while self.result_q.empty():
            pass
        return self.result_q.get()

    def exit(self):
        self.server_thread.join()