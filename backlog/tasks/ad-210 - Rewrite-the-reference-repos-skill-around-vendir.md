---
id: AD-210
title: Rewrite the reference-repos skill around vendir
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-205
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write a `reference-repos` skill in skills/ under Apache-2.0, rewritten around vendir (the older GPL-2.0-or-later skill's text must not be copied unless its author agrees). Procedures: choose the kind (explore, mirror, comparison), add an entry (look up the default branch with `git ls-remote --symref`, confirm the ref, standard settings and excludes, description in our own words, sync), run a major upgrade, remove an entry. Done through LID with evals.

**Why it matters:** Lets any agent add or retire a reference clone correctly.

**Why an agent:** skill authoring through LID
<!-- SECTION:DESCRIPTION:END -->
