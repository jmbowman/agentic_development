---
id: AD-207
title: Write the SessionStart hook that reports reference-clone problems
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-205
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A SessionStart hook that prints nothing when every clone is healthy and one line per problem otherwise, without quoting clone content: a clone not yet cloned (with the setup command), a mirror or comparison clone whose HEAD differs from the lock, a modified working tree (ignoring excluded files git lists as deleted), any excluded file present on disk, and a directory no configuration names. Explore clones get no staleness check.

**Why it matters:** Catches tampered or missing clones at session start.

**Why an agent:** hook with tests
<!-- SECTION:DESCRIPTION:END -->
