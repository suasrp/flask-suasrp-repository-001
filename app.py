from flask import Flask, render_template, request, redirect, url_for, flash
from gtts import gTTS
import os
import nltk

nltk.download('wordnet')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_test')
def select_test():
    return render_template('select_test.html', tests=tests)

@app.route('/start_test/<letter>')
def start_test(letter):
    word_list = tests.get(letter, [])
    return render_template('test.html', letter=letter, words=word_list)

@app.route('/check_spelling', methods=['POST'])
def check_spelling():
    user_input = request.form['spelling'].strip().lower()
    current_word = request.form['current_word']
    score = int(request.form['score'])

    if user_input == current_word:
        score += 1
        result_message = "Correct!"
    else:
        result_message = "Incorrect!"

    return redirect(url_for('test_result', result=result_message, score=score, current_word=current_word))

@app.route('/test_result')
def test_result():
    result = request.args.get('result')
    score = request.args.get('score')
    current_word = request.args.get('current_word')
    return render_template('result.html', result=result, score=score, current_word=current_word)

@app.route('/pronounce/<word>')
def pronounce(word):
    tts = gTTS(text=word, lang='en')
    filename = f'temp_{word}.mp3'
    tts.save(filename)

    # Serve the audio file from a temporary location
    audio_file_url = f'/audio/{filename}'
    return redirect(url_for('select_test', audio_file=audio_file_url))

@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    app.run(debug=True)
