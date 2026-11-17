---
id: AD-133
title: Reconcile the 2026-11-03 eval note's verdict with the interactive-evals design
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-5
dependencies: []
references:
  - docs/prior-art/2026-11-03-interactive-skill-evals.md#Verdict
  - docs/intent/interactive-evals/interactive-evals-design.md
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-03 note's verdict is the Claude Agent SDK driving the session plus tui-test plus a small harness. The interactive-evals design (commit eeb9a44) instead moves the harness into the separate pytest-claude-code-evals plugin, which runs Claude Code in a terminal emulator and answers dialogs with hooks. The note's could-not-verify items (tui-test idle waits against the spinner, how the SDK returns a dismissed dialog, SDK issue #767) may be moot. Add a pointer in the note to the design and mark what still applies. Done when the note and design agree.

**Why it matters:** Keeps the prior-art record honest about what was built.

**Why an agent:** Docs edit
<!-- SECTION:DESCRIPTION:END -->
