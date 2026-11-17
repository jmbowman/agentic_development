---
id: AD-46
title: Add an extend-upstream comparison before a build verdict in prior-art-search
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/202
  - skills/prior-art-search/SKILL.md
  - docs/prior-art/2026-10-30-change-presentation.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #202: step 10 (Evaluate blends) never asks whether finalists' gaps could be closed by extending them, which conflicts with HLD tenet 2. Before a build verdict or a custom piece larger than small, for each verified finalist and each missed requirement, classify the gap as additive (extension point exists; cite path:line and size S/M/L) or fundamental (with evidence); for additive gaps record upstream receptiveness (outside PRs among recent merges, median time to merge, open-PR backlog, whether the gap's issue exists and the maintainer's stance, AI-contribution policy). Prefer build on (extend upstream) with a fork as fallback. Needs a LID pass: design in docs/intent/prior-art-search/, EARS specs, tests and an eval case.

**Why it matters:** Keeps searches from recommending new tools whose gaps are small missing features upstream.

**Why an agent:** skill, spec and test edits following a written proposal
<!-- SECTION:DESCRIPTION:END -->
