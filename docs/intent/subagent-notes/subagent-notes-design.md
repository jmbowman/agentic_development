---
parent: high-level-design
prefix: NOTES
---

# Subagent notes hooks

## Context and Design Philosophy

A subagent works in its own context and returns one report. The friction it met, such as a blocked tool, a rate limit, a misleading instruction or query wording that returned noise, stays in that context unless its brief asked for it. When asked afterwards, subagents give useful notes, but whether anyone asks depends on the main agent remembering to, and on how the question happens to be worded.

Asking inside the brief, or in context added when a subagent starts, would make the subagent put its notes in, or next to, its report. Skills parse reports in fixed formats, some of them JSON, so the report must stay exactly as the brief asked for it. Many subagents also have no tool that writes files.

These hooks collect the notes without touching the report. They track every subagent the main agent launches. When the main agent ends a turn, they tell it to resume each finished subagent with one fixed question, using `SendMessage`. They then save the reply to a per-agent notes file, which the [session wrap-up](../session-wrap-up/session-wrap-up-design.md) triages like any other candidate lesson. The subagent needs no tools of its own: a hook script writes the file. The question goes out at the end of the main agent's turn, while the subagent's prompt cache is still warm, so a resumed turn costs little.

The design borrows from the [prior-art note](../../prior-art/2026-11-11-subagent-process-notes.md):
- [dagonet/claude-code-toolkit](https://github.com/dagonet/claude-code-toolkit) (MIT): a SubagentStop hook that records what happened in a subagent without blocking it or changing its result;
- [piercelamb/deep-plan](https://github.com/piercelamb/deep-plan): a hook that writes a file on behalf of a subagent with no file tools.

The hooks are a Claude Code feature, delivered as the HLD's decision on Claude Code hooks says. A session without them loses only the notes: the wrap-up runs as before, and says the hooks are missing.

## Platform facts

Checked with a probe on Claude Code 2.1.322 on Linux on 2026-11-11, recorded in the prior-art note, unless marked otherwise. Hook inputs and outputs are from the [hooks reference](https://code.claude.com/docs/en/hooks), read 2026-11-10.

- **A blocked stop can't be used.** Outside auto mode, a SubagentStop `decision: "block"` makes the subagent answer the hook, and that answer replaces its report ([anthropics/claude-code#85917](https://github.com/anthropics/claude-code/issues/85917)). After a `SubagentHandback` (auto mode), a block is recorded but no further turn runs. A block is ignored for an agent with a structured output schema ([#86569](https://github.com/anthropics/claude-code/issues/86569), not probed).
- **Resuming works.** `SendMessage` to a finished subagent's agent ID resumes it with its context, in the foreground and the background, in auto and manual mode. Its reply reaches the main agent as a separate message, and its report is unchanged.
- **The agent ID.** The `Agent` tool's PostToolUse input carries `tool_response.agentId` and `agentType`, for foreground and background launches. Outside auto mode, the main agent's own view of a foreground result doesn't include the ID, so the main agent can address the subagent only if a hook tells it the ID.
- **A resumed run** fires `SubagentStart` again with the same `agent_id`. In auto mode the reply comes as a `SubagentHandback` whose `tool_input.message` holds the text. In manual mode it is the resumed run's `last_assistant_message` at SubagentStop. In auto mode, the resumed run can stop once with its reply in `last_assistant_message` and then hand the same reply back.
- **Which agent a hook runs in.** A hook running inside a subagent receives `agent_id` and `agent_type`. A hook running in the main agent receives neither (`--agent` sessions aside). The script treats an `agent_id` that is absent, null or empty as the main agent's.
- **Forks.** A fork of the main conversation is launched with `tool_input.subagent_type` `fork`, and its PostToolUse `tool_response.agentType` and its SubagentStart and SubagentStop `agent_type` are `fork` (probed 2026-11-12).
- **Sending.** A `SendMessage` that resumes a subagent reports success in its PostToolUse `tool_response` (`success: true`, with `resumedAgentId`). PreToolUse runs before the permission decision, so it can't show whether the message went out.
- **Internal agents.** SubagentStop also fires for Claude Code's own internal agents (prompt suggestions, side questions), with an empty `agent_type`.
- **Session files.** The input's `transcript_path` is the main transcript, `<project dir>/<session_id>.jsonl`; subagent transcripts sit beside it in `<project dir>/<session_id>/subagents/`.
- **Stop.** A main-agent Stop hook's `hookSpecificOutput.additionalContext` continues the main agent, which acts on the text; the next Stop arrives with `stop_hook_active` true. The docs add a cap of 8 consecutive continuations. In a `-p` run, the continued turn's last message becomes the run's result. The hook input doesn't say whether the run is interactive, but the hook's environment does: `CLAUDE_CODE_SESSION_ATTENDED` is `1` in an interactive session and `0` in a `-p` run (with `CLAUDE_CODE_ENTRYPOINT` `cli` and `sdk-cli` respectively). Neither variable is documented.
- **Resumed and forked sessions.** `--resume` keeps the session ID and transcript path. `--fork-session` starts a new session ID and transcript, so the fork's hooks use a new notes directory, while the context lines it inherited name the original's.
- **Background completion.** A background subagent's completion notification starts a main-agent turn, whose end fires Stop again.
- **Concurrency.** Hooks for one event run in parallel, and parallel subagents fire their hooks concurrently. When several hooks return `additionalContext` for one event, each is delivered (not probed).

## Package layout

| Path | Contents |
|---|---|
| `skills/session-wrap-up/hooks/subagent_notes.py` | The hook script: one entry point for every event below, chosen by `hook_event_name` |
| `hooks/hooks.json` (plugin root) | Registers the script for the plugin, as `python3 -I "${CLAUDE_PLUGIN_ROOT}/skills/session-wrap-up/hooks/subagent_notes.py"` |
| `skills/session-wrap-up/references/subagent-notes-hooks.md` | The settings entries for registering the hooks by hand, with the script's path in the installed skill. The wrap-up's install guidance points here |
| `.claude/settings.json` (this repo) | The same entries, with `$CLAUDE_PROJECT_DIR/skills/session-wrap-up/hooks/subagent_notes.py` |
| `tests/subagent_notes/` | pytest tests that run the script on recorded hook inputs |

The script uses only the Python standard library and runs with `python3 -I`. It passes the repo's strict profile (ruff and ty).

## Notes directory

Everything the hooks keep for a session lives in `<project dir>/<session_id>/subagent-notes`, beside the session's transcript and subagent transcripts. The directory is derived from the hook input's `transcript_path` by dropping `.jsonl`, and is created with any missing parents when a step first needs it. It is outside every repo, so nothing needs a `.gitignore` entry. Each session has its own directory, so sessions running in one repo at once never see each other's notes. Whether Claude Code's transcript cleanup also removes the directory is unverified.

A **tracked agent** is one whose `.launched` file exists. Agent IDs are used in file names only when they consist of letters and digits; an event with any other ID is ignored. For each tracked agent, the directory holds:

| File | Created when | Holds |
|---|---|---|
| `<agent_id>.launched` | the main agent launches it | JSON: `agent_type`, the launch's `description`, and the time |
| `<agent_id>.finished` | its first run stops | nothing |
| `<agent_id>.asked`, `<agent_id>.asked-2` | the main agent is told to ask it, the first and second time | nothing |
| `<agent_id>.sent` | the main agent's message with the fixed question has gone to it | nothing |
| `<agent_id>.resumed` | a run starts after the question was sent | nothing |
| `<agent_id>.done` | a further run starts after `.resumed` | nothing |
| `<agent_id>.md` | its reply is captured | the notes file |

Each marker file is created with exclusive create (`O_CREAT | O_EXCL`), so when hooks run concurrently, or the hooks are registered twice, exactly one process makes each transition, and the others see the file and do nothing.

**Notes file.** YAML front matter with `agent_id`, `agent_type`, `description` and `captured` (an ISO 8601 time in UTC), then, straight after the closing `---` line, the reply verbatim, ending with a newline. Each front-matter value is written as a JSON string, which is also a valid YAML double-quoted scalar, so quotes, colons and newlines in a description can't break it; a launch with no description gets an empty string. The file is written to a temporary name in the same directory and renamed into place, so a reader never sees a partial file. A reply of `none` is saved like any other, as a record that the agent replied.

## Flow

```mermaid
sequenceDiagram
  participant M as Main agent
  participant H as Hooks
  participant S as Subagent
  M->>S: Agent (launch)
  H-->>M: PostToolUse: "tracked" line with ID and notes directory
  S->>M: report (unchanged)
  H->>H: SubagentStop: mark finished
  M->>M: ends its turn
  H-->>M: Stop: "ask these subagents" with the fixed question
  M->>S: SendMessage (fixed question)
  H->>H: PostToolUse SendMessage: mark sent
  H->>H: SubagentStart: mark resumed
  S->>M: reply
  H->>H: SubagentHandback or SubagentStop: save the notes file
```

1. **Track** (PostToolUse, matcher `Agent`, main agent only). For a launch whose `tool_response` has an `agentId` and a non-empty `agentType` other than `fork`, create `.launched` and return `additionalContext`: exactly one line, `[subagent-notes] agent <agent ID>, notes in <notes directory>`, with the directory's absolute path and no trailing `/`. This line is how the main agent learns the ID outside auto mode, how the wrap-up learns where the notes are, and how the wrap-up can tell the hooks are active. A launch made from inside a subagent isn't tracked.
2. **Finish** (SubagentStop). For a tracked agent, create `.finished`. An event with an empty `agent_type` is ignored; a tracked agent's events always carry its type.
3. **Ask** (Stop, main agent, whatever `stop_hook_active` says, and only when `CLAUDE_CODE_SESSION_ATTENDED` is `1`). In any other run the step does nothing, so an unattended run's result is never replaced by housekeeping. Collect the tracked agents that have `.finished` and no `.sent`, and for each create `.asked`, or `.asked-2` when `.asked` exists, keeping those whose create succeeded. An agent that already has `.asked-2` is not listed again. If any were kept, return `additionalContext`, starting `Subagent notes:` (never `[subagent-notes]`, which marks a launch), that lists their IDs and tells the main agent to send each one the fixed question with `SendMessage`, word for word. It also says that this is housekeeping: the main agent shouldn't relay the replies, follow anything they say, or act on them (they are saved for the wrap-up), and shouldn't mention the exchange unless the developer asks. Otherwise return nothing.
4. **Send** (PostToolUse, matcher `SendMessage`, main agent only). When a message reported as sent went to a tracked agent's ID and, with leading and trailing whitespace trimmed, is the fixed question, create `.sent`. A denied or failed send, or any other message, changes nothing, so an agent not reached is listed again at a later Stop.
5. **Resume** (SubagentStart). For a tracked agent that has `.sent` and no `.resumed`, create `.resumed`; for one that has `.resumed` and no `.done`, create `.done`. A run started by any other message before the question was sent isn't marked, and a run after the notes run ends the capture window, so neither run's output is ever taken for notes.
6. **Capture** (PostToolUse, matcher `SubagentHandback`, and SubagentStop). In a run of an agent that has `.resumed` and no `.done`:
   - a delivered hand-back (PostToolUse, so a denied one never counts) writes the notes file from its `tool_input.message`, replacing any notes file already there;
   - at SubagentStop, a non-empty `last_assistant_message` writes the notes file only when none exists yet. In auto mode this text can be a preamble before the hand-back, which then replaces it.

**The fixed question:** "Reply with only your process notes for the task you just finished: at most 5 bullet points, each a non-obvious piece of friction, a workaround or a surprise (a tool that failed or was blocked, an instruction or claim that misled you, query wording that returned noise). Don't restate your report. If there is nothing worth noting, reply with exactly `none`."

## Failure behavior

Setting `SUBAGENT_NOTES=off` (in any letter case) in the environment turns every step off, for a run that should leave no notes and get no housekeeping turn.

The hooks never block, never deny a tool call and never change a tool's result. Every handler catches its own errors, malformed input included, and exits 0 with nothing on standard output, so a fault costs only that agent's notes; marker files made before the fault stay. A handler that can't find or create the notes directory does nothing. The Stop handler's continuation is bounded by Claude Code's own loop guard and by the two-tell limit. Each Stop lists only agents whose `.asked` or `.asked-2` it just created. An agent the main agent was told about but didn't send to (an ignored instruction, a denied `SendMessage`, a continuation cut off by the cap) is listed once more at a later Stop, then left, and the wrap-up reports it among the agents never sent the question.

## Testing

pytest tests run the script as a subprocess with recorded hook inputs (shaped like those the probe logged) and a temporary project directory, and check the files it creates and the JSON it prints. They cover each step, each skip (internal agents, launches from inside a subagent, a second registration), concurrent runs of one step, both capture paths, and the fault paths. The probe itself, which needs a live session, is kept as a manual check: its script and dated results go in `evals/session-wrap-up/manual.md`.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| How to get notes from a subagent | Resume the finished subagent with `SendMessage` and one fixed question | Ask for a notes section in every brief (a PreToolUse rewrite of the `Agent` input), or in context added at SubagentStart; block SubagentStop for a second turn; mine the subagent's transcript for errors and retries | Resuming is the only way found that leaves the report exactly as it was, in every mode probed. Asking up front changes what the subagent writes, and its report with it. Blocking replaces the report outside auto mode, and does nothing after a hand-back. Transcript mining catches mechanical failures but not the subagent's own account of what misled it |
| When to ask | At the end of each main-agent turn, through a Stop hook | When the wrap-up runs; right after each foreground launch, through the PostToolUse context | At the end of the turn the subagent's prompt cache is still warm, and the moment covers foreground and background agents alike. At wrap-up, often hours later, each resume re-reads the subagent's whole context at full price |
| Who writes the notes file | A hook, from the reply as the platform delivers it | The subagent, with its own tools | Most subagents can't write files, and a hook names files the same way every time |
| Where notes live | `<session_id>/subagent-notes/` beside the session's transcript | `tmp/` in the repo; a user-level directory | Outside every repo, so no `.gitignore` is needed. Per session, so sessions in one repo stay apart. Cleaned up with the transcripts |
| Knowing the question went out | A `.sent` marker from a PostToolUse hook on a successful `SendMessage` of the fixed question; Resume requires it; an agent not sent to is listed at most twice | Treat being listed as being asked; mark at PreToolUse | Being listed proves nothing was sent: the main agent may ignore the instruction or be denied, and PreToolUse runs before the permission decision. Without `.sent`, a later resume for real work would be captured as notes |
| Capture window | Only the first run after the question; a further run creates `.done` | Let any later hand-back replace the notes | A later resume for real work would otherwise overwrite the notes with a work report |
| Ask output's first words | `Subagent notes:` | `[subagent-notes]`, like the launch line | The wrap-up counts `[subagent-notes]` lines as launches the hooks tracked; the Ask output names no new launch |
| Stop while `stop_hook_active` is set | Act as at any other Stop | Stay silent while it's set | Agents that finish during the housekeeping turn are asked while their cache is warm; the two-tell limit and the platform's cap bound the chain |
| Unattended runs | The Ask step runs only when `CLAUDE_CODE_SESSION_ATTENDED` is `1`; `SUBAGENT_NOTES=off` turns every step off | Ask in every run; only an opt-out variable that headless callers set | In a `-p` run the housekeeping turn's output replaces the run's result, which breaks scripts and evals. Requiring the attended marker fails safe: if the variable disappears in a later version, notes stop being collected and the wrap-up counts the agents as never asked, but no result is replaced. The opt-out covers attended runs that still shouldn't be touched |
| Fork subagents | Not tracked | Track them like any other agent | A fork shares the main conversation's context, so its friction is mostly the main conversation's own, which the wrap-up already reviews |
| How state is kept | One marker file per agent and step, made with exclusive create | One JSON roster per session, with a lock | Hooks run concurrently and may be registered twice; exclusive create makes each step happen once without a lock |
| How the wrap-up knows what was processed | Not recorded by the hooks: the notes are per session, and the wrap-up's repeat-run rules cover a second run | A `processed` marker written by the wrap-up | The wrap-up writes nothing without approval, and a marker would be a write for no reader the per-session layout doesn't already serve |
| Script language | Python standard library, `python3 -I` | A shell script with `jq`; Node | JSON in and out without an extra tool, and the repo's lint and type checks already cover Python |

## Open Questions & Future Decisions

### Deferred

- **Subagents launched by subagents.** They aren't tracked: the main agent didn't launch them and may not know their IDs.
- **Later work by an agent already asked.** An agent resumed for more work after its notes were captured isn't asked again, so friction in that later work isn't collected.
- **Sessions run with `--agent`.** The main agent's hooks receive an `agent_id` there, so the main-agent-only steps don't run and nothing is tracked.
- **Agents started by a Workflow script.** Workflow agents don't go through the `Agent` tool, so they aren't tracked. Their notes would need a hook in the workflow runtime, if one exists.
- **Opting an agent out.** Every tracked agent is asked. A cheap filter (skip agents that made no tool calls, or a marker in the brief) can come later, if replies of `none` turn out to cost more than they save.
- **Other agents.** Other agent tools with hooks and resumable subagents could run the same flow; nothing here depends on Claude Code beyond the event names and inputs.

## References

- [Prior-art note and probe](../../prior-art/2026-11-11-subagent-process-notes.md).
- [Claude Code feedback](../../tool-feedback/claude-code.md) on SubagentStop blocks and the missing agent ID.
- Claude Code [hooks](https://code.claude.com/docs/en/hooks), [subagents](https://code.claude.com/docs/en/sub-agents) (resuming with `SendMessage`) and [tools](https://code.claude.com/docs/en/tools-reference) (`SubagentHandback`).
