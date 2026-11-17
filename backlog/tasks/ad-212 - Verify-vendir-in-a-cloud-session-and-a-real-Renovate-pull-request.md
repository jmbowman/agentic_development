---
id: AD-212
title: Verify vendir in a cloud session and a real Renovate pull request
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-205
  - AD-209
references:
  - >-
    docs/prior-art/2026-11-06-agent-reference-clones.md#Limitations checked in
    source
priority: medium
type: chore
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Needs the developer's accounts: run the clone setup in a Claude Code cloud session (a hard criterion still untested) and confirm in a real Renovate PR that the artifact step updates vendir.lock.yml with the new tag's commit, gitignored clones stay out of the PR's commit, a vendir binary exists in the Renovate environment actually used, and the major-update approval flow works for a grouped mirror entry.

**Why it matters:** Closes the one hard criterion still unverified.

**Why the developer:** cloud session and Renovate run under the developer's accounts
<!-- SECTION:DESCRIPTION:END -->
