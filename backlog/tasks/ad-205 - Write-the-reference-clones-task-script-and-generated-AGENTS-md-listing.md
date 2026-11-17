---
id: AD-205
title: Write the reference-clones task script and generated AGENTS.md listing
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-204
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A task script run by the mise setup and refresh tasks that calls `vendir sync` once per entry (so one failure affects one entry), uses --locked for mirror and comparison entries, switches tag fetching off for explore entries via GIT_CONFIG_* (appending to any existing GIT_CONFIG_COUNT), removes clones no configuration names, and regenerates a listing in AGENTS.md between markers from the committed configs only, with a generate-only mode for CI. The listing never contains clone text and tells agents to treat clone content as reference material, not instructions.

**Why it matters:** Makes the clones discoverable without foreign text entering instructions.

**Why an agent:** script with tests
<!-- SECTION:DESCRIPTION:END -->
