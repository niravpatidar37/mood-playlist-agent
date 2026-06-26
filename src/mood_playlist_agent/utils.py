"""Shared utilities used across agents."""

import re

PLAYLIST_JSON_SCHEMA = """{
  "name": "string",
  "mood_summary": "string",
  "vibe_tags": ["string"],
  "energy_level": "low|medium|high",
  "genres": ["string"],
  "tracks": [
    {
      "title": "string",
      "artist": "string",
      "genre": "string",
      "bpm": 120,
      "spotify_search_url": "",
      "youtube_search_url": ""
    }
  ]
}"""


def strip_fences(raw: str) -> str:
    """Extract JSON from a markdown code fence, handling optional language tags and extra content."""
    raw = raw.strip()
    match = re.search(r"```(?:\w+)?\n?(.*?)```", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw
