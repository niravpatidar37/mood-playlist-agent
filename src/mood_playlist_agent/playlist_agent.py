"""Single LangChain agent that generates a mood-based playlist."""

import json
from typing import Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError

from .models import Playlist, Track
from .context import build_context_string
from .memory import get_preference_context, save_session
from .spotify import enrich_tracks_with_spotify

load_dotenv()

SYSTEM_PROMPT = """You are MoodTunes, an expert music curator AI.
Your job is to craft a playlist that feels both personal and fresh — a mix of familiar comfort and new discoveries.

Rules:
- Return ONLY valid JSON matching the Playlist schema — no markdown, no extra text.
- Include exactly 10 tracks that genuinely fit the mood.
- Blend: include 2-3 tracks from the user's "favorites" list if they match the mood and weather, fill the rest with fresh songs the user hasn't heard yet.
- Skip any track listed under "recently heard" — those were just played.
- Let weather and time of day shape the energy and texture of the playlist (e.g. rainy night → mellow; sunny morning → upbeat).
- Vary artists — no artist should appear more than twice.
- Support all languages and genres (Bollywood, K-pop, Latin, Afrobeats, etc.).
- Set spotify_search_url and youtube_search_url to empty strings — they will be filled automatically.
- bpm should be an integer reflecting the track's approximate tempo.

Playlist JSON schema:
{
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


def generate_playlist(
    mood_input: str,
    context_extra: str = "",
    model: str = "llama-3.3-70b-versatile",
    spotify_enrich: bool = True,
) -> Playlist:
    """Generate a Playlist from a natural-language mood description."""
    llm = ChatGroq(model=model, temperature=0.8)

    context = build_context_string(context_extra)
    preferences = get_preference_context()

    user_content_parts = [
        f"Mood / activity: {mood_input}",
        f"Context:\n{context}",
    ]
    if preferences:
        user_content_parts.append(f"Memory context (follow strictly):\n{preferences}")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n".join(user_content_parts)),
    ]

    for attempt in range(3):
        response = llm.invoke(messages)
        raw = response.content.strip()
        # Strip markdown code fences if model wraps response
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            data = json.loads(raw)
            playlist = Playlist(**data)
            break
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == 2:
                raise RuntimeError(f"LLM returned invalid playlist JSON after 3 attempts: {exc}") from exc
            messages.append(HumanMessage(content=f"Your response had errors: {exc}. Please fix and return valid JSON only."))

    if spotify_enrich:
        enriched = enrich_tracks_with_spotify([t.model_dump() for t in playlist.tracks])
        playlist.tracks = [Track(**t) for t in enriched]

    save_session(mood_input, playlist.model_dump())
    return playlist
