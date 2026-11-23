---
id: AD-351
title: >-
  Close two installer rough edges: overwriting a versioned package mid-install,
  and the icon hint
status: To Do
assignee: []
created_date: '2026-11-23T12:08:00Z'
labels:
  - loose-end
milestone: m-6
dependencies: []
references:
  - tools/parallel-sessions/orca_install.py
  - docs/intent/parallel-sessions/parallel-sessions-specs.md
  - AD-334
priority: low
type: bug
ordinal: 42000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 27e13044-1d02-40c4-90d7-0134d1214b1d
    role: created
    date: '2026-11-23'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two edges left in orca_install.py by AD-334. (1) If another program creates orca-<version>.AppImage between the installer's check and its rename, the rename overwrites it, against PAR-INSTALL-017; linking the temporary file into place (os.link, which fails when the name exists) would close the window, and the test that expects a rename needs to accept that. (2) On a first install, setup's menu entry has no icon until setup runs again after the installer saves icon.png; the developer hit this. The closing message could say to re-run setup only when it has just saved an icon the menu entry doesn't use yet.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An install never replaces a versioned package that appears during it
- [ ] #2 After a first install, the installer's message says that re-running setup adds the icon
<!-- AC:END -->
