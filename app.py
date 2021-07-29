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
    result = boggle_game.check_valid_word(session['board'], guess)
    return jsonify(
        {"response" : result}
    )