---
id: AD-154
title: >-
  Add a Superseded-by header to the 2026-10-19 reference-clones note and fix
  links to it
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-6
dependencies: []
references:
  - docs/prior-art/2026-10-19-agent-reference-clones.md
  - docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Verdict
  - docs/prior-art/2026-11-06-agent-reference-clones.md
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Commit 6e0018f says the 2026-11-06 reference-clones note supersedes the 2026-10-19 one (west replaced by vendir), but the 2026-10-19 note's header has no 'Superseded by' line and still presents west as the verdict. The knowledge-base note links to it at its cross-repo lookup step, and the docs-site note is companion to it. Add the header and repoint links to the 2026-11-06 note. Done when the old note carries a supersession line and no live doc cites its verdict.

**Why it matters:** Stops readers acting on a replaced verdict.

**Why an agent:** Docs edit
<!-- SECTION:DESCRIPTION:END -->
