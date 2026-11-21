# Behavior evals for this repo's skills

Cases for `claude plugin eval`, run by hand from the repo root with `mise run eval -- <runner arguments>`. The repo root is the plugin, and the runner refuses a plugin directory with more than 20,000 entries, gitignored scratch and clones included, so the task runs `claude plugin eval .` in a copy of only the plugin's files (tracked, plus untracked and not ignored, uncommitted edits included) under `~/.cache/agentic-development/eval-plugin` (or `$XDG_CACHE_HOME/agentic-development/eval-plugin`), then copies the run's results back. Only one run at a time: a second one started meanwhile exits with an error. Each skill's cases live in `evals/<skill>/`, one directory per case, and carry the skill's name as a tag; `--eval-dir evals/<skill>` runs one skill's suite. `prior-art-search`, `session-wrap-up` and `task-tracker` have cases. Each run is a real model call, and the online cases search the web and clone repositories, so a full suite takes a while and costs real usage. Runs are isolated: no user or project instructions load, so a pass shows what the skill itself contributes, and every case also runs without the plugin for comparison.

Cases are also tagged `online` (they need web search and network access) or `offline` (everything they need is in the case's scaffold). `--tag` matches any of the tags given, so combine a skill and a network tag with `--eval-dir` plus `--tag`, not two tags. Every case that seeds a workspace needs `--scaffold`.

```bash
# Offline cases: no network grants.
mise run eval -- --eval-dir evals/prior-art-search --tag offline --scaffold --model claude-sonnet-5-5 \
  --allow-tools Bash Write Edit

# Online cases: web tools, plus network for the shell's git and API calls.
mise run eval -- --eval-dir evals/prior-art-search --tag online --scaffold --model claude-sonnet-5-5 \
  --allow-tools WebSearch WebFetch Bash Write Edit \
  "WebFetch(domain:github.com)" "WebFetch(domain:api.github.com)" \
  "WebFetch(domain:codeload.github.com)" "WebFetch(domain:raw.githubusercontent.com)" "WebFetch(domain:pypi.org)" \
  "WebFetch(domain:files.pythonhosted.org)" "WebFetch(domain:registry.npmjs.org)" \
  "WebFetch(domain:crates.io)" "WebFetch(domain:static.crates.io)" "WebFetch(domain:index.crates.io)" \
  "WebFetch(domain:gitlab.com)" "WebFetch(domain:codeberg.org)" \
  "WebFetch(domain:api.openalex.org)" "WebFetch(domain:api.semanticscholar.org)" \
  "WebFetch(domain:api.crossref.org)" "WebFetch(domain:libraries.io)" \
  "WebFetch(domain:export.arxiv.org)" "WebFetch(domain:arxiv.org)" "WebFetch(domain:api.openaire.eu)" \
  "WebFetch(domain:zenodo.org)" "WebFetch(domain:huggingface.co)" "WebFetch(domain:www.ebi.ac.uk)" \
  "WebFetch(domain:papers.cool)" "WebFetch(domain:packages.ecosyste.ms)" \
  "WebFetch(domain:formulae.brew.sh)" "WebFetch(domain:registry.modelcontextprotocol.io)" \
  "WebFetch(domain:skills.sh)"
```

The model under test is pinned with `--model claude-sonnet-5-5`; the judge stays the runner's default (Haiku) unless `--judge-model` says otherwise. The `WebFetch(domain:…)` grants also set the sandbox's network allowlist for the shell, so a route whose host isn't listed fails with a `deny network-outbound` sandbox violation; add a host here when `references/sources.md` gains a route that the agent calls with `curl`.

The runner also refuses a plugin that contains hard-linked files. The copy is made of fresh files, so this can't happen through `mise run eval`; running `claude plugin eval .` directly in the repo still could. If a run fails with "a file in the plugin has more than one name", find the culprit with `find . -path ./.git -prune -o -type f -links +1 -print`.

Cases that grant Bash need Claude Code's sandbox (bubblewrap and socat on Linux). On Ubuntu 24.04 and later, AppArmor restricts unprivileged user namespaces (`sysctl kernel.apparmor_restrict_unprivileged_userns` returns `1`). Claude Code's [sandbox docs](https://code.claude.com/docs/en/sandboxing) give an AppArmor profile for `bwrap`, but Ubuntu 26.04 already ships `/etc/apparmor.d/bwrap-userns-restrict`, which defines a profile with the same name and moves bwrap's children into a confined `unpriv_bwrap` profile; every sandboxed command then fails with `apply-seccomp ... setgroups: Permission denied`, and graders that assert a command was never run pass vacuously (a report that says it couldn't run `git status` is the sign). Disabling that profile before adding the documented one (a host-wide security trade-off, confirmed working on Ubuntu 26.04.1), or running the evals in a VM without the restriction, are the options. `bwrap --ro-bind / / --unshare-user --unshare-pid true` is a quick first check. Then check that Bash works with one cheap run: `mise run eval -- --eval-dir evals/prior-art-search --case no-trigger-bug-fix --runs 1 --ablation none --scaffold --model claude-sonnet-5-5 --allow-tools Bash Write Edit`; a working run tests its fix instead of reporting a sandbox error.

The runner puts each run's directory under `$TMPDIR` (`/tmp` by default), and its sandbox settings deny writes to `//tmp`, which overrides the run's own allow: with the default, the shell can write nowhere, not even in the case's workspace. Until `mise run eval` sets it, prefix the commands with `TMPDIR=~/.cache/agentic-development/eval-tmp` (create the directory first); the shell can then write in the run's home and workspace, though not in `~/.cache`. To diagnose a write failure, read `sandbox.filesystem` in the kept run's `config/settings.json`. The prior-art search harvester needs a writable uv cache, so the online literature cases' scaffolds (`harvester-literature`, `approach-need-literature`, `settings-canary`) give the workspace a git-ignored `tmp/` and warm uv's cache in `tmp/prior-art-search/uv-cache` (about 170 MB, downloaded while the scaffold runs outside the sandbox). The agent still has to point `UV_CACHE_DIR` there itself, as the skill says to in a sandboxed shell, so the cases test that rule.

Add `--case <name> --runs 1 --ablation none` to iterate on one case. Results go to `results/` inside the eval directory, which is gitignored; the task copies each new run's directory there from the copy. A relative path given to `--json` resolves inside the copy and isn't copied back, so give it an absolute path.

Runner details worth knowing:
- `--case` takes one name; given more than once, only the last applies. Loop over names to run several.
- Each run gets its own sandboxed home and config directories, and its system prompt states a memory directory inside that sandbox. A case can't make a run with no memory location. The sandbox home is itself a git repo, so a case can't run outside git either.
- `--keep-temp` keeps each run's directory; its `out/trace.jsonl` lists every tool call. The rest is sealed (mode 000); don't run git inside it.
- `results/` folders are named by UTC time, so sort them by name, not by a date prefix; `docs/review-log.md` dates are local. Each runner invocation writes its own folder, and one folder can hold several runs (`.cases[].arms.with[]`), so total a wave by adding up its folders for each case, matched to the wave by run-time gaps and the row's text, not by date.
- Without `--no-publish`, the report is published to claude.ai (private to you).
- The default judge is Haiku; `--judge-model` changes it. `--model` sets the model under test.
- A `tool_used` grader's "called Nx" counts only calls that match its `input_match`, so 0x doesn't show that the tool went unused or that the sandbox failed.
- `results/<run>/aggregate-result.json` holds each `llm` grader's evidence but not the judges' reasons. The evidence is cut at about 100,000 characters, so on a long run (an online full-method search with subagents) the judges see only the main agent's first steps: keep the run's temp directory and check the conditions in `out/trace.jsonl` before trusting a PASS or a FAIL. Diagnose a flaky grader by comparing a passing and a failing run.

Each case's `case.yaml` lists the specs it exercises in `@spec` comments. Each skill's structure tests (`tests/test_prior_art_skill.py`, `tests/test_session_wrap_up_skill.py`) check that every spec its specs file marks *(eval)* has a case in its own suite. `tests/test_evals.py` checks that every case loads in the runner and sits under its skill's directory with its tag.

The session-wrap-up cases are offline, and each gives the skill a record of a session to wrap up inside its prompt, since an eval is a single prompt. A record can hold an earlier report or a simulated compaction summary, and the scaffold seeds any transcript the case needs. Run them with:

```bash
mise run eval -- --eval-dir evals/session-wrap-up --tag offline --scaffold --model claude-sonnet-5-5 \
  --allow-tools Bash Write Edit
```

The task-tracker cases are offline too. Each scaffold builds a small repo with a backlog of four tasks, and the prompt asks for one change to it. `create-with-custom-keys` needs Backlog.md's `backlog` CLI on the agent's `PATH`, which `mise run eval` provides from this repo's pin. The runner's sandbox lets a command read only the folders on `PATH`, so the pin is Backlog.md's release binary: the npm package's bin folder holds only a launcher for code in a sibling folder, and fails there with `MODULE_NOT_FOUND`. Without a working CLI, the skill tells the agent to create nothing, and the case fails. The task tool runs with `uv run --script`, which needs PyYAML in uv's cache or the network, so a `check` run that fails inside the sandbox still counts as running it. Set `TMPDIR` as above:

```bash
mise run eval -- --eval-dir evals/task-tracker --tag offline --scaffold --model claude-sonnet-5-5 \
  --allow-tools Bash Write Edit
```

Behavior an eval can't reach (an interactive run, another live session, a real compaction, or the order of tool calls) is checked by hand from the scripts in `evals/session-wrap-up/manual.md`, which also hold the dated results. Its specs are marked *(manual)*. These scripts are to become interactive scenarios, pytest tests in `evals/<skill>/interactive/` that drive a real Claude Code session through the pytest-claude-code-evals plugin ([design](../docs/intent/interactive-evals/interactive-evals-design.md)). A scenario names the script it replaces with a `replaces` marker, the script then leaves `manual.md`, and the specs it checked become *(interactive)*, or *(eval, interactive)* when an eval case also checks them. `mise run check` imports every scenario without running one; `tests/test_interactive_scenarios.py` holds these rules.

## Latest results

Each skill's `latest-results.md` has one row per eval case (and per interactive scenario), giving its most recent triaged run: the date, Claude Code version, model, runs and failures, and the `docs/review-log.md` row that reported it (its Date, Component, Phase and Wave), or `never run`. Runs whose failure triage traced to the grader or the case, not the skill, are left out of both counts. After triaging a run, update the rows it covered in the same change as its review-log row. `tests/test_interactive_scenarios.py` fails when a case or scenario has no row, a row names something that doesn't exist, or a row is malformed.

## Writing graders

- A `tool_used` grader's `input_match` runs against the tool input as JSON, so a command's quotes are escaped (`\"`). Match command text with `(?:[^"\\]|\\.)*`, not `[^"]*`. In a grader that bans reading a path, end the stretch between the reader command and the path at command separators (`(?:[^"\\;&|]|\\.)*`), and anchor on the path's parent directory, so neither `cat a; ls dir` nor a `grep` for the directory's name matches.
- The runner compiles a `regex` grader's `pattern` as a JavaScript regular expression, which rejects inline flags such as `(?i)` (the grader throws and fails). Set `flags: i` in the front matter instead; `tests/test_evals.py` checks this.
- Anchor a home-directory check on paths that start at a home (`~/.claude`, `/home/<user>/.claude`), or a project's own `.claude/` will match too.
- Before trusting a regex, test it against tool inputs from a real trace (`--keep-temp`), both a call it should catch and one it shouldn't.
- An `llm` grader's judge sees only the final reply unless the grader sets `focus: trace`, which shows it the run's first 12 and last 12 messages, tool calls included. Use `focus: trace` when the verdict rests on what the agent did (a file it changed, a key it added) rather than what it said, and keep such a case short enough for that window. A `regex` grader can read one workspace file after the run with `target: { source: file, path: <path> }`.
- Keep each `llm` grader to one or two checks. A long multi-clause grader gets noisy verdicts, especially under the Haiku judge; split it, or judge with `--judge-model claude-sonnet-5-5`.
- Write the grader to accept every reading the spec allows, not just the one you expected.
- Before calling a failing grader wrong, read the case's scaffold and any transcript or notes file it seeds, not only `prompt.md`: the session record can continue there (in `notes-compacted-transcript`, the developer's decline is a line in the scaffold's JSONL).
- A scaffold must hold what its session record says was done, and what any notes file or transcript it seeds claims. The agent checks the repo, so a change the record claims and the scaffold lacks becomes a loose end, and it changes the report.
- A prompt can't name an absolute path: the runner substitutes nothing in it, and a scaffold can't edit it. A case that needs a directory outside the repo seeds it in a gitignored folder of the workspace and names it relative to the workspace.
