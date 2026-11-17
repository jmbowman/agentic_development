---
id: AD-39
title: Decide on a central committer to keep the App key out of consumers
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/lock-refresh/lock-refresh-design.md:86
priority: low
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The lock-refresh design defers keeping the GitHub App's private key out of every consumer, using a central repo that makes the commits (securefix-action's client and server design), to revisit if per-repo secrets become a burden. Decide when that point is reached. Done when recorded.

**Why it matters:** Reduces the blast radius of the App's key across repos.

**Why the developer:** a security and operations judgment about secrets

**Also waits on (not tracked as a task):** per-repo secrets become a burden
<!-- SECTION:DESCRIPTION:END -->
