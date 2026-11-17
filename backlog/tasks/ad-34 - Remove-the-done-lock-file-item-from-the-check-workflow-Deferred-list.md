---
id: AD-34
title: Remove the done lock-file item from the check-workflow Deferred list
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-2
dependencies: []
references:
  - docs/intent/check-workflow/check-workflow-design.md:120
  - docs/intent/lock-refresh/lock-refresh-design.md
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`docs/intent/check-workflow/check-workflow-design.md` still lists 'Consumer lock files and template updates' as Deferred item 4 and calls a workflow on Renovate's branches 'the likely mechanism', but that workflow exists (`.github/workflows/lock-refresh.yml`, with its own lock-refresh LLD and specs). Rewrite the item out, pointing to the lock-refresh design, per the docs-carry-current-intent rule. Done when the Deferred list holds only open items.

**Why it matters:** Keeps the design readable cold.

**Why an agent:** a docs fix with no judgment needed
<!-- SECTION:DESCRIPTION:END -->
