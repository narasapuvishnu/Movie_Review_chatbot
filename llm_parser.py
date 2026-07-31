import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

def get_movie_answer(user_message):
    """
    Uses Groq to directly answer the user's query about any movie worldwide.
    Covers Hollywood, Tollywood, Bollywood, Kollywood, and all regional cinema.
    """
    if not client:
        return "I'm sorry, my AI brain (Groq) isn't connected right now! Please add your GROQ_API_KEY to the .env file."

    prompt = f"""
    You are CineBot, an expert AI Movie Assistant with deep knowledge of ALL world cinema.
    This includes Hollywood, Bollywood, Telugu (Tollywood), Tamil (Kollywood), Malayalam (Mollywood),
    Kannada, Marathi, Bengali, Korean, Japanese, and every other regional and international film industry.

    The user is asking: "{user_message}"
    
    If they are asking about a specific movie (in ANY language or industry), provide a detailed and conversational response that includes:
    - 🎬 **Movie Title** and **Industry/Language** (e.g., Telugu, Tamil, Hindi, English etc.)
    - 🎭 **Cast** - Lead actors and director
    - 💰 **Budget** (if known)
    - 📊 **Box Office Performance** - Worldwide/India collection and whether it was a **Hit, Blockbuster, Super Hit, Average, Flop, or Disaster**
    - ⭐ **Ratings** - IMDB, Rotten Tomatoes or critic ratings if available
    - 📝 **Review / Critic Consensus** - What audiences and critics said about it
    - 🏆 **Awards** (if any)
    
    IMPORTANT: Never say you don't have information about a regional or Indian movie. Telugu, Tamil, Hindi, Malayalam movies are extremely popular and well-documented. Always do your best to provide as much accurate detail as possible.
    
    Format your response beautifully using markdown (bolding, lists, emojis).
    Act like a knowledgeable and enthusiastic movie expert who loves ALL kinds of cinema.
    If they are not asking about a movie, just respond conversationally and warmly.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1200
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return "I'm having trouble processing that right now. Please try again in a moment."
