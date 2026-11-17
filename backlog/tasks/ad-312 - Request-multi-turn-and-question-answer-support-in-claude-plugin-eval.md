---
id: AD-312
title: Request multi-turn and question-answer support in claude plugin eval
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
  - upstream
milestone: m-9
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-03-interactive-skill-evals.md#Refresh, 2026-11-13:
    test-framework plugins
  - docs/tool-feedback/claude-plugin-eval.md
priority: medium
type: upstream
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The plugin-evals docs say each run is a fresh non-interactive session that never stops to ask for permission, `context.history_file` gives only one new turn, and nothing scripts AskUserQuestion answers. Add this to docs/tool-feedback/claude-plugin-eval.md (it does not mention it) and raise a feature request upstream. Done when the feedback page has the entry and the request is filed or dropped.

**Why it matters:** Could let plain `claude plugin eval` replace parts of the harness.

**Why the developer:** Outward-facing upstream request
<!-- SECTION:DESCRIPTION:END -->
