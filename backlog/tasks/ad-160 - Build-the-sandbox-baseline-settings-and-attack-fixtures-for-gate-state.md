---
id: AD-160
title: Build the sandbox baseline settings and attack fixtures for gate state
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-143
  - AD-161
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#13.
    Enforcement and its calibration
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 1 of the build order: configure sandbox on, a protected directory for gate state, permission denies for the file tools, the unsandboxed escape removed, fail-if-unavailable, credential reads denied, plus a fixture suite that attacks each bypass (encoded commands, interpreters, heredocs, symlinks, file tools, the unsandboxed request) and must refuse all. The first test is the undocumented precedence of a write-deny inside the working directory; also check that `.claude/skills` being write-denied does not break the skills-install task run through the shell. Done when the fixtures pass on Linux and run again on each Claude Code update.

**Why it matters:** Its answer decides how much machinery every later gate needs.

**Why an agent:** configuration and fixtures a coding agent can write and run locally once the sandbox is installed
<!-- SECTION:DESCRIPTION:END -->
