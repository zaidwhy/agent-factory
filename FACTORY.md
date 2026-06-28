# Agent Factory — Pipeline Spec

A team of seven specialized agents that turns *nothing* into a production-ready
software project. Each agent owns one job and hands off through files in a
per-run folder. No agent guesses another's output — it reads it.

## The pipeline

```
  /forge "<theme>" [--devops]
        │
        ▼
  ┌─────────────┐   idea.md
  │ idea-hunter │ ─────────────►┐
  └─────────────┘               │
                                ▼
                        ┌──────────────┐  architecture.md  (API contract = law)
                        │  architect   │ ───────────────►┐
                        └──────────────┘                 │  (tech-lead: challenges
                                                         │   bad decisions, pins
                            ┌────────────────────────────┤   deps, scalability notes)
                            ▼ (parallel — contract frozen) ▼
                    ┌──────────────────┐      ┌───────────────────┐
                    │ backend-engineer │      │ frontend-engineer │
                    │  output/api/     │      │  output/web/      │
                    └──────────────────┘      └───────────────────┘
                            └────────────────────┬──────────────────┘
                                                 ▼
                                          ┌────────────┐  review.md
                                          │  reviewer  │  (contract + correctness +
                                          └────────────┘   security + perf + arch)
                                                 │
                                                 ▼
                                       ┌──────────────┐  debug-report.md
                                       │  debugger    │  (runs it, fixes bugs,
                                       └──────────────┘   perf + security)
                                                 │
                                          [--devops]
                                                 ▼
                                     ┌──────────────────┐  devops.md + CI/CD files
                                     │ devops-engineer  │  (Dockerfile, GitHub
                                     └──────────────────┘   Actions, monitoring)
                                                 │
                                                 ▼
                                       runnable project + recap
```

## The agents

| Agent | Model | Owns | Reads | Writes |
|---|---|---|---|---|
| `idea-hunter` | opus | a novel, buildable-at-scale idea | theme | `idea.md` |
| `architect` | opus | plan + frozen contract + tradeoffs | `idea.md` | `architecture.md` |
| `backend-engineer` | sonnet | server code to spec, scale-ready | `architecture.md` | `output/`, `backend-notes.md` |
| `frontend-engineer` | sonnet | UI to spec, accessible, reusable | `architecture.md` | `output/`, `frontend-notes.md` |
| `reviewer` | opus | judge: contract + security + perf + arch | plan + code | `review.md` |
| `debugger` | opus | run it, fix bugs + perf + security | everything | `debug-report.md` |
| `devops-engineer` | opus | CI/CD, Docker, monitoring, deploy | everything | `devops.md`, config files |

`reviewer` only judges (read-only). `debugger` actually fixes.
`devops-engineer` runs optionally — add `--devops` to `/forge` or invoke directly.

## Key design principles (from the images)

- **Scale mindset:** Every agent builds like it could serve millions — clean
  separation of concerns, no tight coupling, performance-aware from day one.
- **Senior engineer mindset:** Architect challenges bad decisions before they're
  built. Reviewer checks architecture quality, not just bugs. Debugger traces
  root causes, never guesses.
- **Production-level quality bar:** No TODOs, no stubs, no placeholder code.
  Loading/empty/error states in the frontend. Proper auth, input validation,
  and security hardening.

## The artifact contract

Every run is a self-contained folder `runs/<YYYY-MM-DD_HHMM>/`:

```
runs/2026-06-25_1430/
  idea.md
  architecture.md          # API contract + scalability notes
  backend-notes.md
  frontend-notes.md
  review.md
  debug-report.md
  devops.md                # optional
  output/
    api/                   # backend (or single-package root)
    web/                   # frontend
    Dockerfile             # added by devops-engineer
    docker-compose.yml
    .github/workflows/ci.yml
```

## Running it

Open Claude Code in this folder and run:
```
/forge "developer tools"          # basic pipeline
/forge "developer tools" --devops # full pipeline including deployment
```
