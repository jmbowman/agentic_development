---
id: AD-59
title: 'Harden prior-art-search verification: provenance, safety, native audit'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/156
  - skills/prior-art-search/references/verification.md
  - skills/prior-art-search/SKILL.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #156 and comment: add to references/verification.md and SKILL.md (Safety, step 4): a provenance check (a hit that copies another repo's description or license copyright, or whose README pushes a binary installer, gets its original found by name and the copy rejected); never start an agent session rooted inside a candidate clone (its CLAUDE.md would load as instructions); native audit in step 4 (check what the agent harness loads from directories it can read: nested CLAUDE.md, AGENTS.md and .claude/skills load on demand, additionalDirectories loads none); and a comparison article, listicle or aggregator found by web search is a pointer to candidates, never evidence. Needs spec, test and eval updates.

**Why it matters:** Prevents lookalike repos and prompt injection from entering notes.

**Why an agent:** skill text edit following a written proposal
<!-- SECTION:DESCRIPTION:END -->
