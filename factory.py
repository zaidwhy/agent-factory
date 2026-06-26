#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import anthropic
from rich.console import Console
from rich.rule import Rule

from agents.base import run_agent
from agents.prompts import (
    ARCHITECT,
    BACKEND_ENGINEER,
    DEBUGGER,
    FRONTEND_ENGINEER,
    IDEA_HUNTER,
    REVIEWER,
)
from agents.tools import TOOL_SCHEMAS

OPUS = "claude-opus-4-8"
SONNET = "claude-sonnet-4-6"

PROJECT_ROOT = Path(__file__).parent
console = Console()


def _make_run_dir(custom: str | None) -> Path:
    if custom:
        p = Path(custom)
        return p if p.is_absolute() else PROJECT_ROOT / p
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    return PROJECT_ROOT / "runs" / stamp


def _launch(
    name: str,
    system: str,
    model: str,
    user_msg: str,
    run_dir: Path,
    client: anthropic.Anthropic,
) -> None:
    run_agent(
        name=name,
        system=system,
        tools=TOOL_SCHEMAS,
        messages=[{"role": "user", "content": user_msg}],
        model=model,
        run_dir=run_dir,
        client=client,
        project_root=PROJECT_ROOT,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="factory.py",
        description="Agent Factory -- runs the 6-agent pipeline to generate a full software project.",
    )
    parser.add_argument(
        "--theme",
        default="",
        metavar="THEME",
        help='Idea theme hint for idea-hunter, e.g. "developer tools"',
    )
    parser.add_argument(
        "--run-dir",
        default=None,
        metavar="DIR",
        help="Custom run folder path (default: runs/YYYY-MM-DD_HHMM/)",
    )
    args = parser.parse_args()

    run_dir = _make_run_dir(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()

    theme_clause = f" Theme: {args.theme}." if args.theme else ""
    base_msg = f"Run folder: {run_dir}.{theme_clause}"
    stage_msg = f"Run folder: {run_dir}."

    console.print(Rule("[bold cyan]Agent Factory[/bold cyan]"))
    console.print(f"Run folder: [green]{run_dir}[/green]")
    if args.theme:
        console.print(f"Theme: [yellow]{args.theme}[/yellow]")
    console.print()

    console.print(Rule("[yellow]Stage 1 -- Idea Hunter[/yellow]"))
    _launch("idea-hunter", IDEA_HUNTER, OPUS, base_msg, run_dir, client)

    console.print(Rule("[yellow]Stage 2 -- Architect[/yellow]"))
    _launch("architect", ARCHITECT, OPUS, stage_msg, run_dir, client)

    console.print(Rule("[yellow]Stage 3 -- Backend + Frontend (parallel)[/yellow]"))
    with ThreadPoolExecutor(max_workers=2) as pool:
        be = pool.submit(_launch, "backend-engineer", BACKEND_ENGINEER, SONNET, stage_msg, run_dir, client)
        fe = pool.submit(_launch, "frontend-engineer", FRONTEND_ENGINEER, SONNET, stage_msg, run_dir, client)
        be.result()
        fe.result()

    console.print(Rule("[yellow]Stage 4 -- Reviewer[/yellow]"))
    _launch("reviewer", REVIEWER, OPUS, stage_msg, run_dir, client)

    console.print(Rule("[yellow]Stage 5 -- Debugger[/yellow]"))
    _launch("debugger", DEBUGGER, OPUS, stage_msg, run_dir, client)

    console.print(Rule("[bold green]Pipeline Complete[/bold green]"))
    console.print(f"\nAll output written to: [green]{run_dir}[/green]\n")
    console.print("Artifacts:")
    artifacts = [
        "idea.md",
        "architecture.md",
        "backend-notes.md",
        "frontend-notes.md",
        "review.md",
        "debug-report.md",
    ]
    for artifact in artifacts:
        p = run_dir / artifact
        status = "[green]OK[/green]" if p.exists() else "[red]MISSING[/red]"
        console.print(f"  {status}  {artifact}")
    console.print()


if __name__ == "__main__":
    main()
