"""Two-stage multi-agent pipeline: Mood Analyst → Music Curator.

Implements the same conceptual flow as CrewAI but via two sequential
LangChain calls, avoiding crewai/litellm dependency issues with Groq.
"""

from __future__ import annotations

import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from .models import MoodAnalysis, Playlist
from .context import build_context_string
from .memory import get_preference_context, save_session
from .utils import strip_fences

_MOOD_ANALYST_PROMPT = """You are a music psychologist and emotion expert.
Analyse the user's mood/activity input and return ONLY valid JSON matching this schema — no markdown, no extra text:
{
  "primary_emotion": "string",
  "secondary_emotions": ["string"],
  "energy_level": "low|medium|high",
  "bpm_range": "60-80",
  "recommended_genres": ["string"],
  "avoid_genres": ["string"],
  "time_of_day_context": "string",
  "activity_context": "string",
  "musical_key_feel": "major|minor|modal"
}"""

_MUSIC_CURATOR_PROMPT = """You are a world-class DJ and music curator with encyclopaedic knowledge of songs across all genres, eras, and languages.
Given a mood analysis, curate a 10-track playlist.
Return ONLY valid JSON — no markdown, no extra text:
{
  "name": "string",
  "mood_summary": "string",
  "vibe_tags": ["string"],
  "energy_level": "low|medium|high",
  "genres": ["string"],
  "tracks": [
    {"title": "string", "artist": "string", "genre": "string", "bpm": 120, "spotify_search_url": "", "youtube_search_url": ""}
  ]
}
Rules:
- Exactly 10 tracks, no artist more than twice, support all languages and genres.
- Quality mix (like Spotify/YouTube algorithm): 2 well-known hits, 3 cult classics or deep cuts, 3 fresh discoveries, 2 wildcard picks from other languages/genres that still fit the vibe.
- Prioritise user's "loved tracks" — match their energy, genre, and era. Include 1-2 if they fit the mood.
- Include 1-2 "session favorites" if they fit and aren't recently heard.
- Skip every track under "recently heard" and "never play again" — no exceptions.
- Genre diversity: no single genre > 40% of tracks (max 4 out of 10). Actively mix genres.
- Let weather, season, and day of week shape the energy and texture.
- BPM values must fall within the bpm_range from the mood analysis."""



def generate_playlist_with_crew(mood_input: str, context_extra: str = "", seed: str = "") -> Playlist:
    """Two-stage pipeline: analyse mood, then curate playlist."""
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    context = build_context_string(context_extra, seed=seed)
    preferences = get_preference_context()

    # ── Stage 1: Mood Analyst ────────────────────────────────────────────────
    analyst_user = "\n\n".join(filter(None, [
        f"Mood / activity: {mood_input}",
        f"Context:\n{context}",
        f"Memory context (follow strictly):\n{preferences}" if preferences else "",
    ]))
    for attempt in range(3):
        resp = llm.invoke([SystemMessage(content=_MOOD_ANALYST_PROMPT), HumanMessage(content=analyst_user)])
        try:
            mood_data = json.loads(strip_fences(resp.content.strip()))
            mood_analysis = MoodAnalysis(**mood_data)
            break
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == 2:
                raise RuntimeError(f"Mood Analyst returned invalid JSON after 3 attempts: {exc}") from exc

    # ── Stage 2: Music Curator ───────────────────────────────────────────────
    curator_user = f"Mood analysis:\n{mood_analysis.model_dump_json(indent=2)}"
    for attempt in range(3):
        resp = llm.invoke([SystemMessage(content=_MUSIC_CURATOR_PROMPT), HumanMessage(content=curator_user)])
        try:
            playlist_data = json.loads(strip_fences(resp.content.strip()))
            playlist = Playlist(**playlist_data)
            break
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == 2:
                raise RuntimeError(f"Music Curator returned invalid JSON after 3 attempts: {exc}") from exc

    save_session(mood_input, playlist.model_dump())
    return playlist
