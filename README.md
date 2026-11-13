# Agent Factory

Parallel code-writing agents drift apart unless something fixes the interface between them
before either starts. Agent Factory makes the architect's API contract the first thing that is
written and the one thing nobody may change: the backend and frontend agents then build at the
same time without seeing each other's code, and the contract is what has to line up when a
reviewer checks the result.

It is for anyone who wants to see a multi-agent build pipeline whose handoffs are plain files
you can read, not messages inside a framework. Six agents (seven in the Claude Code version)
take a theme to a runnable project: idea, plan, backend and frontend in parallel, review, debug.

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # PowerShell: $env:ANTHROPIC_API_KEY = "..."
python factory.py --theme "developer tools"      # --theme is optional
```

A full run costs several million tokens and takes a long time; cost and duration were not
measured for this README. Everything lands in `runs/<YYYY-MM-DD_HHMM>/`.

## How the handoffs work

| Stage | Agent (model) | Reads | Writes |
|---|---|---|---|
| 1 | idea-hunter (opus) | the theme | `idea.md` |
| 2 | architect (opus) | `idea.md` | `architecture.md`, with the frozen API contract |
| 3 | backend-engineer and frontend-engineer (sonnet), in parallel | `architecture.md` | `output/`, `backend-notes.md`, `frontend-notes.md` |
| 4 | reviewer (opus) | plan and code | `review.md` |
| 5 | debugger (opus) | everything | `debug-report.md`, fixes in `output/` |
| optional | devops-engineer (Claude Code version only) | everything | `devops.md`, Dockerfile, CI workflow |

Agents never share memory; each stage starts from the files the earlier stages left. The Python
orchestrator uses `claude-opus-4-8` and `claude-sonnet-4-6` and runs stage 3 on a
`ThreadPoolExecutor` with two workers. The file layout is the artifact contract in
[`FACTORY.md`](./FACTORY.md), shared by both ways of running it, so a run from `factory.py` and
a run from the subagents have the same shape.

## Run it as Claude Code subagents

Open Claude Code with this folder as the working directory, so `.claude/agents` and the
`/forge` command are active, then:

```
/forge "developer tools"              # stages 1 to 5
/forge "developer tools" --devops     # adds the devops stage
```

Single agents can be driven directly, for example `@idea-hunter` or `@architect`.

## What was produced

Three runs, 25 to 30 June 2026. The full run folders are not in the repository (`runs/` is
gitignored); the markdown each run wrote is kept under [`docs/evidence/`](./docs/evidence/),
and the figures below are quoted from those debug reports.

| Run | Project | Debugger's report |
|---|---|---|
| 2026-06-25 | PinPoint, a CLI dependency scanner | 65 tests collected, 65 passed; 5 bugs fixed, including a path-segment matching flaw |
| 2026-06-28 | DriftGuard, a schema drift detector for OpenAPI, TypeScript and Prisma | 108 tests passed, 0 type errors, 0 lint errors; devops stage added a Dockerfile and CI |
| 2026-06-30 | Receipts.dev, a developer profile platform with grounded AI chat | all 16 reviewer findings addressed, including 1 critical and 4 high; GitHub OAuth and pgvector retrieval |

These are the debugger's own statements about its run; the test counts come from the agent
that fixed the code. Nothing outside the three runs measures how often the pipeline produces a
project that works.

## Architecture

- `factory.py` - the CLI and the five stages in order.
- `agents/prompts.py` - one system prompt per agent.
- `agents/base.py` - the model loop: stream a reply, run the tool calls, repeat until the
  model ends its turn.
- `agents/tools.py` - the four tools: `read_file`, `write_file`, `run_bash`, `web_search`.
  Paths outside the repository are refused. `run_bash` takes one command with no shell
  operators, from an allow-list of executables (python, pytest, ruff, node, npm, git and a few
  more), with a 120 s timeout.
- `.claude/agents/*.md` and `.claude/commands/forge.md` - the same pipeline as subagents.
- `scripts/collect_evidence.py` - copies a run's markdown into `docs/evidence/`.

`factory.py` refuses a run folder that already holds files, so a reused `--run-dir` or two runs
in the same minute cannot overwrite an earlier run.

## Tests

`python -m pytest tests -q` - 25 passed on 2026-11-13 (Windows 11, Python 3.14). One of them
drives the real `factory.py` with the Anthropic client mocked, so it needs no key and costs
nothing; it asserts every artifact in the contract is written and that each stage's tool calls
succeed only because the stage before it ran. The others cover the `run_bash` and path
sandbox and the evidence script. CI runs the same command on Python 3.12
([workflow](./.github/workflows/ci.yml)). Plain `pytest` from the repository root also
collects PinPoint's own tests inside the local `runs/` folder and reports 90, which is not the
suite's count.

## Limits

- The reviewer is read-only by instruction, not by enforcement. Its prompt says not to modify
  files, but it holds `Write` and `Bash` in the subagent version, and every agent gets every
  tool in the Python version.
- Three runs, one author, no comparison against a single agent building the same project. The
  pipeline's value over that baseline is unmeasured.
- The frozen contract stops interface drift, not wrong behaviour behind the interface. The
  debugger's reports list real bugs in all three runs, so the build stages did not ship clean.
- The three proof runs are not reproducible from the repository alone, since `runs/` is not
  committed and a run depends on live model output.

## Status

Maintained, no active development. Last behaviour change was refusing a non-empty run folder
(2026-10-28, see [`CHANGELOG.md`](./CHANGELOG.md)).

MIT licensed ([LICENSE](./LICENSE)). Part of [Zaid Ali Syed](https://www.solstine.dev)'s portfolio.
