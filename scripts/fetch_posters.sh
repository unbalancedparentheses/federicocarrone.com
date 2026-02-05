#!/bin/bash

# Fetch TV/Movie posters from TMDB
# Usage: ./fetch_posters.sh

DEST_DIR="/Users/unbalancedparen/federicocarrone.com/static/images/watching"

fetch_poster() {
    local search_term="$1"
    local output_name="$2"
    local type="$3"  # tv or movie

    echo "Fetching: $search_term -> $output_name"

    # Search TMDB for the show/movie
    search_url="https://www.themoviedb.org/search/${type}?query=$(echo "$search_term" | sed 's/ /+/g')"

    # Get the search results page and extract the first poster image
    poster_path=$(curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
        "$search_url" | grep -oE '/t/p/w[0-9]+/[a-zA-Z0-9]+\.(jpg|png)' | head -1)

    if [ -n "$poster_path" ]; then
        full_url="https://image.tmdb.org${poster_path}"
        echo "  Found: $full_url"
        curl -sL -A "Mozilla/5.0" -o "${DEST_DIR}/${output_name}" "$full_url"

        # Verify it's actually an image
        if file "${DEST_DIR}/${output_name}" | grep -qE 'image|JPEG|PNG'; then
            echo "  Success!"
            return 0
        else
            echo "  Failed - not an image"
            rm -f "${DEST_DIR}/${output_name}"
            return 1
        fi
    else
        echo "  No poster found"
        return 1
    fi
}

# TV Series
fetch_poster "The Sopranos" "the-sopranos.jpg" "tv"
fetch_poster "The Wire" "the-wire.jpg" "tv"
fetch_poster "The Killing" "the-killing.jpg" "tv"
fetch_poster "Boardwalk Empire" "boardwalk-empire.jpg" "tv"
fetch_poster "Sherlock" "sherlock.jpg" "tv"
fetch_poster "Band of Brothers" "band-of-brothers.jpg" "tv"
fetch_poster "Game of Thrones" "game-of-thrones.jpg" "tv"
fetch_poster "The Office" "the-office.jpg" "tv"
fetch_poster "Succession" "succession.jpg" "tv"

# Anime
fetch_poster "Attack on Titan" "attack-on-titan.jpg" "tv"

# Movies
fetch_poster "Watchmen 2009" "watchmen.jpg" "movie"

echo ""
echo "Done! Checking results..."
ls -la "$DEST_DIR"/*.jpg | tail -15
