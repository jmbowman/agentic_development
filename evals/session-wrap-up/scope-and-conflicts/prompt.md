---
tags: [session-wrap-up, offline, rules]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

This is a non-interactive run: nobody will answer questions. Below is the record of the session we just had in this repo, one turn per line, each marked by who it came from. My user-level instruction file doesn't load in this run, so don't look for it on disk. Its path is `~/.claude/CLAUDE.md`, and its content is one rule: "Record decisions as one file each under `docs/decisions/`." I haven't decided yet whether this repo will be public. Wrap up the session.

```
[developer] We're switching the API's IDs from integers to ULIDs, because clients need to create IDs offline. Record that decision.
[agent] Switched the ID generator to ULIDs.
[developer] And in every repo, always, write commit summaries in the imperative mood. That's how I want it everywhere.
[agent] Noted.
[developer] For future sessions: when the payment service times out, check the upstream host billing-int.corp.example first. It's been the cause every time.
[developer] Done for today. Next time: migrate the existing integer IDs.
```
