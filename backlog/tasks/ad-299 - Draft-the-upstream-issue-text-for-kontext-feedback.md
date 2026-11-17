---
id: AD-299
title: Draft the upstream issue text for kontext feedback
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/kontext.md
priority: medium
type: upstream
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft an issue for patkusch/kontext from docs/tool-feedback/kontext.md entry 1: `package.json:41` declares `@patkusch/kontext` 0.1.0 but the npm registry returned 404 (checked 2026-11-06); ask for a publish or tagged releases so mise and Renovate can pin it. Re-check the registry first, since it may have been published since. Done when the draft is shown inline or the entry is closed.

**Why it matters:** Needed before the optional staleness check can be pinned.

**Why an agent:** text plus one registry check
<!-- SECTION:DESCRIPTION:END -->
