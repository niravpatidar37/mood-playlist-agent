"""Gathers runtime context: time of day, optional weather."""

import os
from datetime import datetime

import requests


def get_time_of_day() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "late night"


def get_weather(city: str | None = None) -> str:
    """Return a short weather description, or empty string on failure."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = city or os.getenv("OPENWEATHER_CITY", "")
    if not api_key or not city:
        return ""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={"q": city, "appid": api_key, "units": "metric"}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{desc}, {temp:.0f}°C in {city}"
    except Exception:
        return ""


def build_context_string(extra: str = "") -> str:
    parts = [f"Time of day: {get_time_of_day()}"]
    weather = get_weather()
    if weather:
        parts.append(f"Weather: {weather}")
    if extra:
        parts.append(f"Additional context: {extra}")
    return "\n".join(parts)
