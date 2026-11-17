---
id: AD-188
title: Build the advisory earned-stop hook with fire-rate logging
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-181
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#7. The
    implementation loop
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 8: a small Stop hook that runs the fast checks and logs each decision with a denominator so a fire rate can be measured; advisory only because a Stop hook cannot be made fail-closed by configuration and is never the only check. Ideas from spec-flow-plugin, foreman and claimcheck. Promotion to blocking waits for a measured fire rate.

**Why it matters:** Early feedback at stop time, measured before it blocks anything.

**Why an agent:** hook script with fixtures
<!-- SECTION:DESCRIPTION:END -->
