from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass

import socket
import importlib.util
import json

socket.setdefaulttimeout(20)

with open('go.config') as json_file:
    data = json.load(json_file)
    IP = str(data['IP'])
    port = int(data['port'])
    
# print('starting server...')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, port))
    
s.listen(5)

from board_components.go_factories import GoPlayerFactory
from board_components.go_players import GoPlayerRemoteProxy
from board_components.go_referee import GoReferee
from board_components.definitions import GO_HAS_GONE_CRAZY

class GoAdministratorInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(path='str')
    def create_default_player(self, path):
        """
            Dynamically load the default player using the path provided.
        """
        pass

    @abstractmethod
    @contract(returns='None')
    def setup_game(self):
        """
            Instantiate the two players and integrate with the referee before starting game.
        """
        pass

    @abstractmethod
    @contract(returns='list[>=1,<=2](str)')
    def play_game(self):
        """
            Play the game between the two players.
        """
        pass

######## Implementation below ########

class GoAdministrator(GoAdministratorInterface):
    def __init__(self, socket):
        # retrieve path of default player
        with open('go.config') as json_file:
            data = json.load(json_file)
            path = data['default-player']

        playerFactory = GoPlayerFactory()

        self.default_player = self.create_default_player(path)
        self.default_player = playerFactory.enforce_constraints(self.default_player, constraint='all')
        # blocks until a connection is made
        self.remote_player = GoPlayerRemoteProxy(socket)
        self.remote_player = playerFactory.enforce_constraints(self.remote_player, constraint='all')

        # set up game
        self.setup_game()

    def create_default_player(self, path):
        spec = importlib.util.spec_from_file_location("default.player", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        default_player = mod.GoPlayer()
        return default_player

    def setup_game(self):
        self.referee = GoReferee()
        # assign players to referee
        self.referee.assign_player(self.default_player)
        self.referee.assign_player(self.remote_player)

    def get_other_player_name(self, current_player):
        if self.default_player == current_player:
            return self.referee.get_dict_names()['second']
        else:
            return self.referee.get_dict_names()['first']

    def clean_up_resources(self):
        self.remote_player.exit()

    def play_game(self):
        # move logic to referee
        # auto play game with moves each player make until a win occurs
        while True:
            hist = self.referee.get_history()
            player = self.referee.get_current_player()
            # attempt the players given moves
            move = player.make_a_move(hist)
            
            print(move, hist)

            if move == GO_HAS_GONE_CRAZY:
                cheating = True
                print(GO_HAS_GONE_CRAZY)
                # either invalid move returned or connection reset has occurred
                other_player = self.get_other_player_name(player)
                return [other_player]

            result = self.referee.get_history()
            print('\n', result)

            # a player wins if double passes or other player performs illegal move
            output = self.referee.perform_action(move)

            # check if output shows a player has won
            if isinstance(output, list) and all(isinstance(item, str) for item in output):
                return output

def main():
    try:
        admin = GoAdministrator(socket=s)
        res = json.dumps(admin.play_game())
    except socket.timeout:
        s.close()
        return "timed out"

    s.close()
    print(res)
    return res
            
if __name__== "__main__":
    main()