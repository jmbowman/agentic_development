---
id: AD-209
title: Add Renovate rules for mirrored vendir tags
status: To Do
assignee: []
created_date: '2026-11-16'
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
