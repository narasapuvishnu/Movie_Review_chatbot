# CineBot: AI Movie Review Chatbot

CineBot is an intelligent, conversational movie assistant built with Python, Flask, and Groq's high-performance LLM APIs. CineBot can answer your questions about movies, providing cast details, budget estimates, box office performance, and critical consensus reviews.

## Features

- **Conversational Interface**: Chat naturally with the bot about any movie.
- **Powered by Groq**: Uses `llama-3.1-8b-instant` via the Groq API for lightning-fast and highly knowledgeable responses.
- **Rich Formatting**: Responses are beautifully formatted in Markdown for readability.
- **Web App**: Built on a lightweight Flask backend serving a clean, responsive frontend.

## Prerequisites

- Python 3.8+
- [Groq API Key](https://console.groq.com/keys)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/narasapuvishnu/Movie_Review_chatbot.git
   cd Movie_Review_chatbot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY="your_groq_api_key_here"
   ```

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. Start chatting with CineBot!

## Project Structure

- `app.py`: The main Flask application and routing.
- `llm_parser.py`: The core logic that interfaces with the Groq API to generate responses.
- `movie_api.py`: (Optional) Logic for querying The Movie Database (TMDB) directly.
- `requirements.txt`: Python dependencies.
- `templates/`: Contains the `index.html` frontend.
- `static/`: Contains CSS and JS for the frontend.
