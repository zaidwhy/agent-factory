---
description: Run the full Agent Factory pipeline — idea → plan → build → review → debug → (optional) devops — producing a runnable project under runs/.
argument-hint: [optional theme, e.g. "developer tools"] [--devops to add deployment stage]
---

You are the Orchestrator of the Agent Factory. Run the whole pipeline and hand
work between the specialist subagents via files. The optional theme is: `$ARGUMENTS`.

Execute these steps in order. Pass the run folder path to every agent.

1. **Create the run folder.** Make `runs/<YYYY-MM-DD_HHMM>/`. Tell the user the
   path. This folder is the shared workspace — every agent reads inputs and writes
   outputs here.

2. **Idea.** Invoke `idea-hunter` with the run folder and theme. Wait for `idea.md`.
   Briefly relay the one-liner to the user.

3. **Plan.** Invoke `architect` with the run folder. It reads `idea.md`, challenges
   any weak decisions, and writes `architecture.md` (with frozen API contract, stack
   pins, scalability notes, and tradeoff analysis). Wait for it.

4. **Build (parallel).** The API contract is frozen — launch both engineers at once
   (a single message with two Agent calls):
   - `backend-engineer` → builds `output/`, writes `backend-notes.md`
   - `frontend-engineer` → builds `output/`, writes `frontend-notes.md`
   Wait for both.

5. **Review.** Invoke `reviewer`. It reads plan + code, checks contract conformance,
   correctness, security, performance, and architecture quality, then writes
   `review.md` with a SHIP/FIX-FIRST verdict. Wait for it.

6. **Debug & secure.** Invoke `debugger`. It runs the project, fixes runtime/logic
   errors, performance bottlenecks, and security flaws, then writes `debug-report.md`.
   Wait for it.

7. **DevOps (optional).** If `--devops` is in the arguments OR the run produced a
   web service (not just a CLI), invoke `devops-engineer`. It writes Dockerfiles,
   a CI/CD workflow, and `devops.md`. Wait for it.

8. **Summary.** Print a one-screen recap:
   - Project name + one-liner
   - Run folder path
   - Reviewer verdict + debugger run status
   - Exact commands to run the project locally
   - Any remaining risks the debugger flagged
   - (If devops ran) deployment checklist location

Rules:
- Always pass the run folder path explicitly to each subagent.
- Steps 2, 3, 5, 6, 7 run sequentially (each depends on the prior). Only step 4
  is parallel.
- If an agent reports it could not finish, stop and surface the blocker rather
  than pressing on with broken inputs.
- **After each sequential stage, verify the expected output file exists before proceeding:**
  - After step 2: check `<run>/idea.md` exists
  - After step 3: check `<run>/architecture.md` exists
  - After step 4: check `<run>/backend-notes.md` AND `<run>/frontend-notes.md` exist
  - After step 5: check `<run>/review.md` exists — if missing, the reviewer failed to write it; surface this to the user before invoking the debugger
  - After step 6: check `<run>/debug-report.md` exists
  - After step 7: check `<run>/devops.md` exists
  If a file is missing, report exactly which agent failed and what file was expected. Do not silently continue.
- **DevOps stage is context-heavy.** If prior stages were large (100+ tool uses total), warn the user that the devops stage may hit rate limits and suggest running `/forge --devops-only <run-folder>` in a fresh session.
