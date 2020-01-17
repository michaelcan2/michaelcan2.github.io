import json
import socket

socket.setdefaulttimeout(20)

with open('go.config') as json_file:
    data = json.load(json_file)
    IP = str(data['IP'])
    port = int(data['port'])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, port))

from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass

from copy import copy
import importlib.util
import sys
import random

from board_components.board import Board
from board_components.definitions import ROUND_ROBIN, SINGLE_ELIMINATION
from board_components.go_factories import GoPlayerFactory, GoStrategyFactory
from board_components.go_players import GoPlayerRemoteProxy
from board_components.go_referee import GoReferee

####################################################
## This module implements the GO tournament admin ##
####################################################

class GoTournamentAdministratorInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    def play_match(self, player_1, player_2):
        """
            Plays a game between two players and returns the outcome of who wins. Updates 
            rankings and replaces cheating players with default players internally. Returns the winner of that round.
        """
        pass

    @abstractmethod
    @contract(player_ids='list(*)')
    def play_round(self, player_ids):
        """
            Plays a round of the tournament and updates the matchings of the opponents for the next round.
        """
        pass

    @abstractmethod
    @contract(returns='str')
    def play_tournament(self):
        """
            Executes the entire tournament and returns the rankings of the resulting players.
        """
        pass

    @abstractmethod
    @contract(n='int', returns='None')
    def registration(self, n):
        """
            Registers n remote players into the tournament and additional delta default players if n is not a 
            power of two number.
        """
        pass

    @abstractmethod
    @contract(path='str')
    def create_default_player(self, path):
        """
            Dynamically load the default player using the path provided.
        """
        pass

########################################
## Go tournament admin implementation ##
########################################

# players
# {
#     id: index (INVARIANT: unique)
#     player: some_player_instance
#     name: some_name
#     has_cheated: bool
#     score: num
# }

class GoTournamentAdministrator(GoTournamentAdministratorInterface):
    def __init__(self, socket, n, style):
        # retrieve path of default player
        with open('go.config') as json_file:
            data = json.load(json_file)
            path = data['default-player']
        
        self.path = path
        self.s = socket
        self.style = style
        # INVARIANT: objects in players list are never removed or shuffled, only new players are appended
        self.players = []
        self.referee = GoReferee()

        self.default_id = 1

        self.registration(n)

    def create_default_player(self, path):
        strats = ['random', 'pass']
        chosen_strat = random.choice(strats)

        strategy_factory = GoStrategyFactory()
        strat = strategy_factory.get_strategy(chosen_strat)

        spec = importlib.util.spec_from_file_location("default.player", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        default_player = mod.GoPlayer(name='default player #' + str(self.default_id), strategy=strat)
        self.default_id += 1
        return default_player

    def protect_player_and_register(self, player, player_factory):
        new_player = player_factory.enforce_constraints(player, constraint='all')
        # blocks until remote player connection is made
        name = new_player.register()
        return (name, new_player)

    def registration(self, n):
        print('Starting tournament of type ' + str(self.style) + ' with ' + str(n) + ' remote players.')

        player_factory = GoPlayerFactory()

        for i in range(n):
            try:
                print('waiting for remote player ' + str(i+1) + '...')
                remote_player = GoPlayerRemoteProxy(self.s)
                (name, new_player) = self.protect_player_and_register(remote_player, player_factory)
            except:
                # replace with default player
                print('remote player ' + str(i+1) + ' failed to connect, replacing with default player...')
                # remote player failed, use default player instead
                default_player = self.create_default_player(self.path)
                (name, new_player) = self.protect_player_and_register(default_player, player_factory)
            
            self.players.append({
                'id': i,
                'player': new_player,
                'name': name,
                'has_cheated': False,
                'score': 0
            })
        
        # find closest power of 2 to n
        target_player_count = 2
        while target_player_count < n:
            target_player_count *= 2
        
        # add remaining players using the default player from config
        for j in range(n, target_player_count):
            # registering default players
            default_player = self.create_default_player(self.path)
            (name, new_player) = self.protect_player_and_register(default_player, player_factory)

            self.players.append({
                'id': j,
                'player': new_player,
                'name': name,
                'has_cheated': False,
                'score': 0
            })

        # check tournament style and use appropriate field for managing matches
        # use indices to match players
        if self.style == ROUND_ROBIN:
            self.player_matchings = list(range(len(self.players)))
        elif self.style == SINGLE_ELIMINATION:
            self.remaining_players = list(range(len(self.players)))

    def play_match(self, player_1_obj, player_2_obj):
        self.referee.reset_state()
        # assign players to referee
        self.referee.assign_player(player_1_obj)
        self.referee.assign_player(player_2_obj)
        (result, cheating) = self.referee.play_game()

        # check if tie, if so choose a random winner
        if len(result) > 1:
            winner_name = random.choice(result)
        else:
            winner_name = result[0]

        # find winner using the winner id and update rankings
        if player_1_obj['name'] == winner_name:
            winner_id = player_1_obj['id']
            loser_id = player_2_obj['id']
        else:
            winner_id = player_2_obj['id']
            loser_id = player_1_obj['id']

        if not self.players[winner_id]['has_cheated']:
            self.players[winner_id]['score'] += 1
            print(str(winner_name) + ' has won the match and earned a point!')
            # determine if losing player cheated during the game
            if cheating:
                # give current score points to winning player
                self.players[winner_id]['score'] += self.players[loser_id]['score']
                # punish by setting points to zero and update status
                print(self.players[loser_id]['name'] + ' has cheated during the game!')
                print(str(winner_name) + ' has gained an additional ' + str(self.players[loser_id]['score']) + ' point(s)!')
                self.players[loser_id]['score'] = 0
                self.players[loser_id]['has_cheated'] = True
                # if round robin, replace player with a new default player
                if self.style == ROUND_ROBIN:
                    self.replace_player_with_default(loser_id)

        # announce game is over for both players
        try:
            player_1_obj['player'].end_game()
        except:
            # disconnect happened, treat as cheating
            if self.style == ROUND_ROBIN:
                self.replace_player_with_default(player_1_obj['id'])
            self.punish_cheating_player(player_1_obj['id'])

        try:
            player_2_obj['player'].end_game()
        except:
            # disconnect happened, treat as cheating
            if self.style == ROUND_ROBIN:
                self.replace_player_with_default(player_2_obj['id'])
            self.punish_cheating_player(player_2_obj['id'])

        return winner_id

    def punish_cheating_player(self, player_id):
        print(self.players[player_id]['name'] + ' has cheated by disconnection!')
        print(str(self.players[player_id]['score']) + ' points has been lost to the void!')
        self.players[player_id]['has_cheated'] = True
        self.players[player_id]['score'] = 0
                        
    def replace_player_with_default(self, player_id):
        player_factory = GoPlayerFactory()
        # register new default player into rankings
        default_player = self.create_default_player(self.path)
        (name, new_player) = self.protect_player_and_register(default_player, player_factory)
        new_player_id = len(self.players)

        self.players.append({
            'id': new_player_id,
            'player': new_player,
            'name': name,
            'has_cheated': False,
            'score': 0
        })

        # replace player from round robin matchings
        for i in range(len(self.player_matchings)):
            if self.player_matchings[i] == player_id:
                self.player_matchings[i] = new_player_id

    def play_match_and_update_winners(self, id_one, id_two, winner_ids):
        player_one = self.players[id_one]
        player_two = self.players[id_two]
        print('====== playing match ... ' + player_one['name'] + ' vs. ' + player_two['name'] + ' ======')
        winner_id = self.play_match(player_one, player_two)
        winner_ids.append(winner_id)

    def play_round(self, player_ids):
        # invariant, always given even number of players
        assert len(player_ids) % 2 == 0, "Not an even amount of players given!"

        winner_ids = []

        if self.style == ROUND_ROBIN:
            i = 0
            j = len(player_ids) - 1
            while i < j:
                self.play_match_and_update_winners(player_ids[i], player_ids[j], winner_ids)
                i += 1
                j -= 1

        elif self.style == SINGLE_ELIMINATION:
            it = iter(player_ids)
            for p in it:
                p_2 = next(it)
                self.play_match_and_update_winners(p, p_2, winner_ids)

        return winner_ids

    def play_tournament(self):
        total_rounds = len(self.players) - 1

        while total_rounds > 0:
            if self.style == ROUND_ROBIN:
                self.play_round(self.player_matchings)
                # update player matchings to use for next round (rotate counter-clockwise)
                self.player_matchings = self.player_matchings[-1:]+self.player_matchings[:-1]
                # each round consists for # players / 2 games per day, total of # players - 1 scheduling
                total_rounds -= 1

            elif self.style == SINGLE_ELIMINATION:
                winner_ids = self.play_round(self.remaining_players)
                # break
                # remaining rounds decreases by games played
                games_played = len(self.remaining_players) / 2
                # use winners to update remaining players to match
                # only remaining players will face off
                self.remaining_players = winner_ids
                total_rounds -= games_played
        
        rankings_str = self.get_rankings()

        return rankings_str

    def get_rankings(self):
        rankings = sorted(self.players, key = lambda p: p['score'], reverse=True)
        rankings_str = '====== Final standings =======\n\n'

        cheating_players = []
        same_score_players = []
        current_rank = 1
        for player in rankings:
            # check if they cheated
            if player['has_cheated']:
                if player['score'] != 0:
                    raise AssertionError("Cheating player has non-zero score!")
                cheating_players.append(player)
                continue

            if len(same_score_players) == 0:
                same_score_players.append(player)
            elif same_score_players[-1]['score'] == player['score']:
                same_score_players.append(player)
            else:
                # different scores flush the current players to rankings str
                same_score_players_str = ', '.join(list(map(lambda p: p['name'], same_score_players)))
                rankings_str += str(current_rank) + '. ' + same_score_players_str
                rankings_str += ' (with a score of ' + str(same_score_players[-1]['score']) + ')\n'
                current_rank += 1
                same_score_players = [player]
        
        # flush remaining players
        if len(same_score_players) > 0:
            same_score_players_str = ', '.join(list(map(lambda p: p['name'], same_score_players)))
            rankings_str += str(current_rank) + '. ' + same_score_players_str
            rankings_str += ' (with a score of ' + str(same_score_players[-1]['score']) + ')\n'
        
        # print cheaters
        # print(len(cheating_players))
        cheating_players_str = ', '.join(list(map(lambda p: p['name'], cheating_players)))
        rankings_str += '\ncheaters. ' + cheating_players_str + '\n'

        rankings_str += '\n==============================\n'

        return rankings_str
        
def main():
    tournament_type = str(sys.argv[1])
    remote_count = int(sys.argv[2])
    s.listen(remote_count)

    admin = GoTournamentAdministrator(socket=s, n=remote_count, style=tournament_type)
    rankings = admin.play_tournament()
    print('tournament is over...')
    print(rankings)

    s.close()
    sys.exit(0)
            
if __name__== "__main__":
    main()