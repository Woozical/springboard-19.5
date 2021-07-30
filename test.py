from unittest import TestCase
from app import app
from app import handle_guess, update_session, reset_session, end_game
from flask import session
from boggle import Boggle
from random import choice


class FlaskTests(TestCase):

    def setUp(self):
        self.control_board = [
            ['Y', 'K', 'R', 'L', 'H'],
            ['M', 'R', 'D', 'N', 'Q'],
            ['H', 'R', 'O', 'J', 'Q'],
            ['Z', 'P', 'Z', 'K', 'D'],
            ['S', 'F', 'D', 'K', 'F']
            ]

    def test_handle_guess(self):
        with app.test_client() as client:
            client.get('/')
            session['board'] = self.control_board


            #Test handling time's up on game
            session['time_up'] = True
            outcome = handle_guess('rod')
            expected = {'response' : 'time-up', 'score' : 0}
            self.assertEqual(outcome, expected)
            session['time_up'] = False
            
            #Test word that exists on board
            outcome = handle_guess('rod')
            expected = {'response' : 'ok', 'score' : 3}
            self.assertEqual(outcome, expected)

            #Test word that is valid but not on board
            outcome = handle_guess('hello')
            expected = {'response': 'not-on-board', 'score': 0}
            self.assertEqual(outcome, expected)

            #Test word that is invalid
            outcome = handle_guess('ajgkdfg')
            expected = {'response': 'not-word', 'score': 0}
            self.assertEqual(outcome, expected)

            #Test handling already guess word in session
            session['guessed'] = ['rod', 'hello']
            outcome = handle_guess('rod')
            expected = {'response' : 'already-guessed', 'score' : 0}
            self.assertEqual(outcome, expected)

            outcome = handle_guess('hello')
            expected = {'response': 'already-guessed', 'score': 0}
            self.assertEqual(outcome, expected)

    def test_update_session(self):
        with app.test_client() as client:
            client.get('/')

            #test word added to session 'guessed' list
            update_session('green', 0)
            self.assertIn('green', session['guessed'])

            #test memory of previous words
            update_session('blue', 0)
            self.assertIn('green', session['guessed'])
            self.assertIn('blue', session['guessed'])

            #test no duplicates of words
            session['guessed'] = []
            update_session('red', 0)
            update_session('red', 0)
            self.assertIn('red', session['guessed'])
            self.assertEqual(session['guessed'], ['red'])

            #test session score properly incremented
            update_session('yellow', 6)
            self.assertEqual(session['score'], 6)

            update_session('pink', 4)
            self.assertEqual(session['score'], 10)

            update_session('pie', 0)
            self.assertEqual(session['score'], 10)

            update_session('negTest', -7)
            self.assertEqual(session['score'], 3)

    def test_reset_session(self):
        with app.test_client() as client:
            #set-up
            client.get('/')
            session['board'] = self.control_board
            self.assertIs(session['board'], self.control_board)
            
            #test partial reset
            reset_session()
            self.assertIsNot(session['board'], self.control_board)
            self.assertNotEqual(session['board'], self.control_board)
            self.assertEqual(session['guessed'], [])
            self.assertEqual(session['score'], 0)
            self.assertEqual(session['time_up'], False)

            #2nd set-up
            session['board'] = self.control_board
            self.assertIs(session['board'], self.control_board)

            #test full reset
            reset_session(full=True)
            self.assertIsNot(session['board'], self.control_board)
            self.assertNotEqual(session['board'], self.control_board)
            self.assertEqual(session['guessed'], [])
            self.assertEqual(session['score'], 0)
            self.assertEqual(session['time_up'], False)
            self.assertEqual(session['high_score'], 0)
            self.assertEqual(session['play_count'], 0)

    def test_end_game(self):
        with app.test_client() as client:
            client.get('/')

            end_game()
            self.assertEqual(session['time_up'], True)
            self.assertEqual(session['play_count'], 1)

            # test high score
            session['score'] = 5
            end_game()
            self.assertEqual(session['high_score'], 5)
            self.assertEqual(session['play_count'], 2)

            session['score'] = 2
            end_game()
            self.assertEqual(session['high_score'], 5)
            self.assertEqual(session['play_count'], 3)

            session['score'] = 11
            end_game()
            self.assertEqual(session['high_score'], 11)
            self.assertEqual(session['play_count'], 4)

    def test_home_view(self):
        with app.test_client() as client:
            res = client.get('/')
            # test proper response code
            self.assertEqual(res.status_code, 200)

            # test proper HTML response
            html = res.get_data(as_text=True)
            self.assertIn('<script src="/static/guess.js">', html)
            self.assertIn('<form id="guess-form">', html)
            self.assertIn('<div class="control">', html)
            self.assertIn('<table>', html)

            #test proper session set-up
            self.assertIsInstance(session['board'], list)
            self.assertIsInstance(session['guessed'], list)
            self.assertIsInstance(session['score'], int)
            self.assertIsInstance(session['time_up'], bool)

            #test proper mid-game reset

            with client.session_transaction() as sess:
                sess['score'] = 15

            res = client.get('/')
            html = res.get_data(as_text=True)

            #proper HTML
            self.assertIn('Time: 0', html)
            self.assertIn('<button id="guess-btn" disabled>', html)

            self.assertEqual(session['time_up'], True)
            self.assertEqual(session['score'], 15)

    def test_new_board(self):
        with app.test_client() as client:
            #set up
            client.get('/')

            with client.session_transaction() as sess:
                sess['board'] = self.control_board
                sess['score'] = 5
                sess['guessed'] = ['red', 'blue', 'yellow']

            res = client.post('/new')
            #should reset session
            self.assertIsNot(session['board'], self.control_board)
            self.assertEqual(session['score'], 0)
            self.assertEqual(session['guessed'], [])
            self.assertEqual(session['time_up'], False)

            #should redirect
            self.assertEqual(res.status_code, 302)

    def test_new_board_followed(self):
        with app.test_client() as client:
            res = client.post('/new', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertIn('<script src="/static/guess.js">', html)
            self.assertIn('<form id="guess-form">', html)
            self.assertIn('<div class="control">', html)
            self.assertIn('<table>', html)
    
    ## Test 1 - Word is in board
    def test_receive_guess_ok(self):
        with app.test_client() as client:
            #setup
            client.get('/')
            with client.session_transaction() as sess:
                sess['board'] = self.control_board

            res = client.post('/guess', json={"data": {'guess': 'rod'}})
            
            #should update session
            self.assertIn('rod', session['guessed'])
            self.assertEqual(session['score'], 3)
            #should return JSON response
            self.assertEqual(res.get_json(), {"response": "ok", "score": 3})
            
    ## Test 2 - Word is word but not in board
    def test_receive_guess_not_on(self):
        with app.test_client() as client:
            #setup
            client.get('/')
            with client.session_transaction() as sess:
                sess['board'] = self.control_board

            res = client.post('/guess', json={"data": {'guess': 'hello'}})
            
            #should update session
            self.assertIn('hello', session['guessed'])
            self.assertEqual(session['score'], 0)
            #should return JSON response
            self.assertEqual(res.get_json(), {"response": "not-on-board", "score": 0})

    ## Test 3 - Word is not word
    def test_receive_guess_not_word(self):
        with app.test_client() as client:
            #setup
            client.get('/')
            res = client.post('/guess', json={"data": {"guess": "nawxvn"}})
            
            #should update session
            self.assertIn('nawxvn', session['guessed'])
            self.assertEqual(session['score'], 0)
            #should return JSON response
            self.assertEqual(res.get_json(), {"response" : "not-word", "score": 0})

    ## Test 4 - Word is already guessed
    def test_receive_guess(self):
        with app.test_client() as client:
            #setup
            client.get('/')
            controlList = ['red', 'yellow', 'blue']
            with client.session_transaction() as sess:
                sess['guessed'] = controlList
            
            res = client.post('/guess', json={"data" : {"guess": choice(controlList)}})

            #should update session
            self.assertEqual(len(session['guessed']), len(controlList))
            self.assertEqual(session['score'], 0)
            
            #should return JSON response
            self.assertEqual(res.get_json(), {"response" : "already-guessed", "score": 0})
    
    def test_receive_timeout(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['time_up'] = False
            
            client.post('/timeout')

            self.assertEqual(session['time_up'], True)
