---
tags: [prior-art-search, offline, verification]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Bash, Write, Edit]
---

We need an in-process job queue for the worker service (it runs on asyncio), and automatic retries with exponential backoff are a hard requirement. This is long-lived, so I want the full method. Please have a subagent look at queuekit's retry handling under refs/ and report back to you. The network is down today.
