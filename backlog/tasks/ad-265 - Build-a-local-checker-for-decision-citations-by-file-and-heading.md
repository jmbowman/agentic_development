---
id: AD-265
title: Build a local checker for decision citations by file and heading
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-11-06-decision-records-and-lid.md#Verdict
  - >-
    docs/tool-feedback/lid.md#1. Decision citations from code, checked like
    @spec
  - >-
    docs/tool-feedback/lid.md#1. Decision citations from code, checked like
    `@spec`
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A script run beside lidc in `mise run lid` that resolves citations of the form `<name>.md § <heading>` (never a line number) from code and docs against real headings, failing on a missing file or heading. It must say what a citation means (implements vs mentions), matching LID discussion #33. Done through LID with fixtures; offer upstream after it has run here.

**Why it matters:** Stale decision citations fail instead of staying silently wrong.

**Why an agent:** script through LID
<!-- SECTION:DESCRIPTION:END -->
