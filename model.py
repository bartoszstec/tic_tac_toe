import numpy as np
import random
import pickle
import json, os

# -----------------------------
# AUXILIARY FUNCTIONS
# -----------------------------

# list of tuples representing all moves in TIC TAC TOE game
ACTIONS = [
    (0, 0), (0, 1), (0, 2),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2)
]

#function converting board as array to string to represent state in Q table
def board_to_string(board):
    return ''.join(cell if cell is not None else '-' for row in board for cell in row)

# return list of tuples with coordinates of empty cells
def list_possible_moves(board):
    possible_moves = []

    for row, col in ACTIONS:
        if board[row][col] is None:
            possible_moves.append((row, col))
    if not possible_moves:
        return None  # no moves

    return possible_moves

#return tuple with random move
def random_move(board):
    possible_moves = list_possible_moves(board)

    if possible_moves is not None:
        return possible_moves[np.random.randint(len(possible_moves))]
    else:
        return None

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
    if is_board_full(board):            # WIN -> True, winning line
        return True, 'draw'             # DRAW -> True, 'draw'
    return False, None                  # STILL PLAYING -> None

def is_board_full(board):
    return all(element is not None for row in board for element in row)


# -----------------------------
# Q-learning PARAMS
# -----------------------------

# Learning pace (learning rate).
# It determines how much new experiences (new Q-values) overwrite old values.
# - High value (e.g. 0.5) → fast learning but unstable.
# - Low value (e.g. 0.001) → slow learning, but more stable.
learning_rate = 0.01

# Factor that discounts future rewards (discount factor).
# It determines how much the agent "cares" about rewards in the future compared to rewards in the here and now.
# - close to 1.0 → the agent learns to plan "for the long term".
# - close to 0 → the agent only looks at immediate benefits.
discount_factor = 0.85

# Exploration rate (using ε).
# Determines how often the agent chooses a random action instead of the best known one.
# - High value (e.g. 0.9) → a lot of testing random moves (exploration).
# - Low value (e.g. 0.1) → mainly using what has already been learned (exploitation).
# exploration_rate parameter is different for each episode and is determined by:
# FORMULA:      ϵ = ϵ_min + (ϵ_max - ϵ_min) * e^(-decay_rate * episode)
# (calculations in the training function)
epsilon_min = 0.01
epsilon_max = 0.9
decay_rate = 0.001


# Number of training episodes (number of times the agent plays the entire game from start to finish).
# The more episodes, the better the agent learns because he has more experience.
# Typically from several thousand to hundreds of thousands.
num_episodes = 100000

# -----------------------------
# CHOOSE MOVE
# -----------------------------
def choose_action(board, Q_table, exploration_rate):
    state = board_to_string(board)

    if random.uniform(0, 1) < exploration_rate or state not in Q_table:
        action = random_move(board)
    else:
        q_values = Q_table[state]
        empty_cells = list_possible_moves(board)
        empty_q_values = [q_values[row, col] for (row, col) in empty_cells]
        max_q_value = max(empty_q_values)
        max_q_indices = [i for i in range(len(empty_cells)) if empty_q_values[i] == max_q_value]
        max_q_index = random.choice(max_q_indices)
        action = empty_cells[max_q_index]

    return action

def board_next_state(board, cell, player):
    next_state = board.copy()                      #create a copy of current board state
    next_state[cell[0], cell[1]] = player
    return next_state


# -----------------------------
# UPDATE Q
# -----------------------------
def update_q_table(Q_table, state, action, next_state, reward):
    q_values = Q_table.get(state, np.zeros((3, 3))) # Retrieve the Q-values for a particular state from the Q-table dictionary Q.

    # Calculate the maximum Q-value for the next state
    next_q_values = Q_table.get(next_state, np.zeros((3, 3)))
    max_next_q_value = np.max(next_q_values)

    # Q-learning update equation
    q_values[action[0], action[1]] += learning_rate * (reward + discount_factor * max_next_q_value - q_values[action[0], action[1]])

    Q_table[state] = q_values

# -----------------------------
# TRAINING
# -----------------------------

def train_agents(epsilon_min, epsilon_max, decay_rate):
    Q_attack, Q_defence = {}, {}

    for episode in range(num_episodes):
        board = np.array([[None, None, None],
                          [None, None, None],
                          [None, None, None]])

        current_player = 'X'
        game_over = False
        last_moves = {"X": None, "O": None}

        # Set exploration rate for this episode
        exploration_rate = epsilon_min + (epsilon_max - epsilon_min) * np.exp(-decay_rate * episode)
        # print(exploration_rate)
        if episode % (num_episodes/10) == 0:
            simulate_games("attack", Q_attack, 500)
            simulate_games("defence", Q_defence, 500)

        while not game_over:
            Q = Q_attack if current_player == 'X' else Q_defence

            # Choose an action
            action = choose_action(board, Q, exploration_rate)
            state_str = board_to_string(board)
            next_board = board_next_state(board, action, current_player)
            next_state_str = board_to_string(next_board)

            # remember the player's last move
            last_moves[current_player] = (state_str, action, next_state_str)

            # Make the chosen move
            row, col = action
            board[row, col] = current_player

            # Check if the game is over
            game_over, winner = is_game_over(board)

            if game_over:
                if winner == 'X':
                    update_q_table(Q_attack, *last_moves['X'], reward=1)
                    update_q_table(Q_defence, *last_moves['O'], reward=-1)
                elif winner == 'O':
                    update_q_table(Q_attack, *last_moves['X'], reward=-1)
                    update_q_table(Q_defence, *last_moves['O'], reward=1)
                else:  # draw
                    update_q_table(Q_attack, *last_moves['X'], reward=0)
                    update_q_table(Q_defence, *last_moves['O'], reward=1)
            else:
                # ongoing reward
                ongoing_reward = -0.5 if current_player == 'X' else 0
                update_q_table(Q, state_str, action, next_state_str, ongoing_reward)

            current_player = 'O' if current_player == 'X' else 'X'
    return Q_attack, Q_defence

# -----------------------------
# SAVE AND LOAD
# -----------------------------
def save_model(Q_table, filename="q_table.pkl"):
    try:
        with open(filename, "wb") as f:
            pickle.dump(Q_table, f)
            print(f"Saved a file named: {filename}")
    except Exception as e:
        print(f"An error occurred while saving: {e}")


def load_model(filename="q_table.pkl"):
    try:
        with open(filename, "rb") as f:
            print(f"File successfully loaded: {filename}!")
            return pickle.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' has not been found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the model: {e}")
        return None

# -----------------------------
# PERFORM TRAINED MOVE
# -----------------------------
def trained_move(board, Q_table):
    """
        Choosing the best move basen on trained Q-table.

        Args:
            board (np.array): Current state of board.
            Q_table (dict): table with Q values,

        Returns:
            Tuple: (row, col) representing the best move.
            None: if there are no moves available.
        """
    state = board_to_string(board)
    possible_moves = list_possible_moves(board)

    if not possible_moves:
        return None

    if state not in Q_table:
        print("Unknown state, making a random move.")
        return random_move(board)

    q_values = Q_table[state]

    # Find the Q values for available moves
    empty_q_values = [q_values[row, col] for (row, col) in possible_moves]
    max_q_value = max(empty_q_values)

    # Randomly choose one of all moves with the highest Q value to avoid determinism
    best_moves_indices = [i for i, q_val in enumerate(empty_q_values) if q_val == max_q_value]
    best_move_index = random.choice(best_moves_indices)

    return possible_moves[best_move_index]

# -----------------------------
# PERFORM LEARNING MOVE
# -----------------------------
def learning_move(board, Q_table):
    # strategy dependent move and update of Q_table by playing with human player
    pass #return action


# -----------------------------
# EVALUATE MODEL
# -----------------------------
def simulate_games(purpose, model, games=1000):
    wins, draws, losses = 0, 0, 0
    Q_table = model

    if purpose == 'attack':
        agent_player = 'X'
    elif purpose == 'defence':
        agent_player = 'O'
    else:
        return print("Unknown evaluate purpose, evaluation process breaking...")

    for _ in range(games):
        board = np.array([[None] * 3 for _ in range(3)])
        current_player = 'X'
        game_over = False
        winner = None

        while not game_over:
            if current_player == agent_player:  # agent turn
                move = trained_move(board, Q_table)
            else:  # random opponent
                possible = list_possible_moves(board)
                move = random.choice(possible)

            board[move] = current_player
            game_over, winner = is_game_over(board)
            current_player = 'O' if current_player == 'X' else 'X'

        if winner == agent_player:
            wins += 1
        elif winner == 'draw':
            draws += 1
        else:
            losses += 1
    return wins, draws, losses

def evaluate(purpose, model, games=1000):
    wins, draws, losses = simulate_games(purpose, model, games)

    dane = []
    filename = 'effectiveness_vs_parameters.json'

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                dane = json.load(f)
            except json.JSONDecodeError:
                dane = []

    effectiveness = wins/games*100
    effectiveness_draws = draws/games*100
    loss_ratio = 100 - effectiveness_draws - effectiveness
    stats = {"training_purpose": f"{purpose}", "effectiveness": f"{effectiveness:.2f}%", "effectiveness_draws": f"{effectiveness_draws:.2f}%",
               "loss_ratio":f"{loss_ratio:.2f}%", "wins": wins, "draws": draws, "losses": losses,
               "learning_rate": learning_rate, "discount_factor": discount_factor, "num_episodes": num_episodes,
               "epsilon_min": epsilon_min, "epsilon_max": epsilon_max, "decay_rate": decay_rate}

    dane.append(stats)

    with open(filename, 'w') as f:
        json.dump(dane, f, indent=2)

    print("--------------------------------------------------------------------")
    print(f"PURPOSE: {purpose}")
    print(f"Wins: {wins}, Draws: {draws}, Losses: {losses}")
    print(f"Win-ratio: {effectiveness:.2f}%")
    print(f"Draw-ratio: {effectiveness_draws:.2f}%")
    print(f"Lose-ratio: {loss_ratio:.2f}%")



# RUN MODEL
if __name__ == "__main__":
    print("Loading trained model...")
    Qa = load_model("q_table_A.pkl")
    Qd = load_model("q_table_D.pkl")
    # evaluate("attack", Qa, 10000)
    # evaluate("defence", Qd, 10000)
    if (Qa or Qd) is None:
        print("Agents Training...")
        Qa, Qd = train_agents(epsilon_min, epsilon_max, decay_rate)
        save_model(Qa, "q_table_A.pkl")
        save_model(Qd, "q_table_D.pkl")
        evaluate("attack", Qa, 10000)
        evaluate("defence", Qd, 10000)
        #Qa = load_model("q_table_A.pkl")
        #Qd = load_model("q_table_D.pkl")







