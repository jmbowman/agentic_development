---
tags: [prior-art-search, online, effort]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, WebSearch, WebFetch, Bash, Write, Edit]
---

Small thing, easy to change later: our meeting notes are Markdown files where each action item is a line like `-> @owner (due 2026-01-31) text`. I want a script that appends each new action item to a GitHub Projects board as a draft item with owner and due date fields. Does something already do this?
