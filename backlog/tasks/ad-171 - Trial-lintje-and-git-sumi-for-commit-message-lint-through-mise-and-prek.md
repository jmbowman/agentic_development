---
id: AD-171
title: Trial lintje and git-sumi for commit-message lint through mise and prek
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#12.
    Commit, pull request and merge autonomy
  - docs/prior-art/2026-11-09-agentic-development-process.md
  - docs/high-level-design.md:60
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Check whether lintje (requires a blank line and meaningful body, rejects Conventional Commits, no first-party pre-commit hook) can be pinned through mise and wired as a commit-msg hook in .config/prek.toml, and compare git-sumi (hook and header regex, cannot require a body). The need is this repo's commit format: summary line, blank line, body, as in AGENTS.md. Done when one is wired as a commit-msg hook and passes on a sample or the verdict records why neither fits.

**Why it matters:** Cheap form check for the developer's commits (rung 0).

**Why an agent:** a short trial and config
<!-- SECTION:DESCRIPTION:END -->
