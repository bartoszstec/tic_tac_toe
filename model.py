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
    if is_board_full(board):
        return True, 'draw'
    return False, None

def is_board_full(board):
    return all(element is not None for row in board for element in row)


# -----------------------------
# Q-learning PARAMS
# -----------------------------

# Tempo uczenia się (α, learning rate).
# Określa jak bardzo nowe doświadczenia (nowe Q-value) nadpisują stare wartości.
# - Wysoka wartość (np. 0.5) → szybkie uczenie, ale niestabilne.
# - Niska wartość (np. 0.001) → wolne uczenie, ale bardziej stabilne.
learning_rate = 0.001

# Czynnik dyskontujący przyszłe nagrody (γ, discount factor).
# Określa, jak bardzo agent "dba" o nagrody w przyszłości w porównaniu do nagrody tu i teraz.
# - γ bliskie 1.0 → agent uczy się planować "na długą metę".
# - γ bliskie 0 → agent patrzy tylko na natychmiastowe korzyści.
discount_factor = 0.8

# Współczynnik eksploracji (ε, exploration rate).
# Określa jak często agent wybiera losową akcję zamiast najlepszej znanej.
# - Wysoka wartość (np. 0.9) → dużo testowania losowych ruchów (eksploracja).
# - Niska wartość (np. 0.1) → głównie wykorzystywanie tego, co już się nauczył (eksploatacja).
exploration_rate = 0.85
exploration_decrement_factor = 0.995
starting_exploration_rate = exploration_rate

# Liczba epizodów treningowych (ile razy agent zagra w całą grę od początku do końca).
# Im więcej epizodów, tym lepiej agent się uczy, bo ma więcej doświadczeń.
# Typowo od kilku tysięcy do setek tysięcy.
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

def train_agents():
    global exploration_rate
    Q_attack = {}
    Q_defence = {}
    for episode in range(num_episodes):
        board = np.array([[None, None, None],
                          [None, None, None],
                          [None, None, None]])

        current_player = 'X'
        game_over = False

        while not game_over:
            if current_player == 'X':
                Q = Q_attack
            else:
                Q = Q_defence

            # Choose an action based on the current state of board
            action = choose_action(board, Q, exploration_rate)

            # Save actual and next state of board
            state = board.copy()
            next_state = board_next_state(board, action, current_player)

            # Make the chosen move
            row, col = action
            board[row, col] = current_player

            # Check if the game is over
            game_over, winner = is_game_over(board)
            if current_player == 'O':
                if game_over:
                    # Update the Q-table with the final reward
                    if winner == 'O':
                        reward = 0.6
                    elif winner == 'draw':
                        reward = 1
                    else:
                        reward = -1
                    update_q_table(Q, board_to_string(state), action, board_to_string(next_state), reward)
                else:
                    update_q_table(Q, board_to_string(state), action, board_to_string(next_state), -0.5)

            if current_player == 'X':
                if game_over:
                    # Update the Q-table with the final reward
                    if winner == 'X':
                        reward = 1
                    elif winner == 'draw':
                        reward = 0
                    else:
                        reward = -1
                    update_q_table(Q, board_to_string(state), action, board_to_string(next_state), reward)
                else:
                    update_q_table(Q, board_to_string(state), action, board_to_string(next_state), -0.5)

            current_player = 'O' if current_player == 'X' else 'X'

            # Decay the exploration rate
        exploration_rate = max(0.1, exploration_rate * exploration_decrement_factor)
    return Q_attack, Q_defence

# -----------------------------
# SAVE AND LOAD
# -----------------------------
def save_model(Q_table, filename="q_table.pkl"):
    try:
        with open(filename, "wb") as f:
            pickle.dump(Q_table, f)
            print(f"Zapisano plik o nazwie: {filename}")
    except Exception as e:
        print(f"Wystąpił błąd podczas zapisu: {e}")


def load_model(filename="q_table.pkl"):
    try:
        with open(filename, "rb") as f:
            print(f"Pomyślnie wczytano plik: {filename}!")
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Plik '{filename}' nie został znaleziony.")
        return None
    except Exception as e:
        print(f"Wystąpił błąd podczas wczytywania modelu: {e}")
        return None

# -----------------------------
# PERFORM TRAINED MOVE
# -----------------------------
def trained_move(board, Q_table):
    """
        Choosing the best move basen on trained Q-table.

        Args:
            board (np.array): Aktualny stan planszy.
            table with values of profitability of moves: Q_table

        Returns:
            tuple: Krotka (row, col) reprezentująca najlepszy ruch.
            None: Jeśli nie ma dostępnych ruchów.
        """
    state = board_to_string(board)
    possible_moves = list_possible_moves(board)

    if not possible_moves:
        return None

    if state not in Q_table:
        #print("Nieznany stan, wykonuję losowy ruch.")
        return random_move(board)

    q_values = Q_table[state]

    # Znajdź wartości Q dla dostępnych ruchów
    empty_q_values = [q_values[row, col] for (row, col) in possible_moves]
    max_q_value = max(empty_q_values)

    # Wybierz losowo jeden z ruchów o najwyższej wartości Q, aby uniknąć determinizmu
    best_moves_indices = [i for i, q_val in enumerate(empty_q_values) if q_val == max_q_value]
    best_move_index = random.choice(best_moves_indices)

    return possible_moves[best_move_index]


# -----------------------------
# EVALUATE MODEL
# -----------------------------
def evaluate(purpose, model, games=1000):
    wins, draws, losses = 0, 0, 0
    Q_table = load_model(model)

    if purpose == 'attack':
        agent_player = 'X'
    elif purpose == 'defence':
        agent_player = 'O'
    else:
        return print("Unknown evaluate purpose, evaluation process breaking...")

    for _ in range(games):
        board = np.array([[None]*3 for _ in range(3)])
        current_player = 'X'
        game_over = False
        winner = None

        while not game_over:
            if current_player == agent_player: # agent turn
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

    dane = []
    filename = 'skutecznosc_vs_parametry.json'

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                dane = json.load(f)
            except json.JSONDecodeError:
                dane = []

    effectiveness = wins/games*100
    effectiveness_draws = draws/games*100
    loss_ratio = 100 - effectiveness_draws - effectiveness
    slownik = {"training_purpose": f"{purpose}", "effectiveness": f"{effectiveness:.2f}%", "effectiveness_draws": f"{effectiveness_draws:.2f}%", "loss_ratio":f"{loss_ratio:.2f}", "wins": wins, "draws": draws, "losses": losses,
               "learning_rate": learning_rate, "discount_factor": discount_factor, "starting_exploration_rate": starting_exploration_rate,
               "exploration_decrement_factor": exploration_decrement_factor, "num_episodes": num_episodes}

    dane.append(slownik)

    with open(filename, 'w') as f:
        json.dump(dane, f, indent=2)

    print(f"Wygrane: {wins}, Remisy: {draws}, Przegrane: {losses}")
    print(f"Skuteczność agenta: {effectiveness:.2f}% wygranych")
    print(f"Skuteczność w remisowaniu: {effectiveness_draws:.2f}% zremisowanych")
    print(f"Procent przegranych gier: {loss_ratio:.2f}% przegranych")



# RUN MODEL
if __name__ == "__main__":
    print("Ładowanie wytrenowanego modelu...")
    Qa = load_model("q_table_A.pkl")
    Qd = load_model("q_table_D.pkl")
    if (Qa or Qd) is None:
        print("Trening agenta...")
        Qa, Qd = train_agents()
        save_model(Qa, "q_table_A.pkl")
        save_model(Qd, "q_table_D.pkl")
        evaluate("attack", "q_table_A.pkl", 10000)
        evaluate("defence", "q_table_D.pkl", 10000)
        Qa = load_model("q_table_A.pkl")
        Qd = load_model("q_table_D.pkl")

# print("Ładowanie wytrenowanego modelu...")
# Qa = load_model("q_table_A.pkl")
# Qd = load_model("q_table_D.pkl")
# loaded_Q = Qd
# if (Qa or Qd) is None:
#     print("Model nie został znaleziony, trenuję nowy.")
#     Qa, Qd = train_agents()
#     save_model(Qa, "q_table_A.pkl")
#     save_model(Qd, "q_table_D.pkl")
#     evaluate("attack", "q_table_A.pkl", 10000)
#     evaluate("defence", "q_table_D.pkl", 10000)
#     Qa = load_model("q_table_A.pkl")
#     Qd = load_model("q_table_D.pkl")






