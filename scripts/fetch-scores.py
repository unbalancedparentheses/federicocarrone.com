#!/usr/bin/env python3
"""Fetch IMDb and Metacritic scores using Playwright."""

import re
import sys
from playwright.sync_api import sync_playwright

# All items from the watching page with their IMDb IDs
ITEMS = [
    # Series
    ("Band of Brothers", "tt0185906", "9.4"),
    ("The Wire", "tt0306414", "9.3"),
    ("The Sopranos", "tt0141842", "9.2"),
    ("Game of Thrones", "tt0944947", "9.2"),
    ("Sherlock", "tt1475582", "9.1"),
    ("The Office", "tt0386676", "9.0"),
    ("Succession", "tt7660850", "8.8"),
    ("Boardwalk Empire", "tt0979432", "8.6"),
    ("Homeland", "tt1796960", "8.3"),
    ("The Killing", "tt1637727", "8.3"),
    # Movies: Crime & Drama
    ("The Godfather", "tt0068646", "9.2"),
    ("Pulp Fiction", "tt0110912", "8.9"),
    ("City of God", "tt0317248", "8.6"),
    ("The Departed", "tt0407887", "8.5"),
    ("Oldboy", "tt0364569", "8.4"),
    ("Reservoir Dogs", "tt0105236", "8.3"),
    ("Snatch", "tt0208092", "8.3"),
    ("There Will Be Blood", "tt0469494", "8.2"),
    ("Taxi Driver", "tt0075314", "8.2"),
    ("The Wolf of Wall Street", "tt0993846", "8.2"),
    ("Lock Stock and Two Smoking Barrels", "tt0120735", "8.2"),
    ("Nine Queens", "tt0247586", "8.1"),
    ("The Irishman", "tt1302006", "7.8"),
    ("The Girl with the Dragon Tattoo", "tt1568346", "7.8"),
    ("Zodiac", "tt0443706", "7.7"),
    ("Once Upon a Time in Hollywood", "tt7131622", "7.6"),
    ("Gangs of New York", "tt0217505", "7.5"),
    # Movies: Sci-Fi & Thriller
    ("The Dark Knight", "tt0468569", "9.0"),
    ("Inception", "tt1375666", "8.8"),
    ("Fight Club", "tt0137523", "8.8"),
    ("The Good the Bad and the Ugly", "tt0060196", "8.8"),
    ("The Matrix", "tt0133093", "8.7"),
    ("Apocalypse Now", "tt0078788", "8.5"),
    ("Gladiator", "tt0172495", "8.5"),
    ("Django Unchained", "tt1853728", "8.5"),
    ("Dune Part Two", "tt15239678", "8.5"),
    ("Inglourious Basterds", "tt0361748", "8.4"),
    ("Full Metal Jacket", "tt0093058", "8.3"),
    ("Shutter Island", "tt1130884", "8.2"),
    ("Dune", "tt1160419", "8.0"),
    ("Sin City", "tt0401792", "8.0"),
    ("Drive", "tt0780504", "7.8"),
    ("Watchmen", "tt0409459", "7.6"),
    ("The Assassination of Jesse James", "tt0443680", "7.5"),
    # Movies: Comedy & Indie
    ("The Big Lebowski", "tt0118715", "8.1"),
    ("The Grand Budapest Hotel", "tt2278388", "8.1"),
    ("Little Miss Sunshine", "tt0449059", "7.8"),
    ("Midnight in Paris", "tt1605783", "7.7"),
    ("Babel", "tt0449467", "7.4"),
    ("Blue Jasmine", "tt2334873", "7.3"),
    ("The Darjeeling Limited", "tt0838221", "7.2"),
    ("Vicky Cristina Barcelona", "tt0497465", "7.1"),
    # Anime
    ("Attack on Titan", "tt2560140", "9.1"),
    ("Cowboy Bebop", "tt0213338", "8.9"),
    ("Berserk", "tt0318871", "8.7"),
    ("Ghost in the Shell", "tt0113568", "8.0"),
    ("Akira", "tt0094625", "8.0"),
    # Animation
    ("Rick and Morty", "tt2861424", "9.1"),
    ("Arcane", "tt11126994", "9.0"),
    ("Gravity Falls", "tt1865718", "8.9"),
    ("BoJack Horseman", "tt3398228", "8.8"),
    ("Samurai Jack", "tt0278238", "8.5"),
    ("Love Death Robots", "tt9561862", "8.4"),
    ("Final Space", "tt6317068", "8.2"),
    ("Daria", "tt0118298", "7.8"),
]

def fetch_scores(page, title, imdb_id):
    """Fetch IMDb rating and Metascore from IMDb page."""
    url = f"https://www.imdb.com/title/{imdb_id}/"

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)  # Wait for dynamic content

        # Get IMDb rating
        imdb_rating = "N/A"
        try:
            rating_elem = page.locator('[data-testid="hero-rating-bar__aggregate-rating__score"] span').first
            imdb_rating = rating_elem.text_content(timeout=3000)
        except:
            pass

        # Get Metascore
        metascore = "N/A"
        try:
            meta_elem = page.locator('.metacritic-score-box, [data-testid="hero-rating-bar__aggregate-rating"] .score-meta').first
            metascore = meta_elem.text_content(timeout=3000)
        except:
            # Try alternative selector
            try:
                meta_elem = page.locator('text=/\\d+.*Metascore/').first
                text = meta_elem.text_content(timeout=3000)
                match = re.search(r'(\d+)', text)
                if match:
                    metascore = match.group(1)
            except:
                pass

        return imdb_rating, metascore
    except Exception as e:
        print(f"  Error: {e}")
        return "N/A", "N/A"

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_only = True
    else:
        verify_only = False

    print(f"{'Title':<45} {'Current':>8} {'IMDb':>8} {'Meta':>6}")
    print("-" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        mismatches = []

        for title, imdb_id, current_score in ITEMS:
            imdb_rating, metascore = fetch_scores(page, title, imdb_id)

            # Check if current score matches
            match = "✓" if current_score == imdb_rating else "✗"

            print(f"{title:<45} {current_score:>8} {imdb_rating:>8} {metascore:>6} {match}")

            if current_score != imdb_rating and imdb_rating != "N/A":
                mismatches.append((title, current_score, imdb_rating, metascore))

        browser.close()

    if mismatches:
        print("\n" + "=" * 75)
        print("MISMATCHES FOUND:")
        for title, current, actual, meta in mismatches:
            print(f"  {title}: {current} -> {actual} (Meta: {meta})")

if __name__ == '__main__':
    main()
