# Frontend Notes — PinPoint CLI

## How to install and run

```bash
# 1. Set the required environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Optional: raise GitHub API rate limit
export GITHUB_TOKEN=ghp_...

# 3. Install (editable during development)
cd output
pip install -e .

# 4. Initialize config in your project
pinpoint init /path/to/your/project

# 5. Run a scan
pinpoint scan /path/to/your/project

# 6. CI-friendly (JSON output, fail on high risk)
pinpoint scan /path/to/your/project --output json --min-risk high
echo "Exit code: $?"   # 0 = no high-risk, 1 = high-risk found

# 7. Run tests
pip install -e ".[dev]"
pytest
```

## Files written

All files are under `output/` (the canonical root per architecture.md):

| File | Role |
|------|------|
| `output/pyproject.toml` | Build config, deps, entry point `pinpoint.cli:app` |
| `output/.pinpoint.json.example` | Annotated config reference (not valid JSON — // comments) |
| `output/.env.example` | Environment variable reference |
| `output/README.md` | Install + quickstart + how-it-works |
| `output/pinpoint/__init__.py` | Version = "0.1.0" |
| `output/pinpoint/cli.py` | **FRONTEND** — Typer app, scan + init commands, progress spinner |
| `output/pinpoint/report.py` | **FRONTEND** — Rich table renderer + JSON serializer |
| `output/pinpoint/models.py` | All Pydantic data models (contract shared by all modules) |
| `output/pinpoint/exceptions.py` | Exception hierarchy: PinPointError + 4 subclasses |
| `output/pinpoint/config.py` | `load_config(path, project_root) -> Config` |
| `output/pinpoint/pipeline.py` | `run(root, config) -> list[FinalVerdict]` orchestrator |
| `output/pinpoint/scanner/` | Python (ast) + JS/TS (tree-sitter + regex fallback) scanners |
| `output/pinpoint/fetcher/` | npm + PyPI fetchers + shared httpx client with retry |
| `output/pinpoint/cve/` | OSV.dev client → list[CVERecord] |
| `output/pinpoint/llm/` | ClaudeEngine using tool_use, exact tool schema from contract |
| `output/tests/` | Full pytest suite with respx mocks (9 test files + conftest) |

## Decisions made explicit

### 1. CLI calls only `pipeline.run` — no direct submodule access
The architecture contract states: "Caller (CLI) should not call individual modules
directly — always go through `pipeline.run`." An earlier draft of `cli.py` called
`scanner`, `fetcher`, `cve`, and `llm` directly to enable per-package progress
updates. This was reverted. The spinner now runs for the entire `pipeline.run`
duration (single indeterminate spinner). A callback-hook pattern could restore
per-package granularity without breaking the contract, but that requires adding
an optional `on_progress` param to `pipeline.run` — left for a future iteration.

### 2. Risk filtering in `render_table` uses >= threshold logic
`_RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}`.
A verdict is shown if `risk_rank(verdict) >= risk_rank(min_risk)`.
This means `--min-risk none` shows everything (the default behavior when no flag
is given). This matches the architecture description.

### 3. `--no-color` also reads `$NO_COLOR` env var
Typer's `envvar` param wires `NO_COLOR` env var automatically. Any non-empty
`NO_COLOR` value disables Rich color — follows the `NO_COLOR` convention
(https://no-color.org/).

### 4. `ImportMap` has no `installed` field — version comes from lock files
The scanner builds `ImportMap` from source imports only; it cannot know what
version is installed. The fetchers call `get_installed_version(package, ecosystem,
root)` internally when they receive `installed="0.0.0"`. This reads
`package.json` (npm) or `requirements.txt`/`pyproject.toml` (PyPI).

### 5. JS scanner falls back to regex if tree-sitter is unavailable
`tree-sitter>=0.23` has a slightly different Python binding API than 0.21.
The scanner catches any `ImportError`/`Exception` during parser init and
silently falls back to regex. This makes the tool usable even in environments
where the tree-sitter native extension fails to compile.

### 6. `output/api/` directory exists from a prior backend agent run
The backend agent wrote to `output/api/` instead of `output/` (a deviation from
architecture.md). The canonical deliverable is `output/` — that is the directory
that contains the complete, installable package including `cli.py`.

---

FRONTEND READY: runs/2026-06-25_1737/output

The `output/` directory is a complete, pipx-installable Python package. The
`output/api/` subdirectory is a backend-agent artifact at the wrong path and
should be reconciled or removed by the reviewer before shipping.
