---
id: AD-241
title: Mark generated files linguist-generated in .gitattributes
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-7
dependencies: []
references:
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
priority: medium
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a `.gitattributes` marking lock files (uv.lock, mise.lock, apm.lock.yaml), dependency sidecars and vendored skill copies as `linguist-generated` so their diffs collapse in PRs. The note found none of the three repos had a .gitattributes file; this repo still has none. Done when a Renovate lock-file PR shows those files collapsed. Markdown review should use `--word-diff` since difftastic does not parse Markdown.

**Why it matters:** Hides generated noise at the source with no risk.

**Why an agent:** One small file
<!-- SECTION:DESCRIPTION:END -->
