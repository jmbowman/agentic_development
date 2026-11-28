---
id: AD-177
title: 'Build review triage: verify at the cited line, fingerprint, refute, route'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-163
  - AD-175
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#9. Review
    waves and triage
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
  - docs/decisions/review-wave-stopping.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Triage in BMAD's order with Compound Engineering's mechanics: verify each finding at its cited line before any grouping, fingerprint and dedupe in a script, require a quote of the line, count no agreement between same-model reviewers as corroboration, one independent validator must cite refuting evidence to reject, then route to an arrow level (intent gap, bad plan, patch, defer). Route each severe finding to what settles it (a failing test, demonstration or probe) and check each fix landed everywhere a reader reads, per doctrine. Per docs/decisions/review-wave-stopping.md, triage also rules each verified finding fix now, backlog task or not worth it for the artifact's intended uses (refuting evidence is needed to reject a finding as false, not as not worth fixing), sends findings that choose between readings of intent to the developer as forks, and tags accepted findings that the previous wave's fixes caused. Done when it writes dispositions into the ledger.

**Why it matters:** Cuts rejected findings and routes real ones to the right arrow level.

**Why an agent:** script plus prompt design
<!-- SECTION:DESCRIPTION:END -->
