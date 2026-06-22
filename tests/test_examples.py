"""Integration-style example runs (require GROQ_API_KEY — skipped if absent)."""

import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping live API tests",
)


def test_generate_playlist_chill():
    from src.mood_playlist_agent.playlist_agent import generate_playlist
    playlist = generate_playlist("feeling chill after a long day", spotify_enrich=False)
    assert playlist.name
    assert len(playlist.tracks) >= 8
    assert playlist.energy_level in {"low", "medium", "high"}


def test_generate_playlist_workout():
    from src.mood_playlist_agent.playlist_agent import generate_playlist
    playlist = generate_playlist("pumped up for gym, need high energy", spotify_enrich=False)
    assert playlist.energy_level in {"medium", "high"}
    assert len(playlist.tracks) >= 8


def test_generate_playlist_multilingual():
    from src.mood_playlist_agent.playlist_agent import generate_playlist
    playlist = generate_playlist("nostalgic Bollywood evening", spotify_enrich=False)
    assert playlist.name
    genres_lower = [g.lower() for g in playlist.genres]
    assert any("bollywood" in g or "hindi" in g or "indian" in g for g in genres_lower)
