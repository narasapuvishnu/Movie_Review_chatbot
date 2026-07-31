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
    Uses Groq to directly answer the user's query about a movie.
    Since Groq's models have vast knowledge, they can act as a movie database!
    """
    if not client:
        return "I'm sorry, my AI brain (Groq) isn't connected right now! Please add your GROQ_API_KEY to the .env file."

    prompt = f"""
    You are CineBot, an expert AI Movie Assistant.
    The user is asking: "{user_message}"
    
    If they are asking about a movie, provide a conversational response that includes:
    - The Cast
    - The Budget (if known)
    - Box office performance (Hit or Flop)
    - A summary of reviews or general consensus
    
    Format your response beautifully using markdown (bolding, lists, emojis).
    Act like a knowledgeable and enthusiastic movie expert. 
    If they are not asking about a movie, just respond conversationally.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=800
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return "I'm having trouble processing that right now. Please try again in a moment."
