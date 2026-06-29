"""Two-stage analysis pipeline: Mood Analyst → Music Curator.

Two sequential LangChain calls: a specialist mood analyst first extracts
emotional context, then a music curator uses that analysis to build
a more precisely targeted playlist.
"""

from __future__ import annotations

import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage

from .models import MoodAnalysis, Playlist, Track

logger = logging.getLogger(__name__)
from .context import build_context_string
from .memory import get_preference_context, save_session
from .spotify import enrich_tracks_with_spotify
from .utils import PLAYLIST_JSON_SCHEMA, PLAYLIST_CURATOR_RULES, DEFAULT_MODEL, get_cached_llm, invoke_with_retry

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

_MUSIC_CURATOR_PROMPT = (
    "You are a world-class DJ and music curator with encyclopaedic knowledge of songs across all genres, eras, and languages.\n"
    "Given a mood analysis, curate a 10-track playlist.\n"
    "Return ONLY valid JSON — no markdown, no extra text:\n"
    + PLAYLIST_JSON_SCHEMA + "\n"
    "Rules:\n"
    + PLAYLIST_CURATOR_RULES + "\n"
    "- Let weather, season, and day of week shape the energy and texture.\n"
    "- BPM values must fall within the bpm_range from the mood analysis."
)



def _clamp_bpm(playlist: Playlist, bpm_range: str) -> None:
    """Clamp track BPMs into the analyst's recommended range, logging any violations."""
    match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", bpm_range.strip())
    if not match:
        return
    lo, hi = int(match.group(1)), int(match.group(2))
    for track in playlist.tracks:
        if track.bpm is not None and not (lo <= track.bpm <= hi):
            logger.warning(
                "Track '%s' BPM %d outside range %s — clamping", track.title, track.bpm, bpm_range
            )
            track.bpm = max(lo, min(hi, track.bpm))


def generate_playlist_with_crew(
    mood_input: str,
    context_extra: str = "",
    seed: str = "",
    model: str = DEFAULT_MODEL,
    spotify_enrich: bool = True,
) -> Playlist:
    """Two-stage pipeline: analyse mood, then curate playlist."""
    llm = get_cached_llm(model, 0.7)
    context = build_context_string(context_extra, seed=seed)
    preferences = get_preference_context()

    # ── Stage 1: Mood Analyst ────────────────────────────────────────────────
    analyst_user = "\n\n".join(filter(None, [
        f"Mood / activity: {mood_input}",
        f"Context:\n{context}",
        f"Memory context (follow strictly):\n{preferences}" if preferences else "",
    ]))
    mood_analysis = invoke_with_retry(
        llm,
        [SystemMessage(content=_MOOD_ANALYST_PROMPT), HumanMessage(content=analyst_user)],
        MoodAnalysis,
        "Mood Analyst",
    )

    # ── Stage 2: Music Curator ───────────────────────────────────────────────
    curator_user = f"Mood analysis:\n{mood_analysis.model_dump_json(indent=2)}"
    playlist = invoke_with_retry(
        llm,
        [SystemMessage(content=_MUSIC_CURATOR_PROMPT), HumanMessage(content=curator_user)],
        Playlist,
        "Music Curator",
    )

    _clamp_bpm(playlist, mood_analysis.bpm_range)

    if spotify_enrich:
        enriched = enrich_tracks_with_spotify([t.model_dump() for t in playlist.tracks])
        playlist.tracks = [Track(**t) for t in enriched]

    save_session(mood_input, playlist.model_dump())
    return playlist
