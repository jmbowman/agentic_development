---
id: AD-26
title: Decide what to do about the abandoned pyyaml dependency
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-2
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/4
  - pyproject.toml:14
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Dependency Dashboard (issue #4) flags pyyaml (pep621, pinned at pyyaml==6.0.3 in pyproject.toml line 14, last release 2025-09-25) as abandoned by release inactivity. Decide whether to keep it (it is a stable library), replace it, or set a Renovate rule to ignore the abandonment warning. Done means a decision and, if replacing, an agent item.

**Why it matters:** Silences a standing dashboard warning or removes a risk.

**Why the developer:** judgment on dependency policy
<!-- SECTION:DESCRIPTION:END -->
