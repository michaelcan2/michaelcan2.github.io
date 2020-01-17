import re
# Point Class converts a given point into x and y coordinates

class Point:
    def __init__(self, point):
        if isinstance(point,str):
            regex = r'^[0-9]?[0-9]-[0-9]?[0-9]$'
            assert re.match(regex, point), "Not valid point format!"
            p_tokens = re.split(r'-', point)
            self.x = int(p_tokens[1]) - 1
            self.y = int(p_tokens[0]) - 1

        elif isinstance(point,list):
            self.x = point[0]
            self.y = point[1]

    def get_point_repr(self):
        return "{}-{}".format(self.y+1, self.x+1)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(self.get_point_repr())
