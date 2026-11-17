---
id: AD-231
title: Compare difftastic and delta on recent slices and settle the code diff setup
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - partly-done
  - global
milestone: m-7
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/91
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #91: compare difftastic with delta on recent slices (C++, TOML/YAML) and settle between delta as pager plus a git dft alias, the documented git d mix, or something else. The 2026-10-30 comment records tested ~/.gitconfig, attributes and lazygit settings. This is the developer's own machine configuration and taste. Done means the developer adopts a setup and the choice is recorded in docs.

**Why it matters:** Reviewing diffs is the developer's main bottleneck.

**Why the developer:** a viewing preference and machine-level git config

**Status when filed (partly-done):** a tested config exists in the issue comment; adoption is not recorded; commit 208d05c prefers extending delta and difftastic
<!-- SECTION:DESCRIPTION:END -->
