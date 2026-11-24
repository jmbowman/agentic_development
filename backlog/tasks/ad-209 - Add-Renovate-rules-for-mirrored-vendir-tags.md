---
id: AD-209
title: Add Renovate rules for mirrored vendir tags
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T05:59:00Z'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-204
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
  - renovate/default.json
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add to the Renovate preset: a `groupName` rule per mirrored dependency so the vendir tag and the dependency move in one PR, `dependencyDashboardApproval` for major updates in those groups, lock-file maintenance off for the vendir manager, and a vendir binary available wherever Renovate runs (the artifact step runs plain `vendir sync` and can take over a minute for a Qt-sized repo). Done when a dry run shows the grouped PR and a major is held for approval.

**Why it matters:** Keeps mirrored sources at the version the repo uses automatically.

**Why an agent:** preset config and dry run
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Scope the lock-file maintenance rule to the reference-clone vendir files only (for example by matchFileNames): this repo’s root vendir.yml, which vendors the task tool’s YAML parser, relies on lock-file maintenance to follow oneyaml main (TASK-REPO-010 in docs/intent/task-tracker/task-tracker-specs.md). That repo-level rule should win anyway, but a preset rule scoped to its own files avoids the clash in consumers that vendor this way too.
<!-- SECTION:NOTES:END -->
