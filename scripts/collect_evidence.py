"""Copy the markdown artifacts of every recorded run into docs/evidence/.

runs/ is gitignored (a run writes whole generated projects), so the committed
proof of each run is its markdown: the agent handoff files at the run root and
every README under output/. Each file lands flat in docs/evidence/ as
<run>__<path with / replaced by __>, the naming the existing evidence uses.

Existing evidence files are never overwritten: they were curated after
collection (em dash purge, CHANGELOG 2026-07-02; org URLs moved from syzayd to
zaidwhy on 2026-09-15), so only files missing from docs/evidence/ are written.
New files get the same em dash replacement the purge used.

Usage:
    python scripts/collect_evidence.py          # add evidence for new runs
    python scripts/collect_evidence.py --check  # exit 1 if evidence is missing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EM_DASH = chr(0x2014)
# golden is written by tests/test_golden_run.py, not by a real run.
SKIP_RUNS = {"golden"}
SKIP_DIRS = {"node_modules", "__pycache__", "venv"}


def _is_skipped(rel: Path) -> bool:
    return any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts[:-1])


def planned(runs_dir: Path) -> dict[str, str]:
    """Map evidence file name -> content it should have."""
    out: dict[str, str] = {}
    for run in sorted(p for p in runs_dir.iterdir() if p.is_dir() and p.name not in SKIP_RUNS):
        for md in sorted(run.rglob("*.md")):
            rel = md.relative_to(run)
            if _is_skipped(rel):
                continue
            name = f"{run.name}__{'__'.join(rel.parts)}"
            text = md.read_text(encoding="utf-8")
            out[name] = text.replace(f" {EM_DASH} ", " - ").replace(EM_DASH, " - ")
    return out


def collect(runs_dir: Path, evidence_dir: Path, check: bool) -> int:
    missing = []
    for name, text in planned(runs_dir).items():
        target = evidence_dir / name
        if target.exists():
            continue
        missing.append(name)
        if not check:
            evidence_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="")
    verb = "missing" if check else "written"
    print(f"{len(missing)} evidence file(s) {verb}")
    for name in missing:
        print(f"  {name}")
    return 1 if check and missing else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy run markdown into docs/evidence/.")
    parser.add_argument("--check", action="store_true", help="report missing files, change nothing")
    args = parser.parse_args()
    return collect(ROOT / "runs", ROOT / "docs" / "evidence", args.check)


if __name__ == "__main__":
    sys.exit(main())
