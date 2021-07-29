from boggle import Boggle
from flask import Flask, session, render_template, request, redirect, jsonify

boggle_game = Boggle()
app = Flask(__name__)
app.config['SECRET_KEY'] = "YOUR_KEY_HERE"

@app.route('/')
def home_view():
    if not session.get('board'):
        session['board']  = boggle_game.make_board()
    return render_template('base.html')


@app.route('/new', methods=['POST'])
def new_board():
    session['board']  = boggle_game.make_board()
    session['guessed'] = []
    session['score'] = 0
    session['time_up'] = False
    return redirect('/')

@app.route('/guess', methods=['POST'])
def receive_guess():
    """
    Endpoint for making a guess on the Boggle board in the current session.
    Query should have parameter of 'guess' with the word to be guessed
    Response will be a JSON object where
    {
        "response" : string displaying guess outcome
        "score" : integer representing score value of guess
    }
    As well as an updated session cookie
    """
    data = request.get_json()['data']
    guess = data['guess']
    outcome = handle_guess(guess)
    #update session cookie
    update_session(guess, outcome['score'])

    return jsonify(outcome)

def handle_guess(word):
    """"
    Given a word, check if that word exists in the client's game board.
    Will return a dict where {"response" : outcome, "score": score change}
    
    {response: "ok"} --> guess is in game board
    {response: "not-word"} --> guess is not a recognized word
    {response: "not-on-board"} --> guess is a word, but not found on the board
    {response: "already-guessed"} --> guess is a word on the board, but already guessed
    """
    # check if client has already guessed the given word
    if word in session.get('guessed', {}):
        result = "already-guessed"
    else:
        result = boggle_game.check_valid_word(session['board'], word)
        score = len(word) if result == "ok" else 0

    return {"response" : result, "score" : score}


def update_session(word, num):
    """Updates the session cookie to add word to list of guessed nums, and increases score by num."""
    guessed = set(session.get('guessed', []))
    guessed.add(word)
    session['guessed'] = list(guessed)

    session['score'] = session.get('score', 0) + num

    return session
