"""Shared utilities used across agents."""

import re

PLAYLIST_CURATOR_RULES = """\
- Exactly 10 tracks that genuinely fit the mood.
- Quality mix (like Spotify/YouTube algorithm): 2 well-known hits the user probably loves, 3 cult classics or critically acclaimed deep cuts, 3 fresh discoveries the user likely hasn't heard, 2 wildcard picks from other languages or genres that still fit the vibe.
- Prioritise the user's "loved tracks" — match their energy, genre, and era first. Include 1-2 of them if they fit the mood.
- Include 1-2 "session favorites" if they fit the mood and aren't recently heard.
- Skip every track listed under "recently heard" and "never play again" — no exceptions.
- Genre diversity: no single genre should exceed 40% of the playlist (max 4 out of 10 tracks). Actively mix genres.
- Artist diversity: no artist appears more than twice.
- Support all languages and genres (Bollywood, K-pop, Latin, Afrobeats, jazz, classical, etc.)."""

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
