---
id: AD-320
title: Trial an in-repo architecture-map tool when code-derived PR diffs are wanted
status: To Do
assignee: []
created_date: '2026-11-18T04:30:00Z'
labels: []
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-11-17-in-repo-architecture-maps.md#Verdict
priority: low
type: spike
ordinal: 7000
performer: agent
agent_tier: strong
effort: L
waiting: the developer, to say when a repo needs code-derived PR architecture diffs
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-17 architecture-maps note (docs/prior-art/2026-11-17-in-repo-architecture-maps.md) defers pull-request architecture diffs derived from code. When a repo needs them (a change whose structure Mermaid diagrams in the HLD and LLDs don't show well enough), trial groma.md with its Action in that repo, or LikeC4 with likec4-architecture-diff-action if a hand-written model is enough. Check the note's limits first: groma.md's prototype status and filesystem plan, its AGENTS.md block, its global Backlog.md install when none is on PATH, and its Pages publisher. Done when a trial report is recorded and the note's refresh trigger is updated.

**Why it matters:** The second common use (reviewing drift on a PR with a visual aid) is only partly met today.

**Why an agent:** the trial steps are stated; the trigger is the developer's
<!-- SECTION:DESCRIPTION:END -->
