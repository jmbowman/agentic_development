---
id: AD-263
title: Disable mdbook-lint's ADR002-ADR005 wherever it runs over LID decision docs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies:
  - AD-268
references:
  - docs/prior-art/2026-11-06-decision-records-and-lid.md#Verdict
  - docs/tool-feedback/mdbook-lint.md
  - https://github.com/jmbowman/agentic_development/issues/54
priority: medium
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
mdbook-lint's decision-record rules treat any decisions/ folder as MADR records and fail every LID decision doc; list at least ADR002-ADR005 under `disabled-rules` in `.mdbook-lint.toml` (no wildcard works). This repo does not run mdbook-lint yet, so the work applies when the docs site (#54) or a template documentation layer adds it. Done when the config ships with the rule and a LID decision doc passes.

**Why it matters:** Avoids false failures on every decision doc.

**Why an agent:** config edit
<!-- SECTION:DESCRIPTION:END -->
