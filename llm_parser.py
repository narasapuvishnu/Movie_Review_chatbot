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
    You are a highly accurate intent extraction bot. The user said: "{user_message}"
    If the user is asking for a review, rating, or information about a specific movie (even if it's a regional or upcoming movie like 'Peddi', 'Kalki', etc.), extract the exact movie name.
    If they mention actors (like Ram Charan, Prabhas) along with a movie name, just extract the movie name.
    Reply ONLY with the exact name of the movie. Do not add any year, punctuation, language tag, or conversational text.
    If they are definitively NOT asking about a specific movie, reply ONLY with the word: NONE.
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

        ⚠️ IMPORTANT: This movie may be a VERY RECENT RELEASE (last few weeks or months).
        The following content was scraped LIVE from review websites RIGHT NOW — it is the most
        up-to-date information available. Treat this as ground truth, even if it differs from
        or supplements your training data:

        {reviews_text}

        Using the live review data above as your PRIMARY source, write a detailed response covering:
        - 🎬 **Movie Title** | **Industry / Language** | **Release Year**
        - 🎭 **Cast & Director** (use names from the reviews if your training data doesn't cover this film)
        - 💰 **Budget & Box Office** — state clearly: Hit, Blockbuster, Average, or Flop (say 'data not yet available' if unknown)
        - ⭐ **Ratings** — cite the rating from the scraped reviews (e.g. '3.25/5 by 123telugu.com')
        - 📝 **What Critics & Audiences Are Saying** — summarize the scraped reviews naturally. ⚠️ CRITICAL: If the reviews mention different language versions (e.g., Hindi version, Telugu version), you MUST separate the reviews and audience reception by language. Do NOT combine them.
        - ✅ **Highlights / Plus Points** — extract from the reviews
        - ❌ **Weak Points** — extract from the reviews
        - 💬 **Overall Verdict**

        Format beautifully using markdown bold headers, bullet points, and emojis.
        If this is a very new release, acknowledge that naturally (e.g. 'just released this week').
        Do NOT mention scraping, APIs, or JSON. Do NOT fabricate cast/crew/ratings not in the data.
        """
    else:
        # Fallback: rely on Groq's knowledge alone
        final_prompt = f"""
        You are CineBot, an expert AI Movie Assistant with deep knowledge of ALL world cinema —
        Hollywood, Bollywood, Telugu (Tollywood), Tamil (Kollywood), Malayalam (Mollywood), Kannada, and more.

        The user asked: "{user_message}"
        The movie identified: "{movie_name}"

        ⚠️ NOTE: Live review data could not be fetched for this movie right now.
        If this movie is a VERY RECENT RELEASE (past few weeks) that you don't have training data on,
        be honest and say: "This appears to be a very recent release that I don't have detailed
        information on yet. Here's what I know so far..." and share only what you're confident about.
        Do NOT hallucinate cast, ratings, plot, or box office figures you don't actually know.

        If you DO have knowledge of this film, provide a detailed response covering:
        - 🎬 **Movie Title** | **Industry / Language** | **Release Year**
        - 🎭 **Cast & Director**
        - 💰 **Budget & Box Office** — Hit, Blockbuster, Average, or Flop
        - ⭐ **Ratings** (IMDB, critics, etc.)
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
