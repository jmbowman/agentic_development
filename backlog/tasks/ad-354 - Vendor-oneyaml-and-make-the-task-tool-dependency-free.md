---
id: AD-354
title: Vendor oneyaml and make the task tool dependency-free
status: Done
assignee: []
created_date: '2026-11-24T05:16:00Z'
updated_date: '2026-11-24T13:37:00Z'
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
  - agent: claude-code
    id: 3db836d3-b908-46e0-9723-e32403b8aa4e
    role: worked
    date: '2026-11-24'
  - agent: claude-code
    id: 3db836d3-b908-46e0-9723-e32403b8aa4e
    role: finished
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the dependency-free core settled in AD-336: replace PyYAML with the vendored oneyaml parser and drop the script lock file, so the task tool runs with plain python3 where a uv lock file or package index would break it. Specs: TASK-YAML-001 to 007, TASK-SKILL-001, 003, 032 and 033, and TASK-REPO-001, 005 and 009 to 014. The lint rules that read numbers and booleans (the number definition, TASK-LINT-042) stay with AD-5.2, which builds the lint on top of this. Design: docs/intent/task-tracker/task-tracker-design.md, Reading YAML.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every task tool command runs under python3 -I on the interpreter the project venv was made from, with only the standard library and the vendored parser, and the skill has no tasks.py.lock
- [x] #2 A vendir sync --locked in CI leaves the committed _vendor/ copy unchanged, and fails the build when it doesn't
- [x] #3 Each spec in scope has a test that cites it and passes, and mise run check passes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README.md (the skills/task-tracker/ row) still says the tool needs uv and that uv installs PyYAML; update it in this change to say the tool needs only uv and Python 3.11 or later (which uv can provide). The project itself targets 3.12, so add a test that runs the tool under Python 3.11 (for example uv run --python 3.11 --script), so the 3.11 floor can't creep up unnoticed. PyYAML stays a dev dependency for five test files, so the Dependency Dashboard abandonment warning remains until they move to the vendored parser too.

Vendored oneyaml f41c222 with vendir (vendir.yml, vendir.lock.yml); copy byte-identical to upstream src/oneyaml without compat/, plus both licenses.

Developer rulings 2026-11-24: TASK-REPO-011 runs on pull requests and pushes to main only (spec and design reworded); bad YAML in config.yml, focus.yml and milestones stays with TASK-LAYOUT-004, FOCUS-002, LINT-034, MS-008 and LINT-048, so those still raise until their tasks land.

Tests reviewed by a review wave before code; nine fixes applied. mise run check passes (3078 tests), including real Python 3.10 and 3.11 runs.

Code review wave: two more rulings applied (any exception importing the parser is a setup error, TASK-YAML-004 reworded; HLD names the _vendor/ lint exception). A scratch Renovate 44.257.6 dry run extracts the git-sourced vendir.yml and plans lock-file maintenance. mise run check passes (3080 tests). AC #2 waits on the vendor workflow running in CI on the pull request: locally, vendir sync --locked left the copy byte-identical to upstream f41c222, and step tests cover the compare script.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The task tool now parses YAML with oneyaml's pure-Python backend, vendored by vendir in skills/task-tracker/scripts/_vendor/ (vendir.yml follows main; vendir.lock.yml records f41c222), instead of PyYAML, and has no dependencies or lock file, so it runs on python3 3.11+ or uv run --script with no package index. Verified by tests for every in-scope spec (including real Python 3.10 and 3.11 runs), mise run check (3080 tests), the tool checking this repo's 411 tasks cleanly, and the vendor workflow passing in CI on PR #314 and on the push to main. Developer rulings recorded in TASK-REPO-011, TASK-YAML-004 and the HLD. Risk: bad YAML in config.yml, focus.yml or a milestone still raises a traceback until the tasks for TASK-LAYOUT-004, FOCUS-002, LINT-034, MS-008 and LINT-048 land; oneyaml's Python version is unreleased and its upstream paused, so fixes may stop arriving.
<!-- SECTION:FINAL_SUMMARY:END -->
