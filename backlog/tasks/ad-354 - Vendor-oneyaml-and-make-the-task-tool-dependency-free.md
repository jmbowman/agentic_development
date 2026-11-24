---
id: AD-354
title: Vendor oneyaml and make the task tool dependency-free
status: To Do
assignee: []
created_date: '2026-11-24T05:16:00Z'
updated_date: '2026-11-24T06:11:00Z'
labels: []
milestone: m-1
dependencies: []
priority: high
type: feature
ordinal: 45000
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: d5de0f02-d865-48c6-82a7-a60f7b5669eb
    role: created
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the dependency-free core settled in AD-336: replace PyYAML with the vendored oneyaml parser and drop the script lock file, so the task tool runs with plain python3 where a uv lock file or package index would break it. Specs: TASK-YAML-001 to 007, TASK-SKILL-001, 003, 032 and 033, and TASK-REPO-001, 005 and 009 to 014. The lint rules that read numbers and booleans (the number definition, TASK-LINT-042) stay with AD-5.2, which builds the lint on top of this. Design: docs/intent/task-tracker/task-tracker-design.md, Reading YAML.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every task tool command runs under python3 -I on the interpreter the project venv was made from, with only the standard library and the vendored parser, and the skill has no tasks.py.lock
- [ ] #2 A vendir sync --locked in CI leaves the committed _vendor/ copy unchanged, and fails the build when it doesn't
- [ ] #3 Each spec in scope has a test that cites it and passes, and mise run check passes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README.md (the skills/task-tracker/ row) still says the tool needs uv and that uv installs PyYAML; update it in this change to say the tool needs only uv and Python 3.11 or later (which uv can provide). The project itself targets 3.12, so add a test that runs the tool under Python 3.11 (for example uv run --python 3.11 --script), so the 3.11 floor can't creep up unnoticed. PyYAML stays a dev dependency for five test files, so the Dependency Dashboard abandonment warning remains until they move to the vendored parser too.
<!-- SECTION:NOTES:END -->
