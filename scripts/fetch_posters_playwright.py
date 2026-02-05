#!/usr/bin/env python3
"""Fetch TV/Movie posters using Playwright to scrape TMDB"""

import os
import re
import urllib.request
from playwright.sync_api import sync_playwright

DEST_DIR = "/Users/unbalancedparen/federicocarrone.com/static/images/watching"

# Low-res images that need better versions (under 500px width)
SHOWS = [
    # Movies - 220px wide
    ("Inglourious Basterds", "inglourious-basterds.jpg", "movie"),
    ("Little Miss Sunshine", "little-miss-sunshine.jpg", "movie"),
    ("Midnight in Paris", "midnight-in-paris.jpg", "movie"),
    ("The Departed", "the-departed.jpg", "movie"),
    ("Blue Jasmine", "blue-jasmine.jpg", "movie"),
    ("Django Unchained", "django-unchained.jpg", "movie"),
    ("Drive 2011", "drive.jpg", "movie"),
    ("Inception", "inception.jpg", "movie"),
    ("Shutter Island", "shutter-island.jpg", "movie"),
    ("Fight Club", "fight-club.jpg", "movie"),
    ("Gangs of New York", "gangs-of-new-york.jpg", "movie"),
    ("Apocalypse Now", "apocalypse-now.jpg", "movie"),
    ("The Girl with the Dragon Tattoo 2011", "the-girl-with-the-dragon-tattoo.jpg", "movie"),
    ("The Grand Budapest Hotel", "the-grand-budapest-hotel.jpg", "movie"),
    ("Reservoir Dogs", "reservoir-dogs.jpg", "movie"),
    ("The Big Lebowski", "the-big-lebowski.jpg", "movie"),
    ("There Will Be Blood", "there-will-be-blood.jpg", "movie"),
    ("The Dark Knight", "the-dark-knight.jpg", "movie"),
    ("Dune 2021", "dune-part-one.jpg", "movie"),
    ("Dune Part Two", "dune-part-two.jpg", "movie"),
    ("Once Upon a Time in Hollywood", "once-upon-a-time-in-hollywood.jpg", "movie"),
    ("Gladiator 2000", "gladiator.jpg", "movie"),
    ("Pulp Fiction", "pulp-fiction.jpg", "movie"),
    ("The Wolf of Wall Street", "the-wolf-of-wall-street.jpg", "movie"),
    ("The Good the Bad and the Ugly", "the-good-the-bad-and-the-ugly.jpg", "movie"),
    # Anime
    ("Ghost in the Shell 1995", "ghost-in-the-shell.jpg", "movie"),
    ("Akira 1988", "akira.jpg", "movie"),
    ("Cowboy Bebop", "cowboy-bebop.jpg", "tv"),
    # TV
    ("Rick and Morty", "rick-and-morty.jpg", "tv"),
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
