from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import random

app = Flask(_name_)

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def switch_turn():
    session["turn"] = "O" if session["turn"] == "X" else "X"

def ai_move():
    # Simple AI: Random move (placeholder for a more complex algorithm)
    empty_cells = [(i, j) for i in range(3) for j in range(3) if session["board"][i][j] is None]
    if empty_cells:
        move = random.choice(empty_cells)
        session["board"][move[0]][move[1]] = "O"

def update_score(winner):
    if winner == "X":
        session["score_X"] += 1
    elif winner == "O":
        session["score_O"] += 1

@app.route("/set_mode/<mode>")
def set_mode(mode):
    session["mode"] = mode
    return redirect(url_for("index"))

@app.route("/")
def index():
    if "board" not in session:
        session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
        session["turn"] = "X"
        session["winner"] = False
        session["draw"] = False
        session["mode"] = "multiplayer"  # Default mode
        session["score_X"] = 0
        session["score_O"] = 0

    winner = winnerFound(session["board"])
    if winner[0]:
        session["winner"] = True
        session["turn"] = winner[1]
        update_score(winner[1])

    if not winner[0] and winner[1] == "draw":
        session["draw"] = True

    if session["turn"] == "O" and not session["winner"] and not session["draw"]:
        if session.get("mode") == "singleplayer":
            ai_move()
            switch_turn()

    return render_template("game.html", game=session["board"], turn=session["turn"], 
                           winnerFound=session["winner"], winner=session["turn"], draw=session["draw"],
                           score_X=session["score_X"], score_O=session["score_O"])

@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    if session["board"][row][col] is None and not session["winner"] and not session["draw"]:
        session["board"][row][col] = session["turn"]
        switch_turn()

        if session.get("mode") == "singleplayer" and not winnerFound(session["board"])[0]:
            ai_move()
            switch_turn()

    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
    session["turn"] = "X"
    session["winner"] = False
    session["draw"] = False
    # Reset scores only if the players choose to do so
    if 'reset_scores' in request.args and request.args.get('reset_scores') == 'true':
        session["score_X"] = 0
        session["score_O"] = 0
    return redirect(url_for("index"))

def winnerFound(board):
    # Check rows, columns, and diagonals for a winner
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != None:
            return (True, board[i][0])
        if board[0][i] == board[1][i] == board[2][i] != None:
            return (True, board[0][i])

    if board[0][0] == board[1][1] == board[2][2] != None or board[0][2] == board[1][1] == board[2][0] != None:
        return (True, board[1][1])

    # Check for a draw
    if all(all(row) for row in board):
        return (False, "draw")

    return (False, None)

if _name_ == "_main_":
    app.run(debug=True)