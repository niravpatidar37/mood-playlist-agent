# ⚡ VibeForge — AI Mood-Based Playlist Generator

> Your mood. Forged into sound.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![uv](https://img.shields.io/badge/managed%20by-uv-purple)](https://github.com/astral-sh/uv)
[![LLM: Groq](https://img.shields.io/badge/LLM-Groq%20%28free%29-orange)](https://console.groq.com)
[![LangGraph](https://img.shields.io/badge/agentic-LangGraph-blueviolet)](https://langchain-ai.github.io/langgraph/)

```
$ vibeforge --mood "late night lo-fi study session" --agentic

  Mood Analyst  →  Music Curator  →  Critic (8/10 ✓)  →  Finalise

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
| **Session memory** | Learns your genre preferences and skips recently heard tracks |
| **Multi-language** | Bollywood, K-pop, Latin, Afrobeats, and more |
| **Web UI** | Streamlit app with per-track feedback |
| **Three generation modes** | Fast · Deep (two-stage) · Agentic (LangGraph + self-correction) |
| **100% free to run** | Groq free tier — no credit card needed |

---

## 🏗️ Architecture

VibeForge offers three generation modes, each progressively more agentic:

### Mode 1 — Fast (single LangChain agent)
```
Context + Memory → Groq LLM → Playlist
```

### Mode 2 — Deep (`--deep`, two-stage LangChain)
```
Mood Analyst → Music Curator → Playlist
```

### Mode 3 — Agentic (`--agentic`, LangGraph state machine)

The flagship mode. A stateful graph with a self-correcting Critic loop:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LangGraph State Machine                          │
│                                                                         │
│   ┌──────────────┐    ┌───────────────┐    ┌─────────────────────┐     │
│   │ Mood Analyst │───▶│ Music Curator │───▶│  Playlist Critic    │     │
│   │              │    │               │    │  score 1-10         │     │
│   │ primary mood │    │ 10 tracks     │    │  genre diversity    │     │
│   │ BPM range    │    │ BPM clamped   │    │  artist diversity   │     │
│   │ energy level │    │ quality mix   │    │  mood coherence     │     │
│   └──────────────┘    └───────────────┘    └────────┬────────────┘     │
│                               ▲                     │                  │
│                               │   score < 7         │ score ≥ 7        │
│                               │   (max 2 retries)   ▼                  │
│                               └──────────────  Finalise ──▶ END        │
│                                                                         │
│   Shared state flows through every node:                                │
│   mood_input · context · memory · mood_analysis · playlist · critique   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                ▼
            Spotify Enrichment  Save Session    Rich UI / Streamlit
            (parallel, 5 threads)  (memory.json)
```

**What makes it agentic:**
- **Stateful graph** — all agents share a typed `AgentState` object passed through every node
- **Autonomous routing** — the graph decides whether to refine or accept based on the Critic's score
- **Self-correction loop** — if score < 7, the Critic's feedback is injected into the next Curator call (up to 2 refinements)
- **Specialised roles** — Mood Analyst (temperature 0.7), Curator (0.8), Critic (0.3, deterministic)
- **Persistent memory** — learned preferences feed into every generation cycle

---

## 🌐 Web UI (Streamlit)

```bash
uv run streamlit run streamlit_app.py
# → opens http://localhost:8501
```

Select generation mode from the sidebar: **Fast** / **Deep** / **Agentic (LangGraph + Critic)**. Per-track ♥ / ✕ feedback is saved to `~/.vibeforge/memory.json` and shapes future playlists.

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

### Two-stage deep analysis
```bash
vibeforge --mood "heartbreak, raining outside" --deep
```

### Full agentic mode (LangGraph + self-correcting Critic)
```bash
vibeforge --mood "heartbreak, raining outside" --agentic
```

### All options
```
Options:
  --mood      -m   TEXT   Mood/activity description (skips prompt)
  --context   -c   TEXT   Extra context e.g. 'rainy day, studying'
  --seed      -s   TEXT   Seed track as vibe anchor e.g. 'Blinding Lights by The Weeknd'
  --deep           FLAG   Two-stage mode: Mood Analyst → Music Curator
  --agentic        FLAG   LangGraph mode: Mood Analyst → Curator → Critic → refine
  --model          TEXT   LLM model override  [default: llama-3.3-70b-versatile]
  --no-spotify     FLAG   Skip Spotify link enrichment
  --no-feedback    FLAG   Skip post-playlist feedback prompt
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
│   ├── main.py            # CLI (Typer) — --mood, --deep, --agentic flags
│   ├── playlist_agent.py  # Mode 1: single LangChain agent
│   ├── crew_agent.py      # Mode 2: two-stage pipeline (--deep)
│   ├── graph_agent.py     # Mode 3: LangGraph state machine (--agentic)
│   ├── models.py          # Pydantic schemas: Track, Playlist, MoodAnalysis
│   ├── context.py         # Time-of-day + live weather context
│   ├── memory.py          # Session preference learning (favorites + freshness)
│   ├── spotify.py         # Spotify API enrichment (parallel, 5 threads)
│   ├── utils.py           # Shared: LLM cache, retry helper, prompt constants
│   └── display.py         # Rich terminal UI
├── tests/
│   ├── test_models.py     # Unit tests (no key needed)
│   └── test_examples.py   # Live integration tests (skipped without key)
├── streamlit_app.py       # Web UI (Fast / Deep / Agentic mode selector)
├── main.py                # Root entry point
├── pyproject.toml         # Dependencies + build config (managed by uv)
├── .env.example           # Environment variable template
└── CONTRIBUTING.md
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## 📄 License

MIT — see [LICENSE](LICENSE).
