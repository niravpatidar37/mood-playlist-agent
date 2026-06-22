"""Simple file-based session memory for learning user preferences."""

import json
from pathlib import Path
from datetime import datetime


MEMORY_FILE = Path("memory.json")


def _load() -> dict:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_preference_context() -> str:
    """Return a blended memory context: favorites to revisit + recent tracks to skip."""
    data = _load()
    sessions = data.get("sessions", [])
    feedback = data.get("feedback", {})
    loved_tracks: dict[str, int] = feedback.get("loved", {})
    disliked_tracks: set[str] = set(feedback.get("disliked", {}).keys())

    lines = []

    # Explicit loved tracks (highest priority — always try to match their vibe)
    if loved_tracks:
        top_loved = sorted(loved_tracks, key=loved_tracks.get, reverse=True)[:8]  # type: ignore[arg-type]
        lines.append(
            "User's all-time loved tracks (prioritise their vibe, energy, and genre in your picks):\n"
            + "\n".join(f"  - {t}" for t in top_loved)
        )

    if not sessions:
        if disliked_tracks:
            lines.append(
                "Tracks to NEVER include (user disliked these):\n"
                + "\n".join(f"  - {t}" for t in list(disliked_tracks)[:20])
            )
        return "\n".join(lines)

    # Session-based favorites: appeared in 2+ separate sessions
    track_counts: dict[str, int] = {}
    for s in sessions:
        for t in s.get("tracks", []):
            key = f"{t['title']} by {t['artist']}"
            track_counts[key] = track_counts.get(key, 0) + 1

    session_favorites = [
        t for t, c in sorted(track_counts.items(), key=lambda x: -x[1])
        if c >= 2 and t not in disliked_tracks and t not in loved_tracks
    ]

    # Recently heard (last 2 sessions): skip unless they're session favorites or loved
    recently_heard: set[str] = set()
    for s in sessions[-2:]:
        for t in s.get("tracks", []):
            key = f"{t['title']} by {t['artist']}"
            if key not in session_favorites and key not in loved_tracks:
                recently_heard.add(key)

    # Genre preferences across all sessions
    liked_genres: dict[str, int] = {}
    for s in sessions:
        for g in s.get("genres", []):
            liked_genres[g] = liked_genres.get(g, 0) + 1
    top_genres = sorted(liked_genres, key=liked_genres.get, reverse=True)[:5]  # type: ignore[arg-type]

    if top_genres:
        lines.append(f"Preferred genres: {', '.join(top_genres)}")
    if session_favorites:
        lines.append(
            "Session favorites (include 1-2 of these if they fit the mood):\n"
            + "\n".join(f"  - {t}" for t in session_favorites[:8])
        )
    if recently_heard:
        lines.append(
            "Recently heard — skip these to keep it fresh:\n"
            + "\n".join(f"  - {t}" for t in list(recently_heard)[:20])
        )
    if disliked_tracks:
        lines.append(
            "Tracks to NEVER include (user disliked these):\n"
            + "\n".join(f"  - {t}" for t in list(disliked_tracks)[:20])
        )
    return "\n".join(lines)


def save_feedback(loved: list[dict], disliked: list[dict]) -> None:
    """Persist explicit per-track feedback from the user."""
    data = _load()
    fb = data.setdefault("feedback", {"loved": {}, "disliked": {}})
    for t in loved:
        key = f"{t['title']} by {t['artist']}"
        fb["loved"][key] = fb["loved"].get(key, 0) + 1
        fb["disliked"].pop(key, None)  # un-dislike if previously marked
    for t in disliked:
        key = f"{t['title']} by {t['artist']}"
        fb["disliked"][key] = fb["disliked"].get(key, 0) + 1
        fb["loved"].pop(key, None)  # un-love if previously marked
    _save(data)


def save_session(mood_input: str, playlist: dict) -> None:
    data = _load()
    if "sessions" not in data:
        data["sessions"] = []
    data["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "mood_input": mood_input,
        "playlist_name": playlist.get("name", ""),
        "genres": playlist.get("genres", []),
        "tracks": [{"title": t["title"], "artist": t["artist"]} for t in playlist.get("tracks", [])],
    })
    # Keep last 20 sessions
    data["sessions"] = data["sessions"][-20:]
    _save(data)
