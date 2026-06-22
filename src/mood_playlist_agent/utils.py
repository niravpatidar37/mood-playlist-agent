"""Shared utilities used across agents."""

import re


def strip_fences(raw: str) -> str:
    """Extract JSON from a markdown code fence, handling optional language tags and extra content."""
    raw = raw.strip()
    match = re.search(r"```(?:\w+)?\n?(.*?)```", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw
