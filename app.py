from flask import Flask, render_template, request, redirect, url_for, flash
from gtts import gTTS
from playsound import playsound
import os
import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key

words = [
    # Your list of words here...
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
    playsound(filename)
    os.remove(filename)
    return redirect(url_for('select_test'))

if __name__ == '__main__':
    app.run(debug=True)
