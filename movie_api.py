import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def search_movie(movie_name):
    """Searches for a movie and returns its ID and basic info."""
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0] # Return the most relevant result
    return None

def get_movie_details(movie_id):
    """Gets detailed info including budget and revenue."""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_movie_credits(movie_id):
    """Gets the cast and crew."""
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_movie_reviews(movie_id):
    """Gets reviews for the movie."""
    url = f"{BASE_URL}/movie/{movie_id}/reviews"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def analyze_hit_or_flop(budget, revenue):
    """Analyzes if a movie is a hit or flop based on budget and revenue."""
    if budget == 0 or revenue == 0:
        return "Unknown (Budget or Revenue data is missing)"
    
    # Simple calculation: if revenue > budget, it's a hit.
    if revenue > budget:
        profit = revenue - budget
        return f"Hit! It made a profit of ${profit:,}"
    elif budget > revenue:
        loss = budget - revenue
        return f"Flop. It lost ${loss:,}"
    else:
        return "Breakeven"

def get_movie_info(movie_name):
    """Main orchestrator function."""
    movie = search_movie(movie_name)
    if not movie:
        return f"Sorry, I couldn't find any movie named '{movie_name}'."
    
    movie_id = movie["id"]
    title = movie["title"]
    
    details = get_movie_details(movie_id)
    credits_data = get_movie_credits(movie_id)
    reviews_data = get_movie_reviews(movie_id)
    
    budget = details.get("budget", 0) if details else 0
    revenue = details.get("revenue", 0) if details else 0
    hit_or_flop = analyze_hit_or_flop(budget, revenue)
    
    cast = []
    if credits_data and "cast" in credits_data:
        cast = [actor["name"] for actor in credits_data["cast"][:5]] # Top 5 cast
    
    reviews = []
    if reviews_data and "results" in reviews_data:
        reviews = [rev["content"] for rev in reviews_data["results"][:2]] # Top 2 reviews
    
    return {
        "title": title,
        "overview": movie.get("overview", "No overview available."),
        "budget": f"${budget:,}" if budget > 0 else "Unknown",
        "revenue": f"${revenue:,}" if revenue > 0 else "Unknown",
        "hit_or_flop": hit_or_flop,
        "cast": cast,
        "reviews": reviews
    }
