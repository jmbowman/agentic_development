---
tags: [prior-art-search, offline, trigger]
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Bash, Write, Edit]
---

Fix the off-by-one bug in `paginate()` in pager.py: the last, partial page is always missing.
