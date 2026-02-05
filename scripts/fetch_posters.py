#!/usr/bin/env python3
"""Fetch TV/Movie posters using TMDB API (no key required for basic search)"""

import urllib.request
import urllib.parse
import json
import os

DEST_DIR = "/Users/unbalancedparen/federicocarrone.com/static/images/watching"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

# Known TMDB poster paths (looked up manually - these are stable)
POSTERS = {
    # TV Series
    "the-sopranos.jpg": "/57okJJUBK0AaijxLh3RjNUaMvFI.jpg",
    "the-wire.jpg": "/4lbclFySvugI51fwsyxBTOm4DqK.jpg",
    "the-killing.jpg": "/q1dLFocxkkcGbrJz3VNgr5KhCDT.jpg",
    "boardwalk-empire.jpg": "/ufNmL6Yjv5q7PyGn4bHiwh9eoM1.jpg",
    "sherlock.jpg": "/7WTsnHkbA0FaG6R9twfFde0I9hl.jpg",
    "band-of-brothers.jpg": "/zReEqSIxMjGAFcfEDi4lanQOV6R.jpg",
    "game-of-thrones.jpg": "/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg",
    "the-office.jpg": "/qWnJzyZhyy74gjpSjIXWmuk0ifX.jpg",
    "succession.jpg": "/7HW47XbkNQ5fiwQFYGWdw9gs144.jpg",
    # Anime
    "attack-on-titan.jpg": "/hTP1DtLGFamjfu8WqjnuQdP1n4i.jpg",
    # Movies
    "watchmen.jpg": "/zcKhFvSWvf0GIBcwqxHkMjLPqhE.jpg",
}

def download_poster(filename, poster_path):
    url = f"{TMDB_IMG_BASE}{poster_path}"
    dest = os.path.join(DEST_DIR, filename)

    print(f"Downloading {filename}...")

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()

            # Verify it's an image (JPEG starts with FFD8, PNG with 89504E47)
            if data[:2] == b'\xff\xd8' or data[:4] == b'\x89PNG':
                with open(dest, 'wb') as f:
                    f.write(data)
                print(f"  ✓ Saved ({len(data)//1024}KB)")
                return True
            else:
                print(f"  ✗ Not an image")
                return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print(f"Saving to: {DEST_DIR}\n")

    success = 0
    for filename, poster_path in POSTERS.items():
        if download_poster(filename, poster_path):
            success += 1

    print(f"\nDone! {success}/{len(POSTERS)} posters downloaded.")

if __name__ == "__main__":
    main()
