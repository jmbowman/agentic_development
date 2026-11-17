---
id: AD-230
title: Try staleness as commits since a recorded SHA beside extant and blockwatch
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-270
references:
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
priority: low
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Doctrine counts staleness as commits touching a page's paths since a recorded SHA, ancestry-guarded, and reports 'unknown' when undecidable (a shallow clone); only 8.5% of its memories were ever verified by an agent, so checks beat attestation. Prototype this as a drift check for knowledge pages and compare with extant and blockwatch on this repo's docs.

**Why it matters:** A drift signal that needs no markup.

**Why an agent:** small prototype
<!-- SECTION:DESCRIPTION:END -->
