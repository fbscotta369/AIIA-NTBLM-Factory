#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — Source Collector
Uses YouTube Data API v3 to search for videos about a topic.
Falls back to manual URL input if API key is unavailable.
"""

import json
import os
import sys
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

# Try to import YouTube client
try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Config
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")


def search_videos(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search YouTube for videos about a query.

    Args:
        query: Search string (topic + optional language hint)
        max_results: Max videos to return (default 10)

    Returns:
        List of dicts with:
            - title: video title
            - url: full YouTube URL
            - channel: channel name
            - channel_id: channel ID
            - view_count: number of views
            - duration_seconds: video duration in seconds
            - duration_text: human-readable duration (e.g. "12:34")
            - published: ISO date
            - thumbnail: URL to thumbnail
    """
    if not YOUTUBE_API_KEY:
        print("  ⚠️  YOUTUBE_API_KEY not set — no YouTube search possible")
        print("     Set YOUTUBE_API_KEY in .env or pass manually")
        return []

    if not GOOGLE_API_AVAILABLE:
        print("  ⚠️  google-api-python-client not installed")
        print("     Install with: pip install google-api-python-client")
        return []

    try:
        # Explicitly pass developerKey as keyword argument to avoid ADC
        youtube = build(
            "youtube",
            "v3",
            developerKey=YOUTUBE_API_KEY,
        )

        # Search for videos
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=min(max_results, 50),
            type="video",
            order="relevance",
        ).execute()

        video_ids = []
        for item in search_response.get("items", []):
            video_ids.append(item["id"]["videoId"])
            if len(video_ids) >= max_results * 2:
                break

        if not video_ids:
            return []

        # Get detailed stats for each video
        videos_response = youtube.videos().list(
            part="contentDetails,statistics,snippet",
            id=",".join(video_ids[:max_results * 2]),
            maxResults=min(max_results * 2, 50),
        ).execute()

        results = []
        for item in videos_response.get("items", []):
            content = item.get("contentDetails", {})
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})

            duration_seconds = parse_iso_duration(content.get("duration", "PT0S"))
            view_count = int(stats.get("viewCount", 0))

            results.append({
                "title": snippet.get("title", "Untitled"),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "video_id": item["id"],
                "channel": snippet.get("channelTitle", "Unknown"),
                "channel_id": snippet.get("channelId", ""),
                "view_count": view_count,
                "duration_seconds": duration_seconds,
                "duration_text": format_duration(duration_seconds),
                "published": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "description": snippet.get("description", "")[:500],
            })

        # Sort by relevance (items returned in relevance order, but we re-sort for safety)
        return results[:max_results]

    except Exception as e:
        print(f"  ❌ YouTube search failed: {e}")
        return []


def parse_iso_duration(iso_duration: str) -> int:
    """
    Parse ISO 8601 duration to seconds.
    Example: PT1H2M3S → 3723
    """
    import re
    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
        iso_duration,
    )
    if not match:
        return 0

    hours, minutes, seconds = match.groups(default="0")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def format_duration(seconds: int) -> str:
    """Format seconds as HH:MM:SS or MM:SS."""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def is_youtube_url(url: str) -> bool:
    """Check if a URL is a valid YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("www.youtube.com", "youtube.com", "youtu.be"):
        return True
    if "youtube" in parsed.hostname or "youtu" in parsed.hostname:
        return True
    return False


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    from urllib.parse import parse_qs
    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            return qs.get("v", [None])[0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[-1]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[-1]

    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube source collector")
    parser.add_argument("query", help="Search query (e.g. 'Dan Martell scaling up')")
    parser.add_argument("--max", type=int, default=10, help="Max results")
    args = parser.parse_args()

    if not YOUTUBE_API_KEY:
        print("Set YOUTUBE_API_KEY in .env first")
        sys.exit(1)

    results = search_videos(args.query, max_results=args.max)
    print(f"\nFound {len(results)} videos:")
    for i, r in enumerate(results, 1):
        print(f"\n  {i}. {r['title']}")
        print(f"     Channel: {r['channel']}")
        print(f"     URL: {r['url']}")
        print(f"     Views: {r['view_count']:,}")
        print(f"     Duration: {r['duration_text']}")
        print(f"     Published: {r['published']}")
        if r['thumbnail']:
            print(f"     Thumbnail: {r['thumbnail']}")
