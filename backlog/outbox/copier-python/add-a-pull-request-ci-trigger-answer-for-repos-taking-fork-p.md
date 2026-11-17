---
title: Add a pull_request CI trigger answer for repos taking fork PRs
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/baseline-files/baseline-files-design.md:211
- copier-python:docs/intent/baseline-files/baseline-files-specs.md:40
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The rendered CI stub triggers only on `push` (FILES-CONTENT-005); copier-python defers a `pull_request` trigger, made a copier answer so same-repo PRs aren't checked twice, for repos that accept contributions from forks. Implement it when a consumer accepts fork PRs (pytest-claude-code-evals, a public plugin, is a likely first). Done when the answer exists with specs and tests.

**Why it matters:** Lets public consumers run the shared check on outside contributions.

**Why an agent:** a template change with a clear spec shape

**Also waits on (not tracked as a task):** A consumer accepts PRs from forks

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
