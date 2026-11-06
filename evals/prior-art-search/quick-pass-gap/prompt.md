---
tags: [prior-art-search, offline, effort]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Bash, Write, Edit]
---

Small thing, easy to change later: our docs CI needs a check that every external link in our Markdown files still resolves. It has to run on all three of our CI platforms (see AGENTS.md), with no exceptions. Is there something we can use before I write a script? The network is down today, so work from the clones we already have locally.
