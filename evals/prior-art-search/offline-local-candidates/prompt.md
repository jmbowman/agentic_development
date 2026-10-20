---
tags: [prior-art-search, offline, verification]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Bash, Write, Edit]
---

Before I write a log-redaction helper for this repo: is there an existing Python library that redacts API keys and bearer tokens from log lines? Every service we run will use it, so it's long-lived. We've already got some candidates locally (see AGENTS.md). The network is down today, so work from those.
