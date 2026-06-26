# Agent Factory — Pipeline Spec

A team of specialized agents that turns *nothing* into a runnable software
project. Each agent owns one job and hands off to the next through files in a
per-run folder. No agent guesses another's output — it reads it.

## The pipeline

```
  /forge "<theme>"
        │
        ▼
  ┌─────────────┐   idea.md
  │ idea-hunter │ ─────────────►┐
  └─────────────┘               │
                                ▼
                        ┌──────────────┐  architecture.md  (API contract = law)
                        │  architect   │ ───────────────►┐
                        └──────────────┘                 │
                            ┌────────────────────────────┴───────────┐
                            ▼ (parallel — contract is frozen)         ▼
                    ┌──────────────────┐                  ┌───────────────────┐
                    │ backend-engineer │ output/api/      │ frontend-engineer │ output/web/
                    └──────────────────┘                  └───────────────────┘
                            └────────────────────┬───────────────────┘
                                                 ▼
                                          ┌────────────┐  review.md (SHIP | FIX-FIRST)
                                          │  reviewer  │ ──────────►┐
                                          └────────────┘            │
                                                                    ▼
                                                          ┌──────────────┐  debug-report.md
                                                          │  debugger    │  (runs it, fixes
                                                          └──────────────┘   bugs + security)
                                                                    │
                                                                    ▼
                                                          runnable project + recap
```

## The agents

| Agent | Model | Owns | Reads | Writes |
|---|---|---|---|---|
| `idea-hunter` | opus | a novel, buildable idea | theme | `idea.md` |
| `architect` | opus | the plan + frozen API contract | `idea.md` | `architecture.md` |
| `backend-engineer` | sonnet | server code to spec | `architecture.md` | `output/api/`, `backend-notes.md` |
| `frontend-engineer` | sonnet | UI to spec, looks good | `architecture.md` | `output/web/`, `frontend-notes.md` |
| `reviewer` | opus | judge: bugs/security/contract | plan + code | `review.md` |
| `debugger` | opus | run it, FIX bugs + security flaws | everything | `debug-report.md` |

`reviewer` only judges (read-only). `debugger` actually fixes — runs the app,
reproduces and repairs runtime/logic errors, and remediates security holes.

## The artifact contract (why this is portable)

Every run is a self-contained folder `runs/<YYYY-MM-DD_HHMM>/`:

```
runs/2026-06-25_1430/
  idea.md
  architecture.md          # contains the API contract — the source of truth
  backend-notes.md
  frontend-notes.md
  review.md
  debug-report.md
  output/
    api/                   # backend
    web/                   # frontend
```

Agents communicate only through these files. That file-based hand-off is what
lets the whole team be re-implemented later as a Python program (Phase 2) with
zero change to the contract — see `README.md`.

## Running it

Open Claude Code in this folder and run `/forge` (optionally with a theme), e.g.
`/forge "developer tools"`. The orchestrator drives every stage and prints how
to run the finished project.
