# Subagent notes hooks specs

Design: [subagent-notes-design.md](subagent-notes-design.md). The terms below are used as follows:
- **The script:** `skills/session-wrap-up/hooks/subagent_notes.py` in this repo.
- **The hooks reference:** `skills/session-wrap-up/references/subagent-notes-hooks.md` in this repo.
- **An event:** one run of the script, with a hook's JSON input on standard input.
- **A main-agent event:** an event whose input's `agent_id` is absent, null or empty.
- **The notes directory:** the event's `transcript_path` with its `.jsonl` suffix removed, followed by `/subagent-notes`.
- **A valid agent ID:** a non-empty ID made only of ASCII letters and digits.
- **A tracked agent:** an agent whose `<agent ID>.launched` file exists in the notes directory.
- **A marker file:** one of the files `<agent ID>.launched`, `.finished`, `.asked`, `.sent`, `.resumed` and `.done` in the notes directory.
- **The pending file:** `<agent ID>.pending` in the notes directory, holding `question` or `other`.
- **The state file:** `<agent ID>.state` in the notes directory, holding `running` or `stopped`. An agent with no state file isn't running.
- **A message's agent:** the tracked agent whose ID equals the `SendMessage`'s `tool_input.to`, or else the one tracked agent whose `.launched` records that `name`; none when no tracked agent, or more than one, has that name.
- **Printing:** writing to standard output. Nothing a spec says about printing concerns standard error.
- **The fixed question:** the question text given in the hooks reference.
- **The question:** a `SendMessage` whose `tool_input.message`, with leading and trailing whitespace trimmed, is identical to the fixed question.
- **A notes file:** `<agent ID>.md` in the notes directory.
- **Attended:** the environment variable `CLAUDE_CODE_SESSION_ATTENDED` is set to `1`.

Specs marked *(manual)* need a live Claude Code session; the scripted run is kept in `evals/session-wrap-up/manual.md`. The others are checked by pytest tests that run the script on recorded inputs.

## Package

- [x] **NOTES-PKG-001**: The plugin's `hooks/hooks.json` shall register the command `python3 -I "${CLAUDE_PLUGIN_ROOT}/skills/session-wrap-up/hooks/subagent_notes.py" || true` for PreToolUse with matcher `SendMessage`, PostToolUse with matcher `Agent`, PostToolUse with matcher `SendMessage`, PostToolUse with matcher `SubagentHandback`, Stop, SubagentStart and SubagentStop.
- [x] **NOTES-PKG-002**: This repo's `.claude/settings.json` shall register the command `python3 -I "$CLAUDE_PROJECT_DIR/skills/session-wrap-up/hooks/subagent_notes.py" || true` for the same events and matchers as NOTES-PKG-001.
- [x] **NOTES-PKG-003**: The hooks reference shall give the fixed question, what the hooks cost a session (a housekeeping turn, a resumed subagent turn and, outside auto mode, a permission prompt per subagent), the `SUBAGENT_NOTES=off` opt-out, the commands that install the plugin, the settings entries that register the script by hand from an installed copy of the skill, and the cases in which the hooks don't run (settings that disable hooks, and cloud sessions, which don't install plugins).
- [x] **NOTES-PKG-004**: The fixed question in the script shall be identical to the fixed question in the hooks reference.
- [x] **NOTES-PKG-005**: The script shall import only modules of the Python standard library.
- [x] **NOTES-PKG-006**: If the script file is missing, then each registered command shall exit with status 0.

## Notes directory and markers

- [x] **NOTES-DIR-001**: The script shall write files only inside the notes directory, and shall create the notes directory, with any missing parent directories, when an event needs to write and the directory is missing.
- [x] **NOTES-DIR-002**: The script shall create each marker file with exclusive create, and shall treat a marker file that already exists as that step already taken.
- [x] **NOTES-DIR-003**: If an event's agent ID is not a valid agent ID, then the script shall create no file for that agent.
- [x] **NOTES-DIR-004**: If an event's `transcript_path` isn't an absolute path ending in `.jsonl`, then the script shall create no file and print nothing.

## Track

- [x] **NOTES-TRACK-006**: The script shall take a launch's agent type from `tool_response.agentType` when that is a non-empty string, otherwise from `tool_input.subagent_type` when that is a non-empty string, and otherwise as an empty string.
- [x] **NOTES-TRACK-001**: When a main-agent PostToolUse event for the `Agent` tool has a `tool_response` whose `agentId` is a valid agent ID, and neither `tool_response.agentType` nor `tool_input.subagent_type` is `fork`, the script shall create `<agentId>.launched` holding a JSON object with the keys `agent_type` (the launch's agent type under NOTES-TRACK-006), `description` and `name` (the launch's `tool_input.description` and `tool_input.name`, each an empty string when the launch has none) and `time` (ISO 8601 UTC).
- [x] **NOTES-TRACK-002**: When the script creates a `.launched` file under NOTES-TRACK-001, it shall print a `hookSpecificOutput` whose `hookEventName` is `PostToolUse` and whose `additionalContext` holds exactly the one line `[subagent-notes] agent <agent ID>, notes in <notes directory>`, with the notes directory as an absolute path with no trailing `/`.
- [x] **NOTES-TRACK-003**: When a PostToolUse event for the `Agent` tool is not a main-agent event, the script shall create no file and print nothing.
- [x] **NOTES-TRACK-004**: When a main-agent PostToolUse event for the `Agent` tool has a `tool_response.agentType` or a `tool_input.subagent_type` that is `fork`, the script shall create no file and print nothing.
- [x] **NOTES-TRACK-005**: When the script creates a `.launched` file under NOTES-TRACK-001 for a `tool_response` whose `status` is `completed`, it shall also create `<agentId>.finished`.

## Finish

- [x] **NOTES-FIN-001**: When a SubagentStop event has a valid agent ID and a non-empty `agent_type`, the script shall create `<agent ID>.finished` and set the agent's state file to `stopped`, whether or not the agent is tracked yet.
- [x] **NOTES-FIN-003**: When a SubagentStart event has a valid agent ID and a non-empty `agent_type`, the script shall set the agent's state file to `running`, whether or not the agent is tracked yet.
- [x] **NOTES-FIN-002**: When a SubagentStart or SubagentStop event has an empty `agent_type`, the script shall create no file and print nothing.

## Ask

- [x] **NOTES-ASK-001**: When a main-agent Stop event arrives while attended, the script shall try to create `.asked` for each tracked agent that has `.finished`, isn't running, and has no notes file, no `.asked` and no `.sent`, and shall list each agent whose `.asked` it created.
- [x] **NOTES-ASK-002**: When NOTES-ASK-001 lists at least one agent, the script shall print a `hookSpecificOutput` whose `hookEventName` is `Stop` and whose `additionalContext` is the script's Ask template filled in with the listed agent IDs, sorted and joined with `, `, and the fixed question.
- [x] **NOTES-ASK-003**: When a main-agent Stop event arrives and NOTES-ASK-001 lists no agent, the script shall print nothing.
- [x] **NOTES-ASK-004**: When a main-agent Stop event arrives while not attended, the script shall create no file and print nothing.
- [x] **NOTES-ASK-005**: The script shall handle a main-agent Stop event the same way whether its `stop_hook_active` is true or false.
- [x] **NOTES-ASK-006**: The script's Ask template shall start with `Subagent notes:`, and shall tell the main agent to send the fixed question, word for word, to each listed agent with `SendMessage`, not to relay, follow or act on the replies, and not to mention the exchange unless the developer asks.
- [x] **NOTES-ASK-007**: If creating `.asked` fails for one agent during a Stop event, then the script shall still list each agent whose `.asked` it created.

## Send

- [x] **NOTES-SEND-001**: When a main-agent PostToolUse event for the `SendMessage` tool has a `tool_response` whose `success` is `true`, is the question, and has a message's agent that has `.finished` and whose pending file holds `question`, the script shall create `<agent ID>.sent` for that agent.
- [x] **NOTES-SEND-002**: When a PostToolUse event for the `SendMessage` tool meets any condition of NOTES-SEND-001 but not all of them, the script shall create no file and print nothing.
- [x] **NOTES-SEND-003**: When a main-agent PreToolUse event for the `SendMessage` tool has a message's agent, the script shall replace that agent's pending file with one holding `question` if the event is the question and the agent isn't running, and `other` otherwise, and shall print nothing.
- [x] **NOTES-SEND-004**: When a main-agent PreToolUse event for the `SendMessage` tool has a `tool_input.to` that isn't a tracked agent's ID and is the recorded `name` of more than one tracked agent, the script shall set each of those agents' pending files to `other`.

## Resume

- [x] **NOTES-RES-001**: When a SubagentStart event comes from a tracked agent whose pending file holds `question`, the script shall create `<agent ID>.resumed`.
- [x] **NOTES-RES-002**: When a SubagentStart event comes from a tracked agent that has no pending file, the script shall create no file.
- [x] **NOTES-RES-003**: When a SubagentStart event comes from a tracked agent that has `.resumed` and whose pending file holds `other`, the script shall create `<agent ID>.done`.

## Capture

- [x] **NOTES-CAP-001**: When a PostToolUse event for the `SubagentHandback` tool comes from an agent that has `.resumed` and no `.done`, the script shall write the notes file from the event's `tool_input.message`, replacing any notes file already there.
- [x] **NOTES-CAP-002**: When a SubagentStop event comes from an agent that has `.resumed`, no `.done` and no notes file, and its `last_assistant_message` is non-empty, the script shall write the notes file from that message without replacing a notes file that appears meanwhile, also on a filesystem without hard links.
- [x] **NOTES-CAP-003**: When an event comes from an agent that has no `.resumed`, or has `.done`, the script shall write no notes file.
- [x] **NOTES-CAP-004**: The script shall write each notes file as YAML front matter holding `agent_id`, `agent_type`, `description` (both from the agent's `.launched` file, with an empty string for a missing description) and `captured` (the time in ISO 8601 UTC), each value written as a JSON string, followed directly after the closing `---` line by the reply verbatim and a final newline if the reply lacks one.
- [x] **NOTES-CAP-005**: The script shall write each notes file to a temporary name in the notes directory and then move it into place, except under NOTES-CAP-002 on a filesystem without hard links, where it creates the notes file exclusively and writes it in place.
- [x] **NOTES-CAP-006**: If the agent's `.launched` file can't be read as a JSON object, then the script shall still write the notes file under NOTES-CAP-001 or NOTES-CAP-002, with empty `agent_type` and `description`.

## Safety

- [x] **NOTES-SAFE-001**: The script shall exit with status 0, and shall print no `decision`, `permissionDecision`, `updatedInput` or `updatedToolOutput`.
- [x] **NOTES-SAFE-002**: If reading or handling an event raises an error, malformed JSON input and bytes that aren't valid UTF-8 included, then the script shall exit with status 0, print nothing, and leave in place any marker file it already created.
- [x] **NOTES-SAFE-003**: While the environment variable `SUBAGENT_NOTES` is `off` in any letter case, the script shall create no file and print nothing.
- [x] **NOTES-SAFE-004**: When two runs of the script handle the same step for the same agent at the same time, exactly one of them shall create that step's marker file, and only that one shall list or act on the agent.

## In a live session

- [ ] **NOTES-LIVE-001**: When the hooks are registered and a subagent launched from the main conversation finishes in an attended session, the subagent's report shall reach the main agent unchanged and its notes file shall appear in the notes directory before the main agent's turn that the developer's prompt started has ended, the hooks' continuation of it included. *(manual)*
- [ ] **NOTES-LIVE-002**: When the hooks are registered and a subagent launched from the main conversation finishes in a `-p` run, the run's result shall be the main agent's own last message. *(manual)*
- [ ] **NOTES-LIVE-003**: When the hooks are registered both by the plugin and in `.claude/settings.json`, each finished subagent shall be sent the fixed question exactly once. *(manual)*
