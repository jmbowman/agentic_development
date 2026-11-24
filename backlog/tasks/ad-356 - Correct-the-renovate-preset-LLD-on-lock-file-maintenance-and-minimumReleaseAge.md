---
id: AD-356
title: Correct the renovate-preset LLD on lock-file maintenance and minimumReleaseAge
status: To Do
assignee: []
created_date: '2026-11-24T06:12:00Z'
labels:
  - surfaced
milestone: m-1
dependencies: []
priority: low
type: docs
ordinal: 47000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: d5de0f02-d865-48c6-82a7-a60f7b5669eb
    role: created
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/intent/renovate-preset/renovate-preset-design.md says lock-file maintenance is not covered by minimumReleaseAge. In Renovate 44.257.5 it is: the update inherits minimumReleaseAge, has no release timestamp, and minimumReleaseAgeBehaviour defaults to timestamp-required, so renovate/stability-days stays pending (workers/repository/update/branch/status-checks.js:89-110, util/minimum-release-age.js:100-116). It still merges because platformAutomerge does not wait for that status, which is not a required check: PR #300 merged with it pending. Found in the AD-336 review wave; the task-tracker LLD (Reading YAML) relies on that behaviour. Restate the preset LLD line, and decide whether to set minimumReleaseAge to null for lock-file maintenance so the status stops showing pending.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The renovate-preset LLD states how minimumReleaseAge applies to lock-file maintenance, matching Renovate source and a real PR
<!-- AC:END -->
