---
id: AD-314
title: Fix the stale cocogitto reference in the Renovate preset design
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-9
dependencies:
  - AD-313
references:
  - docs/intent/renovate-preset/renovate-preset-design.md:86
  - docs/prior-art/2026-11-09-agentic-development-process.md:171
  - docs/high-level-design.md:60
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`docs/intent/renovate-preset/renovate-preset-design.md` Deferred item 2 says 'Slice 2's commit tooling (cocogitto) can derive versions from commit messages', but `docs/prior-art/2026-11-09-agentic-development-process.md` rejects cocogitto, and the HLD now plans a commit-message and PR-description skill instead. Reword the item to state the current plan, after the tagging decision. Done when no design doc cites cocogitto as planned tooling.

**Why it matters:** Removes a contradiction a cold reader would trip on.

**Why an agent:** a docs fix once the decision exists
<!-- SECTION:DESCRIPTION:END -->
