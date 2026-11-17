---
id: AD-65
title: Build literature full-text helpers (open-access lookup, arXiv references)
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/157
  - skills/prior-art-search/scripts/harvest.py
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md#Need and criteria
  - docs/intent/prior-art-search/prior-art-search-design.md:520
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #157 item 4 and comments: helpers for open-access lookup (ask OpenAlex for locations as well as best_oa_location; try HTML then arXiv PDF before recording not retrievable; refuse verify=False and use a distinct read state, open, not machine-retrievable), reference extraction from arxiv.org/html/<id> keeping math alttext, and artifact links (GitHub, Zenodo, Hugging Face) from full text; OpenAlex abstract_inverted_index rebuild helper. Extend skills/prior-art-search/scripts/ with tests.

**Why it matters:** Cuts token cost of literature reading and fixes backward snowballing on arXiv-only papers.

**Why an agent:** scripted tooling with written requirements
<!-- SECTION:DESCRIPTION:END -->
