---
id: AD-173
title: Write path-scoped rule files for code authoring as negative constraints
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#7. The
    implementation loop
  - docs/high-level-design.md:61
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use Claude Code's native `.claude/rules/*.md` with `paths:` to load compact authoring rules for the files an agent touches. Write each rule as a 'don't', traced to a real failure (a large study found every helpful rule was a negative constraint). Done when rule files exist in the repo and template with a test or eval showing they load.

**Why it matters:** Keeps authoring rules small and loaded only where relevant.

**Why an agent:** writing rule files from recorded failures
<!-- SECTION:DESCRIPTION:END -->
