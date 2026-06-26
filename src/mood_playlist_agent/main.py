"""CLI entry point — interactive loop and one-shot mode."""

from __future__ import annotations

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

load_dotenv()

from .playlist_agent import generate_playlist
from .display import print_playlist, collect_feedback
from .memory import save_feedback
from .utils import DEFAULT_MODEL

app = typer.Typer(help="VibeForge — AI-powered mood-based playlist generator")
console = Console()


@app.command()
def run(
    mood: str = typer.Option(None, "--mood", "-m", help="Mood/activity description (skips interactive prompt)"),
    context: str = typer.Option("", "--context", "-c", help="Extra context, e.g. 'rainy day, studying'"),
    deep: bool = typer.Option(False, "--deep", help="Use two-stage analysis (Mood Analyst → Music Curator)"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Groq model to use"),
    no_spotify: bool = typer.Option(False, "--no-spotify", help="Skip Spotify enrichment"),
    seed: str = typer.Option("", "--seed", "-s", help="Seed track as vibe anchor, e.g. 'Blinding Lights by The Weeknd'"),
    no_feedback: bool = typer.Option(False, "--no-feedback", help="Skip the post-playlist feedback prompt"),
):
    """Generate a mood-based playlist."""
    if mood:
        _generate_and_display(mood, context, deep, model, not no_spotify, seed, not no_feedback)
    else:
        _interactive_loop(context, deep, model, not no_spotify, seed, not no_feedback)


def _generate_and_display(
    mood: str, context: str, deep: bool, model: str, spotify: bool, seed: str, ask_feedback: bool
) -> None:
    console.print(f"\n[bold magenta]Generating playlist for:[/] [cyan]{mood}[/]\n")
    with console.status("[bold magenta]VibeForge is forging your playlist...[/]"):
        if deep:
            from .crew_agent import generate_playlist_with_crew
            playlist = generate_playlist_with_crew(mood, context, seed=seed, model=model, spotify_enrich=spotify)
        else:
            playlist = generate_playlist(mood, context, model=model, spotify_enrich=spotify, seed=seed)
    print_playlist(playlist)
    if ask_feedback:
        loved, disliked = collect_feedback(playlist)
        if loved or disliked:
            save_feedback(loved, disliked)
            console.print(f"[dim]Saved feedback — {len(loved)} loved, {len(disliked)} disliked.[/]")


def _interactive_loop(context: str, deep: bool, model: str, spotify: bool, seed: str, ask_feedback: bool) -> None:
    console.print(_panel_welcome())
    while True:
        mood = Prompt.ask("\n[bold cyan]How are you feeling? (or 'quit' to exit)[/]")
        if mood.lower() in {"quit", "exit", "q"}:
            console.print("[dim]Goodbye! Keep vibing.[/]")
            break
        if mood.strip():
            _generate_and_display(mood, context, deep, model, spotify, seed, ask_feedback)


def _panel_welcome() -> Panel:
    t = Text()
    t.append("  VibeForge\n", style="bold magenta")
    t.append("  AI-powered mood-based playlist generator\n", style="dim")
    t.append("  Describe your mood or activity and get a personalised playlist.\n", style="italic")
    return Panel(t, border_style="magenta")
