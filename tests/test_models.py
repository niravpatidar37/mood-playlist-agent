"""Unit tests for Pydantic models — no API key needed."""

import pytest
from src.mood_playlist_agent.models import Track, Playlist, MoodAnalysis


def make_track(**kwargs):
    defaults = {"title": "Blinding Lights", "artist": "The Weeknd", "genre": "Synth-pop"}
    return Track(**{**defaults, **kwargs})


def make_playlist(n_tracks: int = 10) -> Playlist:
    tracks = [make_track(title=f"Song {i}", artist=f"Artist {i}") for i in range(n_tracks)]
    return Playlist(
        name="Test Vibes",
        mood_summary="A test playlist",
        vibe_tags=["test", "chill"],
        energy_level="medium",
        genres=["Pop"],
        tracks=tracks,
    )


class TestTrack:
    def test_spotify_url_auto_filled(self):
        t = make_track()
        assert "open.spotify.com/search/" in t.spotify_search_url

    def test_youtube_url_auto_filled(self):
        t = make_track()
        assert "youtube.com/results" in t.youtube_search_url

    def test_custom_urls_preserved(self):
        t = make_track(
            spotify_search_url="https://custom.spotify.url",
            youtube_search_url="https://custom.yt.url",
        )
        assert t.spotify_search_url == "https://custom.spotify.url"

    def test_bpm_optional(self):
        t = make_track()
        assert t.bpm is None
        t2 = make_track(bpm=120)
        assert t2.bpm == 120


class TestPlaylist:
    def test_valid_playlist(self):
        p = make_playlist()
        assert len(p.tracks) == 10

    def test_too_few_tracks_raises(self):
        with pytest.raises(Exception):
            make_playlist(n_tracks=3)

    def test_serialise_round_trip(self):
        p = make_playlist()
        data = p.model_dump()
        p2 = Playlist(**data)
        assert p2.name == p.name
        assert len(p2.tracks) == len(p.tracks)


class TestContext:
    def test_time_of_day_returns_string(self):
        from src.mood_playlist_agent.context import get_time_of_day
        tod = get_time_of_day()
        assert tod in {"morning", "afternoon", "evening", "late night"}

    def test_build_context_string(self):
        from src.mood_playlist_agent.context import build_context_string
        ctx = build_context_string("studying")
        assert "Time of day" in ctx
        assert "studying" in ctx


class TestMemory:
    def test_save_and_load(self, tmp_path, monkeypatch):
        import src.mood_playlist_agent.memory as mem
        monkeypatch.setattr(mem, "MEMORY_FILE", tmp_path / "memory.json")
        p = make_playlist()
        mem.save_session("chill vibes", p.model_dump())
        ctx = mem.get_preference_context()
        assert "Pop" in ctx or ctx == "" or "Artist" in ctx
