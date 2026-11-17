---
id: AD-60
title: 'Sharpen license reading rules: rider grep, canonical texts, registry fields'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - partly-done
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/156
  - skills/prior-art-search/references/verification.md:19
  - skills/prior-art-search/SKILL.md:152
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #156 and comment: SKILL.md line 152 and verification.md line 19 already require reading the whole license file. Add the rest: grep for rider, Commons Clause and additional terms but exclude boilerplate (restriction in MIT, additional terms in Apache-2.0 Section 5) or report hits with lines; keep canonical texts of common licenses to diff against; a registry license field with no readable file is not read. Edit verification.md with spec and test updates.

**Why it matters:** Catches licenses labeled MIT that carry riders.

**Why an agent:** skill text edit

**Status when filed (partly-done):** whole-file reading is already required; rider grep details and canonical-text diff not confirmed
<!-- SECTION:DESCRIPTION:END -->
