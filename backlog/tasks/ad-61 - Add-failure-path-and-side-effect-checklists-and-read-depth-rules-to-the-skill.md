---
id: AD-61
title: Add failure-path and side-effect checklists and read-depth rules to the skill
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
  - skills/prior-art-search/references/verification.md:30
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #156 and comment: add per-kind checklists to verification.md. Sync tools: partial runs, rate limits, errors, deletions and closures, what moves the watermark. File-writing tools: what they overwrite, prune, stage, commit and add to .gitignore, CLAUDE.md, git config or global settings, across every install, init, setup and integration command, not just init. A claimed behavior needs a verified caller (code with no caller proves nothing). Prose-and-script skills: tag what the agent is told to do differently from enforced behavior. WebFetch and web-search reads are docs-level, never full (check verification.md line 30 first); long single-page docs need a second fetch at an offset.

**Why it matters:** Finds silent data loss and side effects that docs-level reads miss.

**Why an agent:** skill text edit

**Status when filed (partly-done):** verification.md already defines full read depth (line 30); checklists not found
<!-- SECTION:DESCRIPTION:END -->
