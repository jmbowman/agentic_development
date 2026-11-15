---
tags: [prior-art-search, online, literature, harvester]
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, WebSearch, WebFetch, Bash, Write, Edit]
---

We're about to design how our review assistant orders the files of a large change for a human reviewer, so they understand it faster. Which ordering approaches have been shown to help, and is there software that already does this? It's a long-lived part of the product, so do the full method, split the searching across subagents, and save a note.
