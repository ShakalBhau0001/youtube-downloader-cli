from __future__ import annotations
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from .display import banner, info_table, ok, err, info
from core.downloader import fetch_info, download_audio, download_video, format_views

console = Console()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Quality mappings

AUDIO_QUALITY = {
    "1": ("320 kbps", "320"),
    "2": ("192 kbps", "192"),
    "3": ("128 kbps", "128"),
}

VIDEO_QUALITY = {
    "1": ("Best Available", "best"),
    "2": ("1080p Full HD", "1080p"),
    "3": ("720p HD", "720p"),
    "4": ("480p", "480p"),
    "5": ("360p", "360p"),
    "6": ("240p", "240p"),
    "7": ("144p", "144p"),
}


def _make_progress():
    return Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(
            bar_width=None, complete_style="red", finished_style="bold green"
        ),
        "[progress.percentage]{task.percentage:>5.1f}%",
        TimeRemainingColumn(),
        console=console,
    )


def _progress_hook_factory(progress, task_id):
    def hook(d):
        if d["status"] == "downloading":
            pct_s = d.get("_percent_str", "0%").strip().replace("%", "")
            try:
                progress.update(task_id, completed=float(pct_s))
            except ValueError:
                pass
        elif d["status"] == "finished":
            progress.update(task_id, completed=100)
    return hook


# ── Interactive flow


def run_interactive():
    banner()

    # URL input
    url = Prompt.ask("[bold white]Enter YouTube URL[/]").strip()
    if not url:
        err("No URL provided — exiting.")
        sys.exit(1)

    # Fetching information
    with console.status("[bold cyan]Fetching video info…[/]"):
        try:
            raw = fetch_info(url)
            raw["views_fmt"] = format_views(raw.get("view_count", 0))
            info_table(raw)
        except Exception as e:
            console.print(f"[dim]Could not fetch info: {e}[/dim]\n")

    # Mode
    console.print("[bold white]Download mode:[/]")
    console.print("  [bold cyan]1[/bold cyan]  →  🎵  Audio (MP3)")
    console.print("  [bold cyan]2[/bold cyan]  →  🎬  Video (MP4)")
    mode_choice = Prompt.ask("Choose", choices=["1", "2"], default="1")
    output = Prompt.ask("[bold white]Output folder[/]", default="downloads")

    # ── Audio
    if mode_choice == "1":
        console.print("\n[bold white]Audio bitrate:[/]")
        for k, (label, _) in AUDIO_QUALITY.items():
            console.print(f"  [bold yellow]{k}[/bold yellow]  →  {label}")
        q_choice = Prompt.ask("Choose", choices=list(AUDIO_QUALITY.keys()), default="2")
        _, bitrate = AUDIO_QUALITY[q_choice]

        with _make_progress() as progress:
            task = progress.add_task("Downloading audio  ", total=100)
            try:
                path = download_audio(
                    url=url,
                    output_dir=output,
                    bitrate=bitrate,
                    progress_hook=_progress_hook_factory(progress, task),
                )
                ok(f"Audio saved → {Path(path).name}   [{output}/]")
            except Exception as e:
                err(str(e))

    # ── Video
    else:
        console.print("\n[bold white]Video quality:[/]")
        for k, (label, _) in VIDEO_QUALITY.items():
            console.print(f"  [bold yellow]{k}[/bold yellow]  →  {label}")
        q_choice = Prompt.ask("Choose", choices=list(VIDEO_QUALITY.keys()), default="3")
        _, quality = VIDEO_QUALITY[q_choice]

        with _make_progress() as progress:
            task = progress.add_task("Downloading video  ", total=100)
            try:
                path = download_video(
                    url=url,
                    output_dir=output,
                    quality=quality,
                    progress_hook=_progress_hook_factory(progress, task),
                )
                ok(f"Video saved → {Path(path).name}   [{output}/]")
            except Exception as e:
                err(str(e))
