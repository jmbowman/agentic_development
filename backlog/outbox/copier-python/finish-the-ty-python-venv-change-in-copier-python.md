---
title: Finish the ty --python .venv change in copier-python
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- loose-end
- partly-done
references:
- copier-python:docs/intent/local-checks/local-checks-design.md:32
- copier-python:docs/intent/local-checks/local-checks-design.md:97
- mise.toml:41-46
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
target: github.com/jmbowman/copier-python
sessions:
- agent: claude-code
  id: 83baf9d8-f511-40e3-875d-3d561ab7a7c4
  role: created
  date: '2026-11-16'
- agent: claude-code
  id: f4b2080f-847f-4a0d-a503-34339722eeb7
  role: worked
  date: '2026-11-16'
- agent: claude-code
  id: a1359d3a-1543-481a-84a6-bac89eb4e6cc
  role: worked
  date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
copier-python's working tree has an uncommitted edit to `docs/intent/local-checks/local-checks-design.md` making the template's `typecheck` task run `ty check --python .venv`, so PEP 723 scripts are checked against the project environment, as agentic_development's own `mise.toml:41-46` already does. Walk the rest of the arrow: EARS spec in `local-checks-specs.md`, failing test, the change to `template/.config/copier-python/mise.toml`, README if affected, and a `commit-message.md` draft. Done when `mise run check` passes and the slice is ready for the developer to commit.

**Why it matters:** Consumers that ship PEP 723 scripts (as the prior-art skill does) get correct type checks.

**Why an agent:** the design choice is already written; the rest is spec, test and code

**Status when filed (partly-done):** git diff in copier-python shows only the LLD edited; no spec, test or template change yet

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
