"""Sandbox containment: tool paths must never escape the per-run project root."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.tools import _resolve, execute_tool


def test_relative_paths_stay_inside_the_root(tmp_path):
    assert _resolve("src/app.py", tmp_path) == (tmp_path / "src" / "app.py").resolve()


def test_the_root_itself_is_allowed(tmp_path):
    assert _resolve(".", tmp_path) == tmp_path.resolve()


def test_dotdot_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        _resolve("../outside.txt", tmp_path)
    with pytest.raises(ValueError):
        _resolve("src/../../outside.txt", tmp_path)


def test_absolute_paths_outside_the_root_are_rejected(tmp_path):
    # A sibling of tmp_path is absolute and genuinely outside the sandbox on any OS -
    # a hardcoded platform-specific path (e.g. "C:/Windows/...") is not absolute on
    # POSIX and silently passes through as a relative path there instead of raising.
    outside = tmp_path.parent / "outside-sandbox" / "hosts"
    with pytest.raises(ValueError):
        _resolve(str(outside), tmp_path)


def test_read_file_escape_returns_error_string(tmp_path):
    result = execute_tool("read_file", {"path": "../secret.txt"}, tmp_path)
    assert result.startswith("Error")
    assert "sandbox" in result


def test_write_file_escape_writes_nothing(tmp_path):
    outside = tmp_path.parent / "escaped.txt"
    result = execute_tool(
        "write_file", {"path": "../escaped.txt", "content": "x"}, tmp_path
    )
    assert result.startswith("Error")
    assert not outside.exists()


def test_run_bash_escape_cwd_returns_error_string(tmp_path):
    result = execute_tool("run_bash", {"command": "echo hi", "cwd": ".."}, tmp_path)
    assert result.startswith("Error")


def test_write_then_read_inside_root_still_works(tmp_path):
    execute_tool("write_file", {"path": "notes/a.txt", "content": "hello"}, tmp_path)
    assert execute_tool("read_file", {"path": "notes/a.txt"}, tmp_path) == "hello"
