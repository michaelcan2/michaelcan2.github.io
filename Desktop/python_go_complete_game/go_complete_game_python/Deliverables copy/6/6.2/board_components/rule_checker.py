from abc import abstractmethod
import contracts
from contracts import contract, ContractsMeta, with_metaclass
from copy import deepcopy
from board_components.point import Point
from board_components.board import Board
from board_components.definitions import MIN_HIST_LENGTH, MAX_HIST_LENGTH, MAX_SCORE, WHITE_STONE, BLACK_STONE, EMPTY_STONE

class RuleCheckerInterface(with_metaclass(ContractsMeta, object)):
    @abstractmethod
    @contract(s='str', returns='bool')
    def move_pass(self, s):
        """
            Player skips turn, this move is always valid.
        """
        pass

    @abstractmethod
    @contract(s='str', returns='s')
    def get_opponent(self, s):
        """
            Returns the opponent's stone given the player's stone.
        """
        pass

    @abstractmethod
    @contract(s='str', p='$Point', b='$Board', returns='$Board')
    def place_and_remove(self, s, p, b):
        """
            Places the given point on the given board, then removes any captured pieces as a result of the placed point. 
            Returns the new board with the piece placed and necessary pieces removed.
        """
        pass

    @abstractmethod
    @contract(s='str', p='$Point', hist='list[>=$MIN_HIST_LENGTH,<=$MAX_HIST_LENGTH]($Board)', returns='bool')
    def move_play(self, s, p, hist):
        """
            Gives point on the current board where the player would like to place one of their stones in addition to history 
            of board. Returns true if the Move is legal for the player whose stones are Stone based on the information provided,
            otherwise false.
        """
        pass

    @abstractmethod
    @contract(b='$Board', returns='dict[2](str: int,>=0,<=$MAX_SCORE)')
    def count_score(self, b):
        """
            Returns a dict with two keys "B" and "W" whose values are numbers representing the scores of the players with 
            the corresponding stones based on the given board.
        """
        pass

    @abstractmethod
    @contract(hist='list[>=1,<=4]($Board)', s='str', returns='bool')
    def verify_history(self, hist, s):
        """
            Checks if the given history is valid, otherwise false.
        """
        pass

    @abstractmethod
    @contract(hist='list[>=1,<=3]($Board)', s='str', returns='bool')
    def verify_history_jr(self, hist, s):
        """
            Checks if the given history is valid, otherwise false.
        """
        pass

######## Implementation below ########

class RuleChecker(RuleCheckerInterface):
    def __init__(self):
        pass

    def move_pass(self, s):
        return True

    def get_opponent(self, s):
        if s == WHITE_STONE:
            return BLACK_STONE
        else:
            return WHITE_STONE

    def place_and_remove(self, s, p, b):
        new_board = deepcopy(b)
        # place a point
        new_board.place(s, p)

        # remove opposing stones that get captured
        not_s = self.get_opponent(s)
        opponent_points = new_board.get_points(not_s)

        points_to_remove = []

        for pp in opponent_points:
            enemy_point = Point(pp)
            if not new_board.reachable(enemy_point, EMPTY_STONE):
                points_to_remove.append(enemy_point)

        # remove any points that are captured
        for pp in points_to_remove:
            new_board.remove(not_s , pp)

        return new_board

    def move_play(self, s, p, hist):
        recent_board = hist[0]
        # if occupied then play cannot be legal
        if recent_board.occupied(p):
            return False
        
        # place down the point
        new_board = self.place_and_remove(s, p, recent_board)

        # checks for illegal suicide
        if not new_board.reachable(p, EMPTY_STONE):
            return False
        
        # create new hist with the valid play
        new_hist = [new_board] + hist

        # validify all hist makes sense
        if not self.verify_history(new_hist, s):
            return False
        
        return True

    def count_score(self, b):
        # count num of points for each maybestone
        B_score = b.get_num_black_stones()
        W_score = b.get_num_white_stones()
        empty_points = b.get_points(EMPTY_STONE)

        # look for territories
        for p in empty_points:
            p = Point(p)
            re_B = b.reachable(p, BLACK_STONE)
            re_W = b.reachable(p, WHITE_STONE)
            # check if neutral, otherwise add to some player score
            if re_B and re_W:
                continue
            elif re_W:
                W_score += 1
            elif re_B:
                B_score += 1

        return {"B": B_score,"W": W_score}

    def verify_history(self, hist, s):
        # recall hist is now [board from play] + [hist]
        # Rule 5: Initial position: At the beginning of the game, the board is empty.
        if len(hist) <= MAX_HIST_LENGTH:
            init_board = hist[-1]
            # last board must be empty
            if not init_board.is_empty():
                return False

            first_turn_board = hist[-2]
            start_black_count = first_turn_board.get_num_black_stones()
            start_white_count = first_turn_board.get_num_white_stones()
            # first turn board must either be empty or contain one black stone only
            if not (first_turn_board.is_empty() or (start_black_count == 1 and start_white_count == 0)):
                return False

        # 2 passes is invalid, ko rule: One may not play in such a way as to recreate the board position following one's previous move.
        if len(hist) == 3:
            if s != WHITE_STONE:
                return False
            if hist[0] == hist[2]:
                return False

        if len(hist) == 4:
            if hist[0] == hist[2] or hist[1] == hist[3]:
                return False
            if hist[-1].is_empty() and hist[-2].is_empty() and s != BLACK_STONE:
                return False

        # Rule 6: The players alternate thereafter. 
        # get player_turn at beginning of history, given the most recent player turn       
        if len(hist) % 2 == 0:
            player_turn = s
            other_player = self.get_opponent(s)
        else:
            other_player = s
            player_turn = self.get_opponent(s)

        # traverse backwards so starting from oldest boards to newest
        i = len(hist) - 1
        while i > 0 and len(hist) > 1:
            prev_board = hist[i]
            next_board = hist[i-1]
            i -= 1
            # get stone counts of {B: int, W: int}
            r1 = prev_board.get_players_stone_count()
            r2 = next_board.get_players_stone_count()
            # check if its a pass
            if prev_board == next_board:
                # swap for next turn
                player_turn, other_player = other_player, player_turn
                continue

            # check player turn added a stone
            if (r2[player_turn] - r1[player_turn]) == 1:
                # check if other player's stone count changes -> capturing occurred
                # check if capturing is valid
                player_points_before = prev_board.get_points(player_turn)
                player_points_after = next_board.get_points(player_turn)
                # get point placed
                placed_point = Point([p for p in player_points_after if p not in player_points_before][0])
                # check if occupied on prev board
                if prev_board.occupied(placed_point):
                    return False
                guessed_board = self.place_and_remove(player_turn, placed_point, prev_board)
                # check between hypothetical new board and next board
                if guessed_board != next_board:
                    return False

                # swap for next turn
                player_turn, other_player = other_player, player_turn
            else:
                return False

        # check if board has a stone with no liberties
        for board in hist:
            B_points = board.get_points(BLACK_STONE)
            for p in B_points:
                pp = Point(p)
                if not board.reachable(pp, EMPTY_STONE):
                    return False
            W_points = board.get_points(WHITE_STONE)
            for p in W_points:
                pp = Point(p)
                if not board.reachable(pp, EMPTY_STONE):
                    return False

        return True

    def verify_history_jr(self, hist, s):
        # Rule 5: Initial position: At the beginning of the game, the board is empty.
        if len(hist) < 3:
            init_board = hist[-1]
            # last board must be empty
            if not init_board.is_empty():
                return False

        if len(hist) == 1:
            if s != BLACK_STONE:
                return False

        # 2 passes is invalid, ko rule: One may not play in such a way as to recreate the board position following one's previous move.
        if len(hist) == 2:
            if s != WHITE_STONE:
                return False

            first_turn_board = hist[-2]
            start_black_count = first_turn_board.get_num_black_stones()
            start_white_count = first_turn_board.get_num_white_stones()
            # first turn board must either be empty or contain one black stone only
            if not (first_turn_board.is_empty() or (start_black_count == 1 and start_white_count == 0)):
                return False

        if len(hist) == 3:
            if hist[0] == hist[2]:
                return False
            if hist[-1].is_empty() and hist[-2].is_empty() and s != BLACK_STONE:
                return False

        # Rule 6: The players alternate thereafter. 
        # get player_turn at beginning of history, given the most recent player turn       
        if len(hist) % 2 != 0:
            player_turn = s
            other_player = self.get_opponent(s)
        else:
            other_player = s
            player_turn = self.get_opponent(s)

        # traverse backwards so starting from oldest boards to newest
        i = len(hist) - 1
        while i > 0 and len(hist) > 1:
            prev_board = hist[i]
            next_board = hist[i-1]
            i -= 1
            # get stone counts of {B: int, W: int}
            r1 = prev_board.get_players_stone_count()
            r2 = next_board.get_players_stone_count()
            # check if its a pass
            if prev_board == next_board:
                # swap for next turn
                player_turn, other_player = other_player, player_turn
                continue
            
            # check player turn added a stone
            if (r2[player_turn] - r1[player_turn]) == 1:
                # check if other player's stone count changes -> capturing occurred
                # check if capturing is valid
                player_points_before = prev_board.get_points(player_turn)
                player_points_after = next_board.get_points(player_turn)
                # get point placed
                placed_point = Point([p for p in player_points_after if p not in player_points_before][0])
                # check if occupied on prev board
                if prev_board.occupied(placed_point):
                    return False
                guessed_board = self.place_and_remove(player_turn, placed_point, prev_board)
                # check between hypothetical new board and next board
                if guessed_board != next_board:
                    return False

                # swap for next turn
                player_turn, other_player = other_player, player_turn
            else:
                return False

        # check if board has a stone with no liberties
        for board in hist:
            B_points = board.get_points(BLACK_STONE)
            for p in B_points:
                pp = Point(p)
                if not board.reachable(pp, EMPTY_STONE):
                    return False
            W_points = board.get_points(WHITE_STONE)
            for p in W_points:
                pp = Point(p)
                if not board.reachable(pp, EMPTY_STONE):
                    return False

        return True