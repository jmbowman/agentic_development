---
id: AD-216
title: Decide whether to maintain the arrows overlay
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-6
dependencies: []
references:
  - docs/arrows/index.yaml
  - AGENTS.md#Navigation
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`docs/arrows/index.yaml` holds `arrows: {}` although the repo has eight design segments, and CLAUDE.md's navigation table points to it and to per-segment docs in `docs/arrows/` that don't exist. Decide whether to populate the overlay (one entry per segment, with status) or drop it from the navigation table. Done when the overlay and the navigation table agree.

**Why it matters:** Either gives segment status at a glance or removes a dead pointer.

**Why the developer:** a choice about which LID artifacts the repo keeps
<!-- SECTION:DESCRIPTION:END -->
