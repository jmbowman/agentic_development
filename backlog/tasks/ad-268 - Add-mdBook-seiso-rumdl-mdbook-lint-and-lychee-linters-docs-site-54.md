---
id: AD-268
title: 'Add mdBook, seiso, rumdl, mdbook-lint and lychee linters (docs site #54)'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-11-06-federated-knowledge-and-work-items.md#Verdict
  - https://github.com/jmbowman/agentic_development/issues/166
  - https://github.com/jmbowman/agentic_development/issues/54
  - docs/prior-art/2026-11-06-federated-knowledge-and-work-items.md
  - docs/prior-art/2026-10-23-progressive-disclosure-knowledge-base.md#Verdict
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Step 1 of the federated note's suggested order: mdBook with SUMMARY.md as the only hierarchy; seiso with kinds mapped from paths in seiso.toml (no frontmatter) and each wanted preview rule enabled explicitly (only 5 stable rules run by default); rumdl MD057 and mdbook-lint MDBOOK005; lychee for anchors and external links; the authoring-rules file from the superseded note. LID's paths excluded from seiso. Ties to #54's docs site and #166.

**Why it matters:** Typed, link-checked knowledge pages with no custom code.

**Why an agent:** tool adoption and configuration
<!-- SECTION:DESCRIPTION:END -->
