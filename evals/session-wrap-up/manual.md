# Manual runs for session-wrap-up

Some specs need a live, interactive session, or another live session, which `claude plugin eval` can't provide. Each section below is a script for one such check. A person runs it in Claude Code with this repo's skills loaded (`claude --plugin-dir <path to this repo>`), and appends a dated result line: the Claude Code version, pass or fail, and a note on any failure.

## Interactive run (WRAP-RUN-008)

1. In a scratch git repo with `cli.py` holding one argparse command, and an `AGENTS.md` that has a `## Working rules` section, start a session.
2. Type: `Add a --verbose flag to cli.py.` Then correct the agent once: `Use logging, not print, for verbose output.`
3. Type: `Wrap up the session.`

Pass: the report starts with `Session wrap-up`, and treats the run as interactive: it doesn't say the run is non-interactive, and it doesn't refuse to continue the conversation. (Until slice 3, it still applies nothing and labels each item `not applied`.)

Results:

## A wrap-up request from another agent (WRAP-RUN-009)

1. In the same scratch repo, ask the agent: `Use a subagent to wrap up this session, passing it the conversation so far.`

Pass: the subagent's report says it treated the run as non-interactive, labels each item `not applied`, and asks nothing.

Results:

## No stated memory location (WRAP-RULE-008, memory half)

An eval's harness always states a sandbox memory directory, so this case needs a real session.

1. Start a session with auto-memory turned off (`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude`) in the scratch repo.
2. Make one change and give one correction about how you like summaries written, then type: `Wrap up the session.`

Pass: the report lists agent memory as a missing role, proposes nothing for memory, and reads nothing under `~/.claude/projects/`.

Results:

## A real compaction (WRAP-LES-015, harness half; WRAP-LES-027)

An eval can simulate a compaction but can't produce one, so the harness stating the transcript's location needs a real session. Tool calls show the order of the search, which an eval's graders can't check.

1. In the scratch repo, make a change that runs a command, give one correction (`From now on, use logging, not print, in cli.py.`), then type `/compact`.
2. Make one more change, then type: `Wrap up the session.`

Pass: the report proposes the correction from before the compaction. The tool calls read the transcript at the path the compaction summary gave, search the developer's and agent's turns first, and open a tool result only to check a specific candidate. No file is written.

Results:

## Applying items after the report (WRAP-RUN-013)

1. After a wrap-up report that proposes at least two items, type: `Apply item 1.`

Pass: the agent applies item 1 as an ordinary request, outside the skill's run. It doesn't start a new wrap-up, and it doesn't apply any other item.

Results:
