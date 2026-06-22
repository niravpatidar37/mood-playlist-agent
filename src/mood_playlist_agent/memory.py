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
    if not sessions:
        return ""

    # Count how many sessions each track appeared in — high count = user loves it
    track_counts: dict[str, int] = {}
    for s in sessions:
        for t in s.get("tracks", []):
            key = f"{t['title']} by {t['artist']}"
            track_counts[key] = track_counts.get(key, 0) + 1

    # Favorites: appeared in 2+ separate sessions
    favorites = [t for t, c in sorted(track_counts.items(), key=lambda x: -x[1]) if c >= 2]

    # Recently heard (last 2 sessions): skip these unless they're favorites
    recently_heard: set[str] = set()
    for s in sessions[-2:]:
        for t in s.get("tracks", []):
            key = f"{t['title']} by {t['artist']}"
            if key not in favorites:
                recently_heard.add(key)

    # Genre preferences across all sessions
    liked_genres: dict[str, int] = {}
    for s in sessions:
        for g in s.get("genres", []):
            liked_genres[g] = liked_genres.get(g, 0) + 1
    top_genres = sorted(liked_genres, key=liked_genres.get, reverse=True)[:5]  # type: ignore[arg-type]

    lines = []
    if top_genres:
        lines.append(f"Preferred genres: {', '.join(top_genres)}")
    if favorites:
        lines.append(
            "User's favorites (include 2-3 of these if they fit the current mood):\n"
            + "\n".join(f"  - {t}" for t in favorites[:10])
        )
    if recently_heard:
        lines.append(
            "Recently heard — skip these to keep it fresh:\n"
            + "\n".join(f"  - {t}" for t in list(recently_heard)[:20])
        )
    return "\n".join(lines)


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
