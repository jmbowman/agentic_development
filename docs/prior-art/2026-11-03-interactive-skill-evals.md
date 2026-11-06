# Prior art: scripted multi-turn evals of an agent skill, question dialogs included (2026-11-03)

- **Effort:** full method, because the result replaces every manual run of this repo's skills, now and in later slices. A quick pass found a base that couldn't reach the question tool's previews.
- **Already known:** the developer hadn't tried or ruled out any tool. A "Playwright for terminals" was their own idea, covered by the terminal-driver routes.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Seed a scratch git repo per run | Each check starts from a known state |
| Drive a real Claude Code session through several typed turns, with this repo loaded as a plugin and a chosen model | Check the skill as it actually runs, not a simulation |
| Answer the question tool's dialogs: choose an option, add a note, type free text, dismiss | The approval gate's behavior depends on each kind of answer |
| See the dialogs' option previews, and check that a preview isn't cropped | The gate puts the exact text to approve in a preview |
| Answer plain-text questions, and run with the question tool turned off | The gate's second route |
| Check files at each stop, the order and inputs of tool calls, and the report text (with an LLM judge) | What `evals/session-wrap-up/manual.md`'s pass criteria check |

**Hard criteria:** an OSI-approved license for what this repo adopts or builds on; runs locally on Linux; drives Claude Code itself, with its own tools, skills and plugin loading; multi-turn, with scripted answers to the question tool. Claude Code is the system under test and is proprietary (`anthropics/claude-code` `LICENSE.md:1` at 26382c0), so the license criterion applies to the test tooling, not to it.

**Preferences:** Python, which the repo already uses for its tests; maintained; cheap to run by hand beside `claude plugin eval`.

## Verdict

**Blend:** the Claude Agent SDK for Python, driving the session and answering the dialogs, plus Microsoft's `tui-test`, for the one check that needs the rendered screen (a preview isn't cropped), plus a small pytest harness of this repo's own that turns each `manual.md` section into a test.

The harness borrows ideas from `smykla-skalski/sai`'s `eval_interview.py` (the SDK's `can_use_tool` answering the question tool, beside an LLM judge), `fullsend-ai/agent-eval-harness` (answers per case, from overrides), and `jfrog/agent-belt` (ordered turns, `git diff` and tool-sequence checks).

## Candidates and matrix

Ranked by hard criteria met, then preferences:
1. **Claude Agent SDK (Python):** the only OSI-licensed driver with structured access to every question-tool answer, previews and notes included (trial run below). It would drop if a later Claude Code version stopped passing previews to it.
2. **tui-test:** the only maintained, OSI-licensed tool that reads a full-screen terminal interface's rendered text, so it alone can check cropping. It would move to first, as the main driver, if the skill under test treats an SDK session as headless, since a tui-test session is genuinely interactive. Its engine is a first-class Rust crate (`tui-test-rs` 0.1.1), with Python, Node and Go bindings.
3. **fullsend-ai/agent-eval-harness:** a mature framework for Claude Code evals, with LLM and Python judges over files, tool calls and the conversation, hooks around each step, and runners for several agents. But each step is a fresh `claude --print` conversation, and it answers the question tool with an answer per question text only. It would move up if it gained a runner that keeps one session across turns.
4. **smykla-skalski/sai `eval_interview.py`:** closest in shape (SDK, `can_use_tool`, simulated user, judge), but it's a script for one skill, with no previews.
5. **adobe/skills stardust eval runner:** multi-turn, answers the question tool from a persona, but builds on the TypeScript SDK (not OSI-licensed) and has no previews.
6. **jfrog/agent-belt:** scripted turns and good checks, but each turn is a `claude -p` resume, with no question-tool answering.
7. **promptfoo's Claude Agent SDK provider:** previews and plugins pass through, but it builds on the TypeScript SDK, and its built-in answers are only first option, random or deny.

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| Claude Agent SDK, Python | build on | MIT (`LICENSE:1-3` at 144b7c9) | Multi-turn client, `can_use_tool` for every dialog, plugins, disallowed tools, hooks; previews through an environment variable |
| tui-test | build on | MIT (`LICENSE:1` at baa4bcc) | Real terminal emulator with screen text, waits and keys; Python bindings |
| fullsend-ai/agent-eval-harness | borrow ideas | Apache-2.0 (`LICENSE:1` at 5d98820) | Judges, step hooks and tool traces worth borrowing; one fresh conversation per step, and question answers by question text only |
| smykla-skalski/sai | borrow ideas | MIT (`LICENSE:1` at d5e0c41) | SDK answering plus judge, in one script |
| jfrog/agent-belt | borrow ideas | Apache-2.0 (`LICENSE:2` at 90bd105) | Ordered turns, `git diff`, tool-sequence checks |
| adobe/skills stardust runner | borrow ideas | Apache-2.0 (`LICENSE:1` at 429cbdc) | Persona answers through `canUseTool`; TypeScript SDK |
| UiPath/coder_eval | borrow ideas | Apache-2.0 (`LICENSE:2` at 484c3d5) | LLM user simulator over the SDK; no question-tool answers |
| promptfoo (Claude Agent SDK provider) | reject | MIT (`LICENSE:1-3` at f2b012e) | Fixed answer policies; TypeScript SDK underneath |
| Inspect AI with `inspect_swe` | reject | MIT (`LICENSE:1-3` at 4c5bf47) | No question-tool handling |
| LangWatch Scenario | reject | Apache-2.0 (`LICENSE:1-3` at 361be49) | `claude -p` per turn; the question tool is denied |
| mgechev/skillgrade | reject | MIT (`LICENSE:1` at ab2afd7) | A fresh `claude -p` per turn, with permissions skipped |
| huggingface/OpenEnv Claude Code harness | reject | BSD-3-Clause (`LICENSE:1` at f6c0043) | Turns off Claude Code's own tools |
| Claude Agent SDK, TypeScript | reject | Anthropic Commercial Terms (`LICENSE.md:1` at 040a7f8) | Not OSI-licensed |
| andyk/ht | reject | Apache-2.0 (`LICENSE:1-2` at ed569e9) | No waits; last push 2025-07 |
| tuiwright | reject | MIT (`LICENSE:1-3` at a875b87) | Its emulator (pyte) has no alternate screen |
| charmbracelet/vhs | reject | MIT (`LICENSE:1-3` at 24fa225) | A fixed tape can't branch on what the screen shows |
| libtmux, pexpect + pyte, node-pty + xterm headless | reject | MIT; ISC + LGPL-3.0; MIT | Building blocks; tui-test already does their job |

Matrix for the finalists:

| Criterion | Agent SDK (Python) | tui-test | agent-eval-harness |
|---|---|---|---|
| OSI license | native (`LICENSE:1-3`) | native (`LICENSE:1`) | native (`LICENSE:1`) |
| Drives real Claude Code with plugin, model, disallowed tools | native (`types.py:2431,2712`; `subprocess_cli.py:616-617,736,741`) | native: starts the real binary in a terminal (`README.md:204-317`) | native (`README.md:40`) |
| Multi-turn, one session | native: `ClaudeSDKClient` (docs) | native: types into the live session | unsupported: each step is a fresh `claude --print` conversation, passing only the earlier step's final message (`website/reference/config/execution.md:166-168`; `agent_eval/agent/claude_code.py:188,320`) |
| Scripted dialog answers: option, free text, dismiss | native: `updated_input` `answers` and `response` ([user input](https://code.claude.com/docs/en/agent-sdk/user-input)) | native: keys, Esc (`_native.pyi:46,72-74,89`) | partial: an answer per question text, then an LLM pick, then the first option; no dismissal, and an unexpected dialog gets the first option with only a warning (`skills/eval-run/scripts/tools.py:123-172`) |
| Notes on an option | native: `annotations` `notes` in the returned input reached the agent (trial run, below) | native: typed into the dialog | unsupported: the returned input holds only `questions` and `answers` (`skills/eval-run/scripts/tools.py:163-171`) |
| Previews present | native: options carried previews in a trial run, with and without `CLAUDE_CODE_QUESTION_PREVIEW_FORMAT` (below), though the Python SDK has no preview option (listing: `grep -rni previewFormat` over the repo at 144b7c9, 0 hits) | native: whatever the interface renders | unverified |
| Preview rendered whole | unsupported: no rendering | native: screen text and snapshots (`README.md:315-340`) | unsupported |
| Tool-call order and inputs | native: `PreToolUse` hook | partial: from the transcript only | native: hooks |
| Python | native | native (bindings) | native |

**Blends considered.** agent-eval-harness plus an SDK runner of this repo's own: its runner contract is one invocation per call (`agent_eval/agent/base.py:49-83`), so a multi-turn runner would carry the whole scripted conversation itself, which is most of the work, while the framework adds its judges, reporting and an agent-run orchestration skill. Agent SDK alone covers every check except cropping. tui-test alone could drive every check through the interface, but each dialog answer becomes keystrokes against a layout that can change between Claude Code versions. The blend keeps the structured route for the logic and uses the screen only where the screen is what's tested.

**Scenario walk.**
- *A new manual section* (for example, slice 4's memory moves): one more pytest test, scripted turns plus checks. Holds.
- *Claude Code changes the dialog's layout:* only the tui-test cropping check is exposed. Holds, with one check to update.
- *The preview variable is dropped or renamed:* the SDK route loses previews and falls back to plain text, which the skill handles. Only the dialog-route tests fail, which shows the change. Holds, and the previews check falls back to tui-test.
- *A reader on GitHub:* tests read as the `manual.md` steps they replace. Holds.

## Limitations checked in source

Verified:
- Python SDK license: the package's own code is MIT (`LICENSE:1-3` at 3be907e; the 0.2.177 wheel's `METADATA` says `License: MIT`). Its Linux wheel also bundles the Claude Code binary (`claude_agent_sdk/_bundled/claude`, 331 MB), which is under Anthropic's Commercial Terms like any Claude Code install; the `cli_path` option points the SDK at an installed `claude` instead. The TypeScript SDK's own code is under the Commercial Terms (`LICENSE.md:1` at 040a7f8).
- agent-eval-harness has no way to seed a case with conversation history. Listing: `grep -rn -iE 'history|--resume|resume_session|seed.*conversation|messages:|preload'` over its code and docs at 5d98820 found only `preloaded_files`, which tells a judge which files count as already read.
- agent-eval-harness, read at 5d98820: the Claude Code runner runs `claude --print` (`agent_eval/agent/claude_code.py:188,320`); steps start a fresh conversation (`website/reference/config/execution.md:166-168`); question answers come from a `PreToolUse` hook returning `questions` and `answers` only (`skills/eval-run/scripts/tools.py:123-172`).
- Python SDK: no preview option. Listing: `grep -rni "previewFormat|preview_format|askuserquestion"` over `claude-agent-sdk-python` at 144b7c9 found nothing.
- Python SDK: `env` is merged into the CLI subprocess's environment (`_internal/transport/subprocess_cli.py:819-823` at 144b7c9).
- Claude Code 2.1.318 reads `CLAUDE_CODE_QUESTION_PREVIEW_FORMAT`, `CLAUDE_CODE_QUESTION_EXTENDED` and `CLAUDE_CODE_QUESTION_OPTIONAL_DESCRIPTIONS` (strings in the installed binary).
- tui-test: idle waits use a fixed 250 ms quiet window (`crates/tui-test/src/engine.rs:3185-3199` at baa4bcc).
- inspect_swe, LangWatch Scenario, testdouble/skills-test-harness: no question-tool handling (listing: `grep -rci askuserquestion` over each repo).
- Licenses read from the files cited above.

- A trial run (2026-11-03, `claude-agent-sdk` 0.2.177, Claude Code 2.1.318, Sonnet 5.5), asked for a question with the file text in each option's preview. Both with `CLAUDE_CODE_QUESTION_PREVIEW_FORMAT=markdown` and without it, the `can_use_tool` callback received options carrying previews. A note returned under `annotations` reached the agent, which quoted it. The documented gate on previews didn't hold in this version, so a check that relies on previews should assert that they are present.

Could not verify:
- Whether tui-test's idle wait settles while Claude Code shows its spinner.
- How a dismissed dialog is best returned through the Python SDK (the docs give `response`; the TypeScript changelog adds `annotations.unanswered`).
- A Python SDK issue (#767) reporting that a hook's `updatedInput` has no effect on the question tool. Its repro uses the wrong key, so it's unclear. The harness uses `can_use_tool`, which the docs describe.
- aitoolnet.com: unavailable (Cloudflare 403 on fetch and curl, after a retry).
- `sjnims/cc-plugin-eval`: unavailable (404). Only mirrors were seen.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | `claude plugin eval` docs (one prompt per case; `context.history_file` resumes a `.jsonl` transcript with the case's prompt as the next user turn, so a case can start from a mock conversation, but there are no scripted follow-up turns or dialog answers, and the run is non-interactive); `claude` CLI reference, headless and env-var docs (`--input-format stream-json`, `--resume`, `--permission-prompt-tool`; no documented preview flag) |
| Earlier notes and decisions | searched | `docs/prior-art/` and `docs/decisions/` for multi-turn, Agent SDK, promptfoo, Inspect: none on this topic |
| GitHub repository search | searched | "claude code eval"; "skill eval agent"; "agent multi-turn eval"; "user simulator agent"; "coding agent eval harness"; "claude code tmux test"; "drive claude code tmux"; "tui testing"; "terminal e2e testing". Three later queries hit the rate limit |
| GitHub topics | searched | `agent-evaluation`; `llm-evaluation` multi-turn; `claude-code` eval; `claude-skills` eval; `user-simulation`; `agent-testing` |
| GitHub code search | searched | `"AskUserQuestion" "can_use_tool" eval simulated`; `marketplace.json` "skill eval"; `"capture-pane AskUserQuestion"` |
| GitLab and Codeberg | searched | "agent eval"; "llm evaluation"; "claude code": nothing relevant |
| npm | searched | "claude agent sdk eval"; "claude code eval"; "multi-turn agent eval"; "user simulator llm" |
| PyPI | searched | `claude-agent-sdk`, `inspect-swe`, `inspect-ai`, `agent-belt`, `coder-eval`, `understudy`, `tuiwright`, `pexpect`, `pyte`, `libtmux`, `tui-test`; site search "claude code eval multi-turn simulated user" |
| crates.io | searched | "agent eval"; "llm eval multi-turn"; "claude" |
| Cross-language equivalents | searched | Python and TypeScript Agent SDKs; tui-test's Python, Node and Go bindings |
| Awesome lists | searched | "awesome claude code skills testing evaluation"; `benchflow-ai/awesome-evals`. Terminal-testing awesome lists weren't reached (time) |
| alternativeto.net | searched | promptfoo's page; "alternatives to promptfoo"; the Inspect AI page returned 404 |
| aitoolnet.com | unavailable | Cloudflare 403 on fetch and curl, after one retry |
| General web search | searched | "Claude Agent SDK canUseTool AskUserQuestion multi-turn plugins"; "multi-turn evaluation Claude Code skills harness"; "promptfoo claude agent sdk multi-turn simulated user"; "inspect_swe claude_code multi-turn"; "test Claude Code skill multi-turn simulated user AskUserQuestion"; "terminal TUI end-to-end testing framework screen assertions" |
| Skill directories | searched | skills.sh "eval", "skill test", "multi-turn": skills that write evals, not harnesses |
| Claude Code plugin marketplaces | searched | code search on `.claude-plugin/marketplace.json` for eval: coder_eval and agent-eval-harness ship as plugins |
| Hosted services | excluded | The need is a local, OSI-licensed harness |
| MCP Registry | excluded | No MCP server is part of the need. tmux MCP servers were seen through web search |

## Snowball rounds

1. From the Agent SDK: promptfoo, Inspect AI with `inspect_swe`, LangWatch Scenario.
2. From the question-tool code search and the plugin marketplaces: fullsend-ai/agent-eval-harness, smykla-skalski/sai, adobe/skills. From "Playwright for terminals": tui-test, tuiwright, ht, getpipher/term.
3. From the agent-CLI repos: Gemini CLI's and Qwen Code's own interface test rigs, which are ideas only, and UiPath/coder_eval, jfrog/agent-belt, mgechev/skillgrade.

Round 3 added no candidate that passes the hard criteria and handles the question tool, so the search stopped there.

## Refresh trigger

When `claude plugin eval` gains multi-turn cases or question-tool answers, or the Python Agent SDK gains a documented preview option.
