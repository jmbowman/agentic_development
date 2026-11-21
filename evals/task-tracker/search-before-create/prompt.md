---
tags: [task-tracker, offline, rules]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

This is a non-interactive run: nobody will answer questions. While I was testing just now, `fetch()` in `src/fetch.py` blew up when the server answered 503 Service Unavailable under load, instead of trying again. Don't fix it now; make sure it's tracked in this repo's backlog so someone picks it up.
