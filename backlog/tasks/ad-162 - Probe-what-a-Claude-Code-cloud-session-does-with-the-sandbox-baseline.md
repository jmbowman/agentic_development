---
id: AD-162
title: Probe what a Claude Code cloud session does with the sandbox baseline
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-160
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
priority: medium
type: chore
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Start a cloud session on this repo and record whether the sandbox, protected paths and permission denies apply, and what a hook can and cannot write there. The docs do not cover cloud sessions for this sandbox, so the result decides whether result checks at commit and pull-request time must be the only backstop. Report the findings in the synthesis' enforcement section or the slice's LLD.

**Why it matters:** Tells whether in-session protection holds where cloud work happens.

**Why the developer:** starting a cloud session needs the developer's account
<!-- SECTION:DESCRIPTION:END -->
