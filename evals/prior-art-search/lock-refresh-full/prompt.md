---
tags: [prior-art-search, online, reference]
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, WebSearch, WebFetch, Bash, Write, Edit]
---

Our repos commit mise.lock and are kept current by the hosted Renovate app, whose copier manager re-renders our template when it releases. Those PRs change tool pins in mise.toml but leave mise.lock stale, and the hosted app can't run `mise lock` as a post-upgrade task. Every repo we own will depend on whatever we pick, so this is a long-lived choice. Find out whether something already solves this before we build anything. Use parallel subagents for the search if you can.
