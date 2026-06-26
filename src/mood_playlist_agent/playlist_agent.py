"""Single LangChain agent that generates a mood-based playlist."""

import json

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError

from .models import Playlist, Track
from .context import build_context_string
from .memory import get_preference_context, save_session
from .spotify import enrich_tracks_with_spotify
from .utils import strip_fences

SYSTEM_PROMPT = """You are VibeForge, an expert music curator AI trained on decades of listening data.
Your job is to craft a playlist that feels handpicked — like a friend who knows your taste perfectly.

Rules:
- Return ONLY valid JSON matching the Playlist schema — no markdown, no extra text.
- Include exactly 10 tracks that genuinely fit the mood.
- Quality mix (like Spotify/YouTube algorithm): 2 well-known hits the user probably loves, 3 cult classics or critically acclaimed deep cuts, 3 fresh discoveries the user likely hasn't heard, 2 wildcard picks from other languages or genres that still fit the vibe.
- Prioritise the user's "loved tracks" — match their energy, genre, and era first. Include 1-2 of them if they fit the mood.
- Include 1-2 "session favorites" if they fit the mood and aren't recently heard.
- Skip every track listed under "recently heard" and "never play again" — no exceptions.
- Genre diversity: no single genre should exceed 40% of the playlist (max 4 out of 10 tracks). Actively mix genres.
- Artist diversity: no artist appears more than twice.
- Let weather, season, and day of week shape the energy (e.g. rainy winter evening → melancholy indie; sunny weekend morning → feel-good pop).
- If a seed track is provided, use it as a vibe anchor — match its era, energy, and feel.
- Support all languages and genres (Bollywood, K-pop, Latin, Afrobeats, jazz, classical, etc.).
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


def _check_genre_diversity(playlist: Playlist) -> str | None:
    """Return a correction message if any genre dominates more than 40% of tracks."""
    from collections import Counter
    genre_counts = Counter(t.genre.lower() for t in playlist.tracks)
    dominant = [(g, c) for g, c in genre_counts.items() if c > len(playlist.tracks) * 0.4]
    if dominant:
        over = ", ".join(f'"{g}" ({c} tracks)' for g, c in dominant)
        return (
            f"Genre diversity violation: {over} exceed 40% of the playlist. "
            "Replace some tracks with different genres while keeping the mood. Return corrected JSON only."
        )
    return None


def generate_playlist(
    mood_input: str,
    context_extra: str = "",
    model: str = "llama-3.3-70b-versatile",
    spotify_enrich: bool = True,
    seed: str = "",
) -> Playlist:
    """Generate a Playlist from a natural-language mood description."""
    llm = ChatGroq(model=model, temperature=0.8)

    context = build_context_string(context_extra, seed=seed)
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

    playlist: Playlist | None = None
    for attempt in range(3):
        response = llm.invoke(messages)
        raw = strip_fences(response.content)
        try:
            data = json.loads(raw)
            playlist = Playlist(**data)
            # Check genre diversity — one auto-correction attempt
            if attempt == 0:
                correction = _check_genre_diversity(playlist)
                if correction:
                    messages.append(HumanMessage(content=correction))
                    playlist = None
                    continue
            break
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == 2:
                raise RuntimeError(f"LLM returned invalid playlist JSON after 3 attempts: {exc}") from exc
            messages.append(HumanMessage(content=f"Your response had errors: {exc}. Please fix and return valid JSON only."))

    if playlist is None:
        raise RuntimeError("Failed to generate a valid playlist.")

    if spotify_enrich:
        enriched = enrich_tracks_with_spotify([t.model_dump() for t in playlist.tracks])
        playlist.tracks = [Track(**t) for t in enriched]

    save_session(mood_input, playlist.model_dump())
    return playlist
