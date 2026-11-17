---
id: AD-227
title: Frame hook output that echoes repo text as data with a nonce delimiter
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adopt doctrine's implemented technique for any hook that echoes repo text (the planned decision index, clone-health and task-list hooks): wrap the text in a delimited block with a nonce terminator and scrub control characters, and label it as data. Add a shared helper plus fixtures that show an echoed injection-shaped line cannot close the block. Apply to subagent_notes.py or new hooks as they appear.

**Why it matters:** Reduces injection risk from echoed repo text.

**Why an agent:** helper with fixtures
<!-- SECTION:DESCRIPTION:END -->
