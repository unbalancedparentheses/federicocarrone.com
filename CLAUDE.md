# Project Instructions

Personal website built with [Zola](https://www.getzola.org/) static site generator.

## Scripts

- **Adding a YouTube video to Listening**: Run `python3 scripts/add-video.py <youtube-url>` to fetch the title, download the thumbnail, and get the HTML snippet. Then add the snippet to `content/listening/_index.md` at the top of the gallery.
- **Adding a poster for Watching**: Add the TMDB poster path to the `POSTERS` dict in `scripts/fetch_posters.py`, then run the script to download it. The destination directory is `static/images/watching/`.

## Site Structure

- **Articles**: `content/articles/` — standalone blog posts
- **Series**: `content/series/` — multi-part article series (e.g. Ethereum, Concrete)
- **Talks**: `content/talks/` — talks and podcast appearances
- **Watching**: `content/watching/_index.md` — series, movies, anime, animation recommendations (sorted by IMDb rating within each section)
- **Listening**: `content/listening/_index.md` — YouTube podcasts and videos (newest first)
- **Reading**: `content/reading/_index.md` — book recommendations grouped by theme
- **About**: `content/about/_index.md`

## Navbar Order

Home — Articles — Series — Talks — Watching — Listening — Reading — About
