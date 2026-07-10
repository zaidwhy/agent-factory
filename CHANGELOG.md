# Changelog

Running log of meaningful changes to Agent Factory. Newest first.

## 2026-07-02 - Open-source release polish

- **MIT LICENSE added** (repo previously had no license at all).
- **README rewritten for release:** now leads with the proof-of-runs table
  (PinPoint: 65 tests passing; DriftGuard: 108 tests, 15 bugs fixed, Docker + CI
  generated; Receipts.dev: 92 files, 16 bugs debugged) and documents BOTH ways
  to run the pipeline: the `factory.py` Python orchestrator (previously described
  as future work despite being live) and the Claude Code `/forge` subagents.
- **GitHub metadata:** six discovery topics (ai-agents, claude, anthropic,
  multi-agent-systems, code-generation, llm) and homepage link added.
- **Repo hygiene:** em dashes purged from README, FACTORY.md, and all seven
  subagent prompt files plus the /forge command per the global style rule.
- Verified: `factory.py` imports and its CLI help renders; all 19 tracked files
  reviewed; `.claude/agents` + `/forge` confirmed tracked so a fresh clone gets
  the complete subagent experience.

## 2026-06-30 - Receipts.dev run (pipeline proof #3)

- Full 7-stage run generated Receipts.dev: developer profile platform with
  grounded AI chat. 92 files, 16 bugs found and debugged (1 critical, 4 high).

## 2026-06-28..30 - DriftGuard run (pipeline proof #2)

- 7-agent pipeline (devops-engineer stage added) generated DriftGuard, a schema
  drift detector for OpenAPI/TypeScript/Prisma. 108 tests passing, 0 type
  errors, 0 lint errors; 15 bugs found and fixed; Docker + GitHub Actions CI.

## 2026-06-25..26 - PinPoint run (pipeline proof #1)

- First full end-to-end run generated PinPoint, a CLI dependency scanner.
  65 tests passing; debugger fixed 5 bugs including a path-segment matching flaw.

## 2026-06 - Phase 1 + Phase 2

- Phase 1: six Claude Code subagents (idea-hunter, architect, backend-engineer,
  frontend-engineer, reviewer, debugger) orchestrated by the `/forge` command,
  handing off through `runs/<timestamp>/` files with a frozen API contract.
- Phase 2: `factory.py` standalone orchestrator on the Anthropic Python SDK.
  Same artifact contract; parallel backend/frontend builds via ThreadPoolExecutor.

## 2026-07-10 - Sandbox path containment

- `_resolve()` in `agents/tools.py` now resolves every tool-supplied path and rejects
  anything outside the per-run project root (absolute paths and `../` traversal raise;
  tool calls surface a readable "Error ... sandbox" string instead of touching the file).
- First test suite in the repo: `tests/test_sandbox.py`, 8 cases, offline
  (`python -m pytest tests/ -q`).
- Source: MASTER-FIX-PLAN v2 finding S4 / Genesis Tier 1 item 7.
