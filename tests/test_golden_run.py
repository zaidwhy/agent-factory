"""Golden-run test for the 6-agent pipeline.

Drives the real orchestration in factory.py (stage order, the parallel backend/
frontend stage, the tool-call loop in agents/base.py) with the Anthropic API
replaced by scripted responses - no key, no cost, no network. Asserts the
artifact contract in FACTORY.md end to end, and specifically that reviewer and
debugger actually READ their upstream files rather than the test only checking
that every file exists once the run is over - proving the handoff order
(architect -> backend/frontend -> reviewer -> debugger) really holds.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import factory
from agents.prompts import (
    ARCHITECT,
    BACKEND_ENGINEER,
    DEBUGGER,
    FRONTEND_ENGINEER,
    IDEA_HUNTER,
    REVIEWER,
)

RUN_DIR_REL = "runs/golden"


def _p(name: str) -> str:
    return f"{RUN_DIR_REL}/{name}"


def _tool_use(tool_id: str, name: str, tool_input: dict) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=tool_id, name=name, input=tool_input)


def _message(stop_reason: str, content: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(stop_reason=stop_reason, content=content)


def _write_turn(tool_id: str, path: str, content: str) -> SimpleNamespace:
    return _message("tool_use", [_tool_use(tool_id, "write_file", {"path": _p(path), "content": content})])


def _write_many_turn(writes: list[tuple[str, str, str]]) -> SimpleNamespace:
    return _message(
        "tool_use",
        [_tool_use(tid, "write_file", {"path": _p(path), "content": content}) for tid, path, content in writes],
    )


def _read_turn(tool_id: str, path: str) -> SimpleNamespace:
    return _message("tool_use", [_tool_use(tool_id, "read_file", {"path": _p(path)})])


def _end_turn() -> SimpleNamespace:
    return _message("end_turn", [SimpleNamespace(type="text", text="done")])


ARCHITECTURE_CONTENT = "# Architecture\n\nAPI: GET /items -> list[Item]\n"


def _build_scripts() -> dict[str, list[SimpleNamespace]]:
    return {
        IDEA_HUNTER: [
            _write_turn("t1", "idea.md", "# Idea\n\nA todo app.\n"),
            _end_turn(),
        ],
        ARCHITECT: [
            _write_turn("t1", "architecture.md", ARCHITECTURE_CONTENT),
            _end_turn(),
        ],
        # backend and frontend each read the architect's contract before writing,
        # so a read that returns the real content (not "Error: file not found")
        # proves the architect stage actually finished first.
        BACKEND_ENGINEER: [
            _read_turn("t1", "architecture.md"),
            _write_many_turn([
                ("t2", "output/api/main.py", "# backend\n"),
                ("t3", "backend-notes.md", "Implemented GET /items.\n"),
            ]),
            _end_turn(),
        ],
        FRONTEND_ENGINEER: [
            _read_turn("t1", "architecture.md"),
            _write_many_turn([
                ("t2", "output/web/index.html", "<!-- frontend -->\n"),
                ("t3", "frontend-notes.md", "Rendered the item list.\n"),
            ]),
            _end_turn(),
        ],
        REVIEWER: [
            _read_turn("t1", "architecture.md"),
            _write_turn("t2", "review.md", "# Review\n\nContract honored.\n"),
            _end_turn(),
        ],
        DEBUGGER: [
            _read_turn("t1", "review.md"),
            _write_turn("t2", "debug-report.md", "# Debug report\n\nNo bugs found.\n"),
            _end_turn(),
        ],
    }


class _FakeStream:
    """Mimics the object `with client.messages.stream(...) as stream:` yields."""

    def __init__(self, final_message: SimpleNamespace) -> None:
        self.text_stream: list[str] = []
        self._final_message = final_message

    def get_final_message(self) -> SimpleNamespace:
        return self._final_message


class _FakeStreamCM:
    def __init__(self, final_message: SimpleNamespace) -> None:
        self._stream = _FakeStream(final_message)

    def __enter__(self) -> _FakeStream:
        return self._stream

    def __exit__(self, *exc: object) -> None:
        return None


class _FakeMessages:
    """Scripted per-agent turn queues, keyed by system prompt so the real
    ThreadPoolExecutor(2) in factory.py (backend + frontend run concurrently)
    can never cross-talk between agents - each only ever pops its own list."""

    def __init__(self, scripts: dict[str, list[SimpleNamespace]]) -> None:
        self._scripts = scripts

    def stream(self, *, model, max_tokens, system, tools, thinking, messages):
        queue = self._scripts.get(system)
        if queue is None:
            raise AssertionError(f"no scripted agent matches this system prompt: {system[:60]!r}")
        if not queue:
            raise AssertionError(f"agent called client.messages.stream() more times than scripted (system: {system[:60]!r})")
        # The full conversation so far is passed on every call - check the most recent
        # tool result (if any) never came back as an error. This is what actually proves
        # the handoff order held: a reviewer/debugger read of an upstream file only
        # succeeds if that upstream stage genuinely already ran and wrote it.
        if messages and messages[-1]["role"] == "user" and isinstance(messages[-1]["content"], list):
            for block in messages[-1]["content"]:
                if block.get("type") == "tool_result":
                    result = block.get("content", "")
                    assert not result.startswith("Error"), (
                        f"agent (system: {system[:40]!r}) received a tool error - handoff order broken: {result}"
                    )
        return _FakeStreamCM(queue.pop(0))


class _FakeClient:
    def __init__(self, scripts: dict[str, list[SimpleNamespace]]) -> None:
        self.messages = _FakeMessages(scripts)


def test_golden_run_produces_the_full_artifact_contract(monkeypatch, tmp_path):
    scripts = _build_scripts()
    fake_client = _FakeClient(scripts)

    # Sandbox root for every tool call is factory.PROJECT_ROOT - point it at tmp_path
    # so this test never touches the real repo's runs/ folder.
    monkeypatch.setattr(factory, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(factory.anthropic, "Anthropic", lambda: fake_client)
    monkeypatch.setattr(sys, "argv", ["factory.py", "--run-dir", RUN_DIR_REL, "--theme", "todo app"])

    factory.main()

    run_dir = tmp_path / RUN_DIR_REL
    for artifact in [
        "idea.md",
        "architecture.md",
        "backend-notes.md",
        "frontend-notes.md",
        "review.md",
        "debug-report.md",
    ]:
        assert (run_dir / artifact).exists(), f"{artifact} missing from the run folder"

    assert (run_dir / "output" / "api" / "main.py").read_text(encoding="utf-8") == "# backend\n"
    assert (run_dir / "output" / "web" / "index.html").read_text(encoding="utf-8") == "<!-- frontend -->\n"
    assert (run_dir / "architecture.md").read_text(encoding="utf-8") == ARCHITECTURE_CONTENT

    # Every scripted turn was consumed exactly once - nothing left over, nothing
    # replayed, meaning the pipeline called each agent exactly as many times as
    # the handoff contract expects.
    for system, remaining in scripts.items():
        assert remaining == [], f"agent with system prompt {system[:40]!r} left {len(remaining)} scripted turn(s) unconsumed"
