---
id: AD-149
title: Decide whether to install LID's arrow-maintenance skills
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-6
dependencies: []
references:
  - docs/intent/repo-setup/repo-setup-design.md:105
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: a1359d3a-1543-481a-84a6-bac89eb4e6cc
    role: created
    date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
LID's arrow-maintenance and map-codebase skills now parse (frontmatter fixed in 1.4.5, map-codebase's broken links fixed in 1.4.6, which this repo pins). Installing them means changing the 'What the manifest may list' decision (core plugin only) in docs/intent/repo-setup/repo-setup-design.md, because every dependency installs in every consumer. The developer decides; the next-session prompt was to read that row and docs/high-level-design.md (template skills) first.

**Why it matters:** Decides whether consumers get LID's arrow-maintenance tooling.

**Why the developer:** a design choice affecting every consumer
<!-- SECTION:DESCRIPTION:END -->
