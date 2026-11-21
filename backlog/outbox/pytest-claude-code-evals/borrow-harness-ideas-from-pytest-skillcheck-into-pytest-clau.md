---
title: Borrow harness ideas from pytest-skillcheck into pytest-claude-code-evals
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- 'docs/prior-art/2026-11-03-interactive-skill-evals.md#Refresh, 2026-11-13: test-framework plugins'
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
target: github.com/jmbowman/pytest-claude-code-evals
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-13 refresh names what is worth borrowing from pytest-skillcheck (MIT): per-turn workspace snapshots, fake gh and curl binaries that log calls, cassette replay, a linter, PEP 723 test files, and credentials symlinked into the scratch home; pytest-copilot adds a `session` marker chaining tests into one conversation, a JSON evidence file and a pricing table. Check each against the plugin's design, adopt the useful ones, and consider whether pytest-skillcheck is an upstream home. Done when a short decision list per idea is recorded in the plugin repo.

**Why it matters:** Improves the plugin without reinventing existing patterns.

**Why an agent:** Read-only comparison then design edits in that repo

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
