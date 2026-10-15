---
parent: high-level-design
prefix: LOCK
---

# Lock-refresh workflow

## Context and Design Philosophy

Consumer repos commit `mise.lock` and its dependency sidecars, and CI installs with `--locked`. A template release that changes a tool pin reaches a consumer through Renovate's copier manager, which re-renders the template's files but doesn't run `mise lock`. The hosted Renovate app can't run it either: its `postUpgradeTasks` allowlist is `^git add --all$`, `^git reset$` and `^pwd$`. Without help, every template update that moves a pin would fail CI and never automerge.

This workflow closes that gap. It runs on Renovate's template-update PRs, reruns `mise lock`, and pushes the refreshed lock files to the PR branch. The push is made with a GitHub App installation token, because a push made with the workflow's own `GITHUB_TOKEN` doesn't start a new workflow run, so CI would never retest the PR.

It reads config it doesn't control (a new template release on a bot's branch) while holding a write credential, so it keeps the two apart. Every mise command in the job runs in mise's safe mode, which stops project config from running code or changing the environment. The token is minted only after `mise lock`, and the steps that hold it call `/usr/bin/git` by absolute path rather than anything a tool manager put on `PATH`.

The pattern follows aquaproj's [update-checksum-workflow](https://github.com/aquaproj/update-checksum-workflow), which does the same for aqua's checksum file.

## Contract with consumer repos

A consumer opts in by:
- installing a GitHub App on the repo, with repository permission **Contents: read and write** and nothing else;
- storing the App's private key as the repository secret `LOCK_REFRESH_APP_PRIVATE_KEY`;
- carrying the template-rendered stub `.github/workflows/lock-refresh.yml`, which holds the App's client ID;
- tracking a lock file in a supported layout: `mise.lock` at the root (sidecars under `.mise/locks/`), `.config/mise/mise.lock` (sidecars under `.config/mise/locks/`), or both. A repo that tracks neither is left alone. A repo that tracks any other mise lock file (`.mise.lock`, `.config/mise.lock`, or an environment-specific `mise.<env>.lock`) fails the job with a message naming it, because those layouts aren't handled (verified with mise 2026.10.8: `conf.d` fragments, symlinked or not, lock to `.config/mise/mise.lock`, and a root `mise.toml` locks to `mise.lock`).

The stub triggers on `pull_request` events whose changes include a copier answers file (`paths: [".copier-answers.*.yml"]`, which matches the layered name `.copier-answers.<template>.yml` at the root). GitHub evaluates the filter on the PR's whole diff for each event, so runs after a push still match. Its diff is capped at 3,000 files: in a larger diff where the answers file isn't among the first 3,000, the workflow doesn't run. Template updates change a handful of files, so the cap doesn't arise. Every template update changes its answers file, and no other kind of Renovate update leaves `mise.lock` stale: Renovate's mise manager refreshes the lock for pins it bumps, and people who change pins run `mise lock` themselves.

The secret name, the stub's inputs and the commit author address are a stable interface. Changing any of them is a major version.

## Workflow file

`.github/workflows/lock-refresh.yml`, triggered by `workflow_call`.

| Element | Design |
|---|---|
| Inputs | `client-id` (required string): the App's client ID |
| Secrets | `app-private-key` (required) |
| Permissions | `contents: read` for the job's own `GITHUB_TOKEN`. Writes go through the App token only |
| Environment | `MISE_SAFE: 1` at job level, so no mise command in the job, mise-action's own included, runs project code |
| When the job runs | A job-level `if` requires a `pull_request` event, a PR opened by `renovate[bot]` (the hosted app's login), and a head repository equal to the base repository. Fork PRs never get secrets, and the job skips them before any step |
| Concurrency | One run per PR (`lock-refresh-<PR number>`), cancelling an older run in progress, so a Renovate rebase supersedes a stale run. The App's own push can cancel the pushing run during its cleanup steps, which shows as a cancelled run and does no harm: this workflow isn't a required check |
| Runner and timeout | The same pinned Ubuntu image as the check workflow, which Renovate bumps. `timeout-minutes: 30`, because `mise lock` downloads every locked platform's artifact for each new tool version to verify its provenance |

Steps, in order:

| Id | Does |
|---|---|
| `checkout` | `actions/checkout` at the PR's head SHA, without persisted credentials |
| `tracked` | Creates the empty directory `$RUNNER_TEMP/lock-refresh-empty` for the `mise` step. Lists the tracked lock files in the supported layouts. If there are none, later steps are skipped. If the repo tracks a mise lock file in an unsupported layout, the step fails with its path |
| `mise` | `jdx/mise-action` with the same pinned mise version as the check workflow, `working_directory` set to `$RUNNER_TEMP/lock-refresh-empty` (so the `mise ls` calls the action always makes see no project config), `install: false`, `env: false` and `cache: false`. The action still puts mise on `PATH` (verified in mise-action 5.1.1's source) |
| `lock` | `mise lock` in the repo, under the job's safe mode, with the job's read-only `GITHUB_TOKEN` in its environment so GitHub API calls are authenticated rather than limited to 60 an hour. Safe mode loads project config without trust, skips hooks, `_.source` and project `[env]` and `[settings]`, and refuses tasks and asdf plugins (verified with mise 2026.10.8: without it, `mise lock` and `mise ls` ran a test repo's `_.source` script; with it, neither did). Entries for new versions are added, and stale entries and their sidecars are pruned. Because project `[settings]` are ignored, the platforms come from the existing lock file. The token is read-only and lives only for this job; if a tool's backend options could send mise's API calls to another host, that token is all they could carry, which is the accepted residual risk |
| `changes` | Stages only lock material, with `/usr/bin/git`: each tracked lock file, and its sibling sidecar directory, including deletions. A sidecar directory is staged only when its lock file is tracked, and a lock file `mise lock` created where none was tracked is never staged. If a tracked lock's sidecar directory is ignored by git, the step fails naming it: CI's locked install would fail without those files anyway. Writes `staged=true` or `staged=false` to its step outputs |
| `token` | Only if `staged` is `true`: `actions/create-github-app-token` with `client-id`, `private-key`, `repositories` set to the current repository's name, and `permission-contents: write` |
| `push` | Commits with `/usr/bin/git`, with the fixed author and committer `Lock Refresh <lock-refresh@agentic-development.invalid>` set on the command (the runner has no git identity), with the message `Refresh mise lock files`. Pushes `HEAD` to the PR's head branch with `--force-with-lease=refs/heads/<branch>:<checked-out SHA>`, which succeeds only if the branch still points at the commit that was checked out, so a moved or deleted branch is never overwritten or recreated. It authenticates with the App token through an HTTP authorization header passed in `GIT_CONFIG_*` environment variables, never on the command line, and the header's encoded value is masked in the log. If the push fails, the step asks the remote for the branch: if the branch moved or is gone, it exits successfully with a notice, since Renovate's new head starts a fresh run or the PR has closed; any other failure (authentication, a ruleset, the network) fails the step |

Every `run` step sets `shell: bash` and takes values through `env:`, as in the check workflow. Actions are pinned by commit digest with a version comment, and Renovate bumps them.

**When `mise lock` fails** (the network, a fragment's `min_version` above the pinned mise, or a file left with conflict markers), the job fails and pushes nothing. The PR's required CI check stays red, so automerge waits. Recovery is a re-run of the job, or Renovate's rebase checkbox once the cause is fixed.

**After the push.** The App's push starts the consumer's CI on the new head and starts this workflow again, which then finds nothing to stage and stops. When Renovate rebases its branch, it drops the lock commit, and the next run makes it again. Renovate treats the lock commit as its own because the shared preset lists the author address in `gitIgnoredAuthors`. Without that, Renovate would consider the PR edited and stop updating or rebasing it.

## Testing

- **Static tests** parse the workflow: the trigger and inputs, `contents: read`, the job condition, concurrency, step order (the token step comes after the lock step), job-level `MISE_SAFE`, mise-action's inputs and its version matching the check workflow, action pins, and the fixed author and committer, which must equal the preset's `gitIgnoredAuthors` entry.
- **Step tests** run the `tracked`, `lock`, `changes` and `push` steps' `run` text with bash against fixture repos that track a `mise.lock` locked for one platform, with a local bare repository as `origin` and no token. They cover: the empty directory for the `mise` step; a changed pin gets a lock commit that touches only lock material; an unchanged pin pushes nothing; a repo without a tracked lock is untouched; the refreshed lock keeps the fixture's single platform; a failing `mise lock` (a `min_version` above the pinned mise) fails before any push; an untracked root `mise.lock` and its sidecars are never staged; an unsupported lock layout fails; a moved or deleted branch makes the push exit successfully without overwriting or recreating it; any other push failure, including a remote that can't be read, fails the step; a gitignored sidecar directory fails with its name; and a fixture whose config has a `_.source` canary shows nothing ran, while a control run without safe mode shows the canary does fire. They need the network for `mise lock`.
- **End to end:** the first consumer's first template-update PR. Only that run exercises the `if:` conditions, the `checkout`, `mise` and `token` steps, and the authorization header against github.com (the step tests push to a local path). This repo can't exercise the App push in its own CI without an App installed on it.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Who runs `mise lock` on template updates | A workflow on the PR branch, pushing with a GitHub App token | Renovate `postUpgradeTasks`; self-hosted Renovate; a personal access token | The hosted app's allowlist excludes `mise lock`. Self-hosted Renovate would replace the hosted app chosen in the config-sync decision. A personal token expires and makes the commits look like the developer's |
| Commit author | A fixed address, `lock-refresh@agentic-development.invalid` | The App's own bot identity, from a verified API commit | A fixed address lets the shared preset list it in `gitIgnoredAuthors` without knowing each adopter's App, and it is unique to this workflow, as Renovate requires. The `.invalid` domain can never belong to a real account. Commits aren't signed; a repo that requires signed commits would need the API commit instead |
| Push tool | Plain git, with the App token in an HTTP header | suzuki-shunsuke/commit-action (API commits, verified) | Plain git needs no third-party action. Signed commits are deferred (below) |
| Where the App's client ID lives | A copier answer rendered into the stub | A repository variable; a secret | The ID isn't sensitive, so each consumer needs only one secret and no extra setup step |
| Which PRs | Template-update PRs only, by a `paths` filter on the copier answers file, plus a `renovate[bot]` author check | Every Renovate PR | Only template updates leave the lock stale. Filtering in the stub keeps other PRs from starting a run at all |
| Lock files a repo doesn't track | Never created or committed | Commit whatever `mise lock` writes | Committing lock files is a repo's choice. The workflow keeps a lock current; it doesn't introduce one |
| Untrusted config next to the token | Safe mode for the whole job, mise-action pointed at an empty directory, no tool installs or exported env, the token minted only after `mise lock`, and git called by absolute path | Safe mode for `mise lock` only; mint the token first, as most examples do | mise-action runs `mise ls` in its working directory, which without safe mode runs a repo's `_.source` script, and a script can change later steps' `PATH` and environment (verified with mise 2026.10.8) |
| Pushing | `--force-with-lease` against the checked-out SHA, then classify a failure by asking the remote | A plain push without force | A plain push recreates a branch Renovate deleted. The lease is a compare-and-swap, and the follow-up check keeps real errors visible |

## Open Questions & Future Decisions

### Deferred
1. A repo that requires signed commits: switch the push to an API commit (for example commit-action), with the App's identity, and list that identity in the repo's own `gitIgnoredAuthors`.
2. Lock layouts beyond the two supported ones (`.mise.lock`, `.config/mise.lock`, environment-specific lock files). Add them when a consumer needs one.
3. Keeping the App's private key out of every consumer, with a central repo that makes the commits (securefix-action's client and server design). Revisit if per-repo secrets become a burden.

## References

- [actions/create-github-app-token](https://github.com/actions/create-github-app-token) (`client-id`; `app-id` is deprecated); [jdx/mise-action](https://github.com/jdx/mise-action) (`install`, `env`); [mise safe mode](https://mise.jdx.dev/security.html#safe-mode); Renovate's [`gitIgnoredAuthors`](https://docs.renovatebot.com/configuration-options/#gitignoredauthors); GitHub, [triggering a workflow from a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow); aquaproj's [update-checksum-workflow](https://github.com/aquaproj/update-checksum-workflow).
