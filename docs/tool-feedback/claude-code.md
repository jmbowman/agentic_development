# Claude Code feedback

[Claude Code](https://code.claude.com/docs) runs this repo's skills and hooks. These items come from a probe run on 2.1.322 (Linux) on 2026-11-11, recorded in [the subagent process-notes note](../prior-art/2026-11-11-subagent-process-notes.md#probe-of-the-platform). Each scenario was a `claude -p` session with one hook plugin loaded through `--plugin-dir` and one Explore subagent told to reply with only a JSON object.

## Open items

### 1. A SubagentStop block still replaces the subagent's report

- **Where:** SubagentStop `decision: "block"`, outside auto mode (no `SubagentHandback`).
- **What:** the subagent answers the hook's `reason`, and that answer, not its report, reaches the parent. A hook can't ask a finishing subagent anything without corrupting what its caller receives.
- **Evidence:** blocking the first stop in manual mode turned the parent's result from `{"entries": [...]}` into the reply to the hook's reason. This is [anthropics/claude-code#85917](https://github.com/anthropics/claude-code/issues/85917) (filed against 2.1.226, closed 2026-09-13) still reproducing.
- **Suggested fix:** when a stop is blocked, return the message the agent was about to stop with as its result, or document that the last message wins so hooks can avoid blocking.
- **Raised upstream:** no. #85917 is closed and locked, so raising it means a new issue that references it. A maintainer's comment there calls the replaced deliverable "how subagent results work today… a product decision rather than a bug", so a new issue asks for the change or for documentation, not a bug fix.

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

### 4. A background launch's result has no agent type

- **Where:** the `Agent` tool's result for a background launch (`status` `async_launched`), on 2.1.323 and 2.1.325 (Linux), 2026-11-13.
- **What:** the result carries `agentId`, `description`, `status`, `isAsync`, `outputFile` and `resolvedModel`, but no `agentType`. A foreground result, and a background one in the 2.1.322 probe, carried `agentType`. A PostToolUse hook that needs to know what kind of agent was launched can't tell from the result, and has to fall back to the call's `tool_input.subagent_type`.
- **Evidence:** three background launches (a `claude-code-guide` agent and two `general-purpose` agents) in one interactive session: the transcript's `toolUseResult` for each lacked `agentType`. The subagent notes hooks, which then tracked a launch only when `tool_response` had both `agentId` and `agentType`, wrote no `.launched` file and no `[subagent-notes]` line for any of them, while their SubagentStart and SubagentStop hooks ran and recorded the same agent IDs. A probe on 2.1.325 (a `claude -p` session with one plugin whose PostToolUse hook logged its input, launching one foreground and one background `general-purpose` agent) confirmed it in the hook itself: the background launch's `tool_response` had `agentId`, `canContinueAgent`, `canReadOutputFile`, `description`, `isAsync`, `outputFile`, `prompt`, `resolvedModel` and `status`, and no `agentType`, while the foreground one had `agentType`. In both launches, the hook's `tool_response` had the same keys as the transcript's `toolUseResult`.
- **Suggested fix:** include `agentType` in the background launch result, as the foreground result does, or document which fields each launch status carries.
- **Raised upstream:** no.

### 5. A hook's "ask" prompt doesn't show the hook's reason

- **Where:** a `PreToolUse` hook answering `permissionDecision: "ask"` with a `permissionDecisionReason`, on 2.1.331 (Linux), 2026-11-23.
- **What:** the permission prompt shows only the tool, the file, the diff and "Do you want to make this edit to README.md?", with nothing of the hook's reason. The person is asked to approve without being told why they're asked, while the agent gets the hook's `additionalContext`. The prompt also offers no "allow for the session" choice, which fits a hook's "ask".
- **Evidence:** [Clash](https://github.com/clash-sh/clash) 0.2.0's `clash check`, run by hand on the same Edit input, answers `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Conflicts on docs/wiki/success-stories/README.md with 1 worktree(s):\nmain [main]: active changes","additionalContext":"<the same text>"}}`. In an interactive session in a second worktree, four runs (auto mode and manual) each prompted for that edit, and none of the prompts showed the reason. The agent gets the reason only afterwards, and only on Yes: an approved edit's result carries the hook's `additionalContext`, while a rejected one's result is the standard rejection text with no trace of the hook, and the agent's turn ends. So nobody sees the reason at the moment of deciding.
- **Suggested fix:** show `permissionDecisionReason` in the prompt when a hook answers "ask", naming the hook that asked.
- **Raised upstream:** no. It's a bug against documented behavior: the hooks reference's PreToolUse decision table says the reason, for `"ask"`, is "shown to the user in the permission prompt" ([hooks](https://code.claude.com/docs/en/hooks.md), read 2026-11-23).
