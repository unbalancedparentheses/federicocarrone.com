#!/usr/bin/env python3
"""Fetch TV/Movie posters using Playwright to scrape TMDB"""

import os
import urllib.request
from playwright.sync_api import sync_playwright

DEST_DIR = "/Users/unbalancedparen/federicocarrone.com/static/images/watching"

SHOWS = [
    # (search_term, filename, type: tv/movie)
    ("The Killing", "the-killing.jpg", "tv"),
    ("Boardwalk Empire", "boardwalk-empire.jpg", "tv"),
    ("Band of Brothers", "band-of-brothers.jpg", "tv"),
    ("Watchmen", "watchmen.jpg", "movie"),
]

def fetch_poster(page, search_term, filename, media_type):
    print(f"Fetching: {search_term} -> {filename}")

    # Go to TMDB search
    search_url = f"https://www.themoviedb.org/search/{media_type}?query={search_term.replace(' ', '+')}"
    page.goto(search_url, wait_until="networkidle")

    # Find the first poster image
    try:
        img = page.locator("img.poster").first
        img.wait_for(timeout=5000)
        src = img.get_attribute("src")

        if src:
            # Convert to full size URL
            import re
            full_url = re.sub(r'/t/p/w\d+_and_h\d+_\w+/', '/t/p/w500/', src)
            full_url = re.sub(r'/t/p/w\d+/', '/t/p/w500/', full_url)

            if not full_url.startswith("http"):
                full_url = "https://image.tmdb.org" + full_url

            print(f"  Found: {full_url}")

            # Download the image
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
    print(f"Saving to: {DEST_DIR}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        success = 0
        for search_term, filename, media_type in SHOWS:
            if fetch_poster(page, search_term, filename, media_type):
                success += 1

        browser.close()

    print(f"\nDone! {success}/{len(SHOWS)} posters downloaded.")

if __name__ == "__main__":
    main()
