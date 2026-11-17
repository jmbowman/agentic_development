---
id: AD-301
title: Draft the upstream issues for mdbook-lint feedback
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/mdbook-lint.md
priority: medium
type: upstream
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft issues for joshrotenberg/mdbook-lint from docs/tool-feedback/mdbook-lint.md: 1. ADR rules fire on any `decisions/` folder and fail LID decision docs (`format.rs:107-147`, `registry.rs:156-211`); 2. documented `[rules] "ADR*"` wildcard and `[ADR016] min-options` have no effect (`config.rs:26-32`). Done when drafts are shown inline.

**Why it matters:** Every LID repo using mdbook-lint otherwise has to disable ADR rules one by one.

**Why an agent:** text from recorded source reads
<!-- SECTION:DESCRIPTION:END -->
