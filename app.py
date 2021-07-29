from flask.json import jsonify
from boggle import Boggle
from flask import Flask, session, render_template, request

boggle_game = Boggle()
app = Flask(__name__)
app.config['SECRET_KEY'] = "YOUR_KEY_HERE"

@app.route('/')
def home_view():
    if not session.get('board'):
        session['board']  = boggle_game.make_board()
    return render_template('base.html')

@app.route('/guess', methods=['GET'])
def receive_guess():
    """
    Endpoint for making a guess on the Boggle board in the current session.
    Payload should be an object where {"guess": "some_string"}
    Response will be a JSON object where {"response" : "response_message"}
    """

    guess = request.args.get('guess', '').lower()
    outcome = handle_guess(guess)

    return jsonify(outcome)

def handle_guess(word):
    """"
    Given a word, check if that word exists in the client's game board.
    Will return a dict where {"response" : outcome}
    
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

        # add guess to already guessed words
        guessed = set(session.get('guessed', []))
        guessed.add(word)
        session['guessed'] = list(guessed)

    return {"response" : result}