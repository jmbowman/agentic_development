# Claude Code feedback

[Claude Code](https://code.claude.com/docs) runs this repo's skills and hooks. These items come from a probe run on 2.1.322 (Linux) on 2026-11-11, recorded in [the subagent process-notes note](../prior-art/2026-11-11-subagent-process-notes.md#probe-of-the-platform). Each scenario was a `claude -p` session with one hook plugin loaded through `--plugin-dir` and one Explore subagent told to reply with only a JSON object.

## Open items

### 1. A SubagentStop block still replaces the subagent's report

- **Where:** SubagentStop `decision: "block"`, outside auto mode (no `SubagentHandback`).
- **What:** the subagent answers the hook's `reason`, and that answer, not its report, reaches the parent. A hook can't ask a finishing subagent anything without corrupting what its caller receives.
- **Evidence:** blocking the first stop in manual mode turned the parent's result from `{"entries": [...]}` into the reply to the hook's reason. This is [anthropics/claude-code#85917](https://github.com/anthropics/claude-code/issues/85917) (filed against 2.1.226, closed 2026-09-13) still reproducing.
- **Suggested fix:** when a stop is blocked, return the message the agent was about to stop with as its result, or document that the last message wins so hooks can avoid blocking.
- **Raised upstream:** #85917 covers it; not yet commented with the 2.1.322 result.

### 2. A SubagentStop block after a hand-back is silently ignored

- **Where:** SubagentStop `decision: "block"` for a subagent that has called `SubagentHandback` (auto mode).
- **What:** the hooks reference says a block "keeps the subagent running and delivers `reason` to the subagent as its next instruction". After a hand-back, the block is written to the subagent's transcript as a `hook_blocking_error`, but no further turn runs and no second SubagentStop fires.
- **Evidence:** foreground and background runs in auto mode, each with a hook that blocked once after the hand-back.
- **Suggested fix:** either run the extra turn (the report is already delivered, so it can't be corrupted), or document that a hand-back ends the run and that SubagentStop can't block it.
- **Raised upstream:** no.

### 3. Outside auto mode, the parent never learns a foreground subagent's ID

- **Where:** the `Agent` tool result for a foreground subagent outside auto mode.
- **What:** the result carries the report but not the agent ID, so the parent can't resume the subagent with `SendMessage`, which the subagents docs describe. In auto mode the ID arrives with the hand-back, and a background launch's result includes it.
- **Evidence:** in manual mode, the parent asked to resume the subagent found no ID and gave up. The ID is present in the PostToolUse hook's `tool_response.agentId`, and passing it on as `additionalContext` made the resume work.
- **Suggested fix:** include the agent ID in the foreground result in every mode.
- **Raised upstream:** no.
