---
id: AD-85
title: Add an offline fixture that forces a snippet-only license read
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-3
dependencies: []
references:
  - docs/review-log/history-to-2026-11-22.md:98
  - docs/intent/prior-art-search/prior-art-search-specs.md:248-249
  - PRIOR-LIC-009
  - PRIOR-LIC-010
  - docs/intent/prior-art-search/prior-art-search-specs.md:248
  - docs/review-log/history-to-2026-11-22.md:96
  - evals/prior-art-search
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: f4b2080f-847f-4a0d-a503-34339722eeb7
    role: created
    date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-16 code review of the search-tactics slice left one gap: no eval fixture forces a snippet-only license read, so PRIOR-LIC-009 (record the license criterion `unverified`) and PRIOR-LIC-010 (never adopt or build on it while unverified) are only covered when a run happens to read a license at snippet depth. Add an offline case or fixture under `evals/prior-art-search/` that makes the only license source a snippet, with graders for both specs and `@spec` comments in its `case.yaml`. Done when `mise run check` passes and latest-results has a row for the case.

**Why it matters:** Makes the unverified-license guard testable on demand.

**Why an agent:** writing a fixture and graders is agent work
<!-- SECTION:DESCRIPTION:END -->
