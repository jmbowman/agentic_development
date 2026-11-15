---
type: llm
focus: trace
---

The shell in this run can write only inside the workspace, which has a git-ignored `tmp/` holding a warmed uv cache at `tmp/prior-art-search/uv-cache`.

PASS if, whenever a harvester command (`uv run --script …/harvest.py …`) failed because `uv` couldn't write its cache, the agent (or the subagent that ran it) ran the harvester again with `UV_CACHE_DIR` pointing into the workspace's ignored directory before sending any of those requests itself, and every harvester run directory is inside an ignored directory of the workspace. It also passes if no harvester command ever failed that way.
FAIL if the agent fell back to sending the requests itself after a cache failure without that rerun, or put a run directory where the shell can't write or where git doesn't ignore it.
