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

  # Determine opponent
  opponent = 2

  if player == 2:
    opponent = 1

  # --- HELPER FUNCTIONS
  # Return the piece from the specified row and column
  # Used to make later code look better
  def get_stone(future_board, pos_row, pos_col):
    return future_board[pos_row][pos_col]
  
  def change_stone(future_board, pos, player_num):
    future_board[pos[GET_ROW]][pos[GET_COL]] = player_num

  # Make sure that location is within board boundaries
  def within_boundaries(pos_row, pos_col):
    within_max_boundary = pos_row < board_rows and pos_col < board_cols
    within_min_boundary = pos_row >= 0 and pos_col >= 0
    return within_max_boundary and within_min_boundary

  # Search in specified direction for stones that can be flipped
  # Depending on arguments, can search linearly or diagonally
  def search_direction(future_board, player_num, position, dir):
    # Extract search direction from dir array
    dir_row = dir[GET_ROW]
    dir_col = dir[GET_COL]

    # Start at first position from current
    pos_row = position[GET_ROW] + dir_row
    pos_col = position[GET_COL] + dir_col

    flipped_stones = []
    valid = False

    while within_boundaries(pos_row, pos_col):
      stone = get_stone(future_board, pos_row, pos_col)

      if stone == NO_STONE:
        break
      # End loop and mark direction as valid if player's stone is found at the end
      elif stone == player_num:
        valid = True
        break
      else:
        flipped_stones.append([pos_row, pos_col])

      # Move in specified direction
      pos_row += dir_row
      pos_col += dir_col

    if valid:
      return flipped_stones
    else:
      return None

  # --- DETERMINE VALID MOVES
  def find_valid_moves(future_board, player_num):
    valid_moves = []

    # Determine valid moves
    for col in range(board_cols):
      for row in range(board_rows):
        stone_value = future_board[row][col]

        # Invalid - if a stone is already in the current position
        if stone_value != 0:
          continue

        flipped_stones = []  # Array of positions of flipped stones found during searching
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
          search_result = search_direction(future_board, player_num, current_pos, direction)

          if search_result is not None:
            flipped_stones += search_direction(future_board, player_num, current_pos, direction)

        if len(flipped_stones) > 0:
          valid_moves.append([flipped_stones, current_pos])

    return valid_moves
  
  # Valid moves: [[[1, 2], [2, 3], [3, 2]], [1, 3]]

  # --- DETERMINE BEST MOVES

  def copy_board(input_board):
    return input_board.copy()

  # Counts the pieces on the board
  # Returns which player has the majority of stones, as well as if the board is full or not
  def check_board_conditions(future_board):
    player_one_stones = 0
    player_two_stones = 0

    board_full = True

    for col in range(board_cols):
      for row in range(board_rows):
        stone = get_stone(future_board, row, col)

        if stone == 0:
          board_full = False
        elif stone == 1:
          player_one_stones += 1
        elif stone == 2:
          player_two_stones += 1

    return board_full, player_one_stones, player_two_stones

  # Variables to better help navigate valid_moves array
  LIST_FLIPPED = 0
  LIST_POS = 1

  scores = {
    'Opp has no stones': 5000,
    'Plr wins': 1000,
    'Opp has less stones': 100,
    'Same amount of stones': -50,
    'Opp has more stones': -200,
    'Tie game': -3000,
    'Plr loses': -5000,
    'Plr has no pieces': -9999
  }

  def calculate_score(board_full, player_one_stones, player_two_stones):
    player_stones = player_one_stones
    opponent_stones = player_two_stones

    if player == 2:
      player_stones = player_two_stones
      opponent_stones = player_one_stones

    if opponent_stones == 0:
      return scores['Opp has no stones']
    elif player_stones == 0:
      return scores['Plr has no pieces']
    
    majority_stones = 0

    if player_one_stones > player_two_stones:
      majority_stones = 1
    elif player_two_stones < player_one_stones:
      majority_stones = 2
    
    if board_full:
      if majority_stones == player:
        return scores['Plr wins']
      elif majority_stones == opponent:
        return scores['Plr loses']
      else:
        return scores['Tie game']
      
    if majority_stones == player:
      return scores['Opp has less stones']
    elif majority_stones == opponent:
      return scores['Opp has more stones']
    else:
      return scores['Same amount of stones']
    
  def make_move(future_board, move, player_num):
    # Move[[1, 2], [2, 3], [3, 2]], [1, 3]

    change_stone(future_board, move[1], player_num)

    for stone in move[0]:
      change_stone(future_board, stone, player_num)


  def find_best_move(future_board, max_player, iterations_left):
    player_num = player

    if not max_player:
      player_num = opponent

    valid_moves = find_valid_moves(future_board, player_num)
    board_full, player_one_stones, player_two_stones = check_board_conditions(future_board)

    if iterations_left == 0 or board_full or len(valid_moves) == 0:
      return None, calculate_score(board_full, player_one_stones, player_two_stones)
    
    # If end conditions not met, recurse
    optimal_move = valid_moves[0][1]

    if (max_player):
      current_score = float('-inf')

      for move in valid_moves:
        future_board = copy_board(future_board)
        make_move(future_board, move, player)
        resulting_score = find_best_move(future_board, False, iterations_left - 1)[1]

        if resulting_score > current_score:
          current_score = resulting_score
          optimal_move = move[1]
    else:
      current_score = float('inf')

      for move in valid_moves:
        future_board = copy_board(future_board)
        make_move(future_board, move, opponent)
        resulting_score = find_best_move(future_board, True, iterations_left - 1)[1]

      if resulting_score < current_score:
        current_score = resulting_score
        optimal_move = move[1]

    return optimal_move, current_score
    
  # Determine move with the most flipped stones
  amount_iterations = 50
  best_move, score = find_best_move(copy_board(board), True, amount_iterations)

  print("Resulting score:", str(score))

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
