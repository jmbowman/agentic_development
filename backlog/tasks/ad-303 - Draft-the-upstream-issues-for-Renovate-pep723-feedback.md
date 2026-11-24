---
id: AD-303
title: Draft the upstream issues for Renovate pep723 feedback
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T06:12:00Z'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/renovate.md
  - .github/renovate.json
priority: medium
type: upstream
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft Renovate issues from docs/tool-feedback/renovate.md: the `pep723` manager doesn't update uv script lock files (no updateArtifacts, `pep723/index.js:6-19`), and can't update a git-pinned dependency (`pep723/schema.js:7-15`). Both entries say 'Raised upstream: not checked', so search Renovate's issues and discussions first. Note that .github/renovate.json already has a custom regex manager that bumps the fork's commit, so the second item is a workaround-covered improvement. Done when drafts or 'already raised' links are recorded.

**Why it matters:** Lets PEP 723 scripts with lock files stay current without manual uv lock --script.

**Why an agent:** issue search plus text
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Also draft the vendir manager item added on 2026-11-24: a git source pinned by commit SHA gets no update and no skip reason (docs/tool-feedback/renovate.md). Hold filing until AD-354 has the workaround running end to end.
<!-- SECTION:NOTES:END -->
