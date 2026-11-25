---
id: AD-65
title: Build literature full-text helpers (open-access lookup, arXiv references)
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T04:00:00Z'
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

## Comments

<!-- COMMENTS:BEGIN -->
author: claude-code:7491ae04
created: 2026-11-24T04:00:00Z

---

From AD-92 (2026-11-23): the fork at 155f360 has ArxivSearcher.download_pdf and read_paper (PDF from arxiv.org, plain text through pypdf, no HTML, math lost). harvest.py cannot carry them as it stands: its transport reads each body whole, saves it under raw/ and judges an arXiv 200 as an Atom feed, and arxiv.org is not an allowed host. arxiv.org robots.txt (read 2026-11-23) sets Crawl-delay: 15 for /abs, /pdf and /html, so the host needs its own 15-second limit, apart from the 3-second API limit. Until this task lands, agents still read arXiv full text themselves, so arXiv is not a harvester-only service.

---
<!-- COMMENTS:END -->
