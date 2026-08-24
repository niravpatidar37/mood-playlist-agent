"""Application service contract tests that do not call external providers."""

import pytest
from pydantic import ValidationError

from mood_playlist_agent.application import GenerationRequest
from mood_playlist_agent.memory import _compact_sections
from mood_playlist_agent.utils import count_tokens, ensure_context_budget


def test_generation_request_normalizes_user_input():
    request = GenerationRequest(
        mood="  late night drive  ",
        context=" rainy city ",
        seed="  Blinding Lights  ",
    ).normalized()

    assert request.mood == "late night drive"
    assert request.context == "rainy city"
    assert request.seed == "Blinding Lights"


def test_generation_request_rejects_blank_mood():
    with pytest.raises(ValueError, match="non-whitespace"):
        GenerationRequest(mood="   ").normalized()


def test_generation_request_rejects_unknown_model():
    with pytest.raises(ValueError, match="model must be one of"):
        GenerationRequest(mood="focus", model="unknown-model").normalized()


def test_generation_request_rejects_unknown_mode():
    with pytest.raises(ValidationError):
        GenerationRequest(mood="focus", mode="experimental")


def test_count_tokens_uses_model_tokenizer_when_available():
    class Tokenizer:
        def encode(self, text, add_special_tokens=False):
            return text.split()

    assert count_tokens(Tokenizer(), "one two three") == 3


def test_context_budget_reserves_output_tokens():
    with pytest.raises(ValueError, match="Prompt is too large"):
        ensure_context_budget([type("Message", (), {"content": "x" * 400})()], context_limit=100, requested_output=20)


def test_preference_sections_are_compacted():
    result = _compact_sections(["loved tracks", "recent history", "disliked tracks"], max_chars=20)
    assert len(result) <= 20
    assert result.startswith("loved tracks")


def test_agentic_pipeline_allows_two_refinements():
    from mood_playlist_agent.graph_agent import PlaylistCritique, _route_after_critique

    critique = PlaylistCritique(score=5, issues=["needs work"], feedback="Improve it")
    base = {"critique": critique, "refinement_attempts": 0}

    assert _route_after_critique(base) == "refine"
    assert _route_after_critique({**base, "refinement_attempts": 1}) == "refine"
    assert _route_after_critique({**base, "refinement_attempts": 2}) == "finalise"


def test_generation_service_caches_base_playlist(monkeypatch):
    from mood_playlist_agent.application import GenerationService
    from tests.test_models import make_playlist

    service = GenerationService()
    playlist = make_playlist()
    calls = 0

    def generate(_request):
        nonlocal calls
        calls += 1
        return playlist

    monkeypatch.setattr(service, "_generate_uncached", generate)
    request = GenerationRequest(mood="focus", spotify_enrich=False)

    first = service.generate(request)
    second = service.generate(request)

    assert calls == 1
    assert first is not second
    assert first.name == second.name


def test_deterministic_playlist_issues_skip_critic_model():
    from mood_playlist_agent.graph_agent import _critique_playlist
    from tests.test_models import make_playlist
    from mood_playlist_agent.models import MoodAnalysis

    playlist = make_playlist()
    for track in playlist.tracks[1:]:
        track.artist = playlist.tracks[0].artist
    analysis = MoodAnalysis(
        primary_emotion="focused",
        secondary_emotions=[],
        energy_level="low",
        bpm_range="60-80",
        recommended_genres=["ambient"],
        avoid_genres=[],
        time_of_day_context="evening",
        activity_context="reading",
        musical_key_feel="minor",
    )

    result = _critique_playlist({"playlist": playlist, "mood_input": "reading", "mood_analysis": analysis})

    assert result["critique"].score == 5
    assert "Artist diversity" in result["critique"].issues[0]