---
id: AD-347
title: Widen the parallel-session setup and Orca guide to macOS and Windows
status: To Do
assignee: []
created_date: '2026-11-22T14:49:00Z'
labels: []
milestone: m-6
dependencies:
  - AD-335
references:
  - docs/intent/parallel-sessions/parallel-sessions-design.md
priority: low
type: feature
ordinal: 38000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The parallel-sessions design (docs/intent/parallel-sessions/parallel-sessions-design.md) supports Linux on x86_64 and arm64 in its pilot. It holds every platform-specific fact in one table, so another platform adds a column, plus an install step where the package type differs. Its other scripts stop with an error on any other platform. The setup is meant to help other developers too, so after the AD-335 trial, add macOS and Windows:
- each platform's column: release manifest and package names, install location, launcher form, menu or shortcut entry, and Orca's user-data directory;
- install steps for a .dmg or the Homebrew cask on macOS, and the Windows installer;
- how each platform gives a desktop app DO_NOT_TRACK at every launch;
- the matching sections of docs/wiki/orca.md, whose macOS and Windows notes come from Orca's docs and haven't been tried.
Walk it through LID as a change to the parallel-sessions segment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The platform table has macOS and Windows columns, and each script handles them or stops with a clear error where a step can't apply
- [ ] #2 docs/wiki/orca.md gives tried instructions for macOS and Windows
<!-- AC:END -->
