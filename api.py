"""FastAPI backend — exposes VibeForge pipeline over HTTP/SSE."""

from __future__ import annotations

import json
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

from mood_playlist_agent.utils import DEFAULT_MODEL, AVAILABLE_MODELS

app = FastAPI(title="VibeForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    mood: str
    context: str = ""
    seed: str = ""
    model: str = DEFAULT_MODEL
    mode: str = "fast"          # "fast" | "deep" | "agentic"
    spotify_enrich: bool = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/models")
def list_models() -> list[str]:
    return AVAILABLE_MODELS


@app.post("/generate")
def generate(req: GenerateRequest) -> dict:
    """Fast and Deep modes — returns the full playlist as JSON."""
    if req.mode == "deep":
        from mood_playlist_agent.crew_agent import generate_playlist_with_crew
        playlist = generate_playlist_with_crew(
            req.mood, req.context, seed=req.seed,
            model=req.model, spotify_enrich=req.spotify_enrich,
        )
    else:
        from mood_playlist_agent.playlist_agent import generate_playlist
        playlist = generate_playlist(
            req.mood, req.context,
            model=req.model, spotify_enrich=req.spotify_enrich, seed=req.seed,
        )
    return playlist.model_dump()


@app.get("/stream")
def stream(
    mood: Annotated[str, Query()],
    context: Annotated[str, Query()] = "",
    seed: Annotated[str, Query()] = "",
    model: Annotated[str, Query()] = DEFAULT_MODEL,
    spotify_enrich: Annotated[bool, Query()] = True,
) -> StreamingResponse:
    """Agentic mode — streams SSE events, one per graph node."""
    from mood_playlist_agent.graph_agent import stream_playlist_with_graph

    def event_generator():
        try:
            for node_name, state in stream_playlist_with_graph(
                mood, context, seed=seed, model=model, spotify_enrich=spotify_enrich,
            ):
                payload: dict = {"node": node_name}

                if node_name == "analyse_mood" and state.get("mood_analysis"):
                    ma = state["mood_analysis"]
                    payload["data"] = {
                        "emotion": ma.primary_emotion,
                        "energy": ma.energy_level,
                        "bpm_range": ma.bpm_range,
                        "occasion": ma.occasion,
                    }
                elif node_name == "critique_playlist" and state.get("critique"):
                    c = state["critique"]
                    payload["data"] = {"score": c.score, "feedback": c.feedback}
                elif node_name == "curate_playlist":
                    payload["data"] = {"attempt": state.get("refinement_attempts", 0)}
                elif node_name == "finalise" and state.get("playlist"):
                    payload["data"] = state["playlist"].model_dump()

                yield f"data: {json.dumps(payload)}\n\n"

            yield "data: {\"node\": \"done\"}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'node': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
