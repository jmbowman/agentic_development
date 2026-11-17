---
id: AD-49
title: Decide the carve-out allowing a pinned finalist to be run after evaluation
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - global
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/196
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #196 proposes a run test after step 9 for a full-method verdict that adopts or builds on a tool: run the finalist against the need's key scenarios in throwaway repos, recorded as verified by running. That needs a carve-out from the global rule never to install, build or run a candidate during evaluation: allow only the pinned released binary or package, after evaluation and before the note's review, in a sandbox. The #196 comment gives a recipe (npm pack plus sha256, bwrap with read-only root, tmpfs HOME, no network, throwaway repo outside the source tree, before/after snapshots) and evidence that a run overturned a source-verified claim for Backlog.md. The developer decides whether to allow it and under which sandbox rules; the global rule lives in the developer's global instructions.

**Why it matters:** Allows the evidence that has twice overturned a note's verdict.

**Why the developer:** changes a safety rule in the developer's global instructions
<!-- SECTION:DESCRIPTION:END -->
