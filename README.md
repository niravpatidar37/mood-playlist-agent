# ⚡ VibeForge — AI Mood-Based Playlist Generator

> Your mood. Forged into sound.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![uv](https://img.shields.io/badge/managed%20by-uv-purple)](https://github.com/astral-sh/uv)
[![LLM: Groq](https://img.shields.io/badge/LLM-Groq%20%28free%29-orange)](https://console.groq.com)

```
$ vibeforge --mood "late night lo-fi study session"

╭──────────────────────────── VibeForge ─────────────────────────────╮
│  Late Night Focus                                                   │
│  Relaxing and concentrated atmosphere for a late night study session│
╰─────────────────────────────────────────────────────────────────────╯
  #lo-fi  #chill  #study

╭────┬─────────────────────────┬──────────────────┬───────────┬───────┬─────────────╮
│ #  │ Title                   │ Artist           │ Genre     │ BPM   │ Links       │
├────┼─────────────────────────┼──────────────────┼───────────┼───────┼─────────────┤
│ 1  │ Rainy Night             │ Jinsang          │ lo-fi     │ 90    │ Spotify  YT │
│ 2  │ Aruarian Dance          │ Nujabes          │ lo-fi     │ 95    │ Spotify  YT │
│ 3  │ Weightless              │ Marconi Union    │ ambient   │ 50    │ Spotify  YT │
│ …  │ …                       │ …                │ …         │ …     │ …           │
╰────┴─────────────────────────┴──────────────────┴───────────┴───────┴─────────────╯

  Genres: lo-fi hip hop, electronic, instrumental   Energy: LOW
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Natural language input** | Any mood, activity, or vibe description |
| **10 curated tracks** | Title, artist, genre, BPM — every time |
| **Clickable links** | Spotify search + YouTube for every track |
| **Context-aware** | Factors in time of day and live weather |
| **Session memory** | Learns your genre preferences over time |
| **Multi-language** | Bollywood, K-pop, Latin, Afrobeats, and more |
| **Web UI** | Streamlit app with clickable links and per-track feedback |
| **Single or multi-agent** | LangChain (fast) or two-stage (deep analysis) |
| **100% free to run** | Groq free tier — no credit card needed |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                     CLI  (Typer)                    │
│         --mood "..."   or   interactive loop        │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │   Context Builder     │  time-of-day + weather (OpenWeatherMap)
        └───────────┬───────────┘
                    │
     ┌──────────────▼──────────────┐
     │      Memory (JSON)          │  top genres/artists from past sessions
     └──────────────┬──────────────┘
                    │
        ┌───────────▼────────────────────────────────┐
        │          LangChain Agent                   │
        │  SystemPrompt + mood + context + memory    │
        │  → Groq (llama-3.3-70b) → JSON Playlist   │
        └───────────┬────────────────────────────────┘
                    │  optional
        ┌───────────▼───────────┐
        │  two-stage (--deep flag) │  Mood Analyst → Music Curator
        └───────────┬───────────┘
                    │  optional
        ┌───────────▼───────────┐
        │   Spotify Enrichment  │  real track URLs via Spotify API
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │    Rich Terminal UI   │  energy-colored table + clickable links
        └───────────────────────┘
```

---

## 🌐 Web UI (Streamlit)

```bash
uv run streamlit run streamlit_app.py
# → opens http://localhost:8501
```

Features: mood input, seed track anchor, Spotify/YouTube links, per-track feedback (♥ / ✕) to teach VibeForge your taste over time.

---

## 🚀 Quick Start

**Prerequisites:** Python 3.11+, [uv](https://github.com/astral-sh/uv)

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/vibeforge.git
cd vibeforge
uv sync

# 2. Add your free Groq API key (console.groq.com — no credit card needed)
cp .env.example .env
# Edit .env and set GROQ_API_KEY=gsk_...

# 3. Run
vibeforge --mood "sunny highway road trip, windows down"
```

---

## 🎛️ Usage

### One-shot mode
```bash
vibeforge --mood "rainy day jazz, working from home"
vibeforge --mood "post-workout cool down"
vibeforge --mood "desi wedding vibes"
vibeforge --mood "3am can't sleep, anxious thoughts"
```

### Interactive loop
```bash
vibeforge
# → prompts you for mood on each loop, type 'quit' to exit
```

### Multi-agent mode (two-stage)
```bash
vibeforge --mood "heartbreak, raining outside" --deep
```

### All options
```
Options:
  --mood    -m   TEXT   Mood/activity description (skips prompt)
  --context -c   TEXT   Extra context e.g. 'rainy day, studying'
  --seed    -s   TEXT   Seed track as vibe anchor e.g. 'Blinding Lights by The Weeknd'
  --deep         FLAG   Use multi-agent two-stage mode
  --model        TEXT   LLM model override  [default: llama-3.3-70b-versatile]
  --no-spotify   FLAG   Skip Spotify link enrichment
  --no-feedback  FLAG   Skip post-playlist feedback prompt
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your keys:

```env
# Required — free tier at console.groq.com
GROQ_API_KEY=gsk_...

# Optional — real Spotify track URLs (developer.spotify.com)
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...

# Optional — weather-aware recommendations (openweathermap.org)
OPENWEATHER_API_KEY=...
OPENWEATHER_CITY=Mumbai
```

### Supported LLM providers

The default is Groq (free). To switch, change `--model` and the import in `playlist_agent.py`:

| Provider | Package | Free tier |
|---|---|---|
| **Groq** (default) | `langchain-groq` | ✅ Yes |
| Google Gemini | `langchain-google-genai` | ✅ Yes |
| Anthropic Claude | `langchain-anthropic` | 💳 Credits |
| OpenAI | `langchain-openai` | 💳 Credits |

---

## 🧪 Tests

```bash
# Unit tests — no API key needed
uv run pytest tests/test_models.py -v

# Live integration tests — requires GROQ_API_KEY
uv run pytest tests/ -v
```

---

## 📁 Project Structure

```
vibeforge/
├── src/mood_playlist_agent/
│   ├── __init__.py
│   ├── main.py            # CLI (Typer) — interactive + --mood flag
│   ├── playlist_agent.py  # LangChain single-agent
│   ├── crew_agent.py      # Two-stage multi-agent pipeline (--deep)
│   ├── models.py          # Pydantic Track + Playlist schemas
│   ├── context.py         # Time-of-day + live weather
│   ├── memory.py          # Session preference learning (favorites + freshness)
│   ├── spotify.py         # Optional Spotify API enrichment
│   ├── utils.py           # Shared helpers (strip_fences)
│   └── display.py         # Rich terminal UI
├── tests/
│   ├── __init__.py
│   ├── test_models.py     # Unit tests (no key needed)
│   └── test_examples.py   # Live API tests (skipped without key)
├── streamlit_app.py       # Web UI (run with: uv run streamlit run streamlit_app.py)
├── main.py                # Root entry point (CLI)
├── pyproject.toml         # Dependencies + build config (managed by uv)
├── uv.lock                # Locked dependency tree
├── .env.example           # Environment variable template
├── .gitignore
├── CONTRIBUTING.md
└── LICENSE                # MIT
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## 📄 License

MIT — see [LICENSE](LICENSE).
