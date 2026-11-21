---
id: AD-27
title: Make scripts/run_evals.py set TMPDIR outside /tmp itself
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-2
dependencies: []
references:
  - evals/README.md:35
  - scripts/run_evals.py
  - docs/tool-feedback/claude-plugin-eval.md
  - mise.toml
priority: medium
type: chore
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 83baf9d8-f511-40e3-875d-3d561ab7a7c4
    role: created
    date: '2026-11-16'
  - agent: claude-code
    id: f4b2080f-847f-4a0d-a503-34339722eeb7
    role: worked
    date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The runner's sandbox denies writes to //tmp, so eval commands currently need a TMPDIR=~/.cache/agentic-development/eval-tmp prefix (documented in evals/README.md). Make scripts/run_evals.py (and so mise run eval) create and export that directory itself, as a change to the repo-setup design/specs first, then tests, then code. Done when mise run eval works without the prefix and evals/README.md drops the 'Until mise run eval sets it' wording.

**Why it matters:** Removes a trap that made every eval write fail silently.

**Why an agent:** small scripted change with a documented target behavior
<!-- SECTION:DESCRIPTION:END -->
