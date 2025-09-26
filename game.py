import requests
import copy

class Game:
    def __init__(self, board=None, current_player='X', game_over=False, winner=None, winning_line=None, strategy='defence'):
        self.board = board or [[None]*3 for _ in range(3)]
        self.current_player = current_player
        self.game_over = game_over
        self.winner = winner
        self.winning_line = winning_line
        self.strategy = strategy
        self.move_log = []

    def __repr__(self):
        return f"{type(self).__name__}(board = {self.board}, current_player = {self.current_player}, game_over = {self.game_over}, winner = {self.winner}, move_log = {self.move_log} winning_line = {self.winning_line}, strategy = {self.strategy})"

    def switch_player(self):
        if self.current_player == 'X':
            self.current_player = 'O'
        else:
            self.current_player = 'X'

    def get_winning_line(self):
        b = self.board
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
                values.append(b[r][c])
            if values[0] is not None and values[0] == values[1] and values[1] == values[2]:
                return line
        return None

    def check_full_board(self):
        return all(element is not None for row in self.board for element in row)

    def reset_game(self):
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.move_log = []

    def save_move_to_log(self, row, col):
        self.move_log.append({
            "player": self.current_player,
            "position": [row, col],
            "board": copy.deepcopy(self.board)
        })

    def save_game_result(self, winner):
        try:
            response = requests.post(
                "http://127.0.0.1:5000/save-game",  # pełny adres serwera
                json={
                    "moves": self.move_log,
                    "board": self.board,
                    "result": winner or "DRAW"
                }
            )
            data = response.json()
            print("Zapisano grę:", data.get("status"))
        except requests.RequestException as err:
            print("Błąd zapisu gry:", err)

    def make_move(self, row, col):
        b = self.board
        if b[row][col] is not None:
            raise ValueError("Pole jest już zajęte!")
        else:
            b[row][col] = self.current_player
            self.save_move_to_log(row, col)
            self.winning_line = self.get_winning_line()
            if self.winning_line:
                self.game_over = True
                self.winner = self.current_player
                self.save_game_result(self.winner)
            elif self.check_full_board():
                self.game_over = True
                self.save_game_result(self.winner)

