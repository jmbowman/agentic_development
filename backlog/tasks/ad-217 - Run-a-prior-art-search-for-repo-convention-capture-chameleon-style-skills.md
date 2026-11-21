---
id: AD-217
title: Run a prior-art search for repo-convention capture (chameleon style) skills
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-6
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/203
priority: low
type: search
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #203 wants skills or tools that analyze a target repo (weighting the maintainer's recent code and commits), capture conventions in a standard descriptive format (docstrings, settings patterns, error idioms, test framework, dependency appetite, commit and PR format, CI expectations), pass them to coding agents, and optionally check a draft diff. Run the prior-art-search skill for repo-convention extractors, AGENTS.md generators and style or lint inference tools. Done means a docs/prior-art/ note with candidates classified and licenses read from files. Motivating case: the paper-search-mcp shared-http-layer proposal needed several rounds to match the maintainer's style.

**Why it matters:** Cuts review rounds on contributions to other people's repos.

**Why an agent:** a prior-art-search skill run; the developer approves scope and cost
<!-- SECTION:DESCRIPTION:END -->
