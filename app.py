from flask import Flask, request, jsonify, session
from flask import render_template
import json, os
from model import choose_move
from game import Game
import uuid

app = Flask(__name__)
FLASK_DEBUG=1
app.secret_key = 'BAD_SECRET_KEY'

games = {}  # słownik: klucz = session_id, wartość = obiekt Game

def generate_unique_id():
    return str(uuid.uuid4()) #generuje losowy unikalny identyfikator UUID w wersji 4 (losowy)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/start-game')
def start_game():
    session_id = generate_unique_id()  # funkcja do generowania ID (np. uuid4)
    session['session_id'] = session_id
    games[session_id] = Game()  # tworzymy nową planszę dla użytkownika
    return jsonify({"status": "utworzono unikalną planszę dla użytkownika"})

@app.route('/save-game', methods=['POST'])
def save_game():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    filename = 'games_history.json'
    games_history = []

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                games_history = json.load(f)
            except json.JSONDecodeError:
                games_history = []

    games_history.append(data)

    with open(filename, 'w') as f:
        json.dump(games_history, f, indent=2)

    return jsonify({"status": "success"})

@app.route('/history')
def history():
    filename = 'games_history.json'
    games_history = []

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                games_history = json.load(f)
            except json.JSONDecodeError:
                games_history = []

    return render_template('history.html', games_history = games_history)

@app.route('/AI-move', methods = ['POST'])
def ai_move():
    session_id = session.get('session_id')
    if not session_id:
        print("Brak session_id!")
        return jsonify({"error": "Brak sesji"}), 400

    game = games[session_id]
    board = game.board

    move = choose_move(board)

    row, col = move

    try:
        game.make_move(row, col)
    except ValueError as e:
        # Zwróć komunikat o błędzie do frontendu
        return jsonify({"error": str(e)}), 400

    winner = game.winner
    winning_line = game.winning_line
    draw = False
    current_player = game.current_player
    if game.check_full_board():
        draw = True
    if game.game_over:
        game.reset_game()
    else:
        game.switch_player()  # koniecznie po zapisaniu playera

    return jsonify({"status": "ruch ai wykonany", "current_player": current_player, "winner": winner, "winning_line": winning_line, "draw": draw, "aiRow": row, "aiCol": col})

@app.route('/player-move', methods = ['POST'])
def player_move():
    session_id = session.get('session_id')
    if not session_id:
        print("Brak session_id!")
        return jsonify({"error": "Brak sesji"}), 400

    data = request.get_json()

    row = data["row"]
    col = data["col"]
    game = games[session_id]

    try:
        game.make_move(row, col)
    except ValueError as e:
        # Zwróć komunikat o błędzie do frontendu
        return jsonify({"error": str(e)}), 400
    winner = game.winner
    winning_line = game.winning_line
    draw = False

    current_player = game.current_player
    if game.check_full_board():
        draw = True
    if game.game_over:
        game.reset_game()
    else:
        game.switch_player()  # koniecznie po zapisaniu playera

    return jsonify({"status": "ruch gracza wykonany", "current_player": current_player, "winner": winner, "winning_line": winning_line, "draw": draw})
