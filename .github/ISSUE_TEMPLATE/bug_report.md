---
name: Bug report
about: Something in Agent Factory doesn't work as expected
title: "[Bug] "
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what went wrong.

**Run mode**
- [ ] `factory.py` standalone orchestrator
- [ ] `/forge` Claude Code subagents

**To reproduce**
Steps to reproduce, ideally the exact command:
```bash
python factory.py --theme "..."
# or
/forge "..."
```

**Which stage/agent failed**
- [ ] idea-hunter
- [ ] architect
- [ ] backend-engineer
- [ ] frontend-engineer
- [ ] reviewer
- [ ] debugger
- [ ] devops-engineer (`--devops`)
- [ ] not stage-specific / orchestration itself

**Expected behavior**
What you expected to happen instead.

**Run folder**
The `runs/<timestamp>/` folder involved (attach or paste the relevant file, e.g.
`architecture.md`, `review.md`, or `debug-report.md`), if you can share it.

**Environment**
- Python version:
- `anthropic` SDK version (`pip show anthropic`):
- OS:
- Model(s) in use (default `claude-opus-4-8` / `claude-sonnet-4-6`, or overridden):

**Additional context**
Logs, stack traces, or anything else relevant.
