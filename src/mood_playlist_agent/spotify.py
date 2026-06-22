"""Optional Spotify API integration for real track links."""

import os
import base64
from typing import Optional

import requests


_token_cache: dict = {}


def _get_token() -> Optional[str]:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None

    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    try:
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {creds}"},
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception:
        return None


def enrich_tracks_with_spotify(tracks: list[dict]) -> list[dict]:
    """Try to add real Spotify track URLs. Falls back to search URLs if API unavailable."""
    token = _get_token()
    if not token:
        return tracks  # search URLs already set in Track.model_post_init

    enriched = []
    for track in tracks:
        query = f"track:{track['title']} artist:{track['artist']}"
        try:
            resp = requests.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": query, "type": "track", "limit": 1},
                timeout=8,
            )
            resp.raise_for_status()
            items = resp.json().get("tracks", {}).get("items", [])
            if items:
                track["spotify_search_url"] = items[0]["external_urls"]["spotify"]
        except Exception:
            pass
        enriched.append(track)
    return enriched
