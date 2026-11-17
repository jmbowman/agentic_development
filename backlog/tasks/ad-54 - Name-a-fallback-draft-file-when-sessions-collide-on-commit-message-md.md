---
id: AD-54
title: Name a fallback draft file when sessions collide on commit-message.md
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/159
  - CLAUDE.md
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #159 and its #98 comment: a second session could not write its draft because the shared root commit-message.md belonged to another uncommitted change, twice. CLAUDE.md's working rules already say to re-read before writing and not replace an uncommitted draft, but name no fallback. Add a rule such as a gitignored commit-message-<topic>.md, make sure .gitignore covers it, and tell the developer to commit it with git commit -F. Done means CLAUDE.md and .gitignore updated.

**Why it matters:** Parallel sessions stop blocking on each other's drafts.

**Why an agent:** small edit to working rules
<!-- SECTION:DESCRIPTION:END -->
