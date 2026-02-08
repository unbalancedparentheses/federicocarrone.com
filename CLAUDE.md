# Project Instructions

Personal website built with [Zola](https://www.getzola.org/) static site generator.

## Development Environment

Use **Nix** for dependencies and the **Makefile** for common tasks:

- `make build` — build the site (zola build via nix)
- `make build-css` — minify CSS with lightningcss
- `make watch` — start dev server (zola serve)
- `make add-video URL=<youtube-url>` — add a video to the listening page
- `make fetch-posters` — download posters for the watching page

All `make` targets that need zola/lightningcss run through `nix develop` automatically.

## Scripts

- **Adding a YouTube video to Listening**: Run `make add-video URL=<youtube-url>` (or `python3 scripts/add-video.py <youtube-url>`) to fetch the title, download the thumbnail, and get the HTML snippet. Then add the snippet to `content/listening/_index.md` at the top of the current year's gallery.
- **Adding a poster for Watching**: Add the TMDB poster path to the `POSTERS` dict in `scripts/fetch_posters.py`, then run `make fetch-posters`. The destination directory is `static/images/watching/`.

## Site Structure

- **Articles**: `content/articles/` — standalone blog posts
- **Series**: `content/series/` — multi-part article series (e.g. Ethereum, Concrete)
- **Talks**: `content/talks/` — talks and podcast appearances
- **Watching**: `content/watching/_index.md` — series, movies, anime, animation recommendations (sorted by IMDb rating within each section)
- **Listening**: `content/listening/_index.md` — YouTube podcasts and videos grouped by year (newest first within each year). When a new year starts, add a new `## YYYY` heading and `<div class="listening-gallery">` section above the previous year.
- **Reading**: `content/reading/_index.md` — book recommendations grouped by theme
- **About**: `content/about/_index.md`

## Navbar Order

Home — Articles — Series — Talks — Watching — Listening — Reading — About
