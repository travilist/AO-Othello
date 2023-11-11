#!/usr/bin/python

import sys
import json
import socket

def get_move(player, board):
  # --- "STATIC" VARIABLES
  # Movement directions
  # Can be combined for diagonals
  SEARCH_UP = 1
  SEARCH_DOWN = -1
  SEARCH_RIGHT = 1
  SEARCH_LEFT = -1
  SEARCH_NONE = 0

  # Array navigators
  # Just to make it easier to read certain code
  GET_ROW = 0
  GET_COL = 1

  # Stone variables
  NO_STONE = 0

  # Board size
  board_rows = len(board)
  board_cols = len(board[0])

  # --- HELPER FUNCTIONS
  # Return the piece from the specified row and column
  # Used to make later code look better
  def get_stone(pos_row, pos_col):
    return board[pos_row][pos_col]

  # Make sure that location is within board boundaries
  def within_boundaries(pos_row, pos_col):
    within_max_boundary = pos_row < board_rows and pos_col < board_cols
    within_min_boundary = pos_row >= 0 and pos_col >= 0
    return within_max_boundary and within_min_boundary

  # Search in specified direction for stones that can be flipped
  # Depending on arguments, can search linearly or diagonally
  def search_direction(position, dir):
    # Extract search direction from dir array
    dir_row = dir[GET_ROW]
    dir_col = dir[GET_COL]

    # Start at first position from current
    pos_row = position[GET_ROW] + dir_row
    pos_col = position[GET_COL] + dir_col

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

  # --- DETERMINE VALID MOVES
  valid_moves = []

  # Determine valid moves
  for col in range(board_cols):
    for row in range(board_rows):
      stone_value = board[row][col]

      # Invalid - if a stone is already in the current position
      if stone_value != 0:
        continue

      flipped_stones = 0  # Amount of flipped stones found during searching
      current_pos = [row, col]  # Current loop position, for searching input

      search_directions = [
        [SEARCH_UP, SEARCH_NONE], # UP
        [SEARCH_DOWN, SEARCH_NONE], # DOWN
        [SEARCH_NONE, SEARCH_RIGHT], # RIGHT
        [SEARCH_NONE, SEARCH_LEFT], # LEFT
        [SEARCH_DOWN, SEARCH_RIGHT], # BOTTOM RIGHT DIAGONAL
        [SEARCH_UP, SEARCH_RIGHT], # TOP RIGHT DIAGONAL
        [SEARCH_DOWN, SEARCH_LEFT], # BOTTOM LEFT DIAGONAL
        [SEARCH_UP, SEARCH_LEFT] # TOP LEFT DIAGONAL
      ]

      # Search all directions for opposing player's stones that can be flipped
      for direction in search_directions:
        flipped_stones += search_direction(current_pos, direction)

      if flipped_stones > 0:
        valid_moves.append([flipped_stones, current_pos])

  # --- DETERMINE BEST MOVES
  def get_amount_flipped(valid_move):
    return valid_move[0]

  # Determine move with the most flipped stones
  best_move = max(valid_moves, key=get_amount_flipped)[1]

  return best_move

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
