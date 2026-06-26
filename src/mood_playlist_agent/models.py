"""Pydantic models for the playlist agent."""

from typing import Any, Literal, Optional
from urllib.parse import quote_plus

from pydantic import BaseModel, Field


class Track(BaseModel):
    title: str
    artist: str
    genre: str
    bpm: Optional[int] = None
    spotify_search_url: str = ""
    youtube_search_url: str = ""

    def model_post_init(self, __context: Any) -> None:
        query = quote_plus(f"{self.artist} {self.title}")
        if not self.spotify_search_url:
            self.spotify_search_url = f"https://open.spotify.com/search/{query}"
        if not self.youtube_search_url:
            self.youtube_search_url = f"https://www.youtube.com/results?search_query={query}"


class Playlist(BaseModel):
    name: str = Field(description="Creative playlist name reflecting the mood")
    mood_summary: str = Field(description="2-3 sentence description of the detected mood and why these songs fit")
    vibe_tags: list[str] = Field(description="3-5 short tags like ['chill', 'lo-fi', 'late-night']")
    energy_level: Literal["low", "medium", "high"]
    tracks: list[Track] = Field(description="Exactly 10 recommended tracks", min_length=10, max_length=10)
    genres: list[str] = Field(description="Primary genres featured in this playlist")


class MoodAnalysis(BaseModel):
    """Intermediate model used by the two-stage analysis pipeline."""
    primary_emotion: str
    secondary_emotions: list[str]
    energy_level: Literal["low", "medium", "high"]
    bpm_range: str
    recommended_genres: list[str]
    avoid_genres: list[str]
    time_of_day_context: str
    activity_context: str
    musical_key_feel: Literal["major", "minor", "modal"]
