# Agent Factory - Claude Instructions

Six-agent pipeline (idea, plan, backend+frontend in parallel, review, debug) that ships a runnable project into `runs/<timestamp>/`. Two run modes share the same artifact contract.
Repo: https://github.com/syzayd/agent-factory

## Run - Python orchestrator

```powershell
cd C:\Users\Asus\projects\agent-factory
$env:ANTHROPIC_API_KEY = "<ask the user>"
$env:PYTHONIOENCODING = "utf-8"
python factory.py --theme "developer tools"   # --theme is optional
```

- Global Python, no venv. Deps: `pip install -r requirements.txt` (anthropic, rich, requests).
- There is NO `.env` and no dotenv loading: `ANTHROPIC_API_KEY` must be set in the shell. Never echo the key; ask the user to set it.
- Models: `claude-opus-4-8` (idea/architecture/review/debug) and `claude-sonnet-4-6` (engineers). A full run costs several million tokens and takes a long time - confirm with the user before launching.

## Run - Claude Code subagents

Open Claude Code with THIS folder as the working directory (activates `.claude/agents` and the `/forge` command), then:
```
/forge "developer tools"
```
Output lands in `runs/<timestamp>/output/`. Single agents can be driven directly, e.g. `@idea-hunter`, `@architect`.

## Tests

- No test suite in this repo (generated projects carry their own tests). Cheap health check: `python factory.py --help` should render the rich CLI help.

## Logs

- Master log: `CHANGELOG.md` - append a dated entry before ending any session with meaningful work. No `handoffs/` folder here.
- `FACTORY.md` is the pipeline spec and artifact contract; update it if the pipeline changes.
- `runs/` holds the proof runs (PinPoint 2026-06-25, DriftGuard 2026-06-28, Receipts.dev 2026-06-30). Do not edit or delete them.

## Gotchas

- The architect's API contract in `runs/<ts>/` is frozen before any code is written; agents communicate only through files, never assume shared state.
- Agent prompts live in `agents/prompts.py`; the tool loop (file IO, shell, search) in `agents/tools.py`.
- Never use the em dash character (U+2014) anywhere; use " - " instead.
