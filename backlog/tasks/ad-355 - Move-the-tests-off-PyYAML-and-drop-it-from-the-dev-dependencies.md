---
id: AD-355
title: Move the tests off PyYAML and drop it from the dev dependencies
status: To Do
assignee: []
created_date: '2026-11-24T06:12:00Z'
labels:
  - loose-end
milestone: m-2
dependencies:
  - AD-354
references:
  - https://github.com/jmbowman/agentic_development/issues/4
priority: low
type: chore
ordinal: 46000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: d5de0f02-d865-48c6-82a7-a60f7b5669eb
    role: created
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After AD-354 the task tool reads YAML with its vendored oneyaml parser, but five test files (tests/support.py, test_backlog_md.py, test_evals.py, test_repo_setup.py, test_subagent_notes_hooks.py) still import PyYAML, so pyproject.toml keeps it as a dev dependency and the Dependency Dashboard keeps flagging it as abandoned (issue #4, AD-26). Move them to the vendored parser or the standard library and drop the pin. Note that YAML 1.2 reads unquoted dates and yes/no differently from PyYAML.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No tracked Python file imports yaml, and pyproject.toml and uv.lock no longer list PyYAML
- [ ] #2 mise run check passes
<!-- AC:END -->
