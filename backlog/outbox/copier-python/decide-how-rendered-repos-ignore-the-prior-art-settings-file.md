---
title: Decide how rendered repos ignore the prior-art settings file and inbox/
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- issue
references:
- https://github.com/jmbowman/copier-python/issues/69
- copier-python:template/.config/copier-python/.gitignore
- docs/intent/prior-art-search/prior-art-search-design.md#Open Questions & Future Decisions
- copier-python:docs/intent/baseline-files/baseline-files-design.md:213
- docs/intent/prior-art-search/prior-art-search-design.md:533
- PRIOR-ACC-007
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue copier-python#69 asks rendered repos to ignore `.config/prior-art-sources.toml` (the prior-art-search skill reads it only when git ignores it) and asks whether to ignore `inbox/` too. The template renders no root `.gitignore`; its only ignore file is `.config/copier-python/.gitignore`, whose rules can't reach `.config/` itself. So the developer must choose the owner and location (a repo-owned root `.gitignore` rendered once, a template-owned `.config/.gitignore`, or another route) and whether `inbox/` is in scope. Done when the choice is recorded in the baseline-files LLD.

**Why it matters:** Prevents a filled-in API-key file from being committed in any consumer.

**Why the developer:** chooses file ownership and scope, which the LID LLD stop reviews

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
