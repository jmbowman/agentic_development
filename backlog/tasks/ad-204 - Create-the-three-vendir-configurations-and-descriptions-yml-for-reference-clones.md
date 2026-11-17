---
id: AD-204
title: >-
  Create the three vendir configurations and descriptions.yml for reference
  clones
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build the clone manager from the 2026-11-06 reference-clones verdict: `.reference-repos/` with vendir.yml (mirror entries pinned to a tag), compare.yml (comparison entries) and explore.yml (branch entries, gitignored lock), each entry depth 1, skipInitSubmodules and lfsSkipSmudge true, excludePaths for .claude, CLAUDE.md, CLAUDE.local.md and AGENTS.md, plus descriptions.yml and gitignore entries. Done when a fresh checkout restores the same clones and an exploration entry tracks a branch.

**Why it matters:** Gives agents pinned, read-only copies of other repos for exact answers from source.

**Why an agent:** configuration files and gitignore
<!-- SECTION:DESCRIPTION:END -->
