---
id: AD-315
title: Group related Renovate updates when volume gets noisy
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-9
dependencies: []
references:
  - docs/intent/renovate-preset/renovate-preset-design.md:85
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Renovate preset design defers grouping related updates (for example all Astral tools) into one branch, to add if update volume becomes noisy. The git log shows frequent single-tool update PRs (renovate, ty, ruff, uv). When noise warrants, add `packageRules` groups to `renovate/default.json` with specs and tests. Done when grouped PRs appear.

**Why it matters:** Fewer PRs and CI runs for every consumer.

**Why an agent:** preset change once triggered

**Also waits on (not tracked as a task):** developer judges update volume noisy
<!-- SECTION:DESCRIPTION:END -->
