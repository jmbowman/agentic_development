# Prior art: collecting process notes from subagents (2026-11-11)

- **Supersedes:** none. [The 2026-10-29 wrap-up note](2026-10-29-session-wrap-up-skills.md) covered wrap-up skills for the main session. This note covers what it left open: process notes from subagents, which a wrap-up in the main conversation sees only through their reports.
- **Effort:** quick pass, by the developer's choice. The searches ran on 2026-11-10. A probe of the platform's hook and resume behavior (described under [Probe](#probe-of-the-platform)) ran on 2026-11-11, because the candidates' main limits were claims about Claude Code itself.
- **Already known:** asked; not answered.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Each subagent's friction, workarounds and surprises reach the session wrap-up | Lessons learned inside a subagent aren't lost when only its report returns |
| Happens without the main agent remembering to ask, with the same wording every time | Collection is consistent, not dependent on how a brief was phrased |
| The subagent's report is unchanged | Skills parse reports in fixed formats, some of them JSON |
| Works for subagents without file-writing tools | Read-only agents (such as Explore) are the common case |
| Notes land in files under a standard path with collision-free names, and the wrap-up knows which it has processed | Several sessions may run in one repo at once, and a repeat wrap-up shouldn't re-triage old notes |

**Hard criteria:**
1. License compatible with this repo's Apache-2.0, for anything adopted or adapted.
2. The report the parent receives is unchanged.
3. Works for a subagent with no Write, Edit or Bash tool.
4. Runs in Claude Code, locally, with no service beyond the agent's own tools and hook scripts.

**Preferences:** works in auto mode and in modes without auto mode's hand-back; per-agent files; a "processed" record; small enough to maintain here.

## Verdict

**Unaudited (quick pass by developer choice).** The evidence points to **build**, borrowing ideas from the candidates below: no candidate meets hard criteria 2 and 3 while capturing the agent's own reflection rather than mechanical signals. A full method would add the routes excluded below and verify the top candidates' code at full depth.

The design the probe supports: a hook records each subagent's ID and gives it to the main agent; the main agent resumes each finished subagent with `SendMessage` and one fixed question; a hook saves the reply to a per-agent file; the wrap-up reads the files it hasn't processed.

## Candidates

| Candidate | Class | License | Reason |
|---|---|---|---|
| [dagonet/claude-code-toolkit](https://github.com/dagonet/claude-code-toolkit) (`hooks/retro-ledger.sh`) | borrow ideas | MIT (`LICENSE:1-3` at e1ef98a) | A SubagentStop hook mines the subagent's own transcript for dead tools, hook blocks and errors, never blocks, and appends one line per subagent to a ledger. Captures mechanical friction, not the agent's reflection; one shared file with no processed marker |
| [tdimino/claude-code-minoan](https://github.com/tdimino/claude-code-minoan) (`hooks/subagent-stop-log.py`) | borrow ideas | MIT (`LICENSE:1-3` at 634a705) | The same approach with issue flags (truncated or tiny output, tool-error rate); triage is manual |
| [joeblackwaslike/lessons-learned](https://github.com/joeblackwaslike/lessons-learned) | borrow ideas | MIT (`LICENSE:1-3` at 3b39f38) | A SubagentStart hook adds context asking every subagent to emit tagged lesson blocks in its own text; a scanner later extracts them from transcripts. Works for read-only agents, but nothing keeps a block out of the final report |
| [piercelamb/deep-plan](https://github.com/piercelamb/deep-plan) (`scripts/hooks/write-section-on-stop.py`) | borrow ideas | not read | A SubagentStop hook writes a file on behalf of a tool-less subagent, from its transcript, without blocking |
| [agentic-retro](https://www.npmjs.com/package/agentic-retro) | borrow ideas | MIT (`package/LICENSE:1-3`, 0.1.10) | A proposal ledger (open, accepted, rejected) keeps declined items from returning |
| [learn-from-mistakes-axi](https://www.npmjs.com/package/learn-from-mistakes-axi) | borrow ideas | MIT (`package/LICENSE:1-3`, 0.12.0) | Offline CLI that reads subagent transcripts and attributes their "user" turns to the parent agent |
| [oscarthroedsson/breadcrumb](https://github.com/oscarthroedsson/breadcrumb) | reject | MIT (`LICENSE:1-3` at 0ffe15a) | Blocks SubagentStop until a handoff block appears; its hook header says the subagent then rewrites its final message (fails criterion 2) |
| [kookr-ai/kookr](https://github.com/kookr-ai/kookr), [jeanibarz/agent-notebook](https://github.com/jeanibarz/agent-notebook) | reject | Apache-2.0; MIT (`LICENSE:1-3` at 9457fa5) | Block one stop per session for a retrospective written with a CLI: fails criteria 2 and 3. agent-notebook's docs call the hook a backstop behind a contract in the brief |
| [zolat/claude-code-retros](https://github.com/zolat/claude-code-retros) | reject | none (no license file at 8f0f145) | Fails criterion 1. Idea noted: a Stop hook forks the finished session to write a retro, leaving the original untouched; whole sessions only |
| [@windyroad/retrospective](https://www.npmjs.com/package/@windyroad/retrospective) | borrow ideas | unverified (manifest says MIT; no license file in 0.28.1) | Scans delegation friction from the parent's side |

Seen and not classified: about 45 whole-session retro skills, cost and telemetry loggers, and friction CLIs that need Bash.

## Probe of the platform

Run on Claude Code 2.1.322 with `claude -p`, a throwaway plugin loaded through `--plugin-dir`, and one Explore subagent told to reply with only a JSON object. Each scenario checked whether the parent received that JSON unchanged.

| Scenario | Result |
|---|---|
| Auto mode, foreground and background: SubagentStop blocks once after the agent's `SubagentHandback` | The block is recorded in the subagent's transcript as a `hook_blocking_error`, but no further turn runs and no second SubagentStop fires. The report arrives unchanged; no notes are produced |
| Manual mode: SubagentStop blocks every first stop | The parent receives the reply to the hook's reason instead of the report, reproducing [anthropics/claude-code#85917](https://github.com/anthropics/claude-code/issues/85917) |
| Auto mode, foreground and background: the parent resumes the finished subagent with `SendMessage` | The report arrives unchanged; the notes arrive as a separate reply. The resumed run fires a second `SubagentStart` with the same agent ID, and its reply comes through a second `SubagentHandback` |
| Manual mode: resume | The parent can't address the subagent: its tool result carries the report but no agent ID |
| Manual mode: resume, with a PostToolUse hook on `Agent` passing `tool_response.agentId` to the parent as `additionalContext` | Works. The reply is in `last_assistant_message` at the resumed run's SubagentStop |

So blocking SubagentStop can't collect notes without changing the report (or, after a hand-back, at all), and resuming can, in every mode tested. [#86569](https://github.com/anthropics/claude-code/issues/86569) adds that a block is ignored for an agent with a structured output schema. Not probed: subagents started by Workflow scripts or by other subagents, and resuming after the prompt cache has expired. Every notes reply in the probe came from a trivial task, yet carried a real note (a misleading claim in the subagent's environment).

## Limitations checked in source

Verified (read at full depth by a search subagent):
- dagonet's hook never blocks and appends to one per-project ledger (`hooks/retro-ledger.sh:47-51,144,167-191` at e1ef98a).
- tdimino's hook has no blocking and no context injection (`hooks/subagent-stop-log.py:17` at 634a705).
- lessons-learned's protocol places lesson blocks in assistant text with no rule against the final message (`hooks/subagent-start-lesson-protocol.mjs:22-32` at 3b39f38).
- kookr's retrospective needs the `nb` CLI (`plugin/hooks/nb-retro.mjs:86-100` at e8430c6).

Could not verify:
- deep-plan's license and commit (clone failed on the network).
- blueman82/recall's SubagentStop hook (repository not found; a mirror timed out).
- blotter-cli's source and license (clone timed out).
- breadcrumb's rewrite claim was read at snippet depth.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Claude Code hooks, tools and subagents reference, fetched 2026-11-10: SubagentStop input and decision control, `SubagentHandback`, resuming subagents |
| Earlier notes and decisions | searched | [2026-10-29 wrap-up note](2026-10-29-session-wrap-up-skills.md); the session-wrap-up design; no decision records on the topic |
| GitHub code search | searched | `SubagentStop`; `"agent_transcript_path"` (the productive one); `SubagentStop lessons`; `SubagentStop retro`; `nb-retrospective` |
| GitHub repository search | searched | SubagentStop hook; subagent retrospective; subagent feedback; subagent learnings; agent retro hook; claude hooks learning; session learnings hook; subagent transcript; agent self reflection claude; claude retrospective; friction log agent; subagent stop hook; agent-notebook |
| GitHub topics | searched | `topic:claude-code-hooks` learning; `topic:claude-code-plugin` retrospective; `topic:claude-code-plugin` learnings |
| Claude Code plugin marketplaces | searched | Anthropic's marketplace file, grepped for retro, learn, lesson, reflect, friction, feedback, subagent, transcript, hook, wrap, insight |
| Skill directories | searched | skills.sh: subagent feedback; subagent retrospective; friction log; session retrospective; lessons learned hook |
| npm | searched | claude code subagent hook; claude-code retro; claude learnings hook; agent retrospective; claude code lessons learned; subagentstop; claude code reflection hook |
| crates.io | searched | claude hooks; subagent; agent retrospective; claude learnings |
| PyPI | searched | web search `site:pypi.org` claude code subagent hook retrospective lessons |
| General web search | searched | five phrasings, including "SubagentStop hook capture subagent learnings" and "mine claude code subagent transcripts jsonl friction" |
| Awesome lists | searched | awesome-claude-code, grepped for subagent stop, retro, lesson, reflect, learning, friction |
| aitoolnet.com | searched | sitemap slugs for retro, reflect, learning, lesson, subagent, friction, hindsight |
| GitLab and Codeberg search | excluded | quick pass |
| LibHunt | excluded | quick pass |
| Literature routes | excluded | quick pass |
| Homebrew, nixpkgs, AUR | excluded | the need is a hook set, not a command-line tool |
| MCP Registry, PulseMCP | excluded | the need isn't an MCP server |
| Hosted services | excluded | the notes must stay local, beside the session |

## Snowball rounds

One round: kookr led to agent-notebook, and dagonet's design docs led to its retro ledger. The round added agent-notebook; the cap wasn't reached, and no further round ran (quick pass).

## Refresh trigger

A Claude Code release that changes SubagentStop blocking after a hand-back, fixes #85917, or puts the agent ID in a manual-mode `Agent` result.
