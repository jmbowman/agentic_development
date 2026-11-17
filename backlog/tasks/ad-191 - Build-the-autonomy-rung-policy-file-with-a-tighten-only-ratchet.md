---
id: AD-191
title: Build the autonomy-rung policy file with a tighten-only ratchet
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-157
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#12.
    Commit, pull request and merge autonomy
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 10 part 1: a committed policy file naming the rung (0 developer commits, 1 agent commits on a work branch, 2 agent opens pull requests, never merges to the default branch) as a value only the developer writes, read from the base commit and tightened but never loosened in conversation (dev-process-toolkit's ratchet). Add a courtesy merge-prompt hook that turns merges and publishing into a question to the developer, understood as a speed bump.

**Why it matters:** Needed before any agent-commit rung.

**Why an agent:** policy file and hook with fixtures
<!-- SECTION:DESCRIPTION:END -->
