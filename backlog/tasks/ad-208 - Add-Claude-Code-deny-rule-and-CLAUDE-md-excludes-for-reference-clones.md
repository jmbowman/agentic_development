---
id: AD-208
title: Add Claude Code deny rule and CLAUDE.md excludes for reference clones
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-204
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Commit Claude Code settings in the template: `claudeMdExcludes` for `**/.reference-repos/**` as a second layer, an `Edit(/.reference-repos/repos/**)` deny rule (also covers Write), and optionally `safe.bareRepository=explicit` through the settings env so git ignores bare repositories planted inside a clone. Test each (see the 'Run the unverified reference-clone checks' item).

**Why it matters:** Stops edits to and instruction loading from clones.

**Why an agent:** settings edits
<!-- SECTION:DESCRIPTION:END -->
