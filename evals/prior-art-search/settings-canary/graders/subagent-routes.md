---
type: llm
focus: trace
---

PASS if the assistant dispatched subagents, gave no two of them the same service at the same time (two routes on one service, such as GitHub repository search and GitHub topics, count as one), didn't query a service itself while a subagent held it, sent every other request to a service through the agent that held it, and put each assigned service's rate limit from `references/sources.md` in that subagent's prompt.
FAIL if two subagents, or a subagent and the assistant, queried the same service at once, or a subagent prompt omits the rate limit of a service it was given.
