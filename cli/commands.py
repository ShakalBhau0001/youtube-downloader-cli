from __future__ import annotations
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from .display import banner, info_table, ok, err, info
from core.downloader import fetch_info, download_audio, download_video, format_views

console = Console()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _make_progress():
    return Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=None, complete_style="red", finished_style="bold green"),
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytdl",
        description="YouTube Downloader CLI — audio & video via yt-dlp - Developed By ShakalBhau0001",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("url", nargs="?", help="YouTube URL to download")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["audio", "video"],
        default="audio",
        help="Download mode: audio (MP3) or video (MP4)  [default: audio]",
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=["best", "1080p", "720p", "480p", "360p", "240p", "144p"],
        default="best",
        help="Video quality  [default: best]  (only for --mode video)",
    )
    parser.add_argument(
        "-b",
        "--bitrate",
        choices=["320", "192", "128"],
        default="192",
        help="Audio bitrate kbps  [default: 192]  (only for --mode audio)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="downloads",
        help="Output directory  [default: downloads/]",
    )
    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Only fetch and display video info, do not download",
    )
    return parser


def run_args(args: argparse.Namespace):
    banner()

    # ── Information only
    if args.info:
        with console.status("[bold cyan]Fetching video info…[/]"):
            try:
                raw = fetch_info(args.url)
                raw["views_fmt"] = format_views(raw.get("view_count", 0))
                info_table(raw)
            except Exception as e:
                err(str(e))
                sys.exit(1)
        return

    # ── Audio
    if args.mode == "audio":
        info(
            f"Mode: Audio MP3  ·  Bitrate: {args.bitrate} kbps  ·  Output: {args.output}/"
        )
        with _make_progress() as progress:
            task = progress.add_task("Downloading audio  ", total=100)
            try:
                path = download_audio(
                    url=args.url,
                    output_dir=args.output,
                    bitrate=args.bitrate,
                    progress_hook=_progress_hook_factory(progress, task),
                )
                ok(f"Audio saved → {Path(path).name}   [{args.output}/]")
            except Exception as e:
                err(str(e))
                sys.exit(1)

    # ── Video
    else:
        info(f"Mode: Video MP4  ·  Quality: {args.quality}  ·  Output: {args.output}/")
        with _make_progress() as progress:
            task = progress.add_task("Downloading video  ", total=100)
            try:
                path = download_video(
                    url=args.url,
                    output_dir=args.output,
                    quality=args.quality,
                    progress_hook=_progress_hook_factory(progress, task),
                )
                ok(f"Video saved → {Path(path).name}   [{args.output}/]")
            except Exception as e:
                err(str(e))
                sys.exit(1)
