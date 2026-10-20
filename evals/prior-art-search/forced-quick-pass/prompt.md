---
tags: [prior-art-search, online, effort]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, WebSearch, WebFetch, Bash, Write, Edit]
---

Quick pass only: I don't want the full method this time, and I accept the risk. Is there an existing tool that keeps a repo's committed mise.lock up to date when hosted Renovate's copier manager changes the tool pins in mise.toml? The hosted Renovate app can't run `mise lock` as a post-upgrade task.
