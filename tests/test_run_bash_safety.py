"""The run_bash tool executes model-written commands. It must never hand them to a shell."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.tools import ALLOWED_EXECUTABLES, _parse_command, execute_tool


@pytest.mark.parametrize(
    "command",
    [
        "echo hi; echo injected",
        "echo hi && echo injected",
        "echo hi | cat",
        "echo hi > out.txt",
        "echo `whoami`",
        "echo $(whoami)",
        "echo $HOME",
    ],
)
def test_shell_operators_are_rejected(command):
    with pytest.raises(ValueError, match="shell operators"):
        _parse_command(command)


def test_unlisted_executable_is_rejected():
    with pytest.raises(ValueError, match="allow-list"):
        _parse_command("curl http://example.com")


def test_missing_executable_is_rejected(monkeypatch):
    monkeypatch.setattr("agents.tools.shutil.which", lambda _: None)
    with pytest.raises(ValueError, match="not found on PATH"):
        _parse_command("python --version")


def test_allowed_command_runs_without_a_shell(tmp_path):
    assert "python" in ALLOWED_EXECUTABLES
    out = execute_tool("run_bash", {"command": 'python -c "print(6*7)"'}, tmp_path)
    assert out.strip() == "42"


def test_injection_attempt_returns_error_string_not_execution(tmp_path):
    marker = tmp_path / "pwned.txt"
    out = execute_tool(
        "run_bash",
        {"command": f'python -c "print(1)" ; python -c "open(r\'{marker}\', \'w\').write(\'x\')"'},
        tmp_path,
    )
    assert out.startswith("Error")
    assert not marker.exists()
