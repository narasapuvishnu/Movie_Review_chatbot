import requests
from bs4 import BeautifulSoup
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ─── Test 1: 123telugu search ────────────────────────────────
print("=== 123telugu search test ===")
query = urllib.parse.quote_plus("Peddi review")
url = f"https://www.123telugu.com/?s={query}"
resp = requests.get(url, headers=HEADERS, timeout=12)
print(f"Status: {resp.status_code}")
soup = BeautifulSoup(resp.text, "lxml")

# Try several link selectors
for sel in ["h2 a", "h3 a", ".entry-title a", ".penci-post-header a", "article a"]:
    links = soup.select(sel)
    if links:
        print(f"Selector '{sel}': {len(links)} links found")
        for a in links[:3]:
            href = a.get("href", "")
            text = a.get_text(strip=True)
            print(f"  href={href[:90]}")
            print(f"  text={text[:60]}")
        break
else:
    print("No heading links found. Printing all <a> tags with 'review' in href:")
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "review" in href.lower():
            print(f"  {href[:100]}")

# ─── Test 2: DuckDuckGo search ───────────────────────────────
print()
print("=== DuckDuckGo snippet test ===")
query2 = urllib.parse.quote_plus("Chennai Love Story telugu movie review rating")
ddg_url = f"https://html.duckduckgo.com/html/?q={query2}"
resp2 = requests.get(ddg_url, headers=HEADERS, timeout=12)
print(f"Status: {resp2.status_code}")
soup2 = BeautifulSoup(resp2.text, "lxml")

# Check what result containers exist
for sel in [".result__snippet", ".result", ".web-result", ".results_links"]:
    items = soup2.select(sel)
    if items:
        print(f"Selector '{sel}': {len(items)} items")
        for item in items[:2]:
            print(f"  Text: {item.get_text(strip=True)[:150]}")
        break
else:
    print("No result containers found.")
    # Print raw snippet of HTML
    print("Raw HTML sample:", resp2.text[2000:3000])
