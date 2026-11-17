---
id: AD-109
title: Decide whether to move the plugin out of the repo root
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies:
  - AD-108
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:534
  - docs/intent/repo-setup/repo-setup-design.md:120
priority: low
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Moving the plugin into a subdirectory would stop gitignored working files counting toward `claude plugin eval`'s entry cap, but must be weighed against the Plugin root decision and is a major version for consumers, whose pins and skill links change. Evals currently run from a cached copy instead. Decide whether to move. Done when recorded in the LLD.

**Why it matters:** Settles the package layout before more consumers pin it.

**Why the developer:** a breaking-change decision for consumers
<!-- SECTION:DESCRIPTION:END -->
