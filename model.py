import numpy as np

ACTIONS = [
    (0, 0), (0, 1), (0, 2),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2)
]

def choose_move(board):
    possible_moves = []

    for row, col in ACTIONS:
        if board[row][col] is None:
            possible_moves.append((row, col))

    if not possible_moves:
        return None  # brak ruchów

    # Na razie losowy wybór
    return possible_moves[np.random.randint(len(possible_moves))]

