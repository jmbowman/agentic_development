---
tags: [prior-art-search, offline, effort]
max_turns: 100
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Bash, Write, Edit]
---

Small thing, easy to change later: I need to format our structured log lines for humans, in one house format we'll call "ops": level letter, a timestamp, then the message, with fields printed in a fixed order. Is there something we can start from? The network is down today, so work from the clones we already have locally (see AGENTS.md).
