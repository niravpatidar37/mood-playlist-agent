"""Rich terminal display for playlists."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .models import Playlist

console = Console()

ENERGY_COLOR = {"low": "cyan", "medium": "yellow", "high": "red"}


def print_playlist(playlist: Playlist) -> None:
    color = ENERGY_COLOR.get(playlist.energy_level, "magenta")

    # Header panel
    header = Text()
    header.append(f"  {playlist.name}\n", style=f"bold {color}")
    header.append(f"  {playlist.mood_summary}\n", style="italic white")
    tags = "  " + "  ".join(f"[{color}]#{t}[/]" for t in playlist.vibe_tags)
    console.print(Panel(header, title="[bold magenta]MoodTunes[/]", border_style=color))
    console.print(tags)
    console.print()

    # Tracks table
    table = Table(box=box.ROUNDED, border_style=color, header_style=f"bold {color}")
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="bold white", min_width=24)
    table.add_column("Artist", style="cyan", min_width=18)
    table.add_column("Genre", style="yellow", min_width=14)
    table.add_column("BPM", style="dim", width=5)
    table.add_column("Links", style="blue")

    for i, track in enumerate(playlist.tracks, 1):
        links = ""
        if track.spotify_search_url:
            links += "[link=" + track.spotify_search_url + "]Spotify[/link]"
        if track.youtube_search_url:
            links += "  [link=" + track.youtube_search_url + "]YT[/link]"
        table.add_row(
            str(i),
            track.title,
            track.artist,
            track.genre,
            str(track.bpm) if track.bpm else "-",
            links,
        )

    console.print(table)
    console.print(f"\n  Genres: [yellow]{', '.join(playlist.genres)}[/]")
    console.print(f"  Energy: [{color}]{playlist.energy_level.upper()}[/]\n")
