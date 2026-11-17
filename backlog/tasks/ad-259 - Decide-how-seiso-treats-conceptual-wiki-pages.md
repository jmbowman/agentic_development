---
id: AD-259
title: Decide how seiso treats conceptual wiki pages
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Verdict
  - >-
    docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Limitations
    checked in source
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
seiso's page kinds are fixed (readme, howto, reference, runbook, agents, adr, plan, changelog, generated) with no explanation or concept kind. Choose a mapping for conceptual pages or record an exemption, and note seiso's false-positive rate on a real wiki, which the note could not verify. Done when the choice is recorded where the seiso gate is designed.

**Why it matters:** Unblocks adopting seiso as the convention gate.

**Why the developer:** Chooses between mapping and exempting; changes the page-kind convention
<!-- SECTION:DESCRIPTION:END -->
