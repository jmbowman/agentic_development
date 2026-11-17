---
id: AD-307
title: Refresh the tool-feedback index and version lines
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/README.md:14
  - docs/tool-feedback/lid.md:3
  - docs/tool-feedback/renovate.md
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Surfaced: docs/tool-feedback/README.md summarizes claude-plugin-eval as two items (gitignored cap, results directory) but the page has four (it also holds the 100,000-character trace cut and the /tmp sandbox write denial); docs/tool-feedback/lid.md says 'in use at v1.4.5' while the repo has updated LID to 1.4.6 (5c20e2f); docs/tool-feedback/renovate.md does not mention the custom regex manager in .github/renovate.json that already bumps the fork's git pin. Correct the README line and these entries. Done when the index matches each page.

**Why it matters:** Keeps the single place that tracks pending upstream feedback accurate.

**Why an agent:** documentation correction against recorded facts
<!-- SECTION:DESCRIPTION:END -->
