---
title: Decide the credentials form for the plugin's isolated sessions
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- docs/intent/interactive-evals/interactive-evals-design.md:94
- docs/prior-art/2026-11-03-interactive-skill-evals.md:142
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
target: github.com/jmbowman/pytest-claude-code-evals
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's interactive-evals LLD leaves to pytest-claude-code-evals how its isolated config directory logs in: a token from `claude setup-token`, a linked credentials file, or an API key. agentic_development's README gives the setup step once it's settled. Decide, weighing cost (API key versus plan usage) and isolation. Done when the plugin's design records the choice.

**Why it matters:** Every scenario run depends on it.

**Why the developer:** involves the developer's accounts and spending

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
