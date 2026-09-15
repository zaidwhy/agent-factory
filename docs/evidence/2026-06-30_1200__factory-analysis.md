# Agent Factory - Pipeline Analysis & Refinements

Run: `2026-06-30_1200` (Receipts.dev)
Observed from idea through devops. All agents on Claude Sonnet 4.6.

---

## What Worked Well

1. **Idea quality was genuinely strong** - idea-hunter found a real pain point (AI resume trust crisis), cited sources, and produced an idea with a clear non-obvious insight. The "receipts" framing is memorable and concrete.

2. **Architect pushed back correctly** - rejected the "public username for MVP" shortcut (would destroy the trust guarantee), rejected BullMQ for a Python stack, and correctly chose Next.js ISR over Vite for the shareable-link use case. This is exactly what the architect should do.

3. **Parallel build worked** - backend and frontend engineers produced 83 files of production code in parallel with no coordination, and the API contract held up across both sides. Only one TypeScript type mismatch (`confidence: number` vs `float | None`) which is minor.

4. **Reviewer was extremely thorough** - found the critical httpOnly/Authorization header mismatch that would have made the entire app non-functional, plus 4 high issues including a race condition and N+1 patterns. Read 83 files in full and cited file:line for every finding.

5. **Debugger fixed root causes** - wrote 3 new Alembic migrations, rewrote the N+1 query as a window function CTE, implemented atomic Redis INCR for rate limiting, fixed the Celery `is_indexed` false-positive. Didn't just patch symptoms.

---

## Problems Found (Factory Bugs)

### Critical: Reviewer cannot write files

**Issue:** The reviewer agent has `tools: Read, Grep, Bash` but NO `Write` tool. Its instructions say to write `review.md` but it physically cannot. The file was never created. The orchestrator then passed a path to `review.md` to the debugger but the file didn't exist.

**Impact:** The debugger had to work from its own memory of the review instead of reading the file. This is fragile - if the debugger started without seeing the review content in its context, it would have no findings to work from.

**Fix:** Add `Write` to the reviewer's tool list:
```
tools: Read, Grep, Bash, Write
```

### High: DevOps agent hit session limit

**Issue:** The devops-engineer hit Anthropic's usage rate limit mid-run (11:20pm IST reset). It completed 29 tool uses but couldn't write `devops.md` or the CI/CD workflow before being cut off.

**Impact:** Required manual intervention to write devops.md, ci.yml, and fix the SSR internal URL bug the devops agent was supposed to handle.

**Mitigations:**
1. Add a note to FACTORY.md that the devops stage is best run in a fresh session if the prior stages were heavy
2. The forge orchestrator should detect when an agent returns a non-substantive result and retry or surface the failure clearly rather than proceeding silently

### Medium: Debugger didn't write debug-report.md

**Issue:** The debugger fixed all 16 issues but didn't write `debug-report.md` to disk. Its result was detailed in the agent notification, but the file was absent from the run folder.

**Likely cause:** The debugger spent most of its context on reading + fixing 83 files and ran out of budget before writing the report. It has Write access so this is a sequencing issue.

**Fix:** Instruct the debugger to write `debug-report.md` BEFORE doing the security audit pass, not after. Structure the prompt so the report is the second thing it does (after making the app run), not the last:
```
Priority: (1) write a stub debug-report.md, (2) make it run, (3) fix issues updating the report as you go, (4) security audit.
```

### Medium: Orchestrator doesn't verify agent outputs

**Issue:** The forge orchestrator trusts agents' "READY" signals without checking if the file was actually written. When `review.md` didn't exist, the orchestrator passed the path to the debugger anyway.

**Fix:** After each stage, the orchestrator should verify the expected output file exists before proceeding:
```python
# After invoking reviewer, before invoking debugger:
if not Path(f"{run}/review.md").exists():
    STOP: reviewer did not write review.md - check reviewer output
```

Add this verification step to forge.md rules.

### Low: Docker SSR internal URL not handled by any agent

**Issue:** The debugger flagged `INTERNAL_API_URL` as a remaining risk. The devops agent was supposed to fix it but hit the rate limit. The fix (add runtime env var to docker-compose + update api.ts) fell through the gap between agents.

**Fix:** Add this as a standard checklist item to the devops-engineer's instructions:
```
- [ ] If using Docker Compose with Next.js SSR: add INTERNAL_API_URL=http://api:<port>
      as a runtime environment variable and use it for server-side fetches
```

---

## Agent-Specific Improvements

### idea-hunter.md
- Currently good. Minor: instruct it to output the run command path at the end so the orchestrator can verify idea.md was written.

### architect.md
- Currently excellent (pushed back on 3 bad decisions). Keep as-is.
- Minor improvement: explicitly instruct the architect to flag any "trust properties" in the idea that would be destroyed by MVP shortcuts (as it did here with auth).

### backend-engineer.md + frontend-engineer.md
- Both solid. 
- Add: "Before finishing, confirm that `<run>/backend-notes.md` (or `frontend-notes.md`) has been written to disk."

### reviewer.md
**REQUIRED FIX:** Add `Write` to tools line:
```
tools: Read, Grep, Bash, Write
```
The reviewer's primary artifact is `review.md`. Without Write, it can never produce it.

### debugger.md
**REQUIRED FIX:** Restructure priorities so the report is written early:
```
Priority order:
1. Write a stub debug-report.md with section headers
2. Install dependencies and make it run
3. Fix CRITICAL + HIGH findings, updating report as you go
4. Performance audit
5. Security audit
6. Finalize debug-report.md
```
This ensures the report exists even if the agent runs out of context.

### devops-engineer.md
- Add checklist item for Docker SSR internal URL (see above)
- Add: "If you cannot complete all sections, write what you have to devops.md before stopping."

### forge.md (Orchestrator)
Add verification after each sequential stage:
```
After each stage, VERIFY the expected output file exists before proceeding.
If it doesn't exist, STOP and report which agent failed to produce its artifact.
```

---

## Summary of Required Changes

| File | Change | Priority |
|---|---|---|
| `.claude/agents/reviewer.md` | Add `Write` to tools | CRITICAL |
| `.claude/agents/debugger.md` | Restructure: write stub report first | HIGH |
| `.claude/commands/forge.md` | Add post-stage output verification | HIGH |
| `.claude/agents/devops-engineer.md` | Add Docker SSR checklist item; partial-write instruction | MEDIUM |
| `.claude/agents/backend-engineer.md` | Add output-file confirmation step | LOW |
| `.claude/agents/frontend-engineer.md` | Add output-file confirmation step | LOW |
