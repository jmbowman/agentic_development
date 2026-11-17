---
id: AD-108
title: Check in APM's source whether it installs a package from a subdirectory
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:534
  - docs/tool-feedback/claude-plugin-eval.md
priority: low
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The prior-art-search LLD defers moving the plugin out of the repo root (to escape `claude plugin eval`'s 20,000-entry cap) and says a move needs APM's support for installing a package from a repository subdirectory checked in its source. Read APM's source read-only and record the answer with file:line in the LLD's Deferred entry. Done when the claim is tagged verified in source or docs only.

**Why it matters:** Supplies the evidence the move decision needs.

**Why an agent:** a read-only source check
<!-- SECTION:DESCRIPTION:END -->
