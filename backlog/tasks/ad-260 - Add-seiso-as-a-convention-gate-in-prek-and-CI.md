---
id: AD-260
title: Add seiso as a convention gate in prek and CI
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies:
  - AD-258
  - AD-259
references:
  - docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install seiso at a pinned version through mise, run it in prek and CI over knowledge-base pages, and exclude docs/intent/, docs/arrows/ and docs/high-level-design.md so LID keeps its own checks. Done when `mise run check` fails on a page that breaks a convention and passes on this repo's current docs. Check seiso's false-positive rate on real pages first (the note could not verify it) and report it.

**Why it matters:** Makes the page conventions mechanically enforced.

**Why an agent:** Tooling change once the conceptual-page choice is made
<!-- SECTION:DESCRIPTION:END -->
