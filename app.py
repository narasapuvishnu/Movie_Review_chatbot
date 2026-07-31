from flask import Flask, render_template, request, jsonify
from llm_parser import get_movie_answer
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Fetch answer directly from Groq AI (Acts as both parser and database)
    bot_response = get_movie_answer(user_message)

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
