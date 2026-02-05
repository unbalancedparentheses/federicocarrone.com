#!/usr/bin/env python3
"""Fetch YouTube video title, download thumbnail, and generate HTML snippet."""

import os
import re
import sys
import urllib.request
import html
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, '..', 'static', 'images', 'listening')

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_title(video_id):
    """Fetch video title from YouTube."""
    url = f'https://www.youtube.com/watch?v={video_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        content = response.read().decode('utf-8')

    match = re.search(r'<title>([^<]+)</title>', content)
    if match:
        title = html.unescape(match.group(1))
        title = re.sub(r'\s*-\s*YouTube$', '', title)
        return title.strip()
    return None

def title_to_filename(title):
    """Convert title to a safe filename."""
    name = title.lower()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')[:50]
    return f"{name}.jpg"

def download_thumbnail(video_id, filename):
    """Download YouTube thumbnail to local images directory."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    dest = os.path.join(IMAGES_DIR, filename)

    # Try maxresdefault first, fall back to hqdefault
    for quality in ['maxresdefault', 'hqdefault']:
        url = f'https://img.youtube.com/vi/{video_id}/{quality}.jpg'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                # maxresdefault returns a small placeholder if not available
                if len(data) > 5000:
                    with open(dest, 'wb') as f:
                        f.write(data)
                    return True
        except Exception:
            continue
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python add-video.py <youtube-url>")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)

    if not video_id:
        print(f"Error: Could not extract video ID from: {url}")
        sys.exit(1)

    title = fetch_title(video_id)
    if not title:
        print(f"Error: Could not fetch title for video: {video_id}")
        sys.exit(1)

    filename = title_to_filename(title)

    print(f"Title: {title}")
    print(f"Video ID: {video_id}")
    print(f"Downloading thumbnail to: static/images/listening/{filename}")

    if download_thumbnail(video_id, filename):
        print("Thumbnail downloaded successfully")
    else:
        print("Warning: Could not download thumbnail")

    date_str = datetime.now().strftime("%b %Y")
    print()
    print("HTML snippet:")
    print()
    snippet = f'''  <div class="listening-item">
    <a href="https://youtube.com/watch?v={video_id}"><img src="/images/listening/{filename}" alt="{html.escape(title)}"></a>
    <div class="content">
      <a class="title" href="https://youtube.com/watch?v={video_id}">{html.escape(title)}</a>
      <span class="date">{date_str}</span>
    </div>
  </div>'''
    print(snippet)

if __name__ == '__main__':
    main()
