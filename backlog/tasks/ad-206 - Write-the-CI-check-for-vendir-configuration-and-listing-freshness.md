---
id: AD-206
title: Write the CI check for vendir configuration and listing freshness
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-150
  - AD-205
references:
  - docs/prior-art/2026-11-06-agent-reference-clones.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A check that fails when a vendir entry lacks skipInitSubmodules or lfsSkipSmudge or the standard excludes, has a depth other than 1 (unless a full-SHA ref with depth 0), sits in the wrong file (tag in explore.yml, branch ref in vendir.yml or compare.yml), uses a non-HTTPS or credential-bearing URL, is a mirror whose tag does not match the mirrored dependency's version via descriptions.yml, or when the AGENTS.md listing differs from generate-only output, or CLAUDE.md is not a symlink to AGENTS.md.

**Why it matters:** Keeps the clone setup safe and in step with its dependencies.

**Why an agent:** check script with fixtures
<!-- SECTION:DESCRIPTION:END -->
