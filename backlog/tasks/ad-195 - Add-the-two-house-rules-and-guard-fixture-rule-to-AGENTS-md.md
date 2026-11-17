---
id: AD-195
title: Add the two house rules and guard-fixture rule to AGENTS.md
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Cross-cutting
    design principles
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#13.
    Enforcement and its calibration
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The synthesis says to adopt two house rules now: judge a change with the base commit's configuration, and every guard ships must-reject and must-accept fixtures (any exception inside a guard denies). Add them to AGENTS.md working rules with the reason for each, so every hook or checker written here follows them. Check with grep that no existing rule already says this.

**Why it matters:** Calibrates every future guard from day one.

**Why an agent:** short rule edit; the developer approves wording
<!-- SECTION:DESCRIPTION:END -->
