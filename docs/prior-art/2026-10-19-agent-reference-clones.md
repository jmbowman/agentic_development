# Prior art: local reference clones of external repos for agents (2026-10-19)

- **Effort:** full method, because whatever is chosen is delivered to every repo through the template, which is costly to reverse.
- **Already known:** the developer uses vcs2l today (the `reference-repos` skill in the public [jmbowman/portabase](https://github.com/jmbowman/portabase), `.claude/skills/reference-repos/`, GPL-2.0-or-later), and tried gitman and similar tools, which weren't better than vcs2l. No exhaustive list of dismissed tools exists.

## Need and criteria

The question: move portabase's `reference-repos` skill into agentic_development as a template-owned skill, or replace it with an existing tool.

| Requirement | Underlying need |
|---|---|
| Agents can clone any repo they need to inspect | Exact answers from source and docs at the version in use, instead of recall or web fetches (the clone is a means; source services compete as partial matches) |
| Careful about prompt injection and other attacks | Nothing from a cloned repo runs; clones are never edited; the tool itself is pinned |
| Quick update of all cached repos | One bounded, parallel refresh before relying on a clone |
| Read-only and pinned; works offline once cloned | A committed manifest restores the same set anywhere; reading needs no network |
| Works in web sessions, low setup per repo | Deliverable through the copier template: a pinned tool, a mise task, a gitignore entry |
| Nice to have: a named branch, tag or commit | Read the dependency's code at the version in use |
| Nice to have: several refs of one repo side by side | Compare the current and target versions during an upgrade |
| Nice to have: refs matched to lock files automatically | No drift between the dependency and its reference clone |
| Nice to have: shared cache across repos | Less disk and network on a developer machine, ideally linked into each repo so it stays inside the agent's workspace |

A manifest entry either **tracks** a branch, which refresh moves, or **pins** a tag or commit, which refresh leaves alone.

**Hard criteria:** a license compatible with use as an installed tool; no repo content runs on clone or update (no hooks, build steps or install scripts, and no submodules by default); installable as a pinned tool through mise; works on Linux in a cloud session; bulk refresh; a committed manifest with per-entry track or pin.

**Preferences:** several refs side by side; shallow or blobless clones; lock-file matching; a shared cache; Renovate support for pins; maintenance and maturity.

## Verdict

**Adopt west (Zephyr's meta-tool) as the clone manager, inside the `reference-repos` skill moved into this repo's skills package and extended with borrowed safety rules and a Renovate rule for pins.** No skill or agent-oriented tool covers the need. Of the multi-repo tools, the search ranked vcs2l first, but follow-up tests of the released versions (run after the search, outside it; see Limitations) showed west handling every scenario the need cares about with no code of our own, while vcs2l needs a custom refresh task and has an open crash in its setup path. The pieces:

1. **West as configured:** a `west.yml` manifest with `clone-depth: 1` per project, `revision:` set to a branch (tracked) or a tag or commit (pinned), and no `import:` or `west-commands:` entries, so nothing from a cloned repo is loaded. In west 1.5.0, `.west/` is created next to the manifest directory, so the manifest lives at `.reference-repos/manifest/west.yml`, committed through a gitignore exception (`/.reference-repos/*` with `!/.reference-repos/manifest/`), and the clones land in `.reference-repos/<name>/`.
2. **mise tasks:** setup runs `west init -l manifest` inside `.reference-repos/` when `.west/` is missing, then `west update`; refresh runs `west update`, optionally one process per project in parallel (`west list -f '{name}' | xargs -P <n> -I{} west update {}`), since west has no parallel option.
3. **Safety rules from clonedeps:** HTTPS URLs only (no `file://`, SSH or embedded credentials); confirm a ref with `git ls-remote` before adding it; never run anything from a clone.
4. **Pins kept current by Renovate:** a custom regex manager on the manifest's `revision:` fields with the `git-tags` datasource, grouped with the dependency it mirrors, keeps a pinned tag in step with the lock file in the same PR.
5. **Edits blocked, not just discouraged:** Claude Code permission rules denying `Edit` and `Write` under `.reference-repos/`.
6. **Several refs side by side:** a second project for the same repository under another name and path. `west update --name-cache` can share objects across workspaces if disk use ever matters.

Relicensing the skill from GPL-2.0-or-later to this repo's Apache-2.0 is its author's call, and the move records it.

The runner-up is vcs2l with a refresh task of our own (`git fetch --depth 1 origin <branch>` then `git reset --hard FETCH_HEAD` per tracking clone, which a follow-up test confirmed). Revisit it if its setup and refresh bugs are fixed upstream and west's workspace layout becomes a burden. opensrc is worth borrowing from if npm lock-file matching on demand matters more than a committed manifest.

## Candidates and matrix

Ranked shortlist:
1. **west (Zephyr's meta-tool):** meets the hard criteria, keeps clones at depth 1, follows rewritten history, and adds a shared object cache. Its costs are a workspace layout (`.west/` beside the manifest, commands run from inside the workspace) and sequential updates. It moved up from second after follow-up tests of the released versions.
2. **vcs2l:** meets every hard criterion, and its pull skips pinned clones by design, with parallel workers. Re-running setup crashes or fails, and refresh stalls after an upstream force-push, so it needs a task of our own. Fixed upstream bugs would move it back up.
3. **opensrc:** the closest tool built for agents. On-demand, cached per version, npm lock-file aware. It has no committed manifest, no bulk refresh, strips `.git`, and silently falls back to the default branch. A manifest and refresh command would move it up.
4. **mani:** worktrees per project and parallel commands, but full clones and branch-only refs by default.
5. **vcspull:** the best hand-written manifest (`rev`, `shallow`, `depth`, parallel sync), but its git layer always updates submodules recursively.
6. **ghq:** a shared root by host and path, with shallow and branch options, but no refs in its import list.
7. **tsrc, peru:** each fails one core need (tsrc can't shallow-clone a pinned commit; peru keeps full mirror clones and checks out plain files).

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [vcs2l](https://github.com/ros-infrastructure/vcs2l) | build on (runner-up) | Apache-2.0 (`LICENSE` at 80da3932) | Meets every hard criterion; setup and refresh need a task of our own |
| [west](https://github.com/zephyrproject-rtos/west) | adopt | Apache-2.0 (`LICENSE` at cc7941cf) | Handles setup, refresh, rewrites and pin moves as configured; sequential updates |
| [opensrc](https://github.com/vercel-labs/opensrc) | borrow ideas | Apache-2.0 (root `LICENSE` at b51de608; `packages/opensrc/package.json:42`, `cli/Cargo.toml:6`) | Per-version cache and lock-file lookup; no manifest or refresh |
| [clonedeps skill](https://github.com/alvinunreal/oh-my-opencode-slim/tree/main/src/skills/clonedeps) | borrow ideas | MIT (`LICENSE` at e0a51336) | The best safety rules of any skill found |
| [mani](https://github.com/alajmo/mani) | reject | MIT (`LICENSE` at ca816095) | Full clones by default; no pin by commit |
| [vcspull](https://github.com/vcs-python/vcspull) | reject | MIT (`LICENSE` at 8a430c6f; libvcs `LICENSE` at 14a23821) | Always updates submodules (via libvcs) |
| [ghq](https://github.com/x-motemen/ghq) | borrow ideas | MIT (`LICENSE` at b9273dd1) | Shared root layout by host and path |
| [tsrc](https://github.com/your-tools/tsrc) | reject | BSD-3-Clause (`LICENSE` at 99b44249) | No shallow clone of a pinned commit; separate manifest repo |
| [peru](https://github.com/buildinspace/peru) | borrow ideas | MIT (`LICENSE` at c50be018) | `reup` writes resolved revisions back to the manifest; full mirror clones |
| [gitman](https://github.com/jacebrowning/gitman) | reject | MIT (`LICENSE.md` at b0f9805c) | The developer found it no better than vcs2l |
| [Google repo](https://gerrit.googlesource.com/git-repo) | reject | Apache-2.0 (`LICENSE` at 46e9866c) | XML manifest in its own repo; launcher updates itself at run time (docs only) |
| [btca-local skill](https://github.com/davis7dotsh/better-context) | reject | MIT (`LICENSE.md` at 864e5ba4) | No safety rules; clones to a home-directory sandbox |
| [orf/git-workspace](https://github.com/orf/git-workspace) | reject | MIT (`LICENSE` at eda0a993) | Syncs whole forge accounts, not chosen external repos |
| [repomix](https://github.com/yamadashy/repomix), [gitingest](https://github.com/coderamp-labs/gitingest) | reject | MIT (`LICENSE` at e696384d, 4e259a02) | Pack a repo into one prompt file; not a maintained clone |
| [Context7](https://github.com/upstash/context7), DeepWiki, Sourcegraph | reject | Context7 MIT (`LICENSE` at c7f80ce5); others hosted | Hosted services; fail "works offline" (docs only) |
| git submodules | reject | (git) | Gitlinks committed to the consumer repo affect every clone and tool (docs only) |
| mrepo, mg, gz-git, ggg, wsfold, grove, codingapi/git-workspace | reject | MIT where read (`LICENSE` at f5fb26ab, 816839d5, 350fefbf, f76c1a10, b032faf9) | Too young for a template-wide dependency |

Matrix (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified):

| Criterion | vcs2l | west | opensrc | mani | vcspull | ghq |
|---|---|---|---|---|---|---|
| License (hard) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| No repo content runs, no submodules (hard) | ✓ | ◐ extension commands only if declared | ✓ | ✓ | ✗ | ✓ |
| Pinned install via mise (hard) | ✓ pipx | ✓ pipx | ✓ npm | ✓ | ✓ pipx | ✓ |
| Linux cloud session (hard) | ✓ | ✓ | ? | ✓ | ✓ | ✓ |
| Bulk refresh (hard) | ◐ parallel, but stalls on rewritten history | ✓ sequential; ⊕ parallel per project | ✗ | ◐ via user tasks | ✓ | ✓ |
| Committed manifest, track or pin (hard) | ✓ | ✓ | ✗ | ◐ branch only | ✓ | ✗ |
| Several refs side by side | ◐ separate clones | ✓ separate projects; `--name-cache` shares objects | ✓ per version | ✓ worktrees | ◐ | ✗ |
| Shallow or blobless | ✓ | ✓ | ✓ | ⊕ custom clone | ✓ | ✓ |
| Lock-file matching | ⊕ Renovate | ⊕ Renovate | ◐ npm only | ✗ | ⊕ Renovate | ✗ |
| Shared cache | ✗ | ✓ | ✓ global | ✗ | ✗ | ✓ |
| Renovate support for pins | ⊕ | ⊕ | ✗ | ⊕ | ⊕ | ✗ |

**Blends considered:** vcs2l plus a refresh task of our own (works, but it's code to maintain, and setup still needs a workaround for the `--skip-existing` crash); vcs2l with a shared cache made of a home-directory clone root and per-repo links (more moving parts, and cloud sessions can't use it); vcs2l plus opensrc (two caches with different rules; only npm gains lock-file matching). West wins because every addition around it is configuration or skill text: no second tool and no code of our own.

**Scenario walk (finalists: west, vcs2l plus a refresh task, opensrc):**
- *Fresh cloud session:* west restores with one setup task (`west init -l manifest` when `.west/` is missing, then `west update`). vcs2l restores with `vcs import --shallow` on an empty directory. opensrc fetches lazily on first use but restores nothing named in the repo.
- *Re-running setup on a machine that already has clones:* west is a no-op. vcs2l's `--skip-existing` crashes, so setup has to clone only the missing entries itself.
- *Dependency upgrade PR:* with the Renovate rule, the pinned revision moves in the same PR as the dependency, and the next update checks out the new tag, with either tool. opensrc follows npm lock files only.
- *Comparing two versions:* a second west project or vcs2l entry for the same repository; opensrc caches each version natively.
- *Upstream force-pushes a tracked branch:* west follows it; `vcs pull` fails and the clone stays stale until the custom refresh task runs; opensrc has no refresh.

## Limitations checked in source

- vcs2l clones submodules only with `--recursive`, which is off by default: *verified in source* (`vcs2l/commands/import_.py:76-80`, `vcs2l/clients/git.py:504-518` at 80da3932).
- vcs2l fetches exactly the pinned tag, commit or branch with `--depth 1`, and offers a blobless clone instead: *verified in source* (`vcs2l/clients/git.py:345-359,429-476`; `vcs2l/commands/import_.py:62-73` at 80da3932).
- `vcs pull` runs a plain `git pull` and warns rather than fails on a detached (pinned) clone: *verified in source* (`vcs2l/clients/git.py:635-660` at 80da3932). *Verified by running* vcs2l 1.1.7 (the latest release) against local test repos: a tracking clone fast-forwards to the branch's newest commit, a pinned clone stays put, and each pull adds the new commits to the shallow history rather than keeping depth 1.
- When upstream rewrites a tracked branch's history, `vcs pull` fails with git's "Need to specify how to reconcile divergent branches" and the clone stays stale: *verified by running* 1.1.7 (git 2.53, no `pull.ff` or `pull.rebase` set). The portabase skill's "fast-forward only" is true only in the sense that pull refuses anything else.
- Re-running `vcs import --shallow` on an existing tracking clone fails: the depth-1 fetch's refspec is rejected as non-fast-forward, and the clone isn't advanced: *verified by running* 1.1.7, and in source (`vcs2l/clients/git.py:345-359,375-397` at 80da3932). The same command does move an existing pinned clone to a new tag: *verified by running* 1.1.7.
- `vcs import --shallow --skip-existing`, portabase's setup task, crashes once clones exist (`AttributeError` in `_check_version_type` in 1.1.7; in upstream source, `checkout_version` becomes `None` and the shallow path reaches `assert False`): *verified by running* 1.1.7 and in source (`vcs2l/clients/git.py:300-301,345-359` at 80da3932). The bug is reported upstream ([dirk-thomas/vcstool#214](https://github.com/dirk-thomas/vcstool/issues/214), open).
- `--blobless-clone` exists in upstream source but not in the released 1.1.7: *verified by running* `vcs import --help` on 1.1.7.
- vcs2l runs jobs in parallel, defaulting to one worker per CPU: *verified in source* (`vcs2l/commands/command.py:64-72` at 80da3932).
- vcs2l has no lock-file, shared-object or worktree support: *verified in source* (`grep -rniE "lockfile|lock\.json|\.lock\b|uv\.lock"`, `grep -rnE -- "--reference|alternates|--shared"` and `grep -rn worktree` over `vcs2l/`, no matches, at 80da3932).
- West shares objects across workspaces through `--name-cache` and `--path-cache`, sets clone depth per project, and initializes submodules only for projects that declare them: *verified in source* (`src/west/app/project.py:1363-1425,1735-1742,2055-2075`; `src/west/manifest.py:823,952` at cc7941cf).
- Upstream west source can make the repo root its workspace with `west init -l --manifest-path` (`src/west/app/project.py:274-282,477-482` at cc7941cf), but the released 1.5.0 doesn't have that option and creates `.west/` next to the manifest directory: *verified by running* `west init -h` on 1.5.0.
- West 1.5.0, with the manifest at `.reference-repos/manifest/west.yml` and `clone-depth: 1`, against local test repos: re-running `west update` exits 0 and changes nothing; a tracking clone advances to the newest commit and stays at depth 1; it follows an upstream history rewrite; a pin moved in the manifest checks out the new tag; no submodule or hooks configuration appears in the clones; with upstream unreachable, update exits 1 and existing clones stay readable. Commands must run from inside `.reference-repos/`, because west looks upward for `.west/`. *Verified by running* (follow-up test, after and outside the search).
- West has no parallel update: a `-j` option shipped in a 0.12 alpha and was reverted after Windows failures ([west#527](https://github.com/zephyrproject-rtos/west/issues/527)); [west#713](https://github.com/zephyrproject-rtos/west/pull/713) (joblib) has been open since 2024, with a maintainer preferring an asyncio redesign; [west#755](https://github.com/zephyrproject-rtos/west/pull/755) closed as outdated. *Docs only* (issue and PR threads).
- Running one `west update <project>` per project in parallel works: every project ended current and `west status` stayed clean, and against six GitHub repos a refresh took 0.6 s six at a time against 1.7 s sequentially. *Verified by running* 1.5.0 (follow-up test, after and outside the search).
- opensrc tries tags `v<version>` and `<version>`, then silently clones the default branch: *verified in source* (`packages/opensrc/cli/src/core/git.rs:37-67` at b51de608).
- opensrc deletes `.git` after cloning, so no history or blame: *verified in source* (`packages/opensrc/cli/src/core/git.rs:148-151,198,247` at b51de608).
- opensrc reads versions from npm lock files only, and has no refresh command: *verified in source* (`packages/opensrc/cli/src/core/version.rs:92-98`; `packages/opensrc/cli/src/main.rs:78-94` at b51de608).
- opensrc caches per version under `~/.opensrc`, or `$OPENSRC_HOME`: *verified in source* (`packages/opensrc/cli/src/core/cache.rs:49-57,81` at b51de608).
- libvcs, under vcspull, always runs `git submodule update --init --recursive` on clone and update: *verified in source* (`src/libvcs/sync/git.py:433-440,710` at 14a23821).
- mani clones full history unless a project supplies its own `clone` command, and supports worktrees per project: *verified in source* (`core/exec/clone.go:132-199,264-287` at ca816095).
- tsrc refuses `--shallow` with a pinned commit: *verified in source* (`tsrc/cloner.py:37-42` at 99b44249).
- peru keeps full `git clone --mirror` copies and checks out plain files: *verified in source* (`peru/resources/plugins/git/git_plugin.py:45,87-94` at c50be018).
- ghq makes shallow clones, single branches and submodules opt-in, and roots clones at `$GHQ_ROOT`: *verified in source* (`vcs.go:109-115,148-149`; `local_repository.go:18` at b9273dd1).
- Renovate can update git tags in a custom manifest through a regex manager: *docs only* ([custom managers](https://docs.renovatebot.com/modules/manager/regex/), [git-tags datasource](https://docs.renovatebot.com/modules/datasource/git-tags/)).
- Claude Code permission rules can deny edits under a path: *docs only* ([permissions](https://code.claude.com/docs/en/permissions)).

Verified:
- every license in the candidate table, read from the named file at the named commit;
- the source claims above tagged *verified in source*;
- the behavior tagged *verified by running*, in follow-up tests of the released west 1.5.0 and vcs2l 1.1.7 against throwaway repos, run after the search and outside it.

Could not verify:
- opensrc's binary on Linux cloud sessions (not run);
- West's extension commands loading only from manifest-declared projects (`src/west/manifest.py:76,234` define the field; the loading path wasn't traced);
- tsrc's need for a separate manifest repository, Google repo's self-updating launcher and git submodules' effect on consumers (docs only);
- the young tools in the last candidate row, beyond their licenses;
- skills seen only through catalog mirrors (jj-clone-third-party, opencode-mirror, project-references, dependency-source-research, upstream-source-research), not evaluated;
- alternativeto.net, unavailable (below).

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | git (shallow and blobless clones, worktrees, `--reference`, submodules); mise tasks and pipx installs; Renovate regex manager and git-tags datasource; installed dependency source in `.venv` and `node_modules`; Claude Code permission rules |
| Earlier notes and decisions | searched | `docs/prior-art/` (one unrelated note); no decision records on this topic |
| GitHub repository search | searched | "manage multiple git repositories manifest yaml", "multi-repo manifest", "repo manager git", "repos yaml clone", "reference repositories", "dependency source agents", "third-party clones agents", "repos lockfile", "git dependencies lock" |
| GitLab and Codeberg search | searched | GitLab: "multi repo manifest", "repositories manifest", "repo tool"; Codeberg: "multi repo", "manifest repos", "reference clones" |
| GitHub topics | searched | `multi-repo`, `multirepo`, `git-repositories`, `repository-management` |
| GitHub code search | searched | READMEs naming opensrc and better-context; `marketplace.json` files naming "clone" |
| npm | searched | "multi repo manifest", "clone repositories config", "dependency source code agents" |
| PyPI | searched | web search `site:pypi.org` "manage multiple git repositories yaml config sync clone" |
| crates.io | searched | "multi repo", "repo manifest", "git workspace" |
| Language registries | searched | Go via web search ("Go CLI clone and update many git repositories from config file"); others excluded: the need names no other language |
| Cross-language equivalents | searched | vcstool-style tools in Go (mani, mrepo, gz-git), Rust (git-workspace, gitgrip) and Python (vcspull, west, tsrc) |
| Awesome lists | searched | "awesome list multi-repo management tools git submodule alternatives"; dfetch's alternatives page (49 tools) |
| alternativeto.net | unavailable | HTTP 404 for the myrepos and ghq pages, after a retry with a second page |
| General web search | searched | "tool clone multiple git repositories from YAML manifest pinned versions", "multi-repo manifest tool shared cache deduplicate clones", "alternatives to myrepos", "multi-repository tool lock file pinned commit SHA", "git clone reference mirror cache tool" |
| Hosted services | searched | Context7, DeepWiki (from the developer's seed list), Sourcegraph (found in Anthropic's plugin marketplace) |
| Skill directories | searched | skills.sh: "reference repos", "clone repo", "dependency source", "library source", "opensrc", "upstream source", "agent reference clone skill" |
| Claude Code plugin marketplaces | searched | Anthropic's official marketplace scanned for clone, source, repository and dependency plugins |
| MCP Registry | searched | "clone", "repository", "docs", "source", "git clone" |
| Anthropic's skills repo | searched | skill list read; none relevant |
| Awesome lists for agent skills | searched | web: "Claude Code skill keep local clones of dependency repositories for reference read-only" |
| GitHub topics for agent skills | searched | `agent-skills`, `claude-skills`, `claude-code-plugin` with "clone", "source", "reference" |

## Snowball rounds

- **Round 1** (the searches above): vcs2l (inherited), vcspull, opensrc, west, tsrc, mani, gita, ghq, myrepos, gitman, Google repo, peru, git submodules, git-aggregator, wsfold, grove, ggg, btca-local, clonedeps, jj-clone-third-party, opencode-mirror, repomix, gitingest, Context7, DeepWiki.
- **Round 2** (alternatives to ghq and opensrc, several refs side by side): gogh, opensrc-mcp, git worktrees.
- **Round 3** (Go equivalents; "third-party", "mirror", "sandbox" vocabulary): mrepo, mg, gz-git.
- **Round 4** ("lock file" vocabulary): codingapi/git-workspace, kas.
- **Round 5** (git-workspace alternatives): orf/git-workspace, git-fastclone, autogit.
- **Round 6** (reference-mirror caches): git-autoshare, which addresses only the shared-cache nice-to-have. No new serious candidate, so the search stopped. The round cap wasn't reached.

## Refresh trigger

When a west release adds `--manifest-path` (the manifest can then move out of `.reference-repos/`) or parallel update, when vcs2l releases fixes for its setup and refresh bugs, when west stops being maintained, or on 2027-10-19, whichever comes first.
