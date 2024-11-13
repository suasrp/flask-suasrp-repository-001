from flask import Flask, render_template, request, redirect, url_for, flash, session
from gtts import gTTS
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

# Predefined list of words
words = [
    "abbreviate", "abnormality", "abode", "abrasion", "abundantly", "academic",
    "accessory", "accordion", "acidic", "acne", "acrobat", "adhesive",
    "admirable", "adoption", "adversary", "affected", "affliction", "affordable",
    "agenda", "airport", "alimony", "allergic", "alliance", "alpaca",
    "alphabetical", "amateur", "amplify", "amusing", "animate", "anklebone",
    "annex", "antibacterial", "antibiotic", "anxiety", "apparition", "appease",
    "applause", "aptitude", "aquamarine", "arcade", "arrangement", "assortment",
    "athletic", "attractive", "auditory", "avalanche", "avocado", "badminton",
    "balky", "Ballyhoo", "barbarian", "bareback", "bargain", "barrette",
    "cat", "dog", "eel", "fog", "girl", "hen", "ink", "jam", "king", "log", "mice", "net", "oak", "pin", "quit", "rat", "silk", "tea", "up",
    "visitation", "vitality", "vivid", "vocation", "volcanic", "volume",
    "waistband", "wallaby", "warehouse", "warrant", "wash-and-wear", "waspish",
    "wearable", "web-footed", "wharf", "wheelchair", "wherefore", "white blood cell",
    "whitening", "wireless", "wisecrack", "wittingly", "woozy", "workmanship",
    "xylophone", "yacht", "yearling", "zealous", "zestfully"
]

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

# Initialize session variables
@app.before_request
def initialize_session():
    if 'incorrect_words' not in session:
        session['incorrect_words'] = set()
    if 'retest_words' not in session:
        session['retest_words'] = set()
    if 'completed_tests' not in session:
        session['completed_tests'] = set()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_test')
def select_test():
    return render_template('select_test.html', tests=tests, scoring_board=scoring_board)

@app.route('/start_test/<letter>', methods=['GET', 'POST'])
def start_test(letter):
    if letter in session['completed_tests']:
        flash('Test complete! All words have been asked.', 'success')
        return redirect(url_for('select_test'))

    # Get session data for the test
    if 'incorrect_words' not in session:
        session['incorrect_words'] = set()

    if request.method == 'POST':
        user_input = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']
        
        # Check if the user input is correct
        if user_input == correct_word:
            flash('Correct!', 'success')
            scoring_board[letter]["correct"] += 1  # Update score
        else:
            flash(f'Incorrect. The correct spelling is: {correct_word}', 'danger')
            session['incorrect_words'].add(correct_word)  # Add misspelled word

        # Check if all words are asked for the test
        if len(tests[letter]) == scoring_board[letter]["correct"]:
            session['completed_tests'].add(letter)
            return redirect(url_for('start_test', letter=letter))

    # Get next word for the test
    words_to_test = tests[letter]
    current_word = random.choice(words_to_test)
    
    return render_template('test.html', letter=letter, current_word=current_word)

@app.route('/test_complete')
def test_complete():
    # Display final score and reset for a new test
    message = "Good job! All words are correct!" if len(session['incorrect_words']) == 0 else "Test complete, please retest the incorrect words."
    return render_template('test_complete.html', message=message, incorrect_words=session['incorrect_words'])

@app.route('/retest_incorrect_words', methods=['GET', 'POST'])
def retest_incorrect_words():
    if len(session['incorrect_words']) == 0:
        flash('No incorrect words to retest!', 'warning')
        return redirect(url_for('home'))

    # Display retest words
    if request.method == 'POST':
        word = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']
        
        if word == correct_word:
            session['retest_words'].remove(correct_word)
            flash('Correct on retest!', 'success')
        
        if len(session['retest_words']) == 0:
            flash('Retest complete! All words are correct!', 'success')
            session['retest_words'] = set()  # Reset retest words
            return redirect(url_for('home'))

        return redirect(url_for('retest_incorrect_words'))

    # If no words in retest list
    if len(session['retest_words']) == 0:
        session['retest_words'] = session['incorrect_words']
    
    word_to_retest = random.choice(list(session['retest_words']))
    
    return render_template('retest.html', current_word=word_to_retest)

@app.route('/historical_misspelled_word_list')
def historical_misspelled_word_list():
    return render_template('historical_misspelled_word_list.html', words=session['incorrect_words'])

@app.route('/edit_misspelled_word_list', methods=['GET', 'POST'])
def edit_misspelled_word_list():
    if request.method == 'POST':
        action = request.form.get('action')
        word = request.form.get('word').strip().lower()

        if action == 'delete' and word in session['incorrect_words']:
            session['incorrect_words'].remove(word)
            flash(f'Removed {word} from historical misspelled list.', 'success')

    return render_template('edit_misspelled_word_list.html', words=session['incorrect_words'])

if __name__ == '__main__':
    app.run(debug=True)
