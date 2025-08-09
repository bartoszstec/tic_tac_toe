from flask import Flask, request, jsonify
from flask import render_template
import json, os
from model import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/save-game', methods=['POST'])
def save_game():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    filename = 'games_history.json'
    games = []

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                games = json.load(f)
            except json.JSONDecodeError:
                games = []

    games.append(data)

    with open(filename, 'w') as f:
        json.dump(games, f, indent=2)

    return jsonify({"status": "success"})

@app.route('/history')
def history():
    filename = 'games_history.json'
    games = []

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                games = json.load(f)
            except json.JSONDecodeError:
                games = []

    return render_template('history.html', games = games)

@app.route('/AI-move', methods = ['POST'])
def aimove():
    data = request.get_json()
    if not data or "board" not in data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    board = data["board"]  # to jest lista list z JS
    move = choose_move(board)

    if move is None:
        return jsonify({"status": "error", "message": "No moves available"}), 400


    #return jsonify({"move": move})
    return jsonify({"move": list(move)})  # np. [1, 0]
