---
id: AD-52
title: Add a fixed portability checklist and license-field rule to prior-art-search
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/159
  - skills/prior-art-search/references/verification.md
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
Issue #159: give a fixed two-part portability check for skills found (frontmatter keys against the agent skills spec, then host dependencies in the body such as CLAUDE_PLUGIN_ROOT, .claude/commands, required CLI or MCP server); state that when a skill frontmatter license disagrees with the LICENSE file the file wins; and say a skills.sh miss does not mean a tool has no skill, so list SKILL.md files in the clone. Add to skills/prior-art-search/SKILL.md or references/verification.md, with spec and test.

**Why it matters:** Makes portability judgments consistent across notes.

**Why an agent:** skill text edit
<!-- SECTION:DESCRIPTION:END -->
