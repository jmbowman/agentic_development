---
tags: [prior-art-search, online, reference]
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, WebSearch, WebFetch, Bash, Write, Edit]
---

We want to share config files (linter settings, editor settings, CI snippets) across about 20 repos. Each repo needs committed, key-level overrides of the shared values, and each developer needs a gitignored local overlay on top. We'll record what we pick as a decision in docs/decisions/. What should we use?
