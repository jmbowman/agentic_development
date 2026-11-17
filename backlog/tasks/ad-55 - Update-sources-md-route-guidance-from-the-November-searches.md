---
id: AD-55
title: Update sources.md route guidance from the November searches
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - partly-done
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/158
  - skills/prior-art-search/references/sources.md
  - https://github.com/jmbowman/agentic_development/issues/260
  - skills/prior-art-search/references/sources.md:31
  - skills/prior-art-search/SKILL.md:81
priority: medium
type: docs
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #158 and comments list route behavior to fold into skills/prior-art-search/references/sources.md: Semantic Scholar throttling (15-20 s spacing; throttles even with key) and the key request form; OpenAlex lacks reference lists for arXiv-only preprints (workarounds: parse arxiv.org/html/<id>, Semantic Scholar citations, grep for repo links); arXiv https and 429 fallbacks, batches of about 8; Zenodo robots rules; publisher PDFs recorded as open, not machine-retrievable; raw Markdown vendor docs (docs.github.com/api/article/body, jsDelivr gh/); PyPI JS challenge so use libraries.io, ecosyste.ms for dependents; GitHub search needs both star-floor and sort=updated runs, and never record private repos; Codeberg 429 treated as unavailable; GitLab mirror noise; crates.io keyword advice; catalog noise; one query per vendor; summaries are leads only; topic vocabulary hints. Done means those rows, rate limits and access text are updated and checks pass.

**Why it matters:** Searches stop rediscovering broken routes.

**Why an agent:** documentation edit from written evidence

**Status when filed (partly-done):** commits 2d835c7 and aec8b25 changed sources.md; lib.rs, aitoolnet trigger and marketplaces rows already exist, but arXiv HTML reference workaround and Zenodo guidance were not found by grep
<!-- SECTION:DESCRIPTION:END -->
