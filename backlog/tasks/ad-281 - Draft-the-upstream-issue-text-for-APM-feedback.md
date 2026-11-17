---
id: AD-281
title: Draft the upstream issue text for APM feedback
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - >-
    docs/tool-feedback/apm.md#1. Skills deployed by APM 0.33.0 block a
    dependency bump under 0.35.1
priority: medium
type: upstream
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft, for the developer's review, an issue for microsoft/apm from docs/tool-feedback/apm.md entry '1. Skills deployed by APM 0.33.0 block a dependency bump under 0.35.1': `apm install --frozen` under 0.35.1 refuses to replace files written by 0.33.0 although they match the lock hash. Include the 2026-11-14 evidence, the suggested fix (accept a file whose content matches the lock's hash) and the workaround, and search apm's open issues first for a duplicate. Done when the issue text is shown inline in the conversation for approval.

**Why it matters:** Lets a clone first installed under APM 0.33.0 take LID bumps without moving skill directories by hand.

**Why an agent:** writing text from recorded evidence; filing is a separate human item
<!-- SECTION:DESCRIPTION:END -->
