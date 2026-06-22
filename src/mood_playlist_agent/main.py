"""CLI entry point — interactive loop and one-shot mode."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.prompt import Prompt

from .playlist_agent import generate_playlist
from .display import print_playlist

app = typer.Typer(help="MoodTunes — AI-powered mood-based playlist generator")
console = Console()


@app.command()
def run(
    mood: str = typer.Option(None, "--mood", "-m", help="Mood/activity description (skips interactive prompt)"),
    context: str = typer.Option("", "--context", "-c", help="Extra context, e.g. 'rainy day, studying'"),
    crew: bool = typer.Option(False, "--crew", help="Use multi-agent CrewAI mode"),
    model: str = typer.Option("llama-3.3-70b-versatile", "--model", help="Groq model to use"),
    no_spotify: bool = typer.Option(False, "--no-spotify", help="Skip Spotify enrichment"),
):
    """Generate a mood-based playlist."""
    if mood:
        _generate_and_display(mood, context, crew, model, not no_spotify)
    else:
        _interactive_loop(context, crew, model, not no_spotify)


def _generate_and_display(mood: str, context: str, crew: bool, model: str, spotify: bool) -> None:
    console.print(f"\n[bold magenta]Generating playlist for:[/] [cyan]{mood}[/]\n")
    with console.status("[bold magenta]MoodTunes is curating your playlist...[/]"):
        if crew:
            from .crew_agent import generate_playlist_with_crew
            playlist = generate_playlist_with_crew(mood, context)
        else:
            playlist = generate_playlist(mood, context, model=model, spotify_enrich=spotify)
    print_playlist(playlist)


def _interactive_loop(context: str, crew: bool, model: str, spotify: bool) -> None:
    console.print(Panel_welcome())
    while True:
        mood = Prompt.ask("\n[bold cyan]How are you feeling? (or 'quit' to exit)[/]")
        if mood.lower() in {"quit", "exit", "q"}:
            console.print("[dim]Goodbye! Keep vibing.[/]")
            break
        if mood.strip():
            _generate_and_display(mood, context, crew, model, spotify)


def Panel_welcome():
    from rich.panel import Panel
    from rich.text import Text
    t = Text()
    t.append("  MoodTunes\n", style="bold magenta")
    t.append("  AI-powered mood-based playlist generator\n", style="dim")
    t.append("  Describe your mood or activity and get a personalised playlist.\n", style="italic")
    return Panel(t, border_style="magenta")
