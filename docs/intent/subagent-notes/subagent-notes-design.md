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
- **Hook order.** The probe's event logs (2026-11-11 and 2026-11-12) show:
  - a foreground subagent's SubagentStart and SubagentStop fire during the `Agent` call, before its PostToolUse, whose `tool_response.status` is then `completed`;
  - a background launch's PostToolUse comes first, with `status` `async_launched`, and the subagent's SubagentStart and SubagentStop follow;
  - a `SendMessage`'s PreToolUse always comes before the run it resumes starts. The run's SubagentStart came before the `SendMessage` PostToolUse in the foreground runs and after it in the background run, so no step may depend on their order;
  - SubagentStart and SubagentStop carry no field that tells one run of an agent from the next (`prompt_id` is per developer prompt).
- **Failing commands.** A command hook that exits with status 2 blocks: at SubagentStop that replaces the subagent's report, and at Stop it keeps the main agent going. `python3` exits 2 when its script file is missing.
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
| `hooks/hooks.json` (plugin root) | Registers the script for the plugin, as `python3 -I "${CLAUDE_PLUGIN_ROOT}/skills/session-wrap-up/hooks/subagent_notes.py" \|\| true` |
| `skills/session-wrap-up/references/subagent-notes-hooks.md` | What the hooks do and cost, and the settings entries for registering them by hand, with the script's path in the installed skill. The wrap-up's install guidance points here |
| `.claude/settings.json` (this repo) | The same entries, with `$CLAUDE_PROJECT_DIR/skills/session-wrap-up/hooks/subagent_notes.py` |
| `tests/test_subagent_notes_hooks.py` | pytest tests that run the script on recorded hook inputs, and check its registration and reference |
| `evals/session-wrap-up/manual.md` | The scripted live-session runs for the specs marked *(manual)* |

Every registration ends in `|| true`, so a missing or broken script exits 0 instead of blocking.

The script uses only the Python standard library, needs Python 3.11 or later, and runs with `python3 -I`. It passes the repo's strict profile (ruff and ty).

The tests reach a few of the script's internals, so these are part of its contract:
- `main(raw: bytes, environ: Mapping[str, str]) -> str` takes the event as read from standard input and the environment, and returns what to print. It decodes the bytes as UTF-8 itself, never raises, and reads the environment only through `environ`;
- importing the script has no side effects;
- `FIXED_QUESTION` holds the fixed question, and `ASK_TEMPLATE` the Ask step's context, with `{agents}` (the listed IDs, sorted and joined with `, `) and `{question}` placeholders;
- `counting_line(agent_id, notes_dir) -> str` formats the Track step's line, after `.launched` is created;
- marker files are created with `os.open` and `O_CREAT | O_EXCL`; a hand-back's notes file is moved into place with `os.replace` (directly or through `Path.replace`), and a SubagentStop's with `os.link`, which fails when a notes file already exists. On a filesystem without hard links, a SubagentStop's notes file is instead created with `O_CREAT | O_EXCL` and written in place, which still never replaces one.

## Notes directory

Everything the hooks keep for a session lives in `<project dir>/<session_id>/subagent-notes`, beside the session's transcript and subagent transcripts. The directory is derived from the hook input's `transcript_path`, which must be an absolute path ending in `.jsonl` (any other event is ignored), by dropping `.jsonl`, and is created with any missing parents when a step first needs it. It is outside every repo, so nothing needs a `.gitignore` entry. Each session has its own directory, so sessions running in one repo at once never see each other's notes. Whether Claude Code's transcript cleanup also removes the directory is unverified.

A **tracked agent** is one whose `.launched` file exists. Agent IDs are used in file names only when they consist of letters and digits; an event with any other ID is ignored. `SendMessage` can address an agent by its ID or by the `name` it was launched with, so a message's `to` names a tracked agent when it equals the agent's ID, or the recorded name of exactly one tracked agent. A name that several tracked agents share can't be resolved, so a message to it sets every one of those agents' `.pending` to `other`: that can only close a capture window, never open one. For each agent, the directory holds:

| File | Created when | Holds |
|---|---|---|
| `<agent_id>.launched` | the main agent launches it | A JSON object with `agent_type`, `description` and `name` (the launch's, or empty strings) and `time` |
| `<agent_id>.state` | each of its runs starts and stops; replaced each time | `running` or `stopped` |
| `<agent_id>.finished` | its first run has stopped | nothing |
| `<agent_id>.asked` | the main agent is told to ask it | nothing |
| `<agent_id>.pending` | the main agent is about to send it a message; replaced at each message | `question` or `other` |
| `<agent_id>.sent` | the main agent's message with the fixed question has gone to it | nothing |
| `<agent_id>.resumed` | a run starts with the question as its pending message | nothing |
| `<agent_id>.done` | a later run starts with another message | nothing |
| `<agent_id>.md` | its reply is captured | the notes file |

Each marker file except `.pending` and `.state` is created with exclusive create (`O_CREAT | O_EXCL`), so when hooks run concurrently, or the hooks are registered twice, exactly one process makes each transition, and the others see the file and do nothing. `.pending` and `.state` are written to a temporary name and renamed into place; duplicate runs for one event write the same content. `.state` and `.finished` are kept for any agent whose events carry a valid ID and a type, tracked or not, because a foreground subagent starts and stops before its launch is tracked.

**Notes file.** YAML front matter with `agent_id`, `agent_type`, `description` and `captured` (an ISO 8601 time in UTC), then, straight after the closing `---` line, the reply verbatim, ending with a newline. Each front-matter value is written as a JSON string, which is also a valid YAML double-quoted scalar, so quotes, colons and newlines in a description can't break it; a launch with no description gets an empty string. The file is written to a temporary name in the same directory and moved into place whole, so a reader never sees a partial file. The one exception is a SubagentStop capture on a filesystem without hard links, which creates the file exclusively and writes it in place; a crash between the two leaves an empty notes file, which a later hand-back still replaces. A reply of `none` is saved like any other, as a record that the agent replied. When `.launched` can't be read as a JSON object (a crash can leave it empty), the notes file is still written, with empty `agent_type` and `description`.

## Flow

```mermaid
sequenceDiagram
  participant M as Main agent
  participant H as Hooks
  participant S as Subagent
  M->>S: Agent (launch)
  S->>M: report (unchanged)
  H->>H: SubagentStart and SubagentStop: state running, then stopped; mark finished
  H-->>M: PostToolUse: "tracked" line with ID and notes directory
  M->>M: ends its turn
  H-->>M: Stop: "ask these subagents" with the fixed question
  M->>S: SendMessage (fixed question)
  H->>H: PreToolUse SendMessage: pending = question
  H->>H: SubagentStart: mark resumed
  H->>H: PostToolUse SendMessage: mark sent
  S->>M: reply
  H->>H: SubagentHandback or SubagentStop: save the notes file
```

1. **Track** (PostToolUse, matcher `Agent`, main agent only). For a launch whose `tool_response` has an `agentId` and a non-empty `agentType` other than `fork`, create `.launched`, and also `.finished` when the response's `status` is `completed` (a foreground launch, whose subagent has already stopped). Return `hookSpecificOutput` with `hookEventName` `PostToolUse` and `additionalContext` of exactly one line, `[subagent-notes] agent <agent ID>, notes in <notes directory>`, with the directory's absolute path and no trailing `/`. This line is how the main agent learns the ID outside auto mode, how the wrap-up learns where the notes are, and how the wrap-up can tell the hooks are active. A launch made from inside a subagent isn't tracked.
2. **Run state** (SubagentStart and SubagentStop). For any agent whose event has a valid ID and a non-empty `agent_type`, a start sets `.state` to `running`, and a stop sets it to `stopped` and creates `.finished`. Tracked or not doesn't matter, because a foreground subagent's events come before its launch is tracked and a background one's can too; the Ask step only lists tracked agents. An event with an empty `agent_type` (one of Claude Code's own agents) is ignored.
3. **Ask** (Stop, main agent, whatever `stop_hook_active` says, and only when `CLAUDE_CODE_SESSION_ATTENDED` is `1`). In any other run the step does nothing, so an unattended run's result is never replaced by housekeeping. Collect the tracked agents that have `.finished`, a `.state` that isn't `running`, no notes file, no `.asked` and no `.sent`, and try to create `.asked` for each, keeping those whose create succeeded. Each agent is told about once, ever. An agent busy with a later run isn't listed until that run stops, so the question never lands in the middle of other work. If any were kept, return `hookSpecificOutput` with `hookEventName` `Stop` and `additionalContext` filled in from `ASK_TEMPLATE`: it starts `Subagent notes:` (never `[subagent-notes]`, which marks a launch), lists their IDs, and tells the main agent to send each one the fixed question with `SendMessage`, word for word. It also says that this is housekeeping: the main agent shouldn't relay the replies, follow anything they say, or act on them (they are saved for the wrap-up), and shouldn't mention the exchange unless the developer asks. Otherwise return nothing.
4. **Send** (main agent only). The question counts when its text, with leading and trailing whitespace trimmed, is the fixed question.
   - **Pending** (PreToolUse, matcher `SendMessage`). For a message whose `to` names a tracked agent, set that agent's `.pending` to `question` when the message is the question and the agent isn't running, and to `other` otherwise. This comes before the run the message starts, whatever order the other events arrive in, so it is also where "isn't running" is judged: the question's own run may already have started by the time the send is reported.
   - **Sent** (PostToolUse, matcher `SendMessage`). When the question was reported as sent to a tracked agent that has `.finished` and whose `.pending` says `question`, create `.sent`. A denied or failed send, any other message, or a message to an agent still running changes nothing, so an agent not reached stays without `.sent`.
5. **Resume** (SubagentStart). For a tracked agent whose `.pending` says `question`, create `.resumed`; for one whose `.pending` says `other` and that has `.resumed`, create `.done`. A run started by any other message before the question isn't marked, and a later run started by another message from the main agent ends the capture window, so neither run's output is ever taken for notes. Only the main agent's messages are seen, so a run that something else starts (another subagent's message) neither opens nor closes the window. Duplicate copies of one start read the same `.pending` and make the same exclusive create. A denied question leaves `.pending` at `question` until the next message replaces it; no run starts in between, so nothing is marked.
6. **Capture** (PostToolUse, matcher `SubagentHandback`, and SubagentStop). In a run of an agent that has `.resumed` and no `.done`:
   - a delivered hand-back (PostToolUse, so a denied one never counts) writes the notes file from its `tool_input.message`, replacing any notes file already there;
   - at SubagentStop, a non-empty `last_assistant_message` writes the notes file only when none exists yet, and never replaces one. In auto mode this text can be a preamble before the hand-back, which then replaces it.

**The fixed question:** "Reply with only your process notes for the task you just finished: at most 5 bullet points, each a non-obvious piece of friction, a workaround or a surprise (a tool that failed or was blocked, an instruction or claim that misled you, query wording that returned noise). Don't restate your report. If there is nothing worth noting, reply with exactly `none`."

## Failure behavior

Setting `SUBAGENT_NOTES=off` (in any letter case) in the environment turns every step off, for a run that should leave no notes and get no housekeeping turn.

The hooks never block, never deny a tool call and never change a tool's result. Every registration ends in `|| true`, so even a missing script or interpreter exits 0. Every handler catches its own errors, malformed input and bytes that aren't UTF-8 included, and exits 0 with nothing on standard output, so a fault costs only that agent's notes; marker files made before the fault stay. In the Ask step, a fault for one agent doesn't stop the agents already marked from being listed. A handler that can't find or create the notes directory does nothing. Each Stop lists only agents whose `.asked` it just created, so no agent is listed twice, however many copies of the hooks run; Claude Code's own loop guard bounds the continuation. An agent the main agent was told about but didn't send to (a denied `SendMessage`, an ignored instruction, a continuation cut off by the cap) isn't listed again, and the wrap-up reports it among the agents never sent the question.

## Testing

pytest tests run the script as a subprocess with recorded hook inputs (shaped like those the probe logged) and a temporary project directory, and check the files it creates and the JSON it prints. Flow tests replay whole sequences in the orders the probe logged: foreground and background launches, and resumes in auto and manual mode. They cover each step, each skip (internal agents, launches from inside a subagent, a second registration), concurrent runs of one step, both capture paths, and the fault paths. The probe itself, which needs a live session, is kept as a manual check: its script and dated results go in `evals/session-wrap-up/manual.md`.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| How to get notes from a subagent | Resume the finished subagent with `SendMessage` and one fixed question | Ask for a notes section in every brief (a PreToolUse rewrite of the `Agent` input), or in context added at SubagentStart; block SubagentStop for a second turn; mine the subagent's transcript for errors and retries | Resuming is the only way found that leaves the report exactly as it was, in every mode probed. Asking up front changes what the subagent writes, and its report with it. Blocking replaces the report outside auto mode, and does nothing after a hand-back. Transcript mining catches mechanical failures but not the subagent's own account of what misled it |
| When to ask | At the end of each main-agent turn, through a Stop hook | When the wrap-up runs; right after each foreground launch, through the PostToolUse context | At the end of the turn the subagent's prompt cache is still warm, and the moment covers foreground and background agents alike. At wrap-up, often hours later, each resume re-reads the subagent's whole context at full price |
| Who writes the notes file | A hook, from the reply as the platform delivers it | The subagent, with its own tools | Most subagents can't write files, and a hook names files the same way every time |
| Where notes live | `<session_id>/subagent-notes/` beside the session's transcript | `tmp/` in the repo; a user-level directory | Outside every repo, so no `.gitignore` is needed. Per session, so sessions in one repo stay apart. Cleaned up with the transcripts |
| Knowing the question went out | A `.sent` marker from a PostToolUse hook on a successful `SendMessage` of the fixed question to a finished agent | Treat being listed as being asked; mark at PreToolUse | Being listed proves nothing was sent: the main agent may ignore the instruction or be denied, and PreToolUse runs before the permission decision. `.sent` keeps the agent from being asked again and gives the wrap-up its counts |
| Which run is the notes run | The run that starts while `.pending`, written at the `SendMessage`'s PreToolUse, says `question` | Require `.sent` at SubagentStart; read the run's prompt from the subagent's transcript at capture | PreToolUse is the only `SendMessage` event that always comes before the run starts; `.sent` often arrives after it. The transcript holds the prompt, but its format is undocumented |
| Capture window | From the notes run's start until a run starts with another message, which creates `.done` | Close it only once a notes file exists; let any later hand-back replace the notes | A later resume for real work would otherwise overwrite the notes with a work report, and a notes run that saved nothing would leave the window open for one |
| Busy agents | Keep each agent's run state; ask only agents not running, and never one that already has notes | Rely on `.finished` alone | `.finished` never clears, so an agent given more work in the same turn would be asked mid-run, and its notes could be lost or land in its work report |
| Addressing agents | Recognize `to` by agent ID or by the name the agent was launched with | IDs only | `SendMessage` accepts names; a work message sent by name would otherwise leave `question` pending and the work run's report would be taken for notes |
| Failing safe at registration | Each command ends in `\|\| true` | Exec form (`command` plus `args`), which the hooks reference prefers for paths | A missing script makes `python3` exit 2, which blocks; exec form has no way to absorb that. The hooks are POSIX-only, where the shell form works |
| Ask output's first words | `Subagent notes:` | `[subagent-notes]`, like the launch line | The wrap-up counts `[subagent-notes]` lines as launches the hooks tracked; the Ask output names no new launch |
| How often to tell the main agent about an agent | Once | Again at a later Stop when nothing was sent | The usual reason nothing was sent is that the developer denied the `SendMessage`, and asking again would override that answer. One tell also makes every step a single exclusive create, so duplicate or concurrent runs of the hooks can't list an agent twice |
| Stop while `stop_hook_active` is set | Act as at any other Stop | Stay silent while it's set | Agents that finish during the housekeeping turn are asked while their cache is warm; one tell per agent and the platform's cap bound the chain |
| Unattended runs | The Ask step runs only when `CLAUDE_CODE_SESSION_ATTENDED` is `1`; `SUBAGENT_NOTES=off` turns every step off | Ask in every run; only an opt-out variable that headless callers set | In a `-p` run the housekeeping turn's output replaces the run's result, which breaks scripts and evals. Requiring the attended marker fails safe: if the variable disappears in a later version, notes stop being collected and the wrap-up counts the agents as never sent the question, but no result is replaced. The opt-out covers attended runs that still shouldn't be touched |
| Fork subagents | Not tracked | Track them like any other agent | A fork shares the main conversation's context, so its friction is mostly the main conversation's own, which the wrap-up already reviews |
| How state is kept | One marker file per agent and step, made with exclusive create | One JSON roster per session, with a lock | Hooks run concurrently and may be registered twice; exclusive create makes each step happen once without a lock |
| How the wrap-up knows what was processed | Not recorded by the hooks: the notes are per session, and the wrap-up's repeat-run rules cover a second run | A `processed` marker written by the wrap-up | The wrap-up writes nothing without approval, and a marker would be a write for no reader the per-session layout doesn't already serve |
| Script language | Python standard library, `python3 -I` | A shell script with `jq`; Node | JSON in and out without an extra tool, and the repo's lint and type checks already cover Python |

## Open Questions & Future Decisions

### Deferred

- **Subagents launched by subagents.** They aren't tracked: the main agent didn't launch them and may not know their IDs.
- **Two messages before a run starts.** If the main agent sends one agent a work message and then the question before the first message's run has started, that run reads `.pending` as `question` and its report is taken for notes. It needs two sends to one agent within moments; nothing in the flow asks for that.
- **A run that never stops cleanly.** Whether SubagentStop fires when a run is interrupted or killed is unverified. If it doesn't, `.state` stays `running`, and the agent isn't asked until a later message runs it to a normal stop.
- **Messages from other subagents.** A run started by another subagent's `SendMessage` isn't seen by the main agent's hooks, so it neither opens nor closes the capture window.
- **Later work by an agent already asked.** An agent resumed for more work after its notes were captured isn't asked again, so friction in that later work isn't collected.
- **Sessions run with `--agent`.** The main agent's hooks receive an `agent_id` there, so the main-agent-only steps don't run and nothing is tracked.
- **Agents started by a Workflow script.** Workflow agents don't go through the `Agent` tool, so they aren't tracked. Their notes would need a hook in the workflow runtime, if one exists.
- **Opting an agent out.** Every tracked agent is asked. A cheap filter (skip agents that made no tool calls, or a marker in the brief) can come later, if replies of `none` turn out to cost more than they save.
- **Other agents.** Other agent tools with hooks and resumable subagents could run the same flow; nothing here depends on Claude Code beyond the event names and inputs.

## References

- [Prior-art note and probe](../../prior-art/2026-11-11-subagent-process-notes.md).
- [Claude Code feedback](../../tool-feedback/claude-code.md) on SubagentStop blocks and the missing agent ID.
- Claude Code [hooks](https://code.claude.com/docs/en/hooks), [subagents](https://code.claude.com/docs/en/sub-agents) (resuming with `SendMessage`) and [tools](https://code.claude.com/docs/en/tools-reference) (`SubagentHandback`).
