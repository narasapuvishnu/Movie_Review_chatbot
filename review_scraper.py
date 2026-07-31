import requests
from bs4 import BeautifulSoup
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_letterboxd_reviews(movie_name):
    """Scrapes real user reviews from Letterboxd for any movie (Hollywood, Telugu, Hindi, etc.)."""
    reviews = []
    try:
        # Step 1: Search for the movie on Letterboxd
        query = urllib.parse.quote_plus(movie_name)
        search_url = f"https://letterboxd.com/search/films/{query}/"
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")

        # Find the first film result — try multiple selectors for robustness
        film_link_tag = (
            soup.select_one(".results .film-detail h2 a") or
            soup.select_one(".results .headline-2 a") or
            soup.select_one("ul.results li h2 a")
        )
        if not film_link_tag:
            print(f"[Letterboxd] No film found for: {movie_name}")
            return []

        film_slug = film_link_tag.get("href")  # e.g., /film/rrr/
        print(f"[Letterboxd] Found film slug: {film_slug}")

        # Step 2: Scrape the film's reviews page
        reviews_url = f"https://letterboxd.com{film_slug}reviews/by/activity/"
        rev_resp = requests.get(reviews_url, headers=HEADERS, timeout=10)
        rev_soup = BeautifulSoup(rev_resp.text, "lxml")

        # Extract review text — try multiple selectors
        review_blocks = (
            rev_soup.select(".film-detail-content .body-text") or
            rev_soup.select(".review-body .body-text") or
            rev_soup.select(".js-reviews-content .body-text")
        )

        for block in review_blocks:
            text = block.get_text(separator=" ", strip=True)
            if text and len(text) > 40:
                reviews.append(text[:600])
                if len(reviews) >= 6:
                    break

    except Exception as e:
        print(f"[Letterboxd] Error: {e}")

    return reviews


def scrape_bookmyshow_reviews(movie_name):
    """Tries to fetch user reviews from BookMyShow (Indian audience reviews)."""
    reviews = []
    try:
        bms_headers = {
            **HEADERS,
            "Referer": "https://in.bookmyshow.com/",
            "Accept": "application/json, text/plain, */*",
            "x-bms-id": "application/json",
        }

        # Step 1: Search for the movie via BMS API
        query = urllib.parse.quote_plus(movie_name)
        search_url = f"https://in.bookmyshow.com/serv/getData?cmd=GETALLEVENTS&type=movies&regionCode=NATIONAL&q={query}"
        resp = requests.get(search_url, headers=bms_headers, timeout=8)

        if resp.status_code == 200:
            data = resp.json()
            events = data.get("BookMyShow", {}).get("arrEvents", [])
            if events:
                event_code = events[0].get("EventCode", "")
                print(f"[BookMyShow] Found event code: {event_code}")

                if event_code:
                    # Step 2: Fetch user reviews for this event
                    review_url = f"https://in.bookmyshow.com/api/content-api/v2/reviews?eventCode={event_code}&count=6&page=1"
                    rev_resp = requests.get(review_url, headers=bms_headers, timeout=8)

                    if rev_resp.status_code == 200:
                        rev_data = rev_resp.json()
                        items = rev_data.get("items", []) or rev_data.get("reviews", [])
                        for item in items[:6]:
                            text = (
                                item.get("review") or
                                item.get("body") or
                                item.get("content") or
                                item.get("text", "")
                            )
                            if text and len(text) > 20:
                                reviews.append(str(text)[:500])
        else:
            print(f"[BookMyShow] Search returned status: {resp.status_code}")

    except Exception as e:
        print(f"[BookMyShow] Error: {e}")

    return reviews


def get_audience_reviews(movie_name):
    """
    Orchestrates all scrapers and returns a combined list of real audience reviews.
    Each review is a dict with 'source' and 'review' keys.
    """
    all_reviews = []

    print(f"[Scraper] Fetching audience reviews for: {movie_name}")

    # Letterboxd reviews (global audience)
    lb_reviews = scrape_letterboxd_reviews(movie_name)
    for r in lb_reviews:
        all_reviews.append({"source": "Letterboxd", "review": r})

    # BookMyShow reviews (Indian local audience)
    bms_reviews = scrape_bookmyshow_reviews(movie_name)
    for r in bms_reviews:
        all_reviews.append({"source": "BookMyShow", "review": r})

    print(f"[Scraper] Total reviews fetched: {len(all_reviews)} "
          f"(Letterboxd: {len(lb_reviews)}, BookMyShow: {len(bms_reviews)})")

    return all_reviews
