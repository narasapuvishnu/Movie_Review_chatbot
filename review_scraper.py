import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import xml.etree.ElementTree as ET

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape_123telugu_rss(movie_name):
    """
    Searches 123telugu.com via their native RSS feed. 
    This bypasses anti-bot protections entirely and reliably returns 
    the latest reviews, box office updates, and news for very recent Telugu movies.
    """
    reviews = []
    print(f"[123telugu RSS] Searching for: {movie_name}")
    try:
        # Search for both "review" and just the movie name to get the best recent articles
        queries = [f"{movie_name} review", movie_name]
        
        seen_links = set()
        
        for q in queries:
            query = urllib.parse.quote_plus(q)
            url = f"https://www.123telugu.com/feed/?s={query}"
            
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue
                
            root = ET.fromstring(resp.content)
            items = root.findall("./channel/item")
            
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                
                if link in seen_links:
                    continue
                
                # Check if the article title is actually relevant to the movie
                movie_words = [w.lower() for w in movie_name.split() if len(w) > 2]
                if not movie_words:
                    movie_words = [movie_name.lower()]
                
                if not any(w in title.lower() for w in movie_words):
                    print(f"  -> Skipping irrelevant article: {title}")
                    continue
                    
                seen_links.add(link)
                
                # Fetch the actual article content
                try:
                    art_resp = requests.get(link, headers=HEADERS, timeout=10)
                    if art_resp.status_code == 200:
                        soup = BeautifulSoup(art_resp.text, "lxml")
                        
                        # Remove noise tags
                        for tag in soup.select("script, style, .ad, ins, .social-share"):
                            tag.decompose()
                            
                        # Extract main content
                        content_div = (
                            soup.select_one(".entry-content") or 
                            soup.select_one(".post-content") or 
                            soup.select_one(".penci-entry-content")
                        )
                        
                        if content_div:
                            text = content_div.get_text(separator=" ", strip=True)
                            text = re.sub(r"\s+", " ", text).strip()
                            if len(text) > 100:
                                reviews.append(f"[{title}] {text[:1500]}")
                                print(f"  -> Extracted from: {title[:50]}...")
                except Exception as e:
                    print(f"  -> Error fetching article {link}: {e}")
                
                # Limit to 3 robust articles to keep prompt size manageable
                if len(reviews) >= 3:
                    break
                    
            if len(reviews) >= 3:
                break
                
    except Exception as e:
        print(f"[123telugu RSS] Error: {e}")
        
    return reviews


def get_audience_reviews(movie_name):
    """
    Orchestrates scrapers and returns a combined list of real, live data.
    Uses RSS feeds to guarantee bypass of anti-bot captcha pages.
    """
    all_reviews = []
    print(f"\n[Scraper] --- Fetching live data for: '{movie_name}' ---")

    # --- Source 1: 123telugu.com via RSS Feed ---
    rss_reviews = scrape_123telugu_rss(movie_name)
    for r in rss_reviews:
        all_reviews.append({"source": "123telugu.com (Latest Updates)", "review": r})

    print(f"[Scraper] --- Total extracted: {len(all_reviews)} articles ---\n")
    return all_reviews
