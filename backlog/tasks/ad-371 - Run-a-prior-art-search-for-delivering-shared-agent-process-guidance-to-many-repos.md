---
id: AD-371
title: >-
  Run a prior-art search for delivering shared agent process guidance to many
  repos
status: To Do
assignee: []
created_date: '2026-11-27T21:43:12Z'
labels: []
milestone: m-6
dependencies: []
references:
  - docs/decisions/review-wave-stopping.md
  - docs/prior-art/2026-11-10-agentic-development-process-synthesis.md
priority: high
type: search
ordinal: 58000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
    role: created
    date: '2026-11-27'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This repo's development process (LID, review waves and the rest of the synthesis's lifecycle) is meant for every repo built from its templates, such as copier-python, not only this one. Skills that agents must choose to load are rarely used unless an instruction file such as AGENTS.md points at them, and hand-maintaining each repo's instruction file does not scale. The process synthesis (docs/prior-art/2026-11-10-agentic-development-process-synthesis.md) does not cover this. Search for tools and methods that let shared process guidance be authored once, reach many repos by version (through a template or a package), be used by agents by default without relying on a skill triggering itself, coexist with each repo's own instructions, and work in cloud sessions. Leave the mechanism open. Include LID's own pattern (a skill plus a directive block that /update-lid writes into each repo's instruction file) as a candidate, and read the AGENTS.md and skill-disclosure papers AD-276 lists. Done when a docs/prior-art/ note classifies the candidates under the prior-art-search skill's rules.

**Why it matters:** The process component cannot be planned without knowing how its guidance reaches and is used in consumer repos.

**Why an agent:** a prior-art-search skill run; the developer approves scope and cost
<!-- SECTION:DESCRIPTION:END -->
