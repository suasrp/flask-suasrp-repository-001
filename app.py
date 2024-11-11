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
tests = {
    "a": ["abbreviate", "abnormality", "abode", "abrasion", "abundantly", "academic",
    "accessory", "accordion", "acidic", "acne", "acrobat", "adhesive",
    "admirable", "adoption", "adversary", "affected", "affliction", "affordable",
    "agenda", "airport", "alimony", "allergic", "alliance", "alpaca",
    "alphabetical", "amateur", "amplify", "amusing", "animate", "anklebone",
    "annex", "antibacterial", "antibiotic", "anxiety", "apparition", "appease",
    "applause", "aptitude", "aquamarine", "arcade", "arrangement", "assortment",
    "athletic", "attractive", "auditory", "avalanche", "avocado"],
    
    "b": ["badminton", "balky", "Ballyhoo", "barbarian", "bareback", "bargain", "barrette"],
    
    "c": ["cat"],
    
    "d": ["dog"],
    
    "e": ["eel"],
    
    "f": ["fog"],
    
    "g": ["girl"],
    
    "h": ["hen"],
    
    "i": ["ink"],
    
    "j": ["jam"],
    
    "k": ["king"],
    
    "l": ["log"],
    
    "m": ["mice"],
    
    "n": ["net"],
    
    "o": ["oak"],
    
    "p": ["pin"],
    
    "q": ["quit"],
    
    "r": ["rat"],
    
    "s": ["silk"],
    
    "t": ["tea"],
    
    "u": ["up"],
    
    "v": ["visitation", "vitality", "vivid", "vocation", "volcanic", "volume"],
    
    "w": ["waistband", "wallaby", "warehouse", "warrant", "wash-and-wear", "waspish",
    "wearable", "web-footed", "wharf", "wheelchair", "wherefore", "white blood cell",
    "whitening", "wireless", "wisecrack", "wittingly", "woozy", "workmanship"],
    
    "x": ["xylophone"],
    
    "y": ["yacht", "yearling"],
    
    "z": ["zealous", "zestfully]"
}

@app.route('/')
def select_test():
    # Display the list of available tests (one for each letter)
    return render_template('select_test.html', letters=tests.keys())

@app.route('/start_test/<letter>', methods=['GET', 'POST'])
def start_test(letter):
    if 'incorrect_words' not in session:
        session['incorrect_words'] = []
    if 'correct_words' not in session:
        session['correct_words'] = 0
    if 'total_words' not in session:
        session['total_words'] = len(tests[letter])
    if 'asked_words' not in session:
        session['asked_words'] = []  # Track which words have been asked

    # If the test is completed, show results and handle retesting logic
    if request.method == 'POST':
        user_input = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']

        # Track if the word has been asked
        if correct_word not in session['asked_words']:
            session['asked_words'].append(correct_word)

        # Check if the word is correct
        if user_input == correct_word:
            flash('Correct!', 'success')
            session['correct_words'] += 1
        else:
            flash(f'Incorrect. The correct spelling is: {correct_word}', 'danger')
            if correct_word not in session['incorrect_words']:
                session['incorrect_words'].append(correct_word)

        # If all words have been asked, evaluate the results
        if len(session['asked_words']) == len(tests[letter]):
            correct_words_count = session['correct_words']
            total_words = len(tests[letter])
            if correct_words_count == total_words:
                flash('Good Job! All words are correct!', 'success')
                session.pop('asked_words', None)
                session.pop('incorrect_words', None)
                session.pop('correct_words', None)
                session.pop('total_words', None)
                return redirect(url_for('select_test'))
            else:
                # Handle retesting scenario
                flash(f'Good Job! {correct_words_count}/{total_words} words are correct. Please complete the retest.', 'warning')

                # Send incorrect words to the retest
                session['incorrect_for_retest'] = session['incorrect_words']

                # Reset session variables for retest
                session['correct_words_for_retest'] = 0
                session['total_words_for_retest'] = len(session['incorrect_for_retest'])

                # Clear asked words for the retest cycle
                session['asked_words_for_retest'] = []

                return redirect(url_for('start_retest'))

        # Select a random word that has not been asked yet
        remaining_words = [word for word in tests[letter] if word not in session['asked_words']]
        current_word = random.choice(remaining_words) if remaining_words else None

        return render_template('test.html', letter=letter, current_word=current_word)

    # Initial GET request, show a random word
    remaining_words = [word for word in tests[letter] if word not in session['asked_words']]
    current_word = random.choice(remaining_words) if remaining_words else None

    return render_template('test.html', letter=letter, current_word=current_word)

@app.route('/start_retest', methods=['GET', 'POST'])
def start_retest():
    if 'incorrect_for_retest' not in session or not session['incorrect_for_retest']:
        flash('No words to retest. Please start a new test.', 'warning')
        return redirect(url_for('select_test'))

    if 'asked_words_for_retest' not in session:
        session['asked_words_for_retest'] = []

    # Handle retest form submission
    if request.method == 'POST':
        user_input = request.form['user_input'].strip().lower()
        correct_word = request.form['correct_word']

        # Track if the word has been asked in the retest cycle
        if correct_word not in session['asked_words_for_retest']:
            session['asked_words_for_retest'].append(correct_word)

        # Check if the word is correct
        if user_input == correct_word:
            flash('Correct!', 'success')
            session['correct_words_for_retest'] += 1
        else:
            flash(f'Incorrect. The correct spelling is: {correct_word}', 'danger')

        # Check if all words for retest have been asked
        if len(session['asked_words_for_retest']) == len(session['incorrect_for_retest']):
            correct_words_count = session['correct_words_for_retest']
            total_words = len(session['incorrect_for_retest'])
            if correct_words_count == total_words:
                flash('Good Job! All words are correct!', 'success')
                session.pop('asked_words_for_retest', None)
                session.pop('incorrect_for_retest', None)
                session.pop('correct_words_for_retest', None)
                session.pop('total_words_for_retest', None)
                return redirect(url_for('select_test'))
            else:
                flash(f'Good Job! {correct_words_count}/{total_words} words are correct. Please complete the retest.', 'warning')

        # Select a random word for the retest that has not been asked yet
        remaining_words = [word for word in session['incorrect_for_retest'] if word not in session['asked_words_for_retest']]
        current_word = random.choice(remaining_words) if remaining_words else None

        return render_template('retest.html', current_word=current_word)

    # Initial GET request for retest
    remaining_words = [word for word in session['incorrect_for_retest'] if word not in session['asked_words_for_retest']]
    current_word = random.choice(remaining_words) if remaining_words else None

    return render_template('retest.html', current_word=current_word)

@app.route('/add_misspelled_word', methods=['POST'])
def add_misspelled_word():
    word = request.form['misspelled_word']
    if word not in session.get('historical_misspelled_words', []):
        session.setdefault('historical_misspelled_words', []).append(word)
    return redirect(url_for('historical_misspelled_word_list'))

@app.route('/delete_misspelled_word/<word>', methods=['GET'])
def delete_misspelled_word(word):
    historical_misspelled_words = session.get('historical_misspelled_words', [])
    if word in historical_misspelled_words:
        historical_misspelled_words.remove(word)
        session['historical_misspelled_words'] = historical_misspelled_words
    return redirect(url_for('historical_misspelled_word_list'))

@app.route('/historical_misspelled_word_list')
def historical_misspelled_word_list():
    historical_misspelled_words = session.get('historical_misspelled_words', [])
    return render_template('historical_misspelled_word_list.html', historical_misspelled_words=historical_misspelled_words)

@app.route('/edit_misspelled_word_list')
def edit_misspelled_word_list():
    historical_misspelled_words = session.get('historical_misspelled_words', [])
    return render_template('edit_misspelled_word_list.html', historical_misspelled_words=historical_misspelled_words)

if __name__ == '__main__':
    app.run(debug=True)
