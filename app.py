# FROM sp_ul_flask_t05d_f 11-05-2024
# Make modifications to keep track of the user's scores, incorrect words, and handle retesting. To track scores and progress, we’ll introduce the following:
# Key Updates:
#Scoring Board (Feature 1):

#Track the correct/total words for each test in the scoring_board dictionary.
#Display the scores on the select_test page.
#Incorrect Words (Feature 2):

#Collect all incorrect words from the tests and store them in session['incorrect_words'].
#Add incorrectly spelled words to session['historical_incorrect_words'] for later use.
#Historical Test (Feature 3):

#Create a new "Historical Test" from the historically incorrect words.
#Display the list of incorrect words and allow the user to create the test.
#Edit Tests (Feature 5):

#Add functionality for users to add or delete words from the individual tests (A-Z).
#"All Words Are Correct" Logic (Feature 6 & 7):

#Show the "All Words Are Correct!" message when the user's score reaches the total words in the test.
#Reset session variables when all words are correct to allow for a fresh start.


from flask import Flask, render_template, request, redirect, url_for, flash, session
from gtts import gTTS
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

# Predefined list of words
# Example alphabet tests (you can expand this with more words for each letter)
words = {
    'a': ['apple', 'ant', 'apricot'],
    'b': ['banana', 'ball', 'bird'],
    'c': ['cat', 'cake', 'car'],
    # Add more letters and words as needed
}

# Create 26 tests (A-Z)
def create_tests(words_list):
    tests = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        filtered_words = [word for word in words_list if word.startswith(letter)]
        tests[letter] = filtered_words
    return tests

tests = create_tests(words)

# Scoring board to track correct/total words per test
scoring_board = {letter: {"correct": 0, "total": len(words)} for letter, words in tests.items()}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_test')
def select_test():
    return render_template('select_test.html', tests=tests, scoring_board=scoring_board)

@app.route('/start_test/<letter>', methods=['GET', 'POST'])
def start_test(letter):
    # Initialize or get session data for the test scores and words asked
    if 'incorrect_words' not in session:
        session['incorrect_words'] = []
    if 'correct_words' not in session:
        session['correct_words'] = 0
    if 'total_words' not in session:
        session['total_words'] = len(tests[letter])
    if 'asked_words' not in session:
        session['asked_words'] = []  # Track which words have been asked

    # When the test is submitted, handle the result
    if request.method == 'POST':
        # Handle answer submission
        user_input = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']

        # Mark the word as asked
        if correct_word not in session['asked_words']:
            session['asked_words'].append(correct_word)

        # Check if the word is correct
        if user_input == correct_word:
            flash('Correct!', 'success')
            session['correct_words'] += 1
            scoring_board[letter]["correct"] += 1  # Update scoring board
        else:
            flash(f'Incorrect. The correct spelling is: {correct_word}', 'danger')
            if correct_word not in session['incorrect_words']:
                session['incorrect_words'].append(correct_word)
#v
            if correct_word not in session.get('historical_incorrect_words', []):
                session.setdefault('historical_incorrect_words', []).append(correct_word)

            return redirect(url_for('start_test', letter=letter))

    #words_to_test = tests[letter]
    #current_word = random.choice(words_to_test)  # Randomly select a word for the test
    #return render_template('test.html', letter=letter, current_word=current_word)
#AAA
        # If all words have been asked, show the result
        if len(session['asked_words']) == len(tests[letter]):
            flash(f'Test Complete! Score: {session["correct_words"]} / {len(tests[letter])}', 'success')
            # Reset session variables for a fresh start
            session.pop('asked_words', None)
            session.pop('incorrect_words', None)
            session.pop('correct_words', None)
            session.pop('total_words', None)
            return redirect(url_for('select_test'))

        # Select a random word that has not been asked yet
        remaining_words = [word for word in tests[letter] if word not in session['asked_words']]
        current_word = random.choice(remaining_words) if remaining_words else None

        return render_template('test.html', letter=letter, current_word=current_word)

    # If it's a GET request, select a random word from the test that has not been asked yet
    remaining_words = [word for word in tests[letter] if word not in session['asked_words']]
    if remaining_words:
        current_word = random.choice(remaining_words)
    else:
        flash('Test Complete! All words have been asked.', 'success')
        return redirect(url_for('select_test'))

    return render_template('test.html', letter=letter, current_word=current_word)
#
#

@app.route('/retest_incorrect_words', methods=['GET', 'POST'])
def retest_incorrect_words():
    if 'incorrect_words' not in session or len(session['incorrect_words']) == 0:
        flash('No incorrect words to retest!', 'warning')
        return redirect(url_for('home'))

    if 'retest_score' not in session:
        session['retest_score'] = 0

    if request.method == 'POST':
        user_input = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']

        if user_input == correct_word:
            flash('Correct on retest!', 'success')
            session['retest_score'] += 1
            session['incorrect_words'].remove(correct_word)
        
        else:
            flash(f'Incorrect. The correct spelling is: {correct_word}', 'danger')

        # If all incorrect words have been spelled correctly
        if len(session['incorrect_words']) == 0:
            flash('All Words Are Correct!', 'success')
            # Reset the app for a new test
            session.pop('incorrect_words', None)
            session.pop('correct_words', None)
            session.pop('total_words', None)
            session['retest_score'] = 0
            return redirect(url_for('home'))

        return redirect(url_for('retest_incorrect_words'))

    # Show retest words
    current_word = random.choice(session['incorrect_words'])  # Choose a word from incorrect list
    return render_template('retest.html', current_word=current_word)

@app.route('/pronounce/<word>')
def pronounce(word):
    tts = gTTS(text=word, lang='en')
    filename = 'static/temp_word.mp3'
    tts.save(filename)
    return redirect(url_for('play_sound', filename='temp_word.mp3'))

@app.route('/play_sound/<filename>')
def play_sound(filename):
    return render_template('play_sound.html', filename=filename)

@app.route('/create_historical_test', methods=['GET', 'POST'])
def create_historical_test():
    if 'historical_incorrect_words' not in session or len(session['historical_incorrect_words']) == 0:
        flash('No incorrect words to create a test!', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Create a new test based on historical incorrect words
        historical_test = session['historical_incorrect_words']
        tests['historical'] = historical_test  # Add new test to the tests dictionary
        flash('Historical Test Created!', 'success')
        return redirect(url_for('select_test'))

    return render_template('create_historical_test.html', historical_words=session['historical_incorrect_words'])

@app.route('/edit_test/<letter>', methods=['GET', 'POST'])
def edit_test(letter):
    if request.method == 'POST':
        action = request.form.get('action')
        word = request.form.get('word').strip().lower()
        if action == 'add' and word not in tests[letter]:
            tests[letter].append(word)
            flash(f'Added {word} to Test {letter.upper()}!', 'success')
        elif action == 'delete' and word in tests[letter]:
            tests[letter].remove(word)
            flash(f'Removed {word} from Test {letter.upper()}!', 'success')

    return render_template('edit_test.html', letter=letter, words=tests[letter])

if __name__ == '__main__':
    app.run(debug=True)
