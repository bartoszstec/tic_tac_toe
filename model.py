import numpy as np
import random

# return list of tuples with coordinates of empty cells
def list_possible_moves(board):
    possible_moves = []

    for row, col in ACTIONS:
        if board[row][col] is None:
            possible_moves.append((row, col))
    if not possible_moves:
        return None  # brak ruchów

    return possible_moves

#return tuple with random move
def random_move(board):
    possible_moves = list_possible_moves(board)

    if possible_moves is not None:
        return possible_moves[np.random.randint(len(possible_moves))]
    else:
        return None


# ------BASIC PARAMETERS------
board = np.array([[None, None, None],
                  ['X', 'O', 'O'],
                  ['O', 'X', 'X']])
current_player = 'X'
Q = {}

# list of tuples representing all moves in TIC TAC TOE game
ACTIONS = [
    (0, 0), (0, 1), (0, 2),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2)
]

# dict with indexes of actions
ACTION_TO_INDEX = {a: i for i, a in enumerate(ACTIONS)}

# ------CRUCIAL HIPERPARAMETERS------

# Tempo uczenia się (α, learning rate).
# Określa jak bardzo nowe doświadczenia (nowe Q-value) nadpisują stare wartości.
# - Wysoka wartość (np. 0.5) → szybkie uczenie, ale niestabilne.
# - Niska wartość (np. 0.001) → wolne uczenie, ale bardziej stabilne.
learning_rate = 0.001

# Czynnik dyskontujący przyszłe nagrody (γ, discount factor).
# Określa, jak bardzo agent "dba" o nagrody w przyszłości w porównaniu do nagrody tu i teraz.
# - γ bliskie 1.0 → agent uczy się planować "na długą metę".
# - γ bliskie 0 → agent patrzy tylko na natychmiastowe korzyści.
discount_factor = 0.9

# Współczynnik eksploracji (ε, exploration rate).
# Określa jak często agent wybiera losową akcję zamiast najlepszej znanej.
# - Wysoka wartość (np. 0.9) → dużo testowania losowych ruchów (eksploracja).
# - Niska wartość (np. 0.1) → głównie wykorzystywanie tego, co już się nauczył (eksploatacja).
exploration_rate = 0.5

# Liczba epizodów treningowych (ile razy agent zagra w całą grę od początku do końca).
# Im więcej epizodów, tym lepiej agent się uczy, bo ma więcej doświadczeń.
# Typowo od kilku tysięcy do setek tysięcy.
num_episodes = 10000

# TRAINING VALUES
agent_wins = 0

#function converting board as array to string to represent state in Q table
def board_to_string(board):
    return ''.join(cell if cell is not None else '-' for row in board for cell in row)

# WIN -> True, winning line
# DRAW -> True, 'draw'
# STILL PLAYING -> None
def is_game_over(board):
    winning_lines = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)]
    ]

    for line in winning_lines:
        values = []
        for (r, c) in line:
            values.append(board[r][c])
        if values[0] is not None and values[0] == values[1] and values[1] == values[2]:
            return True, values[0]
    if (is_board_full(board)):
        return True, 'draw'
    return False, None

def is_board_full(board):
    return all(element is not None for row in board for element in row)

def choose_action(board, exploration_rate):
    state = board_to_string(board)

    if random.uniform(0, 1) < exploration_rate or state not in Q:
        action = random_move(board)
    else:
        q_values = Q[state]
        empty_cells = list_possible_moves(board)
        empty_q_values = [q_values[ACTION_TO_INDEX[cell]] for cell in empty_cells]
        max_q_value = max(empty_q_values)
        max_q_indices = [i for i in range(len(empty_cells)) if empty_q_values[i] == max_q_value]
        max_q_index = random.choice(max_q_indices)
        action = empty_cells[max_q_index]

    return action

def board_next_state(board, cell, player):
    next_state = board.copy()                      #create a copy of current board state
    next_state[cell[0], cell[1]] = player
    return next_state

def update_q_table(state, action, next_state, reward):
    q_values = Q.get(state, np.zeros((3, 3))) # Retrieve the Q-values for a particular state from the Q-table dictionary Q.

    # Calculate the maximum Q-value for the next state
    next_q_values = Q.get(board_to_string(next_state), np.zeros((3, 3)))
    max_next_q_value = np.max(next_q_values)

    # Q-learning update equation
    q_values[action[0], action[1]] += learning_rate * (reward + discount_factor * max_next_q_value - q_values[action[0], action[1]])

    Q[state] = q_values

def start_algorithm(current_player, exploration_rate):
    # Main Q-learning algorithm
    for episode in range(num_episodes):
        board = np.array([[None, None, None],
                          [None, None, None],
                          [None, None, None]])

        current_player = 'X'
        game_over = False

        while not game_over:
            # Choose an action based on the current state
            action = choose_action(board, exploration_rate)

            # Make the chosen move
            row, col = action
            board[row, col] = current_player

            # Check if the game is over
            game_over, winner = is_game_over(board)
            if game_over:
                #Update the Q-table with the final reward
                if winner == current_player:
                    reward = 1
                elif winner == 'draw':
                    reward = 0.5
                else:
                    reward = 0
                update_q_table(board_to_string(board), action, board, reward)
            else:
                # Switch to the next player
                current_player = 'O' if current_player == 'X' else 'X'

            # Update the Q-table based on the immediate reward and the next state
            if not game_over:
                next_state = board_next_state(action)
                update_q_table(board_to_string(board), action, next_state, 0)

            # Decay the exploration rate
        exploration_rate *= 0.99






print(board)
print("---------------------------------------")
action1 = choose_action(board, exploration_rate)
print(action1)
print(board_next_state(board, action1, current_player))
