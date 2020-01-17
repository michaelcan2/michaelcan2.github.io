import pytest
from board_components.board import Board
from board_components.point import Point

def test_invalid_board_size():
  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " ", " ", " "], 
       [" ", " ", " ", " "], 
       [" ", " ", " ", " "], 
       [" ", " ", " ", " "]]
    )

  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " "]]
    )
  
  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "]]
    )

  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "]]
    )

def test_invalid_board_piece():
  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", "w", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "]]
    )

  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", "b", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "]]
    )

  with pytest.raises(AssertionError):
    b = Board(
      [[" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "],
       [" ", " ", "X", " ", " ", " ", " ", " ", " "],
       [" ", " ", " ", " ", " ", " ", " ", " ", " "]]
    )

def test_invalid_point_type():
  with pytest.raises(AssertionError):
    p = Point(9)
  
  with pytest.raises(AssertionError):
    p = Point([1,1])

  with pytest.raises(AssertionError):
    p = Point(['1', '1'])

  with pytest.raises(AssertionError):
    p = Point((1,1))

  with pytest.raises(AssertionError):
    p = Point(('1','1'))

  with pytest.raises(AssertionError):
    p = Point({'value': '1-1'})
  
  with pytest.raises(AssertionError):
    p = Point(True)

def test_invalid_point_format():
  with pytest.raises(AssertionError):
    p = Point('bananas')

  with pytest.raises(AssertionError):
    p = Point('a-a')
  
  with pytest.raises(AssertionError):
    p = Point('1-1 ')

  with pytest.raises(AssertionError):
    p = Point('09-09')

  with pytest.raises(AssertionError):
    p = Point('1-')
  
  with pytest.raises(AssertionError):
    p = Point('1')

def test_out_of_range_point():
  with pytest.raises(AssertionError):
    p = Point('0-0')

  with pytest.raises(AssertionError):
    p = Point('0-1')
  
  with pytest.raises(AssertionError):
    p = Point('-1-1')

  with pytest.raises(AssertionError):
    p = Point('10-10')