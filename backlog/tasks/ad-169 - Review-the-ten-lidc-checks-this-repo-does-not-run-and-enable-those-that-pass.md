---
id: AD-169
title: Review the ten lidc checks this repo does not run and enable those that pass
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#11.
    Traceability and staleness
  - mise.toml:61-62
priority: medium
type: chore
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
lidc registers thirteen checks and mise run lid runs three (reverse-orphan, coverage, spec-id-format). Run the other ten (index schema, arrow-doc structure and references, orphaned design files, cited-but-open specs, LLD decision tables, dependency cycles, implementing-artifact paths, decision-doc structure, prefix coherence) and turn on those that pass or need small fixes in the `lid` task in mise.toml. Done when each of the ten is enabled or has a recorded reason.

**Why it matters:** Free traceability checks the repo already has installed.

**Why an agent:** run, triage and edit a mise task
<!-- SECTION:DESCRIPTION:END -->
