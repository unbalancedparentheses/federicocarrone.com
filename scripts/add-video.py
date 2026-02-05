#!/usr/bin/env python3
"""Fetch YouTube video title and generate HTML snippet for the listening page."""

import re
import sys
import urllib.request
import html

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

    print(f"Title: {title}")
    print(f"Video ID: {video_id}")
    print()
    print("HTML snippet:")
    print()
    snippet = f'''  <div class="listening-item">
    <a href="https://youtube.com/watch?v={video_id}"><img src="https://img.youtube.com/vi/{video_id}/hqdefault.jpg" alt="{html.escape(title)}"></a>
    <a href="https://youtube.com/watch?v={video_id}">{html.escape(title)}</a>
  </div>'''
    print(snippet)

if __name__ == '__main__':
    main()
