import os
from groq import Groq
from dotenv import load_dotenv
from review_scraper import get_audience_reviews

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None


def extract_movie_name(user_message):
    """Uses Groq to extract the movie name from the user's message."""
    if not client:
        return None
    prompt = f"""
    You are an intent extraction bot. The user said: "{user_message}"
    If they are asking about a specific movie, reply ONLY with the exact name of that movie. 
    Do not add any year, punctuation, language tag, or conversational text.
    If they are NOT asking about a specific movie, reply ONLY with the word: NONE.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=30
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Extract] Error: {e}")
        return None


def get_movie_answer(user_message):
    """
    Agentic pipeline:
    1. Extract movie name from user message
    2. Scrape real audience reviews from Letterboxd & BookMyShow
    3. Combine real reviews with Groq's expert knowledge for a rich response
    """
    if not client:
        return "I'm sorry, my AI brain (Groq) isn't connected! Please add your GROQ_API_KEY to the .env file."

    # ── Step 1: Identify the movie ───────────────────────────────────────────
    movie_name = extract_movie_name(user_message)

    # ── Non-movie chat: respond conversationally ─────────────────────────────
    if not movie_name or movie_name.upper() == "NONE":
        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": f"""
                    You are CineBot, a warm and knowledgeable AI Movie Assistant.
                    The user is not asking about a specific movie.
                    User said: "{user_message}"
                    Respond warmly and conversationally. Let them know you can help with any movie from any industry.
                """}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=400
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"[Chat] Error: {e}")
            return "Hi! I'm CineBot. Ask me about any movie — Telugu, Tamil, Hindi, Hollywood, and more!"

    # ── Step 2: Scrape real audience reviews ─────────────────────────────────
    audience_reviews = get_audience_reviews(movie_name)

    # ── Step 3: Generate final rich response ─────────────────────────────────
    if audience_reviews:
        reviews_text = "\n".join([
            f"  [{r['source']} User]: {r['review']}"
            for r in audience_reviews
        ])
        final_prompt = f"""
        You are CineBot, an expert AI Movie Assistant with deep knowledge of ALL world cinema —
        Hollywood, Bollywood, Telugu (Tollywood), Tamil (Kollywood), Malayalam (Mollywood), Kannada, and more.

        The user asked: "{user_message}"
        The movie being discussed: "{movie_name}"

        The following are REAL reviews written by actual audience members, scraped live from the internet:
        {reviews_text}

        Using both the real audience reviews above AND your expert knowledge, write a detailed, enthusiastic response covering:
        - 🎬 **Movie Title** | **Industry / Language**
        - 🎭 **Cast & Director**
        - 💰 **Budget & Box Office** — state clearly if it was a Hit, Blockbuster, Average, or Flop
        - ⭐ **Ratings** (IMDB, Rotten Tomatoes, or similar)
        - 📝 **Real Audience Sentiment** — summarize what real viewers actually said (reference the reviews above, mentioning sources like Letterboxd or BookMyShow naturally)
        - 💬 **Expert Consensus** — your overall expert take
        - 🏆 **Notable Awards** (if any)

        Format beautifully using markdown bold headers, bullet points, and emojis.
        Present audience feedback naturally as if you read what people are saying online.
        Do NOT mention scraping, JSON, or APIs.
        """
    else:
        # Fallback: rely on Groq's knowledge alone
        final_prompt = f"""
        You are CineBot, an expert AI Movie Assistant with deep knowledge of ALL world cinema —
        Hollywood, Bollywood, Telugu (Tollywood), Tamil (Kollywood), Malayalam (Mollywood), Kannada, and more.

        The user asked: "{user_message}"

        Provide a detailed and enthusiastic review covering:
        - 🎬 **Movie Title** | **Industry / Language**
        - 🎭 **Cast & Director**
        - 💰 **Budget & Box Office** — state clearly if it was a Hit, Blockbuster, Average, or Flop
        - ⭐ **Ratings**
        - 📝 **Audience & Critic Consensus**
        - 🏆 **Notable Awards** (if any)
        - 💬 **Expert Take**

        Format beautifully using markdown bold headers, bullet points, and emojis.
        Cover all world cinema including Indian regional films.
        """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": final_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1200
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[Final] Error: {e}")
        return "I'm having trouble processing that right now. Please try again in a moment."
