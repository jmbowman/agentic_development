---
id: AD-313
title: Decide how releases get tagged automatically
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-9
dependencies: []
references:
  - docs/intent/renovate-preset/renovate-preset-design.md:86
  - docs/prior-art/2026-11-09-agentic-development-process.md:171
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Renovate preset design defers automated tagging after a merge; until then the maintainer tags releases by hand. The design's stated mechanism (cocogitto as 'Slice 2's commit tooling') no longer holds, since the 2026-11-09 prior-art note rejects cocogitto. Decide whether and how to automate tagging, likely with the planned commit-message component. Done when the design names a mechanism or keeps manual tagging with a reason.

**Why it matters:** Keeps releases flowing to consumers without manual tagging.

**Why the developer:** a release-policy decision
<!-- SECTION:DESCRIPTION:END -->
