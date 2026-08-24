"""Application service shared by HTTP, CLI, and UI adapters."""

from __future__ import annotations

import copy
import json
import threading
import time
from collections.abc import Generator
from typing import Any, Literal

from pydantic import BaseModel, Field

from .models import Playlist, Track
from .spotify import enrich_tracks_with_spotify
from .utils import AVAILABLE_MODELS, DEFAULT_MODEL

GenerationMode = Literal["fast", "deep", "agentic"]
CACHE_TTL_SECONDS = 900


class GenerationRequest(BaseModel):
    """Validated input accepted by every presentation adapter."""

    mood: str = Field(min_length=1, max_length=500)
    context: str = Field(default="", max_length=500)
    seed: str = Field(default="", max_length=200)
    model: str = DEFAULT_MODEL
    mode: GenerationMode = "fast"
    spotify_enrich: bool = True

    def normalized(self) -> "GenerationRequest":
        values = self.model_dump()
        values["mood"] = self.mood.strip()
        values["context"] = self.context.strip()
        values["seed"] = self.seed.strip()
        if not values["mood"]:
            raise ValueError("mood must contain non-whitespace characters")
        if self.model not in AVAILABLE_MODELS:
            raise ValueError(f"model must be one of: {', '.join(AVAILABLE_MODELS)}")
        return type(self)(**values)


class GenerationService:
    """Owns generation policy while adapters remain transport-specific."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, Playlist]] = {}
        self._cache_lock = threading.Lock()

    def _cache_key(self, request: GenerationRequest) -> str:
        return json.dumps(request.model_dump(exclude={"spotify_enrich"}), sort_keys=True)

    def generate(self, request: GenerationRequest, defer_enrichment: bool = False) -> Playlist:
        request = request.normalized()
        cache_key = self._cache_key(request)
        now = time.monotonic()
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < CACHE_TTL_SECONDS:
                playlist = copy.deepcopy(cached[1])
            else:
                self._cache.pop(cache_key, None)
                playlist = None
        if playlist is None:
            pipeline_request = request.model_copy(update={"spotify_enrich": False})
            playlist = self._generate_uncached(pipeline_request)
            with self._cache_lock:
                self._cache[cache_key] = (time.monotonic(), copy.deepcopy(playlist))
        if request.spotify_enrich and not defer_enrichment:
            playlist = self.enrich(playlist)
        return playlist

    def _generate_uncached(self, request: GenerationRequest) -> Playlist:
        if request.mode == "agentic":
            from .graph_agent import generate_playlist_with_graph
            return generate_playlist_with_graph(request.mood, request.context, seed=request.seed, model=request.model, spotify_enrich=request.spotify_enrich)
        if request.mode == "deep":
            from .crew_agent import generate_playlist_with_crew
            return generate_playlist_with_crew(request.mood, request.context, seed=request.seed, model=request.model, spotify_enrich=request.spotify_enrich)
        from .playlist_agent import generate_playlist
        return generate_playlist(request.mood, request.context, model=request.model, spotify_enrich=request.spotify_enrich, seed=request.seed)

    def enrich(self, playlist: Playlist) -> Playlist:
        enriched = enrich_tracks_with_spotify([track.model_dump() for track in playlist.tracks])
        playlist.tracks = [Track(**track) for track in enriched]
        return playlist

    def stream(self, request: GenerationRequest) -> Generator[tuple[str, dict[str, Any]], None, None]:
        request = request.normalized()
        if request.mode != "agentic":
            raise ValueError("streaming is only supported for agentic generation")
        from .graph_agent import stream_playlist_with_graph
        yield from stream_playlist_with_graph(request.mood, request.context, seed=request.seed, model=request.model, spotify_enrich=False)


generation_service = GenerationService()