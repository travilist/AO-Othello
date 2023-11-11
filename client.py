#!/usr/bin/python

import sys
import json
import socket

# board = [[0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 1, 2, 0, 0, 0],
#          [0, 0, 0, 2, 1, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0]]

def get_move(player, board):
  # Movement directions
  # Can be combined for diagonals
  MOVE_UP = 1
  MOVE_DOWN = -1
  MOVE_RIGHT = 1
  MOVE_LEFT = -1

  # Array navigators
  # Just to make it easier to read certain code
  GET_ROW = 0
  GET_COL = 1

  # Stone variables
  NO_STONE = 0

  # Diagonals:
  # Bottom left:  [MOVE_DOWN, MOVE_LEFT]
  # Top left:     [MOVE_UP, MOVE_LEFT]
  # Bottom right: [MOVE_DOWN, MOVE_RIGHT]
  # Top right:    [MOVE_UP, MOVE RIGHT]

  board_rows = len(board)
  board_cols = len(board[0])

  # Return the piece from the specified row and column
  # Used to make later code look better
  def get_stone(pos_row, pos_col):
    return board[pos_row][pos_col]

  # Make sure that location is within board boundaries
  def within_boundaries(pos_row, pos_col):
    return pos_row < board_rows and pos_col < board_cols

  # Search in specified direction for stones that can be flipped
  # Depending on arguments, can search linearly or diagonally
  def search_direction(position, dir_row, dir_col):
    # Start at current position
    pos_row = position[GET_ROW]
    pos_col = position[GET_COL]

    flipped_stones = 0
    valid = False

    while within_boundaries(pos_row, pos_col):
      stone = get_stone(pos_row, pos_col)

      if stone == NO_STONE:
        break
      # End loop and mark direction as valid if player's stone is found at the end
      elif stone == player:
        valid = True
        break
      else:
        flipped_stones += 1

      # Move in specified direction
      pos_row += dir_row
      pos_col += dir_col

    if valid:
      return flipped_stones
    else:
      return 0

  valid_moves = []

  # Determine valid moves
  for col in range(board_cols):
    for row in range(board_rows):
      stone_value = board[row][col]

      # Invalid - if a stone is already in the current position
      if stone_value != 0:
        continue

      flipped_stones = 0
      # Search all directions for opposing player's stones that can be flipped
      


  # TODO determine best move
  return [2, 3]

def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    while True:
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      maxTurnTime = json_data['maxTurnTime']
      player = json_data['player']
      print(player, maxTurnTime, board)

      move = get_move(player, board)
      response = prepare_response(move)
      sock.sendall(response)
  finally:
    sock.close()
