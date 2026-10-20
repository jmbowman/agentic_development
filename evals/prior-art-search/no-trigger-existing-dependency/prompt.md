---
tags: [prior-art-search, offline, trigger]
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Bash, Write, Edit]
---

Add a 10-second timeout and a retry on connection errors to `fetch()` in client.py, using the requests library we already depend on.
