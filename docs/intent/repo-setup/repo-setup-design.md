---
parent: high-level-design
prefix: SETUP
---

# This repo's own setup

## Context and Design Philosophy

The HLD's decisions on template skills and LID pin bumps reach consumers through copier-python, which renders the manifest, lock file, links, tasks and hook into each of them. This repo doesn't apply that template to itself yet, so it carries the same setup by hand, in the form a repo without a template takes: the manifest sits at the repo root, and there's no `.config/<template>/` directory. Once the template applies itself here, this node shrinks to what the template doesn't cover.

This repo's root `apm.yml` has a second job: because the repo root is the skills package, the same manifest is the package's dependency list. Every template that pins the package installs the LID plugin listed here, so the LID version this repo pins is the one every consumer runs, and anything added to the manifest's `dependencies` reaches them all.

The setup has one rule: a fresh clone plus `mise run setup` locally, the SessionStart hook in a cloud session, or `mise run check` in CI each leaves the repo with the same tools and skills, from committed pins and lock files.

## Skills layout

| Path | Contents |
|---|---|
| `skills/<name>/` | The source of each skill developed here: the skills package's skills |
| `.claude/skills/` | A real directory. For each skill in `skills/`, a committed relative link `<name>` to `../../skills/<name>`. LID's installed skills, as real directories, gitignored |
| `.agents/skills/` | A real directory. For each skill in `skills/`, a committed relative link `<name>` to `../../skills/<name>`. For each skill LID's package deploys, a committed relative link `<name>` to `../../.claude/skills/<name>` |
| `apm.yml` | `targets: [claude]` and one dependency, `jszmajda/lid/plugins/linked-intent-dev#vX.Y.Z`, under `dependencies` (not `devDependencies`, which APM doesn't install for a package's users) |
| `apm.lock.yaml` | The lock file `apm install` writes: each package's commit, and each deployed file and its hash |
| `.gitignore` | `apm_modules/` (APM adds it on install), `/.claude/skills/*`, and a `!/.claude/skills/<name>` line for each skill in `skills/` |

Every skill developed here is a package skill, which consumers load under Claude Code and other agents alike, so each gets both links. The links into `.claude/skills/` for LID's skills let other agents here use LID too. Until the first install they point nowhere, as a consumer's template links do.

"LID's skills" means the skill directories the lock file's LID entry lists in its `deployed_files` (the entries of the form `.claude/skills/<name>`). A real directory in `.claude/skills/` that isn't one of them, such as a skill a newer LID release dropped, is left behind by APM, which removes only what its lock file records. The layout test reports it so a person deletes it. A skill developed here can't share a name with one of LID's: both would claim the same `.agents/skills/<name>`, and the layout test fails on the clash.

The ignore rule ignores everything in `.claude/skills/` and re-includes the links to this repo's own skills, so a skill a later LID release adds is ignored with no edit. Each skill added to `skills/` adds its `!` line along with its two links, and removing a skill removes all three.

## Installing skills

`mise.toml` pins `apm` (mise's `github:microsoft/apm` backend) with the other tools, and `mise.lock` records its download URL and checksum. These tasks use it:
- **`skills`** runs `apm install --frozen` at the repo root. It installs exactly what `apm.lock.yaml` records, restores any deployed file whose content differs from its locked hash, and fails when `apm.yml` and the lock file disagree. It depends on nothing but the `apm` tool.
- **`setup`** runs `mise install`, then `skills`, then `prek install -c .config/prek.toml`. Re-running it after a LID bump installs the new skills.
- **`test`** depends on `skills` as well as `sync`, because the layout tests resolve links into the installed skills. `check` depends on `test`, so `mise run check` installs the skills in CI and locally alike, and the CI workflow needs no step of its own.

A frozen install fetches by git from `github.com` and doesn't use GitHub's API (tested with APM 0.33.0 from an empty cache, behind a proxy refusing `api.github.com`). With the packages already in APM's cache, it needs no network at all, so a local `mise run test` works offline once the skills have been installed once. A first install with no network fails, and so does `test`.

Renovate's apm manager bumps the LID pin in `apm.yml` and, because the lock file sits beside it, runs `apm install` and commits the updated lock file in the same PR. That PR then reaches the LID version gate below.

## LID version gate

A test reads the `## LID` block of `AGENTS.md` (which `CLAUDE.md` links to) and the `apm.lock.yaml` entry whose `repo_url` is `jszmajda/lid` and whose `virtual_path` is `plugins/linked-intent-dev`. It fails:
- while the block's `- Version:` differs from the entry's `version`, with a message naming both versions and `/update-lid`;
- when there's no such entry, no `## LID` block, or no `- Version:` bullet;
- when there's more than one `## LID` block, or more than one `- Version:` bullet in it.

The test runs in `check`. The shared preset holds Renovate's LID PR for a person to merge, and the gate keeps it failing until someone runs `/update-lid` on its branch and pushes the walk. The gate catches a forgotten walk, not an unfinished one: it passes as soon as the bullet names the new version.

A LID release that adds or removes a skill also needs its `.agents/skills/` link added or removed by hand, on the same PR. The layout test fails until the links match, naming each missing or extra link.

## Cloud sessions

`.claude/settings.json` registers one SessionStart hook, `.claude/hooks/session-start.sh`, with no matcher, so it runs on every session source (startup, resume, clear, compact and fork). The script:
1. exits 0 at once unless `CLAUDE_CODE_REMOTE` is `true`, so local sessions keep the developer's own mise;
2. installs mise at the version in its `MISE_VERSION` line into `~/.local/bin`, unless that version is already there. It downloads the Linux x86-64 release archive and its `SHASUMS256.txt` from mise's GitHub release, and verifies the archive before unpacking it. A checksum file with no line for the archive is a failure;
3. enters the project directory (an unset or missing `CLAUDE_PROJECT_DIR` is a failure), runs `mise trust` there, then `mise install apm` and `mise run skills`, then `mise install` for the remaining tools. The skills go first, so a failure in an unrelated tool still leaves the session its skills. `mise run` normally installs every missing tool in the config before running a task, and stops if one fails, so the hook runs `skills` with `MISE_TASK_RUN_AUTO_INSTALL=false`;
4. appends a `PATH` line for mise and every pinned tool to `CLAUDE_ENV_FILE`, unless the file already holds that exact line, so later commands can call `ruff` or `lidc` directly. In a cloud session, an unset `CLAUDE_ENV_FILE` is a failure;
5. prints one JSON object to stdout, `{"hookSpecificOutput": {"hookEventName": "SessionStart", "reloadSkills": true}}`, and exits 0.

Claude Code discovers skills before SessionStart hooks finish, so without `reloadSkills` the skills the hook installs could be missing at the first prompt. With it, Claude Code re-scans the skill directories once the hooks complete (verified in a cloud session on 2026-10-26: LID's skills, installed by the hook, were listed at the first prompt). Claude's first response waits for SessionStart hooks, so the tools and skills exist before the agent's first turn. Since stdout carries that object, every command the script runs sends its own output to stderr.

On any failure, the script runs no later step. It prints the same object with an `additionalContext` field naming the step that failed and what is missing, and exits 0. Claude Code adds a SessionStart hook's output to Claude's context only when the hook exits 0; on a non-zero exit, only the user sees a notice, and the session goes ahead either way. The notice therefore reaches the agent that would otherwise hit the missing tools, and the agent tells the user. The object still asks for a re-scan, because a failure after the skills step leaves them installed. An exit trap prints the object, with a notice, even when the script stops outside its defined steps.

The hook serves cloud sessions started on a repository, such as those at claude.ai/code. A thread in a claude.ai Project loads neither project skills nor project hooks, so it gets none of this setup.

A fresh container pays about 30 seconds; a reused one about a second, since each step skips what's already installed. Claude Code's default timeout for a command hook, 600 seconds, leaves ample room, so the registration sets none. The cloud environment's network policy must allow GitHub (releases and git), `nodejs.org`, npm and PyPI. mise installs its GitHub-hosted tools from the URLs in `mise.lock`, and a full `mise install` succeeded in a cloud session whose proxy refuses other repositories' API calls.

`MISE_VERSION` must equal the `version:` input of every `jdx/mise-action` step in `.github/workflows/`. This repo's `.github/renovate.json` adds a regex manager that reads `MISE_VERSION=` in the hook as the `jdx/mise` GitHub release, the dependency Renovate already bumps in the workflows. Updates of one dependency with the same datasource and version share a branch, so a mise release bumps both in one PR. If they ever split, the equality test fails both PRs rather than letting one merge.

## Testing

pytest tests in `tests/test_repo_setup.py` cover:
- the layout: both directories are real; each skill in `skills/` has both links; each of LID's skills has its `.agents/skills/` link; every link is relative and resolves; neither directory holds anything else apart from LID's installed skills in `.claude/skills/`. A link that doesn't resolve fails with a message to run `mise run skills`;
- the ignore rule, through `git check-ignore`: an installed LID skill is ignored and each own-skill link isn't, and every `!` line names a skill in `skills/`;
- `apm.yml`'s target and its single dependency, and the task wiring in `mise.toml`;
- the LID version gate, on the repo itself and on fixture text for each failure case;
- the hook: outside a cloud session it exits 0 and changes nothing; in a cloud session, with a stub `mise` in a temporary home directory, it prints exactly one JSON object with `reloadSkills` true, and when the stub fails a step, the object's `additionalContext` names that step and the hook exits 0; `MISE_VERSION` equals every mise-action `version:` input; `settings.json` registers it with no matcher; and Renovate's extraction (with the pinned Renovate CLI, as the preset tests run it) reports `MISE_VERSION` and the workflows' `version:` inputs with the same `depName`, datasource and current version.

The hook's run in a real cloud session is checked by hand: a cloud session on a branch carrying the hook lists LID's skills at its first turn, `mise run check` passes in it, and a hook run with a broken step shows its notice to the agent.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Loading the skills developed here | A committed link per skill from `.claude/skills/<name>` and `.agents/skills/<name>` into `skills/` | Linking all of `.claude/skills` to `skills/`; a copy kept in sync by a test; `--plugin-dir` | One copy of the source, editable outside `.claude/`, and committed links load in cloud sessions. A whole-directory link would put installed skills inside the package; a copy can drift; `--plugin-dir` doesn't reach cloud sessions |
| `.agents/skills/` | A real directory with a link per skill | One link from `.agents/skills` to `.claude/skills`; APM's `agent-skills` target | Matches the layout the HLD sets for every repo, so a skill can be for other agents only. The single link would also need no edits per skill. The `agent-skills` target would install a second copy of every skill |
| Where LID is pinned | A root `apm.yml`, which is also the skills package's dependency list | A user-level LID plugin; LID's vendored workflow doc; a separate manifest for this repo's own use | A plugin installed per user doesn't reach cloud sessions or other contributors; the workflow doc carries no `/update-lid` or `/lid-coach`. APM reads the package's dependencies from the root manifest, so one pin serves this repo and every consumer, and a second manifest would be a second LID pin to keep in step |
| What the manifest may list | LID's core plugin only | Further packages, such as LID's arrow-maintenance | Every dependency here installs in every consumer, so a package earns a place only when all of them should have it |
| Ignoring installed skills | `/.claude/skills/*` with a `!` line per own skill | One line per LID skill | A skill a later LID release adds stays ignored without an edit; the `!` lines change only when a skill is added here, which already needs hand-made links |
| LID's skills for other agents | A committed `.agents/skills/` link per LID skill | No links, so only Claude Code sees LID | `AGENTS.md` tells every agent to consult the skill; the links cost one edit when a LID release adds or removes a skill, which the layout test flags |
| Where the version gate runs | A pytest test, run by `check` | A step in the `lid` task | Matches how this repo's other structural checks run, and pyyaml is already a test dependency; the `lid` task stays one `lidc` call |
| The version the gate compares | The lock entry's `version` | Its `resolved_ref` without the `v` | `version` is the package's own declared version, which LID treats as its conventions version; a ref could be a commit |
| When `check` installs skills | `test` depends on `skills` | A separate dependency of `check` | The tests are the only part of `check` that reads installed skills |
| Cloud setup | A committed SessionStart hook | The cloud environment's setup script | The hook is reviewed, versioned and updated by Renovate with the repo; a setup script is cached but lives outside the repo |
| Hook sources | No matcher: every source | `startup` only | A resumed or cleared session in a reused container costs about a second, and one that lost its tools gets them back |
| Making installed skills visible | The hook returns `reloadSkills: true` | `/reload-skills` typed at the start of each session; relying on the skills file watcher | Skill discovery runs before the hook finishes, so without a re-scan the first prompt can miss the skills; a manual step would be forgotten |
| Reporting a hook failure | `additionalContext` in the hook's JSON output, exit 0 | A non-zero exit; a plain-text notice on stdout | Only an exit-0 hook's output reaches Claude; a non-zero exit shows the user a notice the agent never sees, and doesn't stop the session either way. Plain text can't share stdout with the `reloadSkills` object, which Claude Code parses as JSON |
| Install order in the hook | `apm`, then skills, then the other tools | One `mise install` first | Skills need only `apm`, so an unrelated tool's failure doesn't cost the session its skills |
| Integrity of the mise download | The release's own `SHASUMS256.txt` | A hash pinned in the hook | Catches a corrupt download without a second value for Renovate to update; it doesn't defend against a compromised release, as a pinned hash would |
| Keeping the hook's mise version in step | A regex manager on the same `jdx/mise` dependency, plus a test | The hook parsing the version out of a workflow file; the version in `mise.toml` | One PR per mise release with no parsing of YAML in bash; `mise.toml` holds only a minimum version |

## Open Questions & Future Decisions

### Deferred
1. Whether `CLAUDE_ENV_FILE` survives a resume in the same container. The hook's check for an existing line makes either answer safe.
2. Moving the regex manager into the shared preset, when the template ships a hook of its own.
3. Other platforms for the hook, if cloud sessions ever run on anything but Linux x86-64.

## References

- HLD: Key Design Decisions on template skills and on LID pin bumps; "The tooling repos' own checks".
- [APM](https://github.com/microsoft/apm) v0.33.0; Claude Code [hooks](https://code.claude.com/docs/en/hooks) (SessionStart output, `reloadSkills` from v2.1.152, `CLAUDE_ENV_FILE`) and [skills](https://code.claude.com/docs/en/skills) (where project skills load, and not in Project threads); [mise releases](https://github.com/jdx/mise/releases).
