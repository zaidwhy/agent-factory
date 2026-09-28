"""scripts/collect_evidence.py: naming, skips, dash replacement, never overwrites."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import collect_evidence

EM_DASH = chr(0x2014)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_collects_new_run_and_skips_noise(tmp_path: Path) -> None:
    runs, evidence = tmp_path / "runs", tmp_path / "evidence"
    _write(runs / "2026-10-01_0900" / "idea.md", f"a {EM_DASH} b{EM_DASH}c")
    _write(runs / "2026-10-01_0900" / "output" / "tool" / "README.md", "readme")
    _write(runs / "2026-10-01_0900" / "output" / ".pytest_cache" / "README.md", "cache")
    _write(runs / "2026-10-01_0900" / "output" / "node_modules" / "x" / "README.md", "dep")
    _write(runs / "golden" / "idea.md", "test output")

    assert collect_evidence.collect(runs, evidence, check=True) == 1
    assert collect_evidence.collect(runs, evidence, check=False) == 0

    assert sorted(p.name for p in evidence.iterdir()) == [
        "2026-10-01_0900__idea.md",
        "2026-10-01_0900__output__tool__README.md",
    ]
    assert (evidence / "2026-10-01_0900__idea.md").read_text(encoding="utf-8") == "a - b - c"
    assert collect_evidence.collect(runs, evidence, check=True) == 0


def test_never_overwrites_curated_evidence(tmp_path: Path) -> None:
    runs, evidence = tmp_path / "runs", tmp_path / "evidence"
    _write(runs / "r1" / "review.md", "raw run text")
    _write(evidence / "r1__review.md", "curated text")

    collect_evidence.collect(runs, evidence, check=False)

    assert (evidence / "r1__review.md").read_text(encoding="utf-8") == "curated text"


def test_committed_evidence_is_complete_when_runs_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    runs = root / "runs"
    if not runs.is_dir() or not any(p.is_dir() and p.name != "golden" for p in runs.iterdir()):
        return  # fresh clone: runs/ is gitignored
    assert collect_evidence.collect(runs, root / "docs" / "evidence", check=True) == 0
