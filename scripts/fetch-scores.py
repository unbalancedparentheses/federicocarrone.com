#!/usr/bin/env python3
"""Fetch IMDb scores using Playwright - simplified version."""

import sys
from playwright.sync_api import sync_playwright

# Sample items to verify (subset for quick testing)
ITEMS = [
    # Series
    ("Band of Brothers", "tt0185906", "9.4"),
    ("The Wire", "tt0306414", "9.3"),
    ("The Sopranos", "tt0141842", "9.2"),
    ("Game of Thrones", "tt0944947", "9.2"),
    ("Succession", "tt7660850", "8.8"),
    # Movies
    ("The Godfather", "tt0068646", "9.2"),
    ("Pulp Fiction", "tt0110912", "8.9"),
    ("The Dark Knight", "tt0468569", "9.0"),
    ("Inception", "tt1375666", "8.8"),
    ("Fight Club", "tt0137523", "8.8"),
]

def fetch_imdb_score(page, imdb_id):
    """Fetch IMDb rating from page."""
    url = f"https://www.imdb.com/title/{imdb_id}/"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(1500)

        rating_elem = page.locator('[data-testid="hero-rating-bar__aggregate-rating__score"] span').first
        return rating_elem.text_content(timeout=3000)
    except Exception as e:
        return "N/A"

def main():
    print(f"{'Title':<30} {'Current':>8} {'Actual':>8} {'Match':>6}")
    print("-" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        mismatches = []
        for title, imdb_id, current in ITEMS:
            actual = fetch_imdb_score(page, imdb_id)
            match = "✓" if current == actual else "✗"
            print(f"{title:<30} {current:>8} {actual:>8} {match:>6}")

            if current != actual and actual != "N/A":
                mismatches.append((title, current, actual))

        browser.close()

    if mismatches:
        print("\nMISMATCHES:")
        for title, current, actual in mismatches:
            print(f"  {title}: {current} -> {actual}")
    else:
        print("\nAll scores match!")

if __name__ == '__main__':
    main()
