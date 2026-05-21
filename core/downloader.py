from __future__ import annotations
import os
import yt_dlp
from pathlib import Path
from typing import Callable, Optional

# ── Quality preset mappings

VIDEO_QUALITY_MAP: dict[str, str] = {
    "best": "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "240p": "bestvideo[height<=240]+bestaudio/best[height<=240]",
    "144p": "bestvideo[height<=144]+bestaudio/best[height<=144]",
}

AUDIO_QUALITY_MAP: dict[str, str] = {
    "320": "320",
    "192": "192",
    "128": "128",
}


# ── Information fetching


def fetch_info(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        raw = ydl.extract_info(url, download=False)

    return {
        "title": raw.get("title", "Unknown"),
        "uploader": raw.get("uploader", "Unknown"),
        "duration": raw.get("duration", 0),
        "view_count": raw.get("view_count", 0),
        "thumbnail": raw.get("thumbnail", ""),
        "upload_date": raw.get("upload_date", ""),
        "description": (raw.get("description") or "")[:300],
        "webpage_url": raw.get("webpage_url", url),
    }


# ── Audio


def download_audio(
    url: str,
    output_dir: str | Path = "downloads",
    bitrate: str = "192",
    progress_hook: Optional[Callable[[dict], None]] = None,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    hooks = [progress_hook] if progress_hook else []
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": AUDIO_QUALITY_MAP.get(bitrate, "192"),
            }
        ],
        "progress_hooks": hooks,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "audio")

    # Locating the mp3 file
    for f in output_dir.iterdir():
        if f.suffix == ".mp3" and _title_match(title, f.stem):
            return f

    mp3s = sorted(
        output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if mp3s:
        return mp3s[0]

    raise FileNotFoundError(f"Downloaded MP3 not found in {output_dir}")


# ── Video


def download_video(
    url: str,
    output_dir: str | Path = "downloads",
    quality: str = "best",
    progress_hook: Optional[Callable[[dict], None]] = None,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    hooks = [progress_hook] if progress_hook else []
    fmt = VIDEO_QUALITY_MAP.get(quality.lower(), VIDEO_QUALITY_MAP["best"])
    ydl_opts = {
        "format": fmt,
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "progress_hooks": hooks,
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {"player_client": ["web", "android"]},
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")

    for f in output_dir.iterdir():
        if f.suffix == ".mp4" and _title_match(title, f.stem):
            return f

    mp4s = sorted(
        output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if mp4s:
        return mp4s[0]

    raise FileNotFoundError(f"Downloaded MP4 not found in {output_dir}")


def _title_match(title: str, stem: str) -> bool:
    sanitized = "".join(c for c in title if c.isalnum() or c in " _-")[:20].lower()
    return sanitized[:10] in stem.lower()


def format_duration(seconds: int) -> str:
    if not seconds:
        return "—"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_views(views: int) -> str:
    if not views:
        return "—"
    if views >= 1_000_000:
        return f"{views/1_000_000:.1f}M"
    if views >= 1_000:
        return f"{views/1_000:.1f}K"
    return str(views)
