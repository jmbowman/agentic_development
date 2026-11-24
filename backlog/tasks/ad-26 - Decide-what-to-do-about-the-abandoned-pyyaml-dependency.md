---
id: AD-26
title: Decide what to do about the abandoned pyyaml dependency
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T06:12:00Z'
labels:
  - issue
milestone: m-2
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/4
  - pyproject.toml:14
  - docs/intent/task-tracker/task-tracker-design.md
  - AD-354
  - AD-355
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: d5de0f02-d865-48c6-82a7-a60f7b5669eb
    role: finished
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Dependency Dashboard (issue #4) flags pyyaml (pep621, pinned at pyyaml==6.0.3 in pyproject.toml line 14, last release 2025-09-25) as abandoned by release inactivity. Decide whether to keep it (it is a stable library), replace it, or set a Renovate rule to ignore the abandonment warning. Done means a decision and, if replacing, an agent item.

**Why it matters:** Silences a standing dashboard warning or removes a risk.

**Why the developer:** judgment on dependency policy
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ruled in AD-336: the task tool drops PyYAML for a vendored copy of oneyaml (pure Python, YAML 1.2), kept current by vendir and Renovate lock-file maintenance, so the tool has no declared dependencies and no lock file. The ruling and its rationale are in docs/intent/task-tracker/task-tracker-design.md (Reading YAML, and the YAML parser and Keeping the vendored parser current rows of Decisions & Alternatives). AD-354 implements it. PyYAML stays a dev dependency for the tests, so the Dependency Dashboard warning remains until those move too.
<!-- SECTION:FINAL_SUMMARY:END -->
