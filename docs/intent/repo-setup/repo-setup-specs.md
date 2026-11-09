# This repo's own setup specs

Design: [repo-setup-design.md](repo-setup-design.md). "This repo" is agentic_development. "An own skill" is a directory in this repo's `skills/` that contains a `SKILL.md`, and `<name>` is its directory name. "LID's lock entry" is the entry in this repo's `apm.lock.yaml` whose `repo_url` is `jszmajda/lid` and whose `virtual_path` is `plugins/linked-intent-dev`. "LID's skills" are the names `<name>` for which LID's lock entry lists `.claude/skills/<name>` in its `deployed_files`. "A task" is a task defined in this repo's `mise.toml`, and "a pinned tool" is an entry in its `[tools]` table. "The layout tests" and "the LID version test" are the pytest tests that verify the specs in their sections. "The hook" is `.claude/hooks/session-start.sh`, and "the project directory" is the directory in `CLAUDE_PROJECT_DIR`. "The eval script" is `scripts/run_evals.py`; in the Evals specs, "this repo's root" is the git top-level directory of the directory the eval script is started in, which is this repo's root when the `eval` task runs it. "The eval copy" is the directory `agentic-development/eval-plugin` under `$XDG_CACHE_HOME`, or under `~/.cache` when that variable is unset, empty or not an absolute path. "The plugin's files" are the paths that `git ls-files --cached --others --exclude-standard` prints in this repo's root. "The runner" is the `claude plugin eval .` process that the eval script starts. "A cloud session" is a run where the environment variable `CLAUDE_CODE_REMOTE` is `true`. "A mise-action step" is a step in a workflow in `.github/workflows/` that uses `jdx/mise-action`. The hook's steps, in order, are: installing mise (SETUP-HOOK-003), entering the project directory (an unset `CLAUDE_PROJECT_DIR`, or one that isn't a directory, fails this step), `mise trust`, `mise install apm`, `mise run skills`, `mise install` (SETUP-HOOK-005), and writing `PATH` (SETUP-HOOK-006 and SETUP-HOOK-007). "A hook failure" is one of those steps failing: a command it runs exiting non-zero, or a condition SETUP-HOOK-004 or SETUP-HOOK-007 names. A check the hook makes to decide whether a step is needed is not a step.

## Layout

- [x] **SETUP-LAYOUT-001**: This repo's `.claude/skills` shall be a real directory, not a link.
- [x] **SETUP-LAYOUT-002**: This repo's `.agents/skills` shall be a real directory, not a link.
- [x] **SETUP-LAYOUT-003**: For each own skill, this repo shall have a `.claude/skills/<name>` link whose target is the relative path `../../skills/<name>`.
- [x] **SETUP-LAYOUT-004**: For each own skill, this repo shall have a `.agents/skills/<name>` link whose target is the relative path `../../skills/<name>`.
- [x] **SETUP-LAYOUT-005**: For each of LID's skills, this repo shall have an `.agents/skills/<name>` link whose target is the relative path `../../.claude/skills/<name>`.
- [x] **SETUP-LAYOUT-006**: This repo's `.claude/skills/` shall contain nothing other than the links SETUP-LAYOUT-003 requires and, for any of LID's skills, a real directory (not a link) named after it.
- [x] **SETUP-LAYOUT-007**: This repo's `.agents/skills/` shall contain only the links SETUP-LAYOUT-004 and SETUP-LAYOUT-005 require.
- [x] **SETUP-LAYOUT-008**: If a link in `.claude/skills/` or `.agents/skills/` doesn't resolve to a directory, then the layout tests shall fail with a message that names the link and says to run `mise run skills`.
- [x] **SETUP-LAYOUT-009**: If a link SETUP-LAYOUT-003, SETUP-LAYOUT-004 or SETUP-LAYOUT-005 requires is missing or has another target, or an entry SETUP-LAYOUT-006 or SETUP-LAYOUT-007 doesn't allow is present, then the layout tests shall fail with a message naming each such entry.
- [x] **SETUP-LAYOUT-010**: No name shall be both an own skill's and one of LID's skills, and if one is, the layout tests shall fail with a message naming it.

## Ignore rule

SETUP-IGNORE-001 to SETUP-IGNORE-003 are verified with `git check-ignore` on the paths, not by reading `.gitignore`'s text.

- [x] **SETUP-IGNORE-001**: This repo's `.gitignore` shall ignore `apm_modules/`.
- [x] **SETUP-IGNORE-002**: This repo's `.gitignore` shall ignore every directory of LID's skills in `.claude/skills/`.
- [x] **SETUP-IGNORE-003**: This repo's `.gitignore` shall not ignore any link SETUP-LAYOUT-003 requires.
- [x] **SETUP-IGNORE-004**: Every line of this repo's `.gitignore` that starts with `!/.claude/skills/` shall be exactly `!/.claude/skills/<name>` for an own skill, with no trailing slash.

## APM pin

- [x] **SETUP-APM-001**: This repo's `apm.yml` shall have a `targets` list whose only item is `claude`.
- [x] **SETUP-APM-002**: This repo's `apm.yml` shall have no dependency other than one string item in its `dependencies.apm` list, `jszmajda/lid/plugins/linked-intent-dev#vX.Y.Z`, where `X`, `Y` and `Z` are numbers.
- [x] **SETUP-APM-003**: This repo's `mise.toml` shall pin the `apm` tool to a version of the form `X.Y.Z`, where `X`, `Y` and `Z` are numbers.

## Tasks

- [x] **SETUP-TASK-001**: The `skills` task shall run `apm install --frozen` in this repo's root.
- [x] **SETUP-TASK-002**: The `run` list of the `setup` task shall be, in order, `mise install`, `mise run skills` and `prek install -c .config/prek.toml`.
- [x] **SETUP-TASK-003**: The `depends` list of the `test` task shall include `skills`.

## LID version gate

"The `## LID` block" runs from a line that is exactly `## LID` to the next line starting with `#`. Versions are compared as strings, exactly as written.

- [x] **SETUP-GATE-001**: While the `- Version:` bullet in the `## LID` block of this repo's `AGENTS.md` differs from the `version` of LID's lock entry, the LID version test shall fail with a message naming both versions and `/update-lid`.
- [x] **SETUP-GATE-002**: If this repo's `apm.lock.yaml` has no LID's lock entry, or more than one, then the LID version test shall fail.
- [x] **SETUP-GATE-003**: If this repo's `AGENTS.md` has no `## LID` block, or that block has no `- Version:` bullet, then the LID version test shall fail.
- [x] **SETUP-GATE-004**: If this repo's `AGENTS.md` has more than one `## LID` block, or more than one `- Version:` bullet in that block, then the LID version test shall fail.

## Cloud-session hook

- [x] **SETUP-HOOK-001**: This repo's `.claude/settings.json` shall have exactly one SessionStart entry, with no `matcher` key, holding exactly one hook of type `command` whose command is `$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh`.
- [x] **SETUP-HOOK-002**: When the hook runs outside a cloud session, it shall exit 0 without printing to stdout, installing anything or writing any file.
- [x] **SETUP-HOOK-003**: When the hook runs in a cloud session and the first word `~/.local/bin/mise --version` prints is anything other than the hook's `MISE_VERSION` (or that command fails), the hook shall download `mise-v<MISE_VERSION>-linux-x64.tar.gz` and `SHASUMS256.txt` from the GitHub release `v<MISE_VERSION>` of `jdx/mise`, verify the archive against the checksum file, and install the archive's `mise/bin/mise` to `~/.local/bin/mise`.
- [x] **SETUP-HOOK-004**: If the checksum file has no line for the archive, or the archive doesn't match it, then the hook shall treat it as a hook failure and leave `~/.local/bin/mise` as it was.
- [x] **SETUP-HOOK-005**: When the hook runs in a cloud session and has mise at `MISE_VERSION`, it shall run, in the project directory and in this order, `mise trust`, `mise install apm`, `mise run skills` with the environment variable `MISE_TASK_RUN_AUTO_INSTALL` set to `false`, and `mise install`.
- [x] **SETUP-HOOK-006**: When the hook runs in a cloud session and SETUP-HOOK-005's commands have succeeded, and `CLAUDE_ENV_FILE` is set, the hook shall append to that file the line `export PATH="<bin>:<paths>:$PATH"`, where `<bin>` is the absolute path of `~/.local/bin` and `<paths>` is the output of `mise bin-paths` joined with `:`, unless a whole line of the file already equals it.
- [x] **SETUP-HOOK-007**: If `CLAUDE_ENV_FILE` is unset when the hook reaches its `PATH` step in a cloud session, then the hook shall treat it as a hook failure.
- [x] **SETUP-HOOK-008**: If a hook failure occurs in a cloud session, then the hook shall run no later step, add to the JSON object SETUP-HOOK-011 requires a `hookSpecificOutput.additionalContext` string naming the step and what it leaves missing, and exit 0.
- [x] **SETUP-HOOK-009**: Every mise-action step shall have a `version:` input, equal to the hook's `MISE_VERSION`.
- [x] **SETUP-HOOK-010**: The pinned Renovate CLI's extraction, run with this repo's `.github/renovate.json`, shall report the hook's `MISE_VERSION` with the same `depName`, datasource and current version as it reports for the `version:` input of each mise-action step.
- [x] **SETUP-HOOK-011**: When the hook runs in a cloud session, its stdout shall be exactly one JSON object followed by a newline, whose `hookSpecificOutput` has `hookEventName` `SessionStart` and `reloadSkills` `true`, whether or not a hook failure occurred.

## Evals

- [x] **SETUP-EVAL-001**: The `eval` task shall run the eval script with `uv run --locked`, with no other task as a dependency, passing it every argument mise passes to the task, in order, and not mise's own `--` separator.
- [x] **SETUP-EVAL-002**: The eval script shall take the eval copy's lock, the file `eval-plugin.lock` beside the eval copy, before it lists the plugin's files, and shall hold it until it exits.
- [x] **SETUP-EVAL-003**: After listing the plugin's files, the eval script shall delete the eval copy if it exists, create it empty, and copy into it each of the plugin's files that exists in the working tree (a symbolic link counts as existing even when its target doesn't), at the same path relative to this repo's root and with the same permission bits.
- [x] **SETUP-EVAL-004**: The eval script shall copy each of the plugin's files that is a symbolic link as a symbolic link whose target is the same string, not as the file it points to.
- [x] **SETUP-EVAL-005**: After copying, the eval script shall start the runner with the eval copy as its working directory and the eval script's own arguments after `.`, in order.
- [x] **SETUP-EVAL-006**: When the runner has exited, by any means, the eval script shall copy to this repo each entry of a directory named `results` anywhere below the eval copy's `evals/` (such as `evals/results/<run>` or `evals/<skill>/results/<run>`) that wasn't in the eval copy when the runner started and doesn't exist at the same path in this repo.
- [x] **SETUP-EVAL-007**: The eval script shall try every copy SETUP-EVAL-006 requires even after one fails, and shall report each failed copy on stderr.
- [x] **SETUP-EVAL-008**: The eval script shall exit with the runner's exit status, whether or not copying results back failed, or with 128 plus the signal number when a signal ended the runner.
- [x] **SETUP-EVAL-009**: If another run of the eval script holds the eval copy's lock, then the eval script shall exit with a non-zero status and a message on stderr, without listing the plugin's files, changing the eval copy or starting the runner.
- [x] **SETUP-EVAL-010**: If listing the plugin's files fails, then the eval script shall exit with a non-zero status and git's error on stderr, without changing the eval copy or starting the runner.
- [x] **SETUP-EVAL-011**: If copying one of the plugin's files into the eval copy fails, then the eval script shall exit with a non-zero status, naming the file on stderr, without starting the runner.
- [x] **SETUP-EVAL-012**: If the runner can't be started, then the eval script shall exit with status 127 and the reason on stderr.
- [x] **SETUP-EVAL-013**: From starting the runner until SETUP-EVAL-006's copy-back has finished, the eval script shall not end on SIGINT, so that an interrupt meant for the run still leads to SETUP-EVAL-006's copy-back and SETUP-EVAL-008's exit status.
- [x] **SETUP-EVAL-014**: The eval script shall clear a previous eval copy even when it holds files or directories without write permission, and if clearing or creating the eval copy fails, it shall exit with a non-zero status and the cause on stderr, without starting the runner.
