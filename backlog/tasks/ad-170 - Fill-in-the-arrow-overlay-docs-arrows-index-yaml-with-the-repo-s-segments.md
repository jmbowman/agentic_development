---
id: AD-170
title: Fill in the arrow overlay docs/arrows/index.yaml with the repo's segments
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-216
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#11.
    Traceability and staleness
  - docs/arrows/index.yaml
priority: medium
type: chore
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/arrows/index.yaml still has `arrows: {}`, so lidc's overlay-dependent checks have nothing to report and an impact query would have no segments. Add the repo's arrow segments (one per leaf LLD under docs/intent/) in lidc's schema. Done when `lidc check` accepts the overlay and the segments match the docs/intent folders.

**Why it matters:** Enables overlay checks and the future impact query.

**Why an agent:** structured file derived from existing docs
<!-- SECTION:DESCRIPTION:END -->
