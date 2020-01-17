import re
# Point Class converts a given point into x and y coordinates
from board_components.definitions import BOARD_SIZE_X, BOARD_SIZE_Y

##########################################
## This module implements the GO point ##
#########################################

class Point:
    def __init__(self, point, is_list=False):
        if isinstance(point,str):
            regex = r'^[0-9]-[0-9]$'
            assert re.match(regex, point), "Not valid point format!"
            p_tokens = re.split(r'-', point)
            self.x = int(p_tokens[1]) - 1
            self.y = int(p_tokens[0]) - 1
            # check if valid range
            assert self.x >= 0 and self.x < BOARD_SIZE_X, "Not valid x range for point!"
            assert self.y >= 0 and self.y < BOARD_SIZE_Y, "Not valid y range for point!"

        elif is_list:
            self.x = point[0]
            self.y = point[1]
        else:
            raise AssertionError("invalid type is given as a point!")

    def get_point_repr(self):
        return "{}-{}".format(self.y+1, self.x+1)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(self.get_point_repr())
