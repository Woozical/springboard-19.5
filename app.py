from boggle import Boggle
from flask import Flask, session, render_template, request, redirect, jsonify

boggle_game = Boggle()
app = Flask(__name__)
app.config['SECRET_KEY'] = "YOUR_KEY_HERE"
app.config['TESTING'] = True

@app.route('/')
def home_view():
    if not session.get('board'):
        reset_session()

    # Some logic to detect if user exited page mid-game last session (Ends current game session)
    if session['score'] != 0 and not session['time_up']:
        end_game()

    return render_template('base.html')


@app.route('/new', methods=['POST'])
def new_board():
    """
    Endpoint for client side to request a new game session
    """
    reset_session()
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


@app.route('/timeout', methods=['POST'])
def receive_timeout():
    """
    Endpoint that the client will send a POST request to when the game is over
    Updates session cookie to indicate that the game is over
    """
    end_game()
    return jsonify({'response' : 'ok'})

def handle_guess(word):
    """"
    Given a word, check if that word exists in the client's game board.
    Will return a dict where {"response" : outcome, "score": score change}
    
    {response: "ok"} --> guess is in game board
    {response: "not-word"} --> guess is not a recognized word
    {response: "not-on-board"} --> guess is a word, but not found on the board
    {response: "already-guessed"} --> guess is a word on the board, but already guessed
    {response: "time-up"} --> session cookie indicates time is up, ignoring guess
    """
    # check if client has already guessed the given word, or is trying to cheat while time is up
    if session['time_up']:
        result = 'time-up'
        score = 0
    elif word in session.get('guessed', {}):
        result = "already-guessed"
        score = 0
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

def reset_session(full=False):
    session['board']  = boggle_game.make_board()
    session['guessed'] = []
    session['score'] = 0
    session['time_up'] = False

    if full:
        session['high_score'] = 0
        session['play_count'] = 0

def end_game():
    session['time_up'] = True
    high_score = session.get('high_score', 0)
    cur_score = session.get('score', 0)
    session['high_score'] = cur_score if cur_score > high_score else high_score
    session['play_count'] = session.get('play_count', 0) + 1