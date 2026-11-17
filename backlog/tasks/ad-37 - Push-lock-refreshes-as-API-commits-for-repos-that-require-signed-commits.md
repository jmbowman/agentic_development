---
id: AD-37
title: Push lock refreshes as API commits for repos that require signed commits
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/lock-refresh/lock-refresh-design.md:84
priority: low
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The lock-refresh design defers repos that require signed commits: switch the push to an API commit (for example commit-action) with the App's identity, and list that identity in the repo's `gitIgnoredAuthors`. Implement when such a consumer appears. Done when the workflow works under a signed-commits rule.

**Why it matters:** Unblocks consumers with branch protection requiring signatures.

**Why an agent:** workflow change once triggered

**Also waits on (not tracked as a task):** a consumer repo requires signed commits
<!-- SECTION:DESCRIPTION:END -->
