---
id: AD-22
title: Tag a release so consumers get the skills and hooks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-2
dependencies: []
references:
  - README.md#Status
  - docs/high-level-design.md#Versioning
  - git tag v0.3.1
  - copier-python:template/.config/copier-python/apm.yml:10
  - copier-python:template/.config/copier-python/apm.lock.yaml:8
  - apm.yml:7
  - docs/high-level-design.md#System Design (Versioning)
priority: high
type: chore
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: a1359d3a-1543-481a-84a6-bac89eb4e6cc
    role: worked
    date: '2026-11-16'
  - agent: claude-code
    id: adcd9127-7ed6-4e96-997f-ec40e55f351c
    role: created
    date: '2026-10-30'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The template has delivered skills from a lock file since copier-python v0.3.0, but it pins this repo at v0.3.1. The last tag here is v0.3.1, and about 157 commits have landed since, including the session-wrap-up skill, the subagent notes hooks and the harvester. Tag a new release of this repo (major/minor per the HLD's Versioning rules), so template repos can bump their pin. Done when the tag exists and the README's Status no longer says those changes are unreleased.

**Why it matters:** Unblocks the template delivering every skill built since v0.3.1.

**Why the developer:** publishing a release is an outward-facing action
<!-- SECTION:DESCRIPTION:END -->
