# Check workflow specs

Design: [check-workflow-design.md](check-workflow-design.md). "The caller repo" is the repo whose CI stub calls the workflow. "The working directory" is the workflow's `working-directory` input, relative to the caller repo's root.

## Workflow definition

- [x] **CHECK-001**: The check workflow (`.github/workflows/check.yml`) shall be triggered only by `workflow_call`.
- [x] **CHECK-002**: The check workflow shall accept exactly one input, the optional string `working-directory`, defaulting to `.`.
- [x] **CHECK-003**: The check workflow shall pass its `working-directory` input both to `jdx/mise-action`'s `working_directory` input and as the working directory of every `run` step.
- [x] **CHECK-004**: The check workflow shall request only the `contents: read` permission.
- [x] **CHECK-005**: The check workflow shall set `MISE_TRUSTED_CONFIG_PATHS` to `${{ github.workspace }}` at job level.
- [x] **CHECK-006**: The check workflow's `runs-on` shall match `^ubuntu-\d{2}\.\d{2}$` (an x86_64 Ubuntu image with an explicit version).
- [x] **CHECK-007**: The check workflow shall install the caller repo's pinned tools with `jdx/mise-action`, passing an exact mise version (matching `^\d{4}\.\d+\.\d+$`) in the action's `version` input.
- [x] **CHECK-008**: The check workflow shall reference every action by a 40-character commit SHA followed by a comment of the form `# v<version>`.
- [x] **CHECK-009**: The check workflow's first step shall check out the commit that triggered the caller repo's run.
- [x] **CHECK-010**: Before any mise step, the check workflow shall export `MISE_CEILING_PATHS` as the normalized absolute path of the working directory's parent, so that mise loads no config from above the working directory.
- [x] **CHECK-011**: After the step that installs tools with `jdx/mise-action` and immediately before the task-location verification step, the check workflow shall run `actions/checkout` with `repository: ${{ job.workflow_repository }}`, `ref: ${{ job.workflow_sha }}`, `path: .check-workflow`, `persist-credentials: false`, `sparse-checkout-cone-mode: false` and `sparse-checkout` set to the single pattern `scripts/verify_check.py`, so that only the verification script from the workflow's own repo and commit is fetched.
- [x] **CHECK-012**: The check workflow's task-location verification step shall move `$GITHUB_WORKSPACE/.check-workflow` to `$RUNNER_TEMP/check-workflow` with `mv -T`, and then run `$RUNNER_TEMP/check-workflow/scripts/verify_check.py` with `/usr/bin/python3 -I`.
- [x] **CHECK-013**: The verification script (`scripts/verify_check.py`) shall import only Python standard-library modules.

## Running the checks

- [x] **CHECK-RUN-001**: The check workflow shall verify where the caller repo's `check` task is defined, in a step that runs before the step that runs the checks.
- [x] **CHECK-RUN-002**: If the absolute source path that `mise tasks info check --json` reports for the caller repo's `check` task starts with neither the logical nor the physical (symlink-resolved) absolute path of `<working directory>/.config/mise/conf.d/`, then the check workflow shall fail with a message containing that source path, without running any check.
- [x] **CHECK-RUN-003**: When the caller repo's `check` task comes from a `.config/mise/conf.d/` entry that is a symlink into another directory, the check workflow shall accept it as defined in `.config/mise/conf.d/`.
- [x] **CHECK-RUN-004**: If the caller repo has no `check` task, then the check workflow shall fail with a message containing `no "check" task`.
- [x] **CHECK-RUN-005**: The check workflow shall run the caller repo's checks with `mise run --continue-on-error check`, so that every dependency of `check` runs even after one fails.
- [x] **CHECK-RUN-007**: If any task in the closure of the caller repo's `check` task (the tasks reached through `depends`, `depends_post`, and the `task` and `tasks` entries of `run`), other than tasks whose names end in `-extra` and tasks reachable only through them (verification doesn't descend into a `-extra` task's dependencies), has a source outside `<working directory>/.config/mise/conf.d/` (a source path with a `..` component counts as outside), then the check workflow shall fail with a message naming that task and its source path, without running any check.
- [x] **CHECK-RUN-008**: If any dependency in the closure checked by CHECK-RUN-007 contains a pattern character (`*`, `?`, `[` or `{`), or mise reports it under a name that, once a leading `//:` or `:` (mise's monorepo root prefix) is removed from both names, is neither the requested name nor one of its aliases, then the check workflow shall fail with a message naming that dependency, because mise reports only the first task a pattern matches.
- [x] **CHECK-RUN-009**: If any task in the closure checked by CHECK-RUN-007 has a `depends`, `depends_post` or `run` value that isn't a list, a `depends` or `depends_post` entry other than a non-empty string, an array whose first element is a non-empty string, or an object whose `task` is a non-empty string, or a `run` entry other than a string or an object whose `task` is a non-empty string or whose `tasks` is a list of non-empty strings (the first word of each naming the task), then the check workflow shall fail with a message reporting the unrecognized form.
- [x] **CHECK-RUN-010**: If `mise tasks info` exits non-zero for a dependency in the closure checked by CHECK-RUN-007, then the check workflow shall fail with a message naming that dependency as not found and including mise's error output.
- [x] **CHECK-RUN-011**: When the task-location verification finds a violation, the check workflow shall continue the walk and report every violation in the closure checked by CHECK-RUN-007 before failing.
- [x] **CHECK-RUN-012**: If `mise tasks info` reports a task in the closure checked by CHECK-RUN-007 with output that isn't a JSON object or has no string `source`, then the check workflow shall fail with a message naming that task as unreadable.
- [x] **CHECK-RUN-006**: The check workflow's job shall fail if the script checkout step, the task-location verification step or the checks step fails, and none of those steps shall set `continue-on-error`.

## Release testing (this repo's CI)

- [x] **CHECK-TEST-001**: On every push, this repo's CI shall call `./.github/workflows/check.yml` with `working-directory` set to a fixture under `tests/fixtures/` whose `check` task succeeds, and shall fail if that call fails.
- [x] **CHECK-TEST-002**: On every push, this repo's CI shall call `./.github/workflows/check.yml` with `working-directory` set to a fixture whose `check` task is defined in a `.config/mise/conf.d/` fragment and runs a tool pinned only in that fragment and absent from the runner image, and shall fail if that call fails.
- [x] **CHECK-TEST-003**: On every push, this repo's CI shall call `./.github/workflows/check.yml` with `working-directory` set to a fixture whose `.config/mise/conf.d/` entry is a symlink into `.config/<template>/`, and shall fail if that call fails.
- [x] **CHECK-TEST-004**: On every push, this repo's CI shall run, in one job, the check workflow's verification and checks steps with `continue-on-error: true` (the checks step writing its output to a file through its own `tee`), against a fixture whose `check` task has one dependency that fails immediately and one that prints a marker after a 1-second delay, followed by a step that fails unless the verification step's outcome is `success`, the checks step's outcome is `failure`, and the output file contains the marker.
- [x] **CHECK-TEST-005**: On every push, this repo's CI shall run, in one job, the check workflow's verification step with `continue-on-error: true` against a fixture whose `.config/mise/config.toml` redefines `check`, followed by a step that fails unless the verification step's outcome is `failure`.
- [x] **CHECK-TEST-007**: On every push, this repo's CI shall run, in one job, the check workflow's verification step with `continue-on-error: true` against a fixture whose `.config/mise/config.toml` redefines `test` (a dependency of a `check` task defined in `conf.d`), followed by a step that fails unless the verification step's outcome is `failure`.
- [x] **CHECK-TEST-006**: Each job that CHECK-TEST-004, CHECK-TEST-005 or CHECK-TEST-007 describes shall repeat the check workflow's `ceiling`, `mise`, `script` and `verify` steps, and its `check` step where it has one, with the same ids, in the same order, and with `uses`, `run` and `with` identical to the corresponding steps in `.github/workflows/check.yml`, apart from mise-action's `working_directory`, which shall equal that job's fixture directory.
