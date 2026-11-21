---
tags: [task-tracker, offline, rules]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

This is a non-interactive run: nobody will answer questions. I just noticed that `fetch()` in `src/fetch.py` never compares the bytes it read with the response's Content-Length, so a download cut off halfway looks like a success. Nothing in the backlog covers it. Don't fix it now: record it as a follow-up task in this repo's backlog for an agent to pick up.
