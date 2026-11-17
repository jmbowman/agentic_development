---
id: AD-32
title: Check whether CLAUDE_ENV_FILE survives a cloud-session resume
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/repo-setup/repo-setup-design.md:126
priority: medium
type: chore
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repo-setup design defers whether `CLAUDE_ENV_FILE` survives a resume in the same container; the SessionStart hook's check for an existing line makes either answer safe. Probe it in a cloud session and record the result. Done when the Deferred entry is replaced by the verified answer.

**Why it matters:** Low: either answer is already safe.

**Why the developer:** needs a Claude Code cloud session on the developer's account
<!-- SECTION:DESCRIPTION:END -->
