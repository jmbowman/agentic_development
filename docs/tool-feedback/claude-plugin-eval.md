# claude plugin eval

Claude Code's plugin eval runner (`claude plugin eval`), which this repo uses for its skills' behavior evals ([evals/README.md](../../evals/README.md)). Items are from Claude Code 2.1.319.

## Gitignored files count toward the plugin's entry cap

- **Where:** the runner's check of the plugin directory before a case runs.
- **What:** a case fails before any model call with `a plugin directory holds more than 20000 entries to check for eval directories — point the case at a smaller plugin directory`. Two things combine to cause it:
  - The runner counts every entry under the plugin directory, gitignored ones included.
  - It runs the check even when `--eval-dir` already names the directory that holds the cases.

  This repo's root is its plugin, as [the HLD](../high-level-design.md) decides, and gitignored working files live there too: `tmp/` scratch, shallow clones read during prior-art searches, `.venv/`, and later reference clones. So the repo's own scratch can block its evals, though the runner would never load any of those files.
- **Evidence:** on 2026-11-08, `settings-canary` failed this way with about 232,000 entries outside `.git`, almost all of them under the gitignored `tmp/`. Running from a copy that holds only `git ls-files --cached --others --exclude-standard` avoids it.
- **Suggested fix**, any one of these:
  - skip the walk when `--eval-dir` names the eval directory;
  - leave out what `.gitignore` excludes when walking or counting;
  - add an `--exclude <glob>` option.

  The error could also name the largest directories it found, so the cause is obvious.
- **Raised upstream:** no. Claude Code's `/feedback` command is the channel.

## A judge sees only the first 100,000 characters of a trace

- **Where:** `llm` graders with `focus: trace`.
- **What:** each grader's evidence, the trace the judges read, is cut at 100,024 characters. A full-method prior-art search with subagents writes megabytes of trace, so the judges see the main agent's first steps and none of the subagents' work. They then vote on conditions they can't see. In one run the split votes (FAIL PASS FAIL) on a condition the full trace showed was met are the sign.
- **Evidence:** on 2026-11-08, settings-canary's trace was 2,041,150 bytes, and every `llm` grader's `evidence` in `aggregate-result.json` was 100,024 characters.
- **Suggested fix:** let a grader ask for the tool calls and results without the system and message noise, or summarize the trace for the judge; or at least warn in the report when evidence was cut.
- **Raised upstream:** no.

## Results go inside the plugin directory

- **Where:** `--eval-dir <dir>`, whose help says results go to `<plugin>/<dir>/results/`.
- **What:** when the plugin directory is a temporary copy (the workaround above), results land in the copy and have to be copied back.
- **Evidence:** `claude plugin eval --help`, Claude Code 2.1.319.
- **Suggested fix:** a `--results-dir <path>` option.
- **Raised upstream:** no.
