---
id: AD-62
title: Require links and SHAs in a note to be checked against records before saving
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/156
  - skills/prior-art-search/SKILL.md
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #156 and comment: before saving a prior-art note, extract every link, license and commit from the records with a script and check every link and SHA in the draft against the records, clones or saved git ls-remote output so nothing comes from memory; briefs must tell subagents to copy SHAs from command output. Add the rule to SKILL.md's Save the note section and the brief guidance. The script itself belongs to the validator item under #157. Done means the rule is in the skill with a spec and test.

**Why it matters:** Stops invented links and SHAs from reaching notes.

**Why an agent:** skill text edit
<!-- SECTION:DESCRIPTION:END -->
