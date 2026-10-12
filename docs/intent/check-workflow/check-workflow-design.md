---
parent: high-level-design
prefix: CHECK
---

# Check workflow

## Context and Design Philosophy

Every consumer repo runs its CI through one reusable workflow in this repo. A consumer's own `.github/workflows/ci.yml` is a stub that calls it and passes nothing. The workflow doesn't know which language a repo uses. It installs the repo's pinned tools with mise and runs the repo's `check` task. What `check` means is defined by the template layers that render the repo's mise config, so a change to what CI runs reaches consumers through a template update, and the workflow itself rarely changes.

## Contract with consumer repos

A consumer repo satisfies the contract when:
- its mise config pins every tool the checks need;
- a mise task named `check` runs every check and exits non-zero if any fails;
- that `check` task comes from a template-owned fragment loaded through `.config/mise/conf.d/`, a directory reserved for templates' links (mise reports a fragment's `conf.d` path as the task's source, even when the fragment is a symlink).

The same rule covers every task in `check`'s closure (the tasks it reaches through `depends`, `depends_post` and the task references in `run`) except those whose names end in `-extra`, the repo's extension points. Verification doesn't descend into a `-extra` task's dependencies, so a repo's extension can depend on its own tasks. The third rule stops a repo from turning CI into a no-op by redefining `check` or one of its dependencies (such as `test`) in a repo-owned mise file (`mise.toml` or `.config/mise/config.toml`), which mise then reports as the source. A dependency named with a pattern fails verification, because mise reports only the first task it matches. A task started by a `mise run` command inside a `run` script can't be checked. Repos extend checks through the `check-extra` task their template provides instead.

The workflow promises to:
- check out the commit being tested;
- install the pinned tools with mise and trust the repo's mise config;
- fail, naming the source file, if `check` or any non-`-extra` task it depends on is defined outside the repo's `.config/mise/conf.d/`, and fail with a clear message if there is no `check` task (see [Verification script](#verification-script));
- run every dependency of `check` even after one fails (`mise run --continue-on-error check`), so one CI run reports every failing check;
- fail the job exactly when `check` fails;
- need only read access to repository contents.

A release that adds a requirement to this contract is a major version. The contract is forge-neutral: a CI definition for another forge would keep the same promises.

**Releasing a contract change.** A consumer's workflow-tag update and its template update arrive as separate PRs, each tested against the other's old version. A new requirement therefore ships in three steps, so that each PR can pass alone:
1. Each template ships a release that satisfies both the old and the new contract.
2. This repo ships the major release that requires the new contract.
3. Only after that may a template release drop what only the old contract needed.

## Workflow file

`.github/workflows/check.yml`, triggered by `workflow_call`.

| Element | Design |
|---|---|
| Inputs | One optional input, `working-directory`, default `.`. It exists for this repo's own tests, and consumer stubs don't pass it. It is passed both to mise-action's `working_directory` and to the run steps |
| Permissions | `contents: read` |
| Trust | `MISE_TRUSTED_CONFIG_PATHS` is set at job level to `${{ github.workspace }}`, an absolute path that covers the repo root and every subdirectory, before any mise step runs |
| Config isolation | Before any mise step, a step exports `MISE_CEILING_PATHS` as the real (normalized) absolute path of the working directory's parent, so mise reads no config from above the working directory. For consumers that is above their checkout and changes nothing; for this repo's fixtures it hides the repo's own root `mise.toml`. mise ignores an unnormalized path containing `..` (verified with mise 2026.7.2) |
| Steps | Check out; set the config ceiling; install tools with `jdx/mise-action`; fetch the verification script; verify where `check` is defined; run `mise run --continue-on-error check 2>&1 \| tee "$RUNNER_TEMP/check-output.log"`. The job still fails on a failed check because GitHub's `shell: bash` sets `-o pipefail` |
| mise version | Pinned exactly through mise-action's `version` input. Renovate recognizes that input (mise-action is one of its known actions) and proposes each new mise release like any other dependency. Template fragments also set mise's `min_version`, so an older local mise fails loudly |
| Step conventions | Steps have stable ids: `checkout`, `ceiling`, `mise`, `script`, `verify` and `check` (and `assert` in this repo's negative-case jobs). Every `run` step sets `shell: bash` and its text contains no `${{ }}` expressions; values reach it through `env:`, so the same text runs unchanged in this repo's tests. Logic beyond a one-line command goes in the verification script, not in `run` text |
| Action pins | Every action, first-party ones such as `actions/checkout` included, is pinned by commit digest with a version comment, maintained by Renovate |
| Runner | A pinned Ubuntu image (`ubuntu-24.04` at first). Renovate's github-actions manager tracks `runs-on` images and proposes newer ones |
| Linting | actionlint checks both workflows, using the maintained fork [kjanat/actionlint](https://github.com/kjanat/actionlint) (MIT), pinned in mise and updated by Renovate. The original, rhysd/actionlint, has had no release since 1.7.12 (March 2026) and reports GitHub's `job.workflow_*` properties as undefined; the fork knows them. The fork turns on new checks by default in some releases, which surface as a failing update PR and are fixed forward |

## Verification script

`scripts/verify_check.py` checks that `check` and its dependencies come from template fragments. It is a standalone script that imports only the Python standard library, so it needs no install step in a caller's CI.

**What it guards against.** Accidental or agent-made overrides that would hollow out CI, not a hostile repo. A repo's own code runs on the same runner (mise hooks, the checks themselves, and `mise`, found through a `PATH` the caller's config can extend), so a repo set on defeating the check can. The script is fetched after `mise install`, so install hooks such as a repo's `postinstall` run before it exists.

**Fetching it.** The script must run at the same commit as the workflow that calls it, and the caller's checkout doesn't contain it. The `script` step, right after mise-action and right before `verify`, is a second `actions/checkout` of `${{ job.workflow_repository }}` at `${{ job.workflow_sha }}`, without persisted credentials, into `.check-workflow/` in the workspace. It uses non-cone sparse checkout (`sparse-checkout-cone-mode: false`) with the single pattern `scripts/verify_check.py`; cone mode, the action's default, would also check out every root file of this repo. For a reusable workflow these `job` properties name the workflow's own repo and commit, while `github.*` names the caller's (GitHub changelog, early September 2026). The fetch uses the caller's `GITHUB_TOKEN`, which can read a public repo.

`actions/checkout` only writes inside the workspace (its `path` resolves against `$GITHUB_WORKSPACE`, not the step's working directory). The `verify` step therefore first runs `mv -T "$GITHUB_WORKSPACE/.check-workflow" "$RUNNER_TEMP/check-workflow"`, which fails rather than nesting if a non-empty destination already exists, then runs `$RUNNER_TEMP/check-workflow/scripts/verify_check.py`. By the time the checks run, nothing from this repo is in the caller's workspace, so a caller's lint and type checks never see it. `.check-workflow/` is reserved: the second checkout replaces whatever a caller keeps there.

**Running it.** The `verify` step runs the script with `/usr/bin/python3 -I`: the runner image's own Python (3.12 on `ubuntu-24.04`), in isolated mode. mise-action exports the caller's mise `[env]` to later steps, and Python repos often set `PYTHONPATH` there, so without `-I` a caller module named like a standard-library one could shadow it inside the script. `PATH` is avoided for the same reason: after mise-action it holds the caller's shims. The script imports only the standard library, and this repo's type check runs against Python 3.12 (the `requires-python` floor), so newer standard-library APIs are type errors.

**Unsupported: GitHub Enterprise Server.** It lacks the `job.workflow_*` properties, so the checkout falls back to the caller's repo and the `verify` step fails because the script file doesn't exist.

**Algorithm.** A breadth-first walk from `check`:
- Each task's source comes from `mise tasks info <task> --json`, which reports a fragment's absolute `conf.d` path even when the fragment is a symlink (verified with mise 2026.7.2).
- A source passes if it has no `..` component and starts with `<working directory>/.config/mise/conf.d/` in either its logical form (`$PWD`, used only when it names the current directory) or its physical, symlink-resolved form, since mise may report either. mise reports paths pulled in through `includes` unnormalized, so without the `..` rule `conf.d/../../x.toml` would pass (verified with mise 2026.7.2).
- The walk follows `depends` and `depends_post` (not `wait_for`), and the task references in `run`. It reads each dependency form mise emits: a name, `"name args"` (the first word), an array (its first element) or an object (its `task` key). In `run`, a string is a script and is skipped; an object names tasks under `task` or `tasks`, each as `"name args"` (the first word). Any other form, or a `depends`, `depends_post` or `run` that isn't a list, is a violation, so an unfamiliar form fails closed.
- A task whose name ends in `-extra` is skipped, along with everything reachable only through it.
- A dependency containing pattern characters (`*`, `?`, `[` or `{`) is a violation, because mise reports only the first task a pattern matches. As a backstop for any other pattern syntax, a task that mise reports under a name that is neither the requested name nor one of its aliases is a violation too (verified with mise 2026.7.2: `lint:[ab]` reports `lint:a`; an alias reports the task's real name and lists the alias). Names are compared after removing a leading `//:` or `:`. In mise's experimental monorepo mode, mise reports root tasks as `//:check`, and `check`, `:check` and `//:check` all resolve to the same task (verified with mise 2026.7.2). A subproject task such as `//sub:lint` is defined in that subproject's own, repo-owned config, so the source check rejects it.
- A dependency for which `mise tasks info` fails is a violation that names it as not found and includes mise's error output, since a config error and a missing task look alike from outside. A missing `check` stops the walk with `no "check" task`.
- Output that isn't a JSON object, or has no string `source`, is a violation that names the task as unreadable. If `mise` itself can't be started, the script fails with that error.

The script reports every violation on stderr, continuing the walk after each one, and exits 1 if there were any.

## Testing a release

This repo's CI exercises the workflow against minimal fixture repos under `tests/fixtures/`, before a release is tagged.
- **Through the reusable workflow** (`uses: ./.github/workflows/check.yml` with `working-directory`):
  - **passing:** a fixture whose `check` task succeeds;
  - **fragment:** a fixture whose `check` task, defined in a `conf.d` fragment, runs a tool pinned only in that fragment and not preinstalled on the runner. This proves fragments are installed, trusted and loaded;
  - **symlinked fragment:** a fixture whose `conf.d` entry is a symlink into `.config/<template>/`, as templates render it. The location check must accept it.
- **Failure behavior, in an ordinary job.** A job that calls a reusable workflow can't tolerate the call failing, so each negative case runs the workflow's steps directly against a fixture, in one job: the steps under test set `continue-on-error: true` (the checks step's shared run text already tees its output to a file), and a final step asserts their `steps.<id>.outcome` values and greps the output file:
  - **failing:** a fixture whose `check` has one dependency that fails at once and one that passes after a 1-second delay. Plain `mise run check` aborts the delayed one (verified with mise 2026.7.2), so its output appears only when `--continue-on-error` is in effect. The verification step passes, the checks step fails, and the delayed dependency's output appears;
  - **overridden:** a fixture whose `.config/mise/config.toml` redefines `check`, and another that redefines `test`. The location check fails for both.

The negative-case jobs repeat the workflow's steps (`ceiling`, `mise`, `script`, `verify` and, where needed, `check`) with the same ids and in the same order, and a static test checks that their `uses`, `run` and `with` match `check.yml`'s, apart from mise-action's `working_directory`, which must equal the job's fixture directory. Every `-extra`, pattern and dependency-form case is tested locally against the script, so CI keeps only these three negative jobs, which prove the steps are wired together on a real runner.

This repo's CI calls the workflow from its own repo, where `job.workflow_sha` is the pushed commit. The first test of a call from another repo is a template's CI calling a published tag; if it fails, the fix is a patch release.

**Harness.** Tests are pytest files in `tests/`, the same toolchain as the Python repos this system serves. Static tests parse `check.yml` and this repo's CI workflow as YAML. Unit tests import the verification script's functions, including the logical-path rule with an injected `$PWD`. Step tests copy the script to where the `script` step puts it, then extract `run` blocks from `check.yml` and run them with bash against a fixture, when mise is available. `@spec` citations for the CI-run cases go in the static tests of this repo's CI workflow; fixtures carry none.

The fixtures test the workflow's mechanics. Whether a real Python repo's checks pass is tested in each template's own suite.

**First release.** This repo is tagged `v0.1.0` (workflow and preset) before any template's first release, because templates render stubs that reference a tag of this repo.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| What the workflow runs | `mise run --continue-on-error check` | Language-specific steps (setup-uv, ruff, ty, pytest); plain `mise run check` | Keeps the stub input-free and the workflow language-agnostic. Plain `mise run` stops the remaining dependencies at the first failure (verified with mise 2026.7.2), which hides later failures |
| Guarding against an overridden `check` | Fail unless `check` comes from `.config/mise/conf.d/` | Trust repos; compare the task to a template checksum | A higher-precedence `run` silently replaces a task (mise's documented merge rule). A location check is cheap and works for any template layer |
| Where the verification logic lives | A Python script in this repo, fetched at the workflow's own commit | Inline bash in `check.yml`; inline `shell: python`; a composite action; a published package installed through the caller's mise config | `run` text in YAML is hard to read, lint and test, and this repo's negative-case jobs would have to repeat it. A composite action needs a `uses:` ref, which can't be an expression, so `check.yml` would have to pin a hand-bumped tag of its own repo, and branch CI would test the old action. A caller's repo-owned mise config could override a package's pin |
| Python that runs the script | The runner image's `/usr/bin/python3`, standard library only | `python3` from `PATH`; a mise-installed Python | `PATH` holds the caller's mise shims after mise-action runs, so the caller's config would choose the interpreter. Installing one costs time and adds a pin |
| Number of workflows | One, shared by every language layer | One per layer | Nothing in the steps is language-specific |
| Fixture strategy | Hand-written minimal fixtures in this repo | A fixture rendered from copier-python | The workflow's release tests must not depend on a template release that depends on this workflow |
| Negative tests | Run the steps in an ordinary job with `continue-on-error` | A failing reusable-workflow call, asserted afterwards | A failed reusable call makes the whole run fail, so this repo's CI would stay red and Renovate could never automerge here |
| Pinned mise and runner | Exact versions, updated by Renovate | `ubuntu-latest` and mise-action's default mise | A floating image or mise version changes under every consumer without a commit. Pinned versions change through update PRs that CI tests first |
| Trust scope | The whole workspace, as an absolute path | Only the working directory | mise also loads config from parent directories. Fixtures inherit this repo's root config, which must be trusted too |

## Open Questions & Future Decisions

### Deferred
1. Caching uv and pytest caches across runs. Add it when CI time matters.
2. Job timeout and concurrency limits.
3. A second runner OS. Add it only when a consumer needs one.

## References

- [jdx/mise-action](https://github.com/jdx/mise-action); Renovate's github-actions manager (`known-actions/github-release-attachments-dynamic.ts` for mise-action's `version`, the `github-runners` datasource for `runs-on`); [mise configuration and task merging](https://mise.jdx.dev/configuration.html); [GitHub reusable workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations) (keywords allowed on a calling job); [GitHub Actions: Early September 2026 updates](https://github.blog/changelog/2026-09-03-github-actions-early-september-2026-updates/) (the `job.workflow_*` properties).
