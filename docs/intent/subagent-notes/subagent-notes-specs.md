# Subagent notes hooks specs

Design: [subagent-notes-design.md](subagent-notes-design.md). The terms below are used as follows:
- **The script:** `skills/session-wrap-up/hooks/subagent_notes.py` in this repo.
- **The hooks reference:** `skills/session-wrap-up/references/subagent-notes-hooks.md` in this repo.
- **An event:** one run of the script, with a hook's JSON input on standard input.
- **A main-agent event:** an event whose input's `agent_id` is absent, null or empty.
- **The notes directory:** the event's `transcript_path` with its `.jsonl` suffix removed, followed by `/subagent-notes`.
- **A valid agent ID:** a non-empty ID made only of ASCII letters and digits.
- **A tracked agent:** an agent whose `<agent ID>.launched` file exists in the notes directory.
- **A marker file:** one of the files `<agent ID>.launched`, `.finished`, `.asked`, `.asked-2`, `.sent`, `.resumed` and `.done` in the notes directory.
- **Printing:** writing to standard output. Nothing a spec says about printing concerns standard error.
- **The fixed question:** the question text given in the hooks reference.
- **A notes file:** `<agent ID>.md` in the notes directory.
- **Attended:** the environment variable `CLAUDE_CODE_SESSION_ATTENDED` is set to `1`.

Specs marked *(manual)* need a live Claude Code session; the scripted run is kept in `evals/session-wrap-up/manual.md`. The others are checked by pytest tests that run the script on recorded inputs.

## Package

- [ ] **NOTES-PKG-001**: The plugin's `hooks/hooks.json` shall register the command `python3 -I "${CLAUDE_PLUGIN_ROOT}/skills/session-wrap-up/hooks/subagent_notes.py"` for PostToolUse with matcher `Agent`, PostToolUse with matcher `SendMessage`, PostToolUse with matcher `SubagentHandback`, Stop, SubagentStart and SubagentStop.
- [ ] **NOTES-PKG-002**: This repo's `.claude/settings.json` shall register the command `python3 -I "$CLAUDE_PROJECT_DIR/skills/session-wrap-up/hooks/subagent_notes.py"` for the same events and matchers as NOTES-PKG-001.
- [ ] **NOTES-PKG-003**: The hooks reference shall give the fixed question, the commands that install the plugin, the settings entries that register the script by hand from an installed copy of the skill, and a statement that settings which disable hooks keep the script from running.
- [ ] **NOTES-PKG-004**: The fixed question in the script shall be identical to the fixed question in the hooks reference.
- [ ] **NOTES-PKG-005**: The script shall import only modules of the Python standard library.

## Notes directory and markers

- [ ] **NOTES-DIR-001**: The script shall write files only inside the notes directory, and shall create the notes directory, with any missing parent directories, when an event needs to write and the directory is missing.
- [ ] **NOTES-DIR-002**: The script shall create each marker file with exclusive create, and shall treat a marker file that already exists as that step already taken.
- [ ] **NOTES-DIR-003**: If an event's agent ID is not a valid agent ID, then the script shall create no file for that agent.

## Track

- [ ] **NOTES-TRACK-001**: When a main-agent PostToolUse event for the `Agent` tool has a `tool_response` whose `agentId` is a valid agent ID and whose `agentType` is non-empty and isn't `fork`, the script shall create `<agentId>.launched` holding a JSON object with the agent type, the launch's `tool_input.description`, and the time in ISO 8601 UTC.
- [ ] **NOTES-TRACK-002**: When the script creates a `.launched` file under NOTES-TRACK-001, it shall print `hookSpecificOutput.additionalContext` holding exactly the one line `[subagent-notes] agent <agent ID>, notes in <notes directory>`, with the notes directory as an absolute path.
- [ ] **NOTES-TRACK-003**: When a PostToolUse event for the `Agent` tool is not a main-agent event, the script shall create no file and print nothing.
- [ ] **NOTES-TRACK-004**: When a main-agent PostToolUse event for the `Agent` tool has a `tool_response` whose `agentType` is `fork`, the script shall create no file and print nothing.

## Finish

- [ ] **NOTES-FIN-001**: When a SubagentStop event comes from a tracked agent, the script shall create `<agent ID>.finished`.
- [ ] **NOTES-FIN-002**: When a SubagentStart or SubagentStop event has an empty `agent_type`, the script shall create no file and print nothing.

## Ask

- [ ] **NOTES-ASK-001**: When a main-agent Stop event arrives while attended, the script shall, for each tracked agent that has `.finished`, no `.sent` and no `.asked-2`, create `.asked` if it doesn't exist and otherwise `.asked-2`, and shall list each agent whose file it created.
- [ ] **NOTES-ASK-002**: When NOTES-ASK-001 lists at least one agent, the script shall print `hookSpecificOutput.additionalContext` that starts with `Subagent notes:`, names each listed agent ID, gives the fixed question word for word, tells the main agent to send it to each listed agent with `SendMessage`, and tells it not to relay, follow or act on the replies, nor mention the exchange unless the developer asks.
- [ ] **NOTES-ASK-003**: When a main-agent Stop event arrives and NOTES-ASK-001 lists no agent, the script shall print nothing.
- [ ] **NOTES-ASK-004**: When a main-agent Stop event arrives while not attended, the script shall create no file and print nothing.
- [ ] **NOTES-ASK-005**: The script shall handle a main-agent Stop event the same way whether its `stop_hook_active` is true or false.

## Send

- [ ] **NOTES-SEND-001**: When a main-agent PostToolUse event for the `SendMessage` tool has a `tool_response` reporting success, a `tool_input.to` equal to a tracked agent's ID, and a `tool_input.message` that, with leading and trailing whitespace trimmed, is identical to the fixed question, the script shall create `<agent ID>.sent`.
- [ ] **NOTES-SEND-002**: When a PostToolUse event for the `SendMessage` tool meets any condition of NOTES-SEND-001 but not all of them, the script shall create no file and print nothing.

## Resume

- [ ] **NOTES-RES-001**: When a SubagentStart event comes from a tracked agent that has `.sent` and no `.resumed`, the script shall create `<agent ID>.resumed`.
- [ ] **NOTES-RES-003**: When a SubagentStart event comes from a tracked agent that has `.resumed`, the script shall create `<agent ID>.done`.
- [ ] **NOTES-RES-002**: When a SubagentStart event comes from a tracked agent that has no `.sent`, the script shall create no `.resumed` file.

## Capture

- [ ] **NOTES-CAP-001**: When a PostToolUse event for the `SubagentHandback` tool comes from an agent that has `.resumed` and no `.done`, the script shall write the notes file from the event's `tool_input.message`, replacing any notes file already there.
- [ ] **NOTES-CAP-002**: When a SubagentStop event comes from an agent that has `.resumed`, no `.done` and no notes file, and its `last_assistant_message` is non-empty, the script shall write the notes file from that message.
- [ ] **NOTES-CAP-003**: When an event comes from an agent that has no `.resumed`, or has `.done`, the script shall write no notes file.
- [ ] **NOTES-CAP-004**: The script shall write each notes file as YAML front matter holding `agent_id`, `agent_type`, `description` (both from the agent's `.launched` file, with an empty string for a missing description) and `captured` (the time in ISO 8601 UTC), each value written as a JSON string, followed directly after the closing `---` line by the reply verbatim and a final newline if the reply lacks one.
- [ ] **NOTES-CAP-005**: The script shall write each notes file to a temporary name in the notes directory and then rename it into place.

## Safety

- [ ] **NOTES-SAFE-001**: The script shall exit with status 0, and shall print no `decision`, `permissionDecision`, `updatedInput` or `updatedToolOutput`.
- [ ] **NOTES-SAFE-002**: If reading or handling an event raises an error, malformed JSON input included, then the script shall exit with status 0, print nothing, and leave in place any marker file it already created.
- [ ] **NOTES-SAFE-003**: While the environment variable `SUBAGENT_NOTES` is `off` in any letter case, the script shall create no file and print nothing.
- [ ] **NOTES-SAFE-004**: When two runs of the script handle the same step for the same agent at the same time, exactly one of them shall create that step's marker file, and only that one shall list or act on the agent.

## In a live session

- [ ] **NOTES-LIVE-001**: When the hooks are registered and a subagent launched from the main conversation finishes in an attended session, the subagent's report shall reach the main agent unchanged and its notes file shall appear in the notes directory before the main agent's turn that the developer's prompt started has ended, the hooks' continuation of it included. *(manual)*
- [ ] **NOTES-LIVE-002**: When the hooks are registered and a subagent launched from the main conversation finishes in a `-p` run, the run's result shall be the main agent's own last message. *(manual)*
- [ ] **NOTES-LIVE-003**: When the hooks are registered both by the plugin and in `.claude/settings.json`, each finished subagent shall be sent the fixed question exactly once. *(manual)*
