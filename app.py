from boggle import Boggle
from flask import Flask, session, render_template

boggle_game = Boggle()
app = Flask(__name__)
app.config['SECRET_KEY'] = "YOUR_KEY_HERE"

@app.route('/')
def home_view():
    if not session.get('board'):
        session['board']  = boggle_game.make_board()
    return render_template('base.html')