"""Streamlit web UI for MoodTunes — AI mood-based playlist generator."""

from __future__ import annotations

import html

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from mood_playlist_agent.playlist_agent import generate_playlist
from mood_playlist_agent.memory import save_feedback
from mood_playlist_agent.models import Track

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoodTunes — AI Playlist Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Header */
.moodtunes-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #a855f7;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.moodtunes-header::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(168,85,247,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.moodtunes-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a855f7, #ec4899, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.moodtunes-sub {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 0.3rem;
}

/* Playlist card */
.playlist-card {
    background: linear-gradient(135deg, #1e1e2e, #16213e);
    border: 1px solid rgba(168,85,247,0.4);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
}
.playlist-name {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0 0 0.3rem 0;
}
.playlist-summary {
    color: #94a3b8;
    font-size: 0.95rem;
    font-style: italic;
    margin: 0 0 1rem 0;
}

/* Energy badges */
.energy-low  { background:#0e4429; color:#3fb950; border:1px solid #3fb950; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; letter-spacing:1px; }
.energy-medium { background:#5a3e00; color:#f0a500; border:1px solid #f0a500; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; letter-spacing:1px; }
.energy-high  { background:#4a0e0e; color:#f85149; border:1px solid #f85149; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; letter-spacing:1px; }

/* Vibe tags */
.vibe-tag {
    display: inline-block;
    background: rgba(168,85,247,0.15);
    color: #c084fc;
    border: 1px solid rgba(168,85,247,0.3);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.82rem;
    margin: 2px 4px 2px 0;
}

/* Track table */
.track-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
.track-table th {
    color: #a855f7;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(168,85,247,0.3);
    text-align: left;
}
.track-table td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); color: #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.track-table tr:hover td { background: rgba(168,85,247,0.07); }
.track-num { color: #64748b; font-size: 0.8rem; width: 30px; }
.track-title { font-weight: 600; }
.track-artist { color: #94a3b8; }
.track-genre { color: #fbbf24; font-size: 0.82rem; }
.track-bpm { color: #64748b; font-size: 0.82rem; }
.track-links a {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    text-decoration: none;
    margin-right: 6px;
}
.spotify-btn { background: rgba(30,215,96,0.15); color: #1ed760; border: 1px solid rgba(30,215,96,0.3); }
.youtube-btn { background: rgba(255,0,0,0.12); color: #ff4444; border: 1px solid rgba(255,0,0,0.25); }

/* Feedback section */
.feedback-section {
    background: rgba(168,85,247,0.07);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
}
.feedback-title { color: #c084fc; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; }

/* Context chip */
.context-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(168,85,247,0.1);
    border: 1px solid rgba(168,85,247,0.25);
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 0.8rem;
    color: #c084fc;
    margin-bottom: 0.5rem;
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
ENERGY_BADGE = {
    "low":    '<span class="energy-low">⬇ LOW</span>',
    "medium": '<span class="energy-medium">⚡ MEDIUM</span>',
    "high":   '<span class="energy-high">🔥 HIGH</span>',
}


def _track_table_html(tracks: list[Track]) -> str:
    rows = []
    for i, t in enumerate(tracks, 1):
        spotify = (
            f'<a href="{html.escape(t.spotify_search_url)}" target="_blank" class="track-links spotify-btn">Spotify</a>'
            if t.spotify_search_url else ""
        )
        youtube = (
            f'<a href="{html.escape(t.youtube_search_url)}" target="_blank" class="track-links youtube-btn">YouTube</a>'
            if t.youtube_search_url else ""
        )
        rows.append(f"""
        <tr>
          <td class="track-num">{i}</td>
          <td class="track-title">{html.escape(t.title)}</td>
          <td class="track-artist">{html.escape(t.artist)}</td>
          <td class="track-genre">{html.escape(t.genre)}</td>
          <td class="track-bpm">{t.bpm or "—"}</td>
          <td>{spotify}{youtube}</td>
        </tr>""")
    return f"""
    <table class="track-table">
      <thead><tr>
        <th>#</th><th>Title</th><th>Artist</th><th>Genre</th><th>BPM</th><th>Links</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>"""


def _vibe_tags_html(tags: list[str]) -> str:
    return "".join(f'<span class="vibe-tag">#{html.escape(t)}</span>' for t in tags)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Options")
    model = st.selectbox(
        "LLM Model",
        ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
        index=0,
    )
    context_extra = st.text_input(
        "Extra context",
        placeholder="e.g. studying, gym, road trip…",
    )
    use_crew = st.toggle("Multi-agent mode (--crew)", value=False)
    skip_spotify = st.toggle("Skip Spotify enrichment", value=False)

    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
- Describe your mood in plain English
- Optionally pin a seed track as a vibe anchor
- MoodTunes crafts a 10-track playlist using Groq (free)
- Rate tracks to teach it your taste over time
""")
    st.markdown("---")
    st.caption("Powered by [Groq](https://console.groq.com) · [LangChain](https://langchain.com) · [Streamlit](https://streamlit.io)")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="moodtunes-header">
  <div class="moodtunes-title">🎵 MoodTunes</div>
  <div class="moodtunes-sub">Describe your vibe. Get a hand-curated 10-track playlist in seconds.</div>
</div>
""", unsafe_allow_html=True)

# ── Input form ───────────────────────────────────────────────────────────────
col_mood, col_seed = st.columns([3, 2])

with col_mood:
    mood = st.text_area(
        "How are you feeling?",
        placeholder="e.g.  late night drive, city lights, windows down…\n       post-workout cool down\n       rainy Sunday morning with coffee",
        height=110,
        label_visibility="visible",
    )

with col_seed:
    seed = st.text_input(
        "🎯 Seed track (optional)",
        placeholder="e.g. Blinding Lights by The Weeknd",
    )
    st.caption("The playlist will match this song's energy and era.")

generate_btn = st.button("✨ Generate Playlist", type="primary", use_container_width=True, disabled=not mood.strip())

# ── Generation ───────────────────────────────────────────────────────────────
if generate_btn and mood.strip():
    with st.spinner("MoodTunes is curating your playlist…"):
        try:
            if use_crew:
                from mood_playlist_agent.crew_agent import generate_playlist_with_crew
                playlist = generate_playlist_with_crew(mood, context_extra, seed=seed)
            else:
                playlist = generate_playlist(
                    mood, context_extra,
                    model=model,
                    spotify_enrich=not skip_spotify,
                    seed=seed,
                )
            st.session_state["playlist"] = playlist
            st.session_state["feedback_submitted"] = False
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            st.stop()

# ── Results ──────────────────────────────────────────────────────────────────
if "playlist" in st.session_state:
    pl = st.session_state["playlist"]
    energy_badge = ENERGY_BADGE.get(pl.energy_level, pl.energy_level.upper())
    vibe_html = _vibe_tags_html(pl.vibe_tags)

    st.markdown("---")

    # Playlist header card
    st.markdown(f"""
    <div class="playlist-card">
      <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
        <div class="playlist-name">{html.escape(pl.name)}</div>
        {energy_badge}
      </div>
      <div class="playlist-summary">{html.escape(pl.mood_summary)}</div>
      <div>{vibe_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # Genres row
    genres_str = " · ".join(pl.genres)
    st.caption(f"Genres: {genres_str}")

    # Track table
    st.markdown(_track_table_html(pl.tracks), unsafe_allow_html=True)

    # ── Feedback ─────────────────────────────────────────────────────────────
    st.markdown("---")
    if not st.session_state.get("feedback_submitted"):
        st.markdown('<div class="feedback-title">📊 Rate this playlist — teach MoodTunes your taste</div>', unsafe_allow_html=True)

        track_labels = [f"{i+1}. {t.title} — {t.artist}" for i, t in enumerate(pl.tracks)]

        fb_col1, fb_col2 = st.columns(2)
        with fb_col1:
            loved_selected = st.multiselect(
                "♥ Loved these tracks",
                options=track_labels,
                placeholder="Select tracks you loved…",
            )
        with fb_col2:
            disliked_selected = st.multiselect(
                "✕ Never play these again",
                options=[t for t in track_labels if t not in loved_selected],
                placeholder="Select tracks to skip…",
            )

        if st.button("💾 Save Feedback", disabled=not (loved_selected or disliked_selected)):
            loved = [pl.tracks[track_labels.index(t)].model_dump() for t in loved_selected]
            disliked = [pl.tracks[track_labels.index(t)].model_dump() for t in disliked_selected]
            save_feedback(loved, disliked)
            st.session_state["feedback_submitted"] = True
            st.rerun()
    else:
        st.success("✅ Feedback saved! Your next playlist will reflect your taste.")
        if st.button("Rate again"):
            st.session_state["feedback_submitted"] = False
            st.rerun()

    # ── Share / rerun ─────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🔄 Generate another playlist", use_container_width=True):
        del st.session_state["playlist"]
        st.session_state.pop("feedback_submitted", None)
        st.rerun()
