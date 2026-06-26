import subprocess
from pathlib import Path

import requests

TOOL_SCHEMAS: list[dict] = [
    {
        "name": "read_file",
        "description": "Read a file. Path may be absolute or relative to the project root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path (absolute or relative to project root)",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write content to a file, creating parent directories as needed. "
            "Path may be absolute or relative to the project root."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path (absolute or relative to project root)",
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_bash",
        "description": "Run a shell command and return combined stdout + stderr.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "cwd": {
                    "type": "string",
                    "description": (
                        "Working directory (absolute or relative to project root). "
                        "Defaults to project root."
                    ),
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the web via DuckDuckGo Instant Answer API and return a brief result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
            },
            "required": ["query"],
        },
    },
]


def execute_tool(name: str, tool_input: dict, project_root: Path) -> str:
    if name == "read_file":
        return _read_file(tool_input["path"], project_root)
    if name == "write_file":
        return _write_file(tool_input["path"], tool_input["content"], project_root)
    if name == "run_bash":
        return _run_bash(tool_input["command"], tool_input.get("cwd"), project_root)
    if name == "web_search":
        return _web_search(tool_input["query"])
    return f"Unknown tool: {name}"


def _resolve(path: str, project_root: Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else project_root / p


def _read_file(path: str, project_root: Path) -> str:
    full = _resolve(path, project_root)
    try:
        return full.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as exc:
        return f"Error reading {path}: {exc}"


def _write_file(path: str, content: str, project_root: Path) -> str:
    full = _resolve(path, project_root)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {path}"


def _run_bash(command: str, cwd: str | None, project_root: Path) -> str:
    work_dir = _resolve(cwd, project_root) if cwd else project_root
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = result.stdout
        if result.stderr:
            out += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            out += f"\n[exit {result.returncode}]"
        return out.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out (120s)"
    except Exception as exc:
        return f"Error: {exc}"


def _web_search(query: str) -> str:
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
            headers={"User-Agent": "agent-factory/1.0"},
            timeout=10,
        )
        data = resp.json()
        parts: list[str] = []
        if data.get("AbstractText"):
            parts.append(data["AbstractText"])
        if data.get("AbstractURL"):
            parts.append(f"Source: {data['AbstractURL']}")
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"):
                parts.append(f"- {topic['Text']}")
        for result in data.get("Results", [])[:2]:
            if isinstance(result, dict) and result.get("Text"):
                parts.append(f"- {result['Text']}")
        return "\n".join(parts) if parts else f"No instant answer found for: {query}"
    except Exception as exc:
        return f"Search error: {exc}"
