#!/usr/bin/env python3
"""Fetch TV/Movie posters using Playwright to scrape TMDB"""

import os
import re
import urllib.request
from playwright.sync_api import sync_playwright

DEST_DIR = "/Users/unbalancedparen/federicocarrone.com/static/images/watching"

# Posters to fetch
SHOWS = [
    # Oldboy 2003 Korean original
    ("올드보이", "oldboy.jpg", "movie"),
]

def fetch_poster(page, search_term, filename, media_type):
    print(f"Fetching: {search_term} -> {filename}")

    search_url = f"https://www.themoviedb.org/search/{media_type}?query={search_term.replace(' ', '+')}"
    page.goto(search_url, wait_until="networkidle")

    try:
        img = page.locator("img.poster").first
        img.wait_for(timeout=5000)
        src = img.get_attribute("src")

        if src:
            # Convert to full size URL (w500)
            full_url = re.sub(r'/t/p/w\d+_and_h\d+_\w+/', '/t/p/w500/', src)
            full_url = re.sub(r'/t/p/w\d+/', '/t/p/w500/', full_url)

            if not full_url.startswith("http"):
                full_url = "https://image.tmdb.org" + full_url

            dest = os.path.join(DEST_DIR, filename)
            req = urllib.request.Request(full_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                with open(dest, 'wb') as f:
                    f.write(data)
                print(f"  ✓ Saved ({len(data)//1024}KB)")
                return True
    except Exception as e:
        print(f"  ✗ Error: {e}")

    return False

def main():
    print(f"Fetching {len(SHOWS)} posters...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        success = 0
        for search_term, filename, media_type in SHOWS:
            if fetch_poster(page, search_term, filename, media_type):
                success += 1

        browser.close()

    print(f"\nDone! {success}/{len(SHOWS)} posters fetched.")

if __name__ == "__main__":
    main()
