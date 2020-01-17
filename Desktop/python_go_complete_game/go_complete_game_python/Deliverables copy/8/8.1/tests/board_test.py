import pytest
from board_components.board import Board
from board_components.point import Point

def test_place_bad_stone():
    with pytest.raises(AssertionError):
        b = Board()
        b.place('w', Point('1-1'))

def test_place_same_spot():
    b = Board()
    b.place('W', Point('1-1'))
    assert b.place('B', Point('1-1')) == 'This seat is taken!'
    
def test_remove_nothing():
    b = Board()
    assert b.remove('B', Point('1-1')) == 'I am just a board! I cannot remove what is not there!'