# Lock-refresh workflow specs

Design: [lock-refresh-design.md](lock-refresh-design.md). "The lock-refresh workflow" is `.github/workflows/lock-refresh.yml`. "The caller repo" is the repo whose stub calls it. "A supported lock file" is `mise.lock` at the caller repo's root or `.config/mise/mise.lock`. Its "sidecar directory" is `.mise/locks/` or `.config/mise/locks/` respectively. "The PR head SHA" is `github.event.pull_request.head.sha`, and "the head branch" is `github.event.pull_request.head.ref`; both reach `run` steps only through `env:`.

## Workflow definition

- [x] **LOCK-001**: The lock-refresh workflow shall be triggered only by `workflow_call`.
- [x] **LOCK-002**: The lock-refresh workflow shall accept exactly one input, the required string `client-id`, and exactly one secret, the required `app-private-key`.
- [x] **LOCK-003**: The lock-refresh workflow shall request only the `contents: read` permission.
- [x] **LOCK-004**: The lock-refresh workflow's job shall set `MISE_SAFE` to `1` in its job-level environment.
- [x] **LOCK-005**: The lock-refresh workflow's job shall run only when the event is `pull_request`, the pull request's author login is `renovate[bot]`, and the pull request's head repository is the caller repo itself.
- [x] **LOCK-006**: The lock-refresh workflow's job shall belong to a concurrency group keyed by the pull request's number, with the group `lock-refresh-${{ github.event.pull_request.number }}` and `cancel-in-progress` set to `true`.
- [x] **LOCK-007**: The lock-refresh workflow's `runs-on` shall equal the check workflow's `runs-on`.
- [x] **LOCK-008**: The lock-refresh workflow's job shall set `timeout-minutes` to `30`.
- [x] **LOCK-009**: The lock-refresh workflow shall reference every action by a 40-character commit SHA followed by a comment of the form `# v<version>`.
- [x] **LOCK-010**: The lock-refresh workflow's steps shall have the ids `checkout`, `tracked`, `mise`, `lock`, `changes`, `token` and `push`, in that order.
- [x] **LOCK-011**: The lock-refresh workflow's `checkout` step shall check out the PR head SHA with `persist-credentials` set to `false`.
- [x] **LOCK-012**: The lock-refresh workflow's `mise` step shall run `jdx/mise-action` with the same `version` as the check workflow's mise step, `install`, `env` and `cache` set to `false`, and `working_directory` set to `${{ runner.temp }}/lock-refresh-empty`.
- [x] **LOCK-013**: The lock-refresh workflow's `token` step shall run `actions/create-github-app-token` only if `steps.changes.outputs.staged == 'true'`, with `client-id` from the input, `private-key` from the secret, `repositories` set to `${{ github.event.repository.name }}`, and `permission-contents` set to `write`.
- [x] **LOCK-014**: Every `run` step of the lock-refresh workflow shall set `shell: bash`, and its `run` text shall contain no `${{ }}` expression.
- [x] **LOCK-015**: The lock-refresh workflow's `changes` and `push` steps shall invoke git only as `/usr/bin/git`, so that a `git` placed earlier on `PATH` never runs.
- [x] **LOCK-016**: The lock-refresh workflow's `lock` step shall run `mise lock` with `GITHUB_TOKEN` set from the job's own `github.token`.

## Refreshing the lock

- [x] **LOCK-RUN-001**: If the caller repo tracks no mise lock file, then the lock-refresh workflow shall succeed without running `mise lock`, minting a token or pushing.
- [x] **LOCK-RUN-002**: If the caller repo tracks `.mise.lock`, `.config/mise.lock`, or a file matching `mise.*.lock` at the root or in `.config/mise/`, then the lock-refresh workflow's `tracked` step shall fail with a message naming that path.
- [x] **LOCK-RUN-003**: When `mise lock` changes a tracked supported lock file or its sidecar directory, the lock-refresh workflow's commit shall contain every added, modified and deleted file in each tracked supported lock file and its sidecar directory, and no change to any other path.
- [x] **LOCK-RUN-004**: The lock-refresh workflow shall never commit a supported lock file the caller repo didn't track before `mise lock` ran, or anything in that lock file's sidecar directory.
- [x] **LOCK-RUN-005**: When no tracked supported lock file or its sidecar directory differs from the PR head SHA after `mise lock`, the lock-refresh workflow's `changes` step shall write `staged=false` to `$GITHUB_OUTPUT`, and the workflow shall mint no token, make no commit and push nothing; otherwise the step shall write `staged=true`.
- [x] **LOCK-RUN-006**: The lock-refresh workflow's commit shall have the author and committer `Lock Refresh <lock-refresh@agentic-development.invalid>`, without relying on any git configuration on the runner, and the message `Refresh mise lock files`.
- [x] **LOCK-RUN-007**: The lock-refresh workflow shall push its commit to the head branch with `--force-with-lease=refs/heads/<head branch>:<PR head SHA>`.
- [x] **LOCK-RUN-008**: If the push fails and the remote head branch is gone or no longer points at the PR head SHA, then the lock-refresh workflow's `push` step shall succeed with a `::notice::` line and leave the remote branch as it was, without recreating it.
- [x] **LOCK-RUN-009**: If the push fails while the remote head branch still points at the PR head SHA, or the remote branch can't be read, then the lock-refresh workflow's `push` step shall fail.
- [x] **LOCK-RUN-010**: The lock-refresh workflow's `push` step shall pass the App token to git only as the `http.https://github.com/.extraheader` value set through `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>` and `GIT_CONFIG_VALUE_<n>` environment variables, never in a command's arguments, and shall print `::add-mask::` for the encoded header before anything else that contains it.
- [x] **LOCK-RUN-011**: While the lock-refresh workflow runs `mise lock` on a caller repo whose mise config defines a `_.source` script, that script shall not run.
- [x] **LOCK-RUN-012**: If `mise lock` fails, then the lock-refresh workflow shall fail without minting a token or pushing.
- [x] **LOCK-RUN-014**: When the lock-refresh workflow refreshes a tracked supported lock file, the refreshed file shall list the same platforms as before.
- [x] **LOCK-RUN-013**: The lock-refresh workflow's `tracked` step shall create `$RUNNER_TEMP/lock-refresh-empty` as an empty directory.
- [x] **LOCK-RUN-015**: If a tracked supported lock file's sidecar directory is ignored by git, then the lock-refresh workflow's `changes` step shall fail with a message naming that directory.
