from __future__ import annotations
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()


def banner():
    t = Text()
    t.append("  YouTube ", style="bold cyan")
    t.append(" Downloader ", style="bold cyan")
    t.append(" (Rich CLI) ", style="bold red")
    t.append("  ·  v1.0  ·  Developed By ShakalBhau0001", style="dim")
    console.print(Panel(Align.center(t), border_style="dim red", padding=(0, 4)), "")


def info_table(info: dict):
    dur = info.get("duration", 0)
    m, s = divmod(int(dur), 60)
    tbl = Table(box=box.SIMPLE_HEAD, show_header=False, padding=(0, 2), min_width=50)
    tbl.add_column("key", style="dim", width=14)
    tbl.add_column("val", style="bold white")
    tbl.add_row("Title", info.get("title", "—")[:68])
    tbl.add_row("Uploader", info.get("uploader", "—"))
    tbl.add_row("Duration", f"{m}:{s:02d}")
    tbl.add_row("Views", info.get("views_fmt", "—"))
    tbl.add_row("Date", _fmt_date(info.get("upload_date", "")))
    console.print(
        Panel(tbl, title="[bold yellow]Video Info[/bold yellow]", border_style="dim yellow")
    )


def _fmt_date(d: str) -> str:
    if len(d) == 8:
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return d or "—"


def ok(msg: str):
    console.print(f"\n[bold green]✓[/bold green]  {msg}\n")


def err(msg: str):
    console.print(f"\n[bold red]✗[/bold red]  {msg}\n")


def info(msg: str):
    console.print(f"[dim]{msg}[/dim]")
