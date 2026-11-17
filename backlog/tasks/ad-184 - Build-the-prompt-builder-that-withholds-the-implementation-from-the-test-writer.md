---
id: AD-184
title: >-
  Build the prompt builder that withholds the implementation from the test
  writer
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-141
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#6. Tests
    first
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In LID Phase 5 dispatch, a test-writing subagent gets the EARS lines and the interface and never the implementation; the coding subagent gets the failing tests; a prompt builder enforces what each sees with a leak check that refuses any prompt where withheld text survives (qikly's design, with a test that proves the check can fail). After code exists, edits to tests are flagged as possible drift. Done when the builder and fixtures exist and the cost of the split is measurable.

**Why it matters:** Independence by context has the clearest evidence among test-first effects.

**Why an agent:** script and dispatch prompts
<!-- SECTION:DESCRIPTION:END -->
