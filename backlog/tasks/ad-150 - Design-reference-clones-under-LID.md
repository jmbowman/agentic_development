---
id: AD-150
title: Design reference clones under LID
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-6
dependencies: []
references:
  - session:be3cdf4b 2026-11-11
  - session:be3cdf4b 2026-11-08
  - docs/prior-art/2026-11-06-agent-reference-clones.md
  - docs/tool-feedback/vendir.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Take the vendir-based reference-clones design from docs/prior-art/2026-11-06-agent-reference-clones.md (verdict and design) through LID: an HLD check and addition, then docs/intent/reference-clones/ LLD deciding which pieces live in this repo and which copier-python renders (vendir.yml and descriptions.yml repo-owned vs template-owned scripts), the AGENTS.md listing plus problems-only SessionStart hook split (HLD tenet 8), and tests for the note's 'Could not verify' items (cloud-session run, a real Renovate PR, Claude Code settings checks). Developer reviews each stop. Done when the LLD, specs and tests exist.

**Why it matters:** Delivers the reference-clone setup the prior-art skill and consumers would use.

**Why an agent:** agent walks the LID arrow; developer approves stops
<!-- SECTION:DESCRIPTION:END -->
