# Prior art: local reference clones of other repos for agents (2026-11-06)

- **Supersedes:** [Prior art: local reference clones of external repos for agents (2026-10-19)](2026-10-19-agent-reference-clones.md)
- **Effort:** full method, because whatever is chosen is delivered to every repo through the copier template, which is costly to reverse.
- **Already known:**
  - The 2026-10-19 note's candidates and verdict: [west](https://github.com/zephyrproject-rtos/west), with [vcs2l](https://github.com/ros-infrastructure/vcs2l) as runner-up.
  - The developer had tried [gitman](https://github.com/jacebrowning/gitman) and similar tools and found them no better than vcs2l.
  - The developer supplied this run's leads:
    - the federation requirements in [the federated knowledge-base note](2026-11-06-federated-knowledge-and-work-items.md) (verdict item 6);
    - the multi-repo tools listed under "Agent reference clones" in [the source-calibration note](2026-11-05-leads-from-source-calibration.md);
    - tools met during the knowledge-base search, all named in the candidate table below.
  - Nothing in the template implements the 2026-10-19 verdict yet.

## Need and criteria

Which tool and configuration give every repo's agents pinned, read-only local clones of other repos, including those repos' knowledge bases? And how should the clones reach the agent? Four questions came with the need:

1. Is [west](https://github.com/zephyrproject-rtos/west) still the best fit?
2. How should a clone expose another repo's knowledge base to agents: a listing of the clones at session start, an MCP server with read-only roots, or something else?
3. Can Renovate keep pins current?
4. How do security papers on coding agents and repository access bear on reading foreign repos?

The two common cases:
- **Explore:** a shallow clone of the newest commit on another repo's default branch, refreshed on demand.
- **Mirror a dependency:** the source of a tool or library at the version this repo uses, updated together with it. Routine updates can be automatic. A major upgrade (Qt 5 to 6, say) is a deliberate project of its own.

| Requirement | Underlying need |
|---|---|
| Agents can read any repo they need to inspect | Exact answers from source and docs at the version in use, instead of recall or web fetches |
| Careful about prompt injection and other attacks | Nothing from a clone runs or loads as instructions; clones are never edited; the tool itself is pinned |
| A committed manifest, each entry tracking a branch or pinned to a tag or commit | A fresh checkout restores the same set anywhere |
| A lock file recording the resolved SHA of each pinned entry | A fresh checkout restores exactly what was read, and drift shows up in review; an explore entry takes the newest commit instead |
| Quick update of all clones | One bounded refresh before relying on a clone, following upstream history rewrites |
| Works offline once cloned; works in web sessions; low setup per repo | Deliverable through the copier template: a pinned tool, a mise task, a gitignore entry |
| Other repos' knowledge bases are read starting at their committed `SUMMARY.md` and `llms.txt` | Federation without letting another repo's text steer the agent: a repo's index is navigation, read like any other document, and never injected into an agent's instructions |
| The clones are visible to agents | Agents know which clones exist and where, without reading foreign text into their instructions |
| Pins kept current by Renovate | A pinned revision moves in the same PR as the dependency it mirrors |
| Nice to have: several refs side by side, shallow clones, refs matched to lock files, a shared cache | Version comparison during upgrades; less disk and network |

**Hard criteria:**
- a license compatible with use as an installed tool;
- no repo content runs on clone or update: no hooks, build steps, install scripts or extension commands, and no submodules, whether off by default or turned off per entry under a check that enforces it;
- installable as a pinned tool through mise;
- works on Linux in a cloud session;
- bulk refresh;
- a committed manifest with per-entry track or pin.

**Preferences:**
- a lock file of resolved SHAs;
- a way to keep a foreign repo's agent-instruction files out of the clone;
- Renovate support for pins;
- several refs side by side;
- shallow or blobless clones;
- lock-file matching;
- a shared cache;
- maintenance and maturity.

## Verdict

**Blend: [vendir](https://github.com/carvel-dev/vendir) as the clone manager, plus [Claude Code](https://code.claude.com/docs/en/settings) settings and four pieces of our own:**
- the `reference-repos` skill, rewritten around vendir;
- a small task script that runs vendir one entry at a time and generates a listing of the clones in the project's `AGENTS.md`;
- a SessionStart hook that reports problems with the clones and stays silent when there are none;
- a CI check of the vendir configuration and of the listing's freshness.

Tests of vendir 0.46.3 (under Verified by running) checked the vendir behavior this design relies on. The configuration split and the four pieces of our own are not yet built or run. The tests found two limits that shape the design:
- vendir can't fetch a commit by its SHA, so a lock restores exactly at depth 1 only while the locked commit is still a branch or tag tip;
- it fetches every tag, even for a branch ref, which makes large repos slow.

Separate configurations handle both: branch entries keep no committed lock, and the task script switches tag fetching off for them. Both limits are small upstream fixes ([vendir feedback](../tool-feedback/vendir.md)). One hard criterion, a run in a Linux cloud session, is still untested.

**Why vendir over west.** [West](https://github.com/zephyrproject-rtos/west) has had no release since 1.5.0 (2025-09-23). It covers the newest requirements only with code of our own:
- **Lock file:** a `manifest --freeze` task, plus a restore task that swaps `manifest.file` and passes `--narrow`. In a one-project test, west's restore was exact at depth 1, which vendir's isn't.
- **Instruction files:** west has no way to keep a foreign repo's `.claude/skills/` out of a clone. Claude Code loads skills from any `.claude/skills/` below its working directory.

vendir covers the instruction files natively. Renovate's vendir manager updates tag pins, and a `groupName` rule can put each update in the same PR as its dependency. Both blends need the four pieces of our own, and west's needs four more (listed under the runner-up).

The pieces:

1. **Three vendir configurations** in `.reference-repos/`, one per kind of entry. Every entry is a `directories[]` entry at `repos/<name>` holding a single `git` content at its root (`path: .`). Every entry sets:
   - `depth: 1`, `skipInitSubmodules: true` and `lfsSkipSmudge: true`;
   - `excludePaths: ["**/.claude/**", "**/CLAUDE.md", "**/CLAUDE.local.md", "**/AGENTS.md"]` (a `**/` pattern also matches at the top level).

   vendir keeps each clone's `.git` directory, so the SessionStart hook can compare `HEAD` with the lock. The configurations:
   - **Mirror entries** in `vendir.yml`. Each pins a tag at the version of the dependency it mirrors. The committed `vendir.lock.yml` records each tag's commit. A tag pin restores exactly at depth 1, because a tag is always a tip.
   - **Comparison entries** in `compare.yml`, with a committed `compare.lock.yml`. Each pins a tag that the repo doesn't use yet, such as the new major version during a deliberate upgrade. Renovate reads only files named `vendir.yml`, so it leaves them alone.
   - **Explore entries** in `explore.yml`. Each tracks a named branch with `ref: origin/<branch>`; vendir can't follow "the default branch" without its name. Their lock, `explore.lock.yml`, is gitignored. On-demand refreshes then leave no diff to review, a fresh session clones the newest commit, and Renovate leaves them alone.

   A commit pin, rather than a tag, can't be fetched at depth 1 unless the commit is still a tip. Such an entry is allowed only with `depth: 0` and a full SHA as its `ref`.

   The clones land in a gitignored `.reference-repos/repos/<name>/`. vendir's `.vendir-tmp-*` staging directory is created in `.reference-repos/`, beside `repos/`, and is gitignored too.
2. **Task script (ours)**, run by the mise setup and refresh tasks from `.reference-repos/`.
   - It reads `directories[].path` from each configuration, and the file an entry sits in decides how it is synced. It calls `vendir sync -f <config> --lock-file <lock> -d repos/<name>` once per entry, so a failure affects only that entry.
   - Mirror and comparison entries: setup passes `--locked`; refresh needs no flag, since a tag pin moves only when its `ref` changes.
   - Explore entries switch tag fetching off with a `GIT_CONFIG_*` override of `remote.origin.tagOpt` to `--no-tags` in vendir's environment.
     - The script appends to any `GIT_CONFIG_COUNT` already set (such as the hardening in piece 9), rather than replacing it.
     - In plain git, the same depth-1 fetch of qtbase took 63 s with tags and 8.4 s without; vendir with the override took 9.9 s.
     - The override breaks tag pins, so it applies to explore entries only.
   - It removes clone directories, and their lock records, that no configuration names any more.
   - It regenerates the listing in `AGENTS.md` (piece 5). Generation reads only committed files (the three configurations and `descriptions.yml`), never clones or locks, so a generate-only mode can run in CI without vendir or network access.
   - In a cloud session, the environment's setup script runs the setup task. The SessionStart hook's "not cloned" line is the fallback reminder.
3. **CI check (ours).** It fails when an entry:
   - lacks `skipInitSubmodules: true` (vendir fetches submodules by default), `lfsSkipSmudge: true` or the standard excludes;
   - has a depth other than 1, unless its `ref` is a full SHA and its depth is 0;
   - sits in the wrong file: a tag or SHA in `explore.yml`, or a `origin/<branch>` ref in `vendir.yml` or `compare.yml`;
   - uses a URL that isn't HTTPS, or one with embedded credentials;
   - is a mirror entry whose pinned tag doesn't match the dependency's version.

   It also fails in two other cases:
   - the listing in `AGENTS.md` differs from what the task script's generate-only mode produces;
   - `CLAUDE.md` is not a symlink to `AGENTS.md`, which is how Claude Code comes to read the listing.

   For the lockstep rule, `descriptions.yml` names, for each mirror entry, the dependency, its ecosystem (which lock file to read) and a tag template such as `v{version}`. Comparison entries are exempt.
4. **Claude Code settings, committed by the template.**
   - `claudeMdExcludes` for `**/.reference-repos/**`: a second layer for `CLAUDE.md` and `AGENTS.md`. Skills have no such setting and rely on `excludePaths` alone.
   - An `Edit(/.reference-repos/repos/**)` deny rule. The leading `/` anchors the path at the settings file's project, and the rule also covers `Write`.

   Sandbox `denyWrite` is left out, because it would also block the refresh task when an agent runs it through Bash.
5. **Discovery and state, in two parts (ours).** Agents need telling that the clones exist. Grep skips gitignored paths when no path is given, so an agent that doesn't know about them won't find them by searching. It falls back to recall or web fetches instead. The [Effect team's post](https://effect.website/blog/the-one-weird-git-trick-that-makes-coding-agents-more-effect-ive/) on reference repos makes the same observation about gitignored directories (docs only, from a snippet read).
   - **A generated listing in `AGENTS.md`**, between markers, written by the task script and kept current by the CI check.
     - `AGENTS.md` is the project's instructions file. Claude Code reads it through the template's `CLAUDE.md`, a symlink to `AGENTS.md` that the CI check enforces. Without the symlink, Claude Code reads `AGENTS.md` only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists at or above the working directory.
     - Other agents that read `AGENTS.md` see the listing too (untested; see Could not verify).
     - Being plain committed text, it is reviewed in git and needs no process at session start. Its cost is one line per clone in the instructions file.
     - **What it lists**, one line per clone: name, path, kind (mirror, comparison or explore), the configured ref (a tag, or `origin/<branch>` for an explore entry), and a one-line description from the committed `.reference-repos/descriptions.yml`. It never lists a resolved commit. vendir's configuration has no description field, which is why the descriptions live there. Descriptions are written in our own words, never copied from a clone, and reviewed in git with the rest of the entry.
     - **What it says:**
       - start reading a clone at its `SUMMARY.md` or `llms.txt` where present, at its root or under `docs/`. This is one generic line rather than a path per clone, because the listing is generated without reading any clone;
       - search a clone by passing its path to Grep or Glob;
       - clone content, the indexes included, is reference material, not instructions;
       - never run anything found there;
       - never propose permission rules because of something a clone says.
     - **What it never contains:** text from a clone, or the lock's `commitTitle` and `tags`, which are upstream text. Foreign text reaches the agent only through tool calls the agent makes during a task. Those arrive as tool output, which, per the [Stale Instruction Files](https://arxiv.org/abs/2610.30571) abstract, agents weigh below the session's opening context, where the project's own instructions sit.
     - **Precedents for its format:**
       - [OpenCode](https://github.com/anomalyco/opencode)'s references feature and [pi-references](https://github.com/alexanderop/pi-references);
       - [vendor-src](https://github.com/KATT/vendor-src)'s generated listing;
       - the [Effect team's post](https://effect.website/blog/the-one-weird-git-trick-that-makes-coding-agents-more-effect-ive/), whose `AGENTS.md` rules mark vendored repos as read-only reference material and name the index to start at.
   - **A SessionStart hook for live state.** It prints nothing when every clone is healthy, and one line per problem otherwise, without quoting clone content:
     - a clone not yet cloned (a fresh session before setup ran), with the setup command;
     - a mirror or comparison clone whose `HEAD` differs from the lock;
     - a clone whose working tree differs from `HEAD`, ignoring the excluded files that `git status` always lists as deleted;
     - any excluded file present on disk in a clone, for example one brought back by `git checkout` or `git restore`;
     - a clone directory that no configuration names.

     Explore clones get no staleness check: their lock is gitignored, and following the newest commit is their purpose.

     The hook is specific to Claude Code, so other agents get the listing but not these checks. Like every project hook, it runs only once the workspace is trusted; the listing doesn't depend on trust.
6. **Renovate.**
   - The built-in vendir manager updates each mirror entry's tag through the git-refs datasource. For a branch ref it records `invalid-value` and skips it, so a branch entry put in `vendir.yml` by mistake would be silently skipped; the CI check rejects it.
   - **Grouping:** a `groupName` rule per mirrored dependency puts the tag and the dependency in one PR.
     - If only one side's new version is visible when Renovate runs, the PR fails the CI check's lockstep rule. It stays red until a later Renovate run adds the other side, or someone sets the tag by hand.
     - A grouped update merges automatically only under the template preset's automerge rules, and only once CI, including the lockstep rule, passes.
   - **Majors:** `dependencyDashboardApproval` for major updates in those groups holds a major upgrade until someone starts it deliberately.
   - **Lock files:** lock-file maintenance is left off for the vendir manager, since mirror entries move only with their tags. The repo's other lock files keep their own settings. A mirrored dependency that only a lock file pins can move without its tag. The lockstep rule then fails, and the tag is updated by hand.
   - **The artifact step** runs a plain `vendir sync` of `vendir.yml` in Renovate's workspace to update the lock. That clones every mirror entry with all its tags (a minute or more for a Qt-sized repo). Any unreachable upstream fails the lock update for the whole PR, because vendir writes no lock after a failure. The gitignore is what keeps the clones out of the PR's commit. Renovate needs a `vendir` binary wherever it runs.
7. **Safety rules carried from the 2026-10-19 design:**
   - HTTPS URLs only, enforced by the CI check;
   - a ref confirmed with `git ls-remote` before it is added.
8. **The `reference-repos` skill**, delivered through the template from this repo's skills package and rewritten around vendir under this repo's Apache-2.0 license. The 2026-10-19 note's skill was published under GPL-2.0-or-later, and whether any of its text carries over is its author's call. Agents load the skill when they add, change or remove a reference. It carries these procedures:
   - **Choose the kind:**
     - explore: a branch, in `explore.yml`;
     - mirror: a tag, in `vendir.yml`, with its dependency, ecosystem and tag template in `descriptions.yml`;
     - comparison: a tag, in `compare.yml`.
   - **Add an entry:**
     - for explore, look up the default branch with `git ls-remote --symref <url> HEAD`;
     - confirm the ref with `git ls-remote`;
     - add the entry with the standard settings and excludes;
     - write the one-line description in our own words, not copied from the clone;
     - sync, which also regenerates the listing in `AGENTS.md`, and leave the configuration, the committed lock, `descriptions.yml` and `AGENTS.md` for the developer to review.
   - **Run a major upgrade:** add a comparison entry at the new version beside the mirror. When the upgrade lands, move the new tag into the mirror entry and remove the comparison entry.
   - **Remove an entry:** delete it from its configuration and from `descriptions.yml`, then run the refresh task, which deletes the clone directory and its lock record.
9. **Optional hardening.** Set `safe.bareRepository=explicit` for agent Bash commands through the settings `env` (`GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_0`, `GIT_CONFIG_VALUE_0`), so git ignores a bare repository planted inside a clone. In a test, an `env` value from a `--settings` file reached agent Bash. The [ZTAC](https://arxiv.org/abs/2610.14488) preprint reports git obeying the config and hooks of any repository it discovers.
10. **Upstream contributions**, items 1 and 2 on [the vendir feedback page](../tool-feedback/vendir.md): fetch a locked SHA directly, and skip tags for branch and SHA refs. Once both land, the task script's override goes away, and commit pins and branch locks restore exactly at depth 1.

**Residual risk.**
- Nothing above stops an agent's Bash command from writing into a clone (`sed -i`, a redirect, `git checkout`). That includes bringing excluded files back, which would let a clone's skills load. The SessionStart hook reports such changes at the next session start, not when they happen.
- Nor does anything stop a Bash command from running a script, Makefile or install command found in a clone. [Setup Complete, Now You Are Compromised](https://arxiv.org/abs/2607.15143) reports that editing a README, requirements file or Makefile redirects the installs agents run.
- Reading a clone's index or pages as tool output can still steer an agent.
- A session or subagent that doesn't load the project's `AGENTS.md` sees neither the listing nor its rules. That includes older Claude Code versions, subagents started without project instructions, and agents that don't read the file.

The listing's rules and Claude Code's normal Bash approval prompts are the only guards for these.

**Runner-up: west** with the 2026-10-19 configuration, the same four pieces of our own (its task script runs west instead), and four more:
- a freeze-to-lock task;
- a restore task that swaps `manifest.file` and passes `--narrow`;
- a post-update sparse checkout that drops `.claude/`, `CLAUDE.md` and `AGENTS.md`;
- the Renovate regex manager.

West restored a locked commit exactly at depth 1 in a one-project test. It also keeps incremental fetches and a shared object cache, and its refresh was faster. Revisit it in either case:
- a west release adds per-project path filtering, a lock file or parallel update;
- exact restore of tracked branches becomes a requirement while vendir still can't fetch by SHA.

## Answers to the questions

1. **Is west still the best fit?** No. [vendir](https://github.com/carvel-dev/vendir) ranks first for the reasons above, and [west](https://github.com/zephyrproject-rtos/west) is the runner-up.
2. **How should clones reach the agent?** Through a generated listing in `AGENTS.md`, and a SessionStart hook for live problems such as a clone not yet set up.
   - The listing gives names, paths, kinds, configured refs and our own descriptions, plus where to start reading. It never contains text from a clone.
   - The agent then reads a clone's index and the pages it links to with ordinary tool calls, like any other file, so foreign text arrives as tool output during a task, not in the session's opening context.
   - A hook-printed listing would reach only Claude Code and escape review; the hook's job is the live state a static file can't show.

   The alternatives:
   - **A links-only index reader**, as in [Manifest-Assisted Retrieval](https://arxiv.org/abs/2610.38361) or [mcpdoc](https://github.com/langchain-ai/mcpdoc): little gain, because the pages an index links to are prose from the same author.
   - **A read-only reader subagent.** It gets only Read, Grep and Glob (no Bash, edits or web access) and returns an answer to the main agent. If foreign text hijacks it, the worst case is a misleading answer. Two costs:
     - answers can be lost at the hand-off: [Deep Agentic Search](https://arxiv.org/abs/2608.01507) reports 41.8% of its grep-by-subagent failures at the hand-off between planner and subagent;
     - a hijacked reader's slant can carry over in its answer.

     The template doesn't ship one. A repo can add one for clones of third-party repos, meaning repos maintained elsewhere. Its prompt must carry the clone paths and the rules itself, since a subagent may start without the project's instructions. Repos maintained by the same people (the federation case) are read directly.
   - **Clones outside the repo, granted through `permissions.additionalDirectories`.** That setting loads none of an added directory's `CLAUDE.md`, rules or skills, whatever the clone contains. Its costs: a location outside the repo that every environment has, and relative paths that resolve against the directory a session starts in. It needs the Edit deny rule too. The two layouts also differ in what waits for workspace trust: the committed `additionalDirectories` entry in this layout, the SessionStart hook in the in-repo one. The in-repo layout is recommended: in tests, the excludes held and Grep reached the clones by path.
   - **An MCP server with read-only roots:** not needed. Claude Code's own file tools with a deny rule do the same job without another process.
3. **Can Renovate keep pins current?** Yes, for mirror entries. In a dry run, the vendir manager proposed a newer tag. With a `groupName` rule, it grouped that minor bump with the matching PyPI pin in one branch. Branch refs are skipped as `invalid-value`. Three parts were not exercised:
   - the lock update in a real PR;
   - a major update held for approval;
   - the artifact step in Renovate's own environment.
4. **What do the security papers say?** They support structural controls over filtering. All are preprints or abstracts unless the papers table says otherwise. Each design piece maps to a reported finding:
   - **Excluding instruction files:** the [Workspace Topology](https://arxiv.org/abs/2608.14876) preprint reports injections in auto-loaded instruction files succeeding most often. The [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) abstract reports context files adding cost without raising success.
   - **No foreign text in the session's opening context:** the [Stale Instruction Files](https://arxiv.org/abs/2610.30571) abstract reports agents following a stale instruction file over the code in 90.1% of choices, and traces it to the channel the text arrives through. The [Manifest-Assisted Retrieval](https://arxiv.org/abs/2610.38361) preprint reports an `llms.txt` read as prose steering 21 of 24 answers in AI search. That shows reading an index as a tool result can still steer, which is listed under residual risk.
   - **Committed Edit deny:**
     - the [Overeager Coding Agents](https://arxiv.org/abs/2605.18583) abstract reports unrequested edits on benign tasks, with no injection;
     - the [Measuring the Permission Gate](https://arxiv.org/abs/2604.04978) abstract reports that auto mode doesn't classify edits inside the project;
     - the [From Approval to Abuse](https://arxiv.org/abs/2610.22987) abstract reports repo text talking agents into proposing broad allow-rules.

     So the rule ships committed in the template, and the developer rejects any allow-rule an agent proposes while reading a clone.
   - **The bare-repository setting:** the [ZTAC](https://arxiv.org/abs/2610.14488) preprint reports git obeying the config and hooks of any repository it discovers.
   - **Residual risk:**
     - the [SoK](https://arxiv.org/abs/2601.17548) abstract reports adaptive attacks beating most defenses;
     - the [NameTrap](https://arxiv.org/abs/2610.34253) abstract reports renamed identifiers steering agents with no instructions at all.

     So treating clone content as data lowers the risk but doesn't remove it.

## Candidates and matrix

Ranked shortlist:
1. **[vendir](https://github.com/carvel-dev/vendir):** meets the hard criteria in source and in local runs once `skipInitSubmodules` is set on every entry, which the planned CI check enforces; the Linux cloud-session run is outstanding.
   - It natively adds a SHA lock, path excludes and a Renovate manager for tag pins.
   - Its costs: no fetch by SHA, so only tag pins restore exactly at depth 1; every tag fetched unless overridden; sequential fetches from scratch; no useful cache.
   - Upstream fixes for the first two would remove most of the gap. A failed cloud-session run would move it down.
2. **[west](https://github.com/zephyrproject-rtos/west):** meets every hard criterion and was tested by running in 2026-10 and 2026-11. It restored a locked commit exactly at depth 1 with `--narrow` in a one-project test. A lock needs tasks of our own, and it can't exclude files natively. A release with path filtering or parallel update would move it back up.
3. **[vcs2l](https://github.com/ros-infrastructure/vcs2l):** no release since 1.1.7 (2026-02-16), and its setup crash ([vcstool#214](https://github.com/dirk-thomas/vcstool/issues/214)) is still open. A release fixing setup and divergent pulls would move it up.
4. **[agent-reference](https://github.com/mutewinter/agent-reference):** the best agent-specific tool found, with a worktree per version from shared blobless mirrors and hardened git calls. It has no committed lock, no refresh command, and lock-file matching for npm only. A committed SHA lock would move it up.
5. **[packref](https://github.com/adelrodriguez/packref):** a committed lock and an exact `install`, but dependency mode serves npm projects only, and repo refs are pinned when added. Tracked branches and other ecosystems would move it up.
6. **[shelf](https://github.com/Rika-Labs/shelf):** per-entry track or pin and parallel install, but no lock, a global cache, Bun, no license file, and idle since 2026-03. A lock and a release would move it up.
7. **[ripvcs](https://github.com/ErickKramer/ripvcs):** a parallel Go reimplementation of vcs2l, but `--shallow` never takes effect, pull ignores pins, and it has been idle since 2025-06. Fixes to both would move it up.

Licenses below were read at the commit named, during the search. Each was read from the whole license file, which was also grepped for riders and added restrictions. The exceptions say which manifest field or probe they rest on. Source claims under Limitations are pinned to the release read for verification, which can be a different commit.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [vendir](https://github.com/carvel-dev/vendir) | adopt | Apache-2.0 (`LICENSE` at 9c925e7d) | SHA lock, path excludes, a Renovate manager for tag pins, single binary through mise (aqua); no fetch by SHA and every tag fetched, both worked around |
| [west](https://github.com/zephyrproject-rtos/west) | build on (runner-up) | Apache-2.0 (`LICENSE` at cc7941cf, carried from the 2026-10-19 note) | Exact locked restore at depth 1 in a one-project test; a lock and file exclusion need tasks of our own |
| [vcs2l](https://github.com/ros-infrastructure/vcs2l) | reject | Apache-2.0 (`LICENSE` at 80da3932, carried from the 2026-10-19 note) | Setup and refresh bugs unfixed |
| [Claude Code](https://code.claude.com/docs/en/settings) (native, 2.1.319) | adopt (settings) | n/a (installed tool) | `claudeMdExcludes` and Edit deny rules carry the exclusion and edit-protection pieces; a SessionStart hook carries the state checks; `AGENTS.md` (through the `CLAUDE.md` symlink) carries the listing |
| [agent-reference](https://github.com/mutewinter/agent-reference) | borrow ideas | MIT (`LICENSE` at b4a05485) | Worktree per version from a blobless mirror; git hardening flags; no committed lock |
| [packref](https://github.com/adelrodriguez/packref) | borrow ideas | MIT (`LICENSE` at a0fb4893) | A committed lock with a tracking mode, and an `install` that follows it exactly; npm only |
| [shelf](https://github.com/Rika-Labs/shelf) | reject | MIT (`package.json` field only, at cafd546f; no license file) | No lock; global cache; Bun |
| [ripvcs](https://github.com/ErickKramer/ripvcs) | reject | MIT (`LICENSE` at 6ee5968c) | `--shallow` never applied; pull ignores pins |
| [graft](https://github.com/min0625/graft) | borrow ideas | Apache-2.0 (`LICENSE` at 74db69a2) | `lock --check`, a check that installed content matches the lock (its per-file hashes aren't adopted); beta; branch entries frozen when added |
| [ingraft](https://github.com/gunta/ingraft) | borrow ideas | MIT (`LICENSE` at 44011002) | Clone-ignore and cache-link strategies; no lock; its skill runs an unpinned `bunx …@latest` |
| [filedist](https://github.com/flaviostutz/filedist) | borrow ideas | MIT (`LICENSE` at e478722d) | `check` against the lock and read-only output (its per-file entries aren't adopted); copies files |
| [devrefs](https://github.com/Blankeos/devrefs) | reject | MIT (`LICENSE` at abe033b0) | Branch only, no pin or lock |
| [metagit-cli](https://github.com/metagit-ai/metagit-cli) | reject | MIT (`LICENSE.md` at 46ce49a6) | No pin field and no lock |
| [vendor-src](https://github.com/KATT/vendor-src) | borrow ideas | MIT (`LICENSE.md` at d747917b) | A generated `AGENTS.md` listing of the clones (borrowed) and pins that follow the installed package versions; commits subtrees into history and adds a postinstall hook |
| [dotdeps](https://github.com/davidturnbull/dotdeps) | borrow ideas | MIT (`Cargo.toml` field only, at 5bd7e701; no license file) | Picks versions from lock files in five ecosystems, an idea behind the lockstep check |
| repoverse (no link found; [crate](https://crates.io/crates/repoverse)) | reject | Apache-2.0 (`Cargo.toml` field only, crate 0.1.11; no license file) | Repository unreachable; built on submodules |
| [OpenCode references](https://github.com/anomalyco/opencode) | borrow ideas | MIT (`LICENSE` at 7b8e93a8) | Injects only name, path and description per reference, never content |
| [pi-references](https://github.com/alexanderop/pi-references) | borrow ideas | MIT (`package.json` field only, at 9c7a1864; no license file) | For the Pi coding agent: description-only listing, read-only wording and a write-blocking hook |
| [Alurith/pi-references](https://github.com/Alurith/pi-references), [jeremyosih/pi-references](https://github.com/jeremyosih/pi-references) | reject | MIT (`LICENSE` at 1f962ea9); MIT (`LICENSE` at 9d2fe428) | Further Pi ports; their minor ideas (refuse to refresh a dirty checkout, locks shared across processes, project settings only after trust) aren't needed here |
| [local-workspace-mcp](https://github.com/peter4leadson/local-workspace-mcp) | borrow ideas | MIT (`LICENSE` at 5af5607d) | The most thorough git-config hardening list; young (0.2.2) |
| [MCP filesystem server](https://github.com/modelcontextprotocol/servers/tree/36380287ed3b15d115b55f546617d723072b1296/src/filesystem) | reject | Apache-2.0 for new contributions, MIT before (`LICENSE` at 36380287) | `--read-only` works, but Claude Code's own tools with a deny rule cover the need |
| [filesystem-mcp](https://github.com/j0hanz/filesystem-mcp) | reject | MIT (`LICENSE` at fc8856dc) | Another server with read-only roots; not needed |
| [mcpdoc](https://github.com/langchain-ai/mcpdoc) | reject | MIT (`LICENSE` at 8d01c085) | Serves `llms.txt` files as links to fetch over MCP; Claude Code's own file tools read a clone's index directly; archived |
| [OpenSpec Stores](https://github.com/Fission-AI/OpenSpec) | borrow ideas | MIT (`LICENSE` at 0fa4a970) | A listing of a referenced store with the exact fetch command; never clones |
| [docflow](https://github.com/EvolveHQ/docflow) | borrow ideas | MIT (`LICENSE` at 612384b8) | "A joining repo only ever writes its own back-pointer" |
| [momentum](https://github.com/LiminaLabsAI/momentum) | reject | MIT (`LICENSE` at 3942983c) | Sibling checkouts plus a pointer block written into `CLAUDE.md` |
| [microsoft/apm](https://github.com/microsoft/apm) | reject | MIT (`LICENSE` at 29200432) | Rejects a repo with no agent files as "Not a valid APM package" |
| [consult-references skill](https://github.com/0x0f0f0f/research-engineering-skills/tree/06e4bd0312385f4d09d731ffb11a4b672eb2629c/skills/consult-references) | reject | MIT (`LICENSE` at 06e4bd03) | A convention (an `INDEX.md` plus clones); writes its own `AGENTS.md` into each clone |
| [explore-repo skill](https://github.com/sjunepark/agent-scripts/tree/03cfe3258c426f6c67a1ecdb32eac60fb6db64fc/skills/explore-repo), [librarian skill](https://github.com/mitsuhiko/agent-stuff/tree/0865c849befd2021490679f96a8dee58c84ac857/skills/librarian), [dependency-docs skill](https://github.com/juanmarin-co/skills/tree/18988b8f11782c5ba303df03e811de4e1ca42c2f/skills/dependency-docs), [source-driven-development skill](https://github.com/addyosmani/agent-skills/tree/301b02b12bff98e4688e6984af6556802322bbde/skills/source-driven-development) | borrow ideas | none found (probes of `LICENSE` variants at 03cfe325); Apache-2.0 (`LICENSE` at 0865c849); none found (probes at 18988b8f); MIT (`LICENSE` at 301b02b1) | Wording that treats fetched files as reference material, not instructions |
| [refs](https://github.com/kaisers-io/refs) | borrow ideas | MIT (`LICENSE` at 6f1f2b6) | Global store with no committed manifest or pin. It installs pre-commit and pre-push hooks in each checkout as a backstop, and says plainly that read-only "is a promise, not a sandbox" |
| [skill-reference-dirs](https://github.com/kennethfan/skill-reference-dirs), [repo-pattern-miner-plugin](https://github.com/prodm93/repo-pattern-miner-plugin), [pi-references-extension](https://github.com/ethanfritzt/pi-references-extension) | reject | Apache-2.0 (`LICENSE` at ec4de27b, no rider grep); none found (API listing only); none found (API listing only) | Lists or samples existing directories; no cloning, pins or lock |
| [depot](https://github.com/acoyfellow/depot), [skillpluck](https://github.com/samettemizer/skillpluck), [offworld](https://github.com/oscabriel/offworld) | reject | MIT (`LICENSE` at 8bcd423d); MIT (`LICENSE` at e9cff2f2); MIT (`LICENSE` at fbc7c0ab) | Global caches with no pin or lock, or skill extraction only |
| [npins](https://github.com/andir/npins), [niv](https://github.com/nmattia/niv) | reject | EUPL-1.2 (`LICENSE` at 4d775645); MIT (`LICENSE` at 702e5156) | Pins are consumed through Nix |
| [all-repos](https://github.com/asottile/all-repos), [git-get](https://github.com/grdl/git-get), [gitopolis](https://github.com/timabell/gitopolis), [ham](https://github.com/kernkonzept/ham) | reject | MIT (`LICENSE` at 2df7fa0a); MIT (`LICENSE.md` at 56a02560); AGPL-3.0-only (`LICENSE` at de814adc); BSD-2-Clause (`LICENSE.spdx` at 8b8e4583, declaration only) | The source-calibration leads: none keeps pinned clones with a lock; ham needs system Perl |
| [dfetch](https://github.com/dfetch-org/dfetch), [git-subrepo](https://github.com/ingydotnet/git-subrepo), [josh](https://github.com/josh-project/josh) | reject | MIT (`LICENSE` at b3dfd1ab); MIT (`License` at 5e0f401f); MIT (`LICENSE` at 8a941047) | Vendor files into the consumer's history, or run a proxy server |
| [Effect "one weird git trick" post](https://effect.website/blog/the-one-weird-git-trick-that-makes-coding-agents-more-effect-ive/) | borrow ideas | n/a (blog post) | `AGENTS.md` rules marking vendored repos read-only and naming the index to start at; vendors with `git subtree` into history |
| [opensrc](https://github.com/vercel-labs/opensrc) | borrow ideas | Apache-2.0 (`LICENSE` at b51de608, carried from the 2026-10-19 note) | Unchanged from the earlier note; now reportedly covers PyPI and crates.io too (docs only) |

Matrix. Each cell gives a support value (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified), then its source in brackets:
- **[V]:** the candidate's section under Limitations below;
- **[R]:** verified by running, under Limitations;
- **[D]:** the docs-level reads listed there;
- **[C]:** the candidate table above;
- **[2026-10-19]:** the superseded note;
- **[CNV]:** a follow-up item under Could not verify;
- **not found:** no source read covers the cell.

| Criterion | vendir | west | vcs2l | agent-reference | packref | shelf | ripvcs |
|---|---|---|---|---|---|---|---|
| License (hard) | ✓ [C] | ✓ [C] | ✓ [C] | ✓ [C] | ✓ [C] | ◐ manifest only [C] | ✓ [C] |
| No repo content runs (hard) | ◐ submodules unless opted out [V], [R] | ✓ no `west-commands` [V] | ✓ [2026-10-19] | ✓ [V] | ? minified source, snippet only [D] | ? not found | ◐ `import -r` follows nested `.repos` [V] |
| Pinned install via mise (hard) | ✓ aqua [D], [R] | ✓ pipx [2026-10-19] | ✓ pipx [2026-10-19] | ✓ npm [D] | ✓ npm [D] | ◐ npm plus Bun [D] | ? release assets unverified [D] |
| Linux cloud session (hard) | ◐ ran on Linux x64, not in a cloud session [R], [CNV] | ✓ [2026-10-19] | ✓ [2026-10-19] | ? not run [CNV] | ? not run [CNV] | ? not run [CNV] | ? not run [CNV] |
| Bulk refresh, follows rewrites (hard) | ✓ fresh fetch per entry [V], [R] | ✓ [V] | ◐ stalls on rewrites [2026-10-19] | ◐ no refresh command; `clone` follows force-pushes [V] | ? refresh of repo refs not found [D] | ? `update` documented, rewrites not checked [D] | ✗ pull ignores pins [V] |
| Committed manifest, track or pin (hard) | ✓ [V], [R] | ✓ [V] | ✓ [2026-10-19] | ✓ [V] | ◐ repo refs pinned when added [D] | ✓ [D] | ✓ [V] |
| Lock of resolved SHAs, exact restore | ◐ exact for tag pins; not for a moved branch or a non-tip commit at depth 1 [V], [R] | ⊕ `--freeze` plus tasks; exact at depth 1 with `--narrow` in a one-project run [V], [R] | ? `vcs export --exact` not read; not found | ◐ machine-local state file only [V] | ◐ lock exists; SHA content unverified [D] | ? not found | ◐ `export -c` [V] |
| Keep instruction files out | ✓ `excludePaths` [V], [R] | ✗ no path filter (listing) [V] | ? not found | ? not found | ? not found | ◐ `--sparse` paths [D] | ? not found |
| Renovate support | ✓ vendir manager for tag pins; grouping by a `groupName` rule [V], [R] | ⊕ regex manager [D] | ⊕ regex manager [D] | ⊕ regex manager on `ref` [D] | ⊕ regex manager [D] | ⊕ regex manager on `pin:tag` [D] | ⊕ regex manager [D] |
| Several refs side by side | ◐ separate entries [V] | ◐ separate projects [2026-10-19] | ◐ separate entries [2026-10-19] | ✓ worktree per version [V] | ✓ versions side by side [D] | ◐ separate aliases [D] | ◐ separate entries [V] |
| Shallow or blobless | ◐ depth 1, but every tag is fetched unless overridden [R] | ✓ `clone-depth` [V] | ✓ [2026-10-19] | ✓ blobless [V] | ✓ archive download [D] | ✓ depth 1 [D] | ✗ flag broken [V] |
| Lock-file matching | ◐ Renovate grouping [R], plus our lockstep check | ⊕ Renovate grouping [2026-10-19] | ⊕ Renovate grouping [2026-10-19] | ◐ npm only [V] | ◐ npm only [D] | ◐ `package.json`, `go.mod` [D] | ? not found |
| Shared cache | ✗ a bundle cache that skips large bundles and still fetches every time [V], [R] | ✓ name, path and auto caches [V] | ✗ [2026-10-19] | ✓ global store [V] | ✓ global store [D] | ✓ global cache [D] | ? not found |
| Maintenance and maturity | ✓ release every 2-8 weeks [V] | ◐ last release 2025-09-23, main active [V] | ◐ last release 2026-02-16 [V] | ✓ v1.0.4, 2026-09-24 [D] | ◐ 0.3.7, young [D] | ✗ idle since 2026-03 [D] | ✗ idle since 2025-06 [D] |

**Blends considered:**
- **vendir plus the skill, the task script (with the `AGENTS.md` listing), the SessionStart hook and the CI check** (chosen): configuration around vendir, plus four pieces of our own.
- **The same, with the listing printed by the SessionStart hook instead of committed to `AGENTS.md`:** the hook can show live state in the same place, but the listing then reaches only Claude Code, isn't reviewed in git, and appears only after workspace trust.
- **vendir with `depth: 0` for branch entries,** for an exact restore of every entry. A depth-0 sync of pytest took 4.6 s and 56 MB (18,864 commits), against 3.8 s and 20 MB at depth 1 with tags and 1.0 s with tags off. vendir starts each sync from scratch, so a refresh costs about as much as a first sync.
- **west plus the same four pieces, plus a freeze task, a restore task, a sparse-checkout step and a regex manager:** exact and faster, but with four more pieces of our own, and the sparse-checkout step is untested.
- **vendir with clones outside the repo through `additionalDirectories`:** the fallback if the in-repo layout later fails (see question 2).
- **agent-reference's store plus a lock of our own:** gives versions side by side, but it is npm-centric and has no committed lock.

**Scenario walk (finalists: vendir blend, west blend):**
- *Explore: a shallow clone of the newest commit, refreshed on demand.*
  - vendir: an `explore.yml` entry. With tags off, a refresh took about 1 s for pytest and 10 s for qtbase, and it leaves no diff to review.
  - west: a tracked project; incremental and faster.
- *Mirror: the dependency's version, updated with it.*
  - vendir: a tag pin, exact at depth 1. Renovate bumps the tag and the dependency in one PR when both releases are visible (a dry run, minor bump); the planned CI check catches a mismatch.
  - west: a pinned revision with the regex manager and a freeze task.
- *A major upgrade done as a project of its own (Qt 5 to 6):*
  - Renovate holds the grouped major for approval.
  - A comparison entry at the new version sits beside the mirror during the work, exempt from the lockstep rule and outside Renovate.
  - When the upgrade lands, the new tag moves into the mirror entry and the comparison entry is removed.
  - With west, the comparison is a second project.
- *Fresh cloud session:* the environment's setup script runs the setup task. If it hasn't run, the `AGENTS.md` listing still names the clones, and the SessionStart hook reports them as not cloned.
  - vendir: mirror and comparison entries restore their locked tags exactly; explore entries clone the newest commit.
  - west: a frozen-manifest restore with `--narrow`.
  - A vendir restore failed for a locked commit that upstream had force-pushed away. The same fetch rules make a re-tagged pin fail, for vendir and probably for west; neither was run.
- *Upstream force-pushes a tracked branch:* both follow it.
- *An agent consults a sibling repo's knowledge base:* the `AGENTS.md` listing gives the clone's path and says to start at its `SUMMARY.md` or `llms.txt`. The agent Reads that index, then the linked pages, all as tool output, and passes the clone's path to Grep. This is the same for both finalists.
- *A foreign repo ships `.claude/skills/`, `CLAUDE.md` and an injection in its README:*
  - vendir: `excludePaths` keeps the instruction files out, and `claudeMdExcludes` is a second layer for `CLAUDE.md` and `AGENTS.md`.
  - west: the sparse-checkout step does the same job, as code of our own.
  - Either way, the README stays readable as data behind the Edit deny rule, and the residual risk above applies.
- *Offline:* both leave existing clones readable when a fetch fails. vendir's lock is unchanged.

## Limitations checked in source

### vendir

[vendir](https://github.com/carvel-dev/vendir) release v0.46.3 at 43e80d11:
- `ref` takes a branch, tag or SHA. The lock records each content's resolved `sha`, `tags` (from `git describe`) and `commitTitle`, with no per-file checksums. `vendir sync --locked` replaces `ref` with the lock's bare SHA and fails without a lock. *Verified in source* (`pkg/vendir/fetch/git/git.go:181-197,219,234-252`; `pkg/vendir/config/lock_directory.go:13-33`; `pkg/vendir/cmd/sync.go:53,100-120`; `pkg/vendir/config/directory.go:349-358`).
- Only a `ref` starting with `origin/` names what to fetch. Any other ref, the locked SHA included, gets a plain `git fetch origin [--depth N]` of the last N commits of each branch and tag, then `git checkout <ref>`. `remote.origin.tagOpt --tags` is set first, so every tag is fetched. *Verified in source* (`pkg/vendir/fetch/git/git.go:181,186-197,219,236-241`).
- The git commands are:
  - init;
  - `config credential.helper`;
  - `remote add`;
  - `config remote.origin.tagOpt --tags`;
  - an optional `bundle unbundle`;
  - `fetch` and checkout.

  After them, `git submodule update --init --recursive` runs unless `skipInitSubmodules` is set. `lfsSkipSmudge` only sets `GIT_LFS_SKIP_SMUDGE=1`, and it is off by default. For `git` contents, the only external command is `git`, run with the inherited environment. So a user's global hooks and filter drivers apply, and `GIT_CONFIG_*` variables override the repo's own config. *Verified in source* (`pkg/vendir/fetch/git/git.go:97-135,151-231,282-302`; listing of execs in `pkg/`).
- `.git` is kept unless excluded: the temp clone is renamed whole into staging, then onto the target. *Verified in source* (`pkg/vendir/fetch/git/sync.go:45-53,64,102-110`; `pkg/vendir/directory/staging_dir.go:132-145`).
- `includePaths` and `excludePaths` are doublestar globs applied to each file after the fetch, and legal files (LICENSE, NOTICE) are put back. *Verified in source* (`pkg/vendir/directory/file_filter.go:19-97`).
- Each `directories[].path` is deleted and replaced by the staging copy. `../x` and absolute paths are accepted; `/`, `.`, `..` and overlapping paths are rejected. *Verified in source* (`pkg/vendir/directory/staging_dir.go:61-115,132-176`; `pkg/vendir/config/directory.go:221-247,312-320`).
- Directories sync one after another. `-d <path>` syncs one directory and merges into the lock, and `-f` and `--lock-file` name the configuration and lock files. *Verified in source* (`pkg/vendir/cmd/sync.go:43-56,140-174`; `rg 'errgroup|WaitGroup|go func' pkg/vendir` finds no non-test hits).
- With `VENDIR_CACHE_DIR` set, vendir saves one git bundle per URL, but not a bundle larger than `VENDIR_MAX_CACHE_SIZE` (1 MiB by default), and a fetch always runs. *Verified in source* (`pkg/vendir/cmd/sync.go:121-126`; `pkg/vendir/fetch/cache/cache.go:35-88`; `pkg/vendir/fetch/git/sync.go:55-100`).
- A fetch error leaves that target untouched and the lock unwritten, and sync stops at the first failure. *Verified in source* (`pkg/vendir/directory/directory.go:63-73,94-119,276-281`).
- Release cadence is every 2 to 8 weeks (v0.45.4 to v0.46.3, 2026-06-01 to 2026-10-19): *docs only* (releases API).

### Renovate's vendir manager

Tag 44.221.6 at af92486c:
- Git contents map to the `git-refs` datasource, with `depName` set to the URL and `currentValue` to `ref`. Only `ssh://` and `http(s)://` URLs pass the schema. *Verified in source* (`lib/modules/manager/vendir/extract.ts:42-50,90-128`; `lib/modules/manager/vendir/schema.ts:10-14,53-67`).
- The artifact step writes `vendir.yml`, runs plain `vendir sync`, and returns the lock plus changed files. It does nothing without a lock. *Verified in source* (`lib/modules/manager/vendir/artifacts.ts:20-89`).

### Verified by running (2026-11-07)

vendir 0.46.3 (through mise's aqua backend) on Linux x64. The local runs used throwaway repos carrying instruction files, nested `.claude/skills/` and a submodule. Timings used public GitHub repos and are single runs. Results:
- **Excludes and contents:**
  - `**/CLAUDE.md` and `**/.claude/**` alone also removed the top-level files;
  - `.git` was kept, the submodule stayed uninitialized, and a content `path: .` worked;
  - `git status` in a clone lists every excluded file as deleted, while an edited file shows as modified.
- **Pins and locks:**
  - At `depth: 1`, a commit pin one commit behind `main` failed ("unable to read tree"), and a `--locked` restore failed once the tracked branch had moved upstream. Both worked at `depth: 0`.
  - A locked commit that upstream force-pushed away failed at any depth.
  - A failing entry stopped the entries after it in a whole-configuration sync, and no lock was written.
- **Refresh:** after a tag pin was edited, a sync into an empty `repos/` checked out the new tag; `-d` refreshed one entry, alone or with `--locked`; a force-pushed branch was followed.
- **Offline:** an unreachable upstream left the existing clone readable and the lock unchanged.
- **Default branch:** `ref: origin/HEAD` and `ref: HEAD` both failed, so an entry must name its branch.
- **Timing:**
  - Six GitHub repos (those of the 2026-10-19 west test): 3.3 s first sync, 3.1 s refresh, 3.8 s `--locked`. The 2026-10-19 run measured a west refresh of the same repos at 1.7 s sequential and 0.6 s with one process per project.
  - pytest:

    | Fetch | Time | Size |
    |---|---|---|
    | vendir, depth 1 (226 commits from all its tags) | 3.8 s | 20 MB |
    | vendir, depth 0 | 4.6 s | 56 MB |
    | plain `git clone --depth 1 --single-branch --no-tags` | 0.65 s | 12 MB |
  - **Cache:** with `VENDIR_MAX_CACHE_SIZE=2Gi`, a second sync was no faster at depth 1 (3.7 s, then 4.3 s). At depth 0 it was 1.3 s faster (4.9 s, then 3.6 s). Source explains the small gain: a fetch always runs.
  - **Tags off:** plain git running vendir's fetch sequence without checkout took 63 s and 426 MB with qtbase's 294 tags, and 8.4 s and 68 MB with `--no-tags`. vendir with `remote.origin.tagOpt` overridden to `--no-tags` through `GIT_CONFIG_*` took 1.0 s for pytest and 9.9 s for qtbase, one `-d` entry at a time. The lock then recorded no `tags`. The override made a tag pin fail.
- **Renovate**, 44.212.0, local-platform dry run (the source read above was 44.221.6):
  - with a `groupName` rule in the test configuration, it grouped west `v1.4.0` → `v1.5.0` with `west==1.4.0` → `1.5.0` from `pyproject.toml` in one branch (a minor bump);
  - it proposed mani `v0.30.0` → `v0.32.1`;
  - it skipped `origin/main` as `invalid-value`.
- **West 1.5.0**, one project: after the tracked branch moved, a frozen-manifest restore with `--narrow` at `clone-depth: 1` checked out the locked commit. Without `--narrow` it failed.
- **Claude Code 2.1.319**, headless in a scratch repo:
  - Grep and Glob given a path inside a gitignored directory found its files, while Grep with no path didn't.
  - An `env` value from a `--settings` file reached a Bash command (`git config --get safe.bareRepository` printed `explicit`).

### west

[west](https://github.com/zephyrproject-rtos/west) v1.5.0 at f0e65772 (released 2025-09-23); main at d7964e4a:
- `west manifest --freeze` writes each project's `manifest-rev` SHA and fails if any project isn't cloned. Restoring means setting `manifest.file` to the frozen file. With `clone-depth: 1`, a SHA that isn't a branch tip arrives only with `--narrow`. *Verified in source* (`src/west/app/project.py:577-751,1055-1198,1721-1808`; `src/west/manifest.py:870-905,1242-1305,1609-1714`).
- Extension commands come only from projects that declare `west-commands` (or an imported manifest's `self:`), and `commands.allow_extensions=false` disables them. With neither `west-commands` nor `import:`, west reads no file from a clone. *Verified in source* (`src/west/commands.py:550-575,604-721`; `src/west/app/main.py:388-420`).
- West finds its workspace by walking up to the first `.west/`. Running west inside a clone that ships its own `.west/` would therefore use that clone's configuration. *Verified in source* (`src/west/util.py:58-79`).
- There is no sparse checkout or per-project path filter: *verified in source* (listing of `src/west` at both commits for sparse and path-filter options; `src/west/app/project.py:1153-1156`).
- Neither v1.5.0 nor main has parallel update; [west#1015](https://github.com/zephyrproject-rtos/west/pull/1015) is open. *Verified in source* (`src/west/app/project.py:1249-1278`, listing); the PR status is *docs only*.
- `-t/--topdir` and `--manifest-path` are merged on main through [west#953](https://github.com/zephyrproject-rtos/west/pull/953) but are in no release: *verified in source* (`src/west/app/project.py:210-300,360-514` at d7964e4a).
- `--name-cache`, `--path-cache` and `--auto-cache` are in v1.5.0. Name and path caches apply only at first clone, while auto-cache keeps a mirror per URL. *Verified in source* (`src/west/app/project.py:1062-1131,1581-1719`).

### vcs2l

- [vcs2l](https://github.com/ros-infrastructure/vcs2l) has had no release since 1.1.7 (2026-02-16), and blobless clone is merged but unreleased: *docs only* (releases API).
- [vcstool#214](https://github.com/dirk-thomas/vcstool/issues/214) is still open. The vcs2l PR that fixed it ([#124](https://github.com/ros-infrastructure/vcs2l/pull/124)) was closed unmerged, and [vcs2l#14](https://github.com/ros-infrastructure/vcs2l/issues/14) (pull on divergent history) is open. *Docs only.*

### agent-reference

[agent-reference](https://github.com/mutewinter/agent-reference) v1.0.4 at fdaaf3c:
- Each entry in `agent-reference.json` takes a `ref` or `#ref` (commit, tag or branch); with none, it tracks the default branch: *verified in source* (`src/config.ts:316-341`; `src/git.ts:851-878`).
- Resolved SHAs go only to a machine-local state file; the code states that the config is the only committed file: *verified in source* (`src/manifest.ts:15-98`).
- The store can move into the project through `cacheDir` or `AGENT_REFERENCE_STORE_DIR`: *verified in source* (`src/git.ts:816-835`).
- There is no separate refresh command. `clone` runs sequentially, and a forced `+refs/heads/*` refspec follows force-pushes: *verified in source* (`src/core.ts:31-160`; `src/git.ts:283-332,424-460`).
- Every git call gets `-c protocol.ext.allow=never -c protocol.file.allow=user`: *verified in source* (`src/git.ts:45-126`).
- Lock-file matching is npm only: *verified in source* (`src/config-dependencies.ts:16-67`).

### ripvcs

[ripvcs](https://github.com/ErickKramer/ripvcs) v1.0.3 at ec7c67a:
- `--shallow` is registered as "shallow" but read as `shallowClone`, so it never applies; main has the same bug. *Verified in source* (`cmd/import.go:39,70`).
- `pull` ignores `.repos` and runs a plain `git pull` in every repo: *verified in source* (`cmd/pull.go:12-62`).
- `import -r` follows `.repos` files found inside cloned repos, and `export -c` writes `rev-parse HEAD` per repo: *verified in source* (`cmd/import.go:150-226`; `cmd/export.go:17-111`).

### Other tools read in source

- **[metagit-cli](https://github.com/metagit-ai/metagit-cli)** (0.38.2 at 46ce49a): no per-repo pin and no lock, *verified in source* (listing of the config model for sha, commit, tag, depth and lock; `src/metagit/core/project/models.py:79-124`). That it makes full clones rests on a snippet of `src/metagit/core/repo/materialize.py:138` and is a lead only.
- **[microsoft/apm](https://github.com/microsoft/apm)** (at 29200432): a repo without `apm.yml`, `SKILL.md`, hooks or a plugin fails validation as "Not a valid APM package", *verified in source* (`src/apm_cli/models/validation.py:396-420`). This repo pins apm 0.35.0 in `mise.toml`. Its `apm.lock.yaml` records per-file sha256 hashes, a precedent this design doesn't follow.
- **[OpenCode references](https://github.com/anomalyco/opencode)** (at 7b8e93a8): only references with a description are injected, each as name, path and description in an `<available_references>` block, and no file content is injected. *Verified in source* (`packages/core/src/reference/instructions.ts:8-65`).
- **[pi-references](https://github.com/alexanderop/pi-references)** (v0.1.1 at 9c7a186):
  - It injects a "## Reference directories" heading, read-only wording and `alias: dir — description` lines: *verified in source* (`src/references/context.ts:10-26`).
  - It blocks only the `write` and `edit` tools, and only inside git-kind references: *verified in source* (`src/extension/index.ts:66-77`).
- **[local-workspace-mcp](https://github.com/peter4leadson/local-workspace-mcp)** (v0.2.2 at 365f2ef):
  - 22 of its 23 tools are read-only, and `task_run` runs only operator-configured commands. Roots come only from operator config. *Verified in source* (`src/server.ts:182,195-828`; `src/config.ts:6-153`).
  - Its git calls disable fsmonitor, sshCommand, gitProxy, the pager, ext-diff and textconv, and turn off system and global config. The repo's own `.git/config` still loads. *Verified in source* (`src/git.ts:1-126`).
- **[MCP filesystem server](https://github.com/modelcontextprotocol/servers/tree/36380287ed3b15d115b55f546617d723072b1296/src/filesystem)** (v2.3.0 at 3638028): `--read-only` registers only read-only tools, *verified in source* (`src/filesystem/index.ts:99-190`; `src/filesystem/server.ts:302-320`).

### Docs-level reads

- [packref](https://github.com/adelrodriguez/packref) (at a0fb4893):
  - Its README says a repo ref can be a tag, a branch or a full SHA, that a ref left out pins the default branch's current commit, and that `install` follows the committed lock exactly (`README.md:20-25,56-63,87-115`).
  - Lock entries are `{name, registry, source, tracking, version}` (`src/lib/workspace/lockfile.ts:18-24`, a snippet).
  - The published package fetches archives rather than cloning (`dist/index.js` 0.3.7, minified, a snippet).
- [shelf](https://github.com/Rika-Labs/shelf) (at cafd546f):
  - The shelffile's `alias url [pin:branch|tag|<sha>]` lines and `install --concurrency` are documented (`docs/shelffile.md:1-50`; `docs/commands.md:7-72`).
  - Clones are made at depth 1 (`src/domain/git/git-service.ts:18-25`, a snippet).
- Install routes (mise and aqua registries; npm metadata):
  - [vendir](https://github.com/carvel-dev/vendir) is in mise's registry through aqua;
  - [agent-reference](https://github.com/mutewinter/agent-reference) and [packref](https://github.com/adelrodriguez/packref) are on npm;
  - [ripvcs](https://github.com/ErickKramer/ripvcs) ships only GitHub release binaries, whose assets weren't checked.
- Release dates and idle periods (GitHub releases API, 2026-11-06): agent-reference v1.0.4 2026-09-24; shelf v0.1.3 2026-03-19; ripvcs v1.0.3 2025-06-24; packref 0.3.7 2026-10-19.
- Renovate:
  - the regex manager can update a `ref` or tag field in any manifest ([regex manager](https://docs.renovatebot.com/modules/manager/regex/), [git-refs datasource](https://docs.renovatebot.com/modules/datasource/git-refs/));
  - `dependencyDashboardApproval` and the separate PR for majors are from Renovate's docs and weren't run.
- MCP's 2026-07-28 revision deprecates Roots ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)).
- Claude Code (2.1.319, as `claude --version` reported on this machine; docs read verbatim from `code.claude.com/docs/en/*.md` on 2026-11-06):
  - At the project root, Claude Code reads `AGENTS.md` by default only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists at or above the working directory; a `CLAUDE.md` symlink to it or an `@AGENTS.md` import loads it otherwise ([memory](https://code.claude.com/docs/en/memory)).
  - A subdirectory's `CLAUDE.md` loads on demand when Claude reads a file there. Its `AGENTS.md` loads only when that subdirectory has no `CLAUDE.md`. `claudeMdExcludes` globs are matched against absolute paths and apply to both. ([memory](https://code.claude.com/docs/en/memory))
  - `.claude/skills/` below the starting directory load the first time Claude reads or edits a file in that subdirectory, and the docs name no path-based exclusion for skills ([skills](https://code.claude.com/docs/en/skills)).
  - Directories in `permissions.additionalDirectories` load no `CLAUDE.md`, rules or skills, while `--add-dir` loads skills. The setting waits for workspace trust, and its relative paths resolve against the starting directory. ([large codebases](https://code.claude.com/docs/en/large-codebases), [permissions](https://code.claude.com/docs/en/permissions))
  - Content searches respect `.gitignore` by default ([large codebases](https://code.claude.com/docs/en/large-codebases)). The run above shows an explicit path overrides that for Grep and Glob.
  - `Edit` deny rules also cover `Write`, and a leading `/` anchors a rule's path at the settings file's project. Sandbox `denyWrite` applies to sandboxed Bash commands. ([permissions](https://code.claude.com/docs/en/permissions), [sandboxing](https://code.claude.com/docs/en/sandboxing))

Verified:
- the licenses in the candidate table read in this run, at the named commits, as the table's note describes; the west, vcs2l and opensrc licenses are carried from the 2026-10-19 note;
- the claims above tagged *verified in source*, at the named commits;
- the behavior under Verified by running.

Could not verify. Each of these belongs in a test before or while the template changes:
- **vendir:**
  - in a Linux cloud session;
  - in the three-configuration layout: `-f <config> --lock-file <lock> -d` creating a lock that doesn't exist yet, and the no-tags override under `-f` with a separate lock.
- **Renovate in a real PR:**
  - that the artifact step updates `vendir.lock.yml` with the new tag's commit;
  - that the gitignored clones stay out of the PR's commit;
  - that a `vendir` binary is available in the Renovate environment actually used;
  - the major-update approval flow for a grouped mirror entry.
- **Claude Code:**
  - the `Edit(/.reference-repos/repos/**)` deny rule blocking Edit and Write;
  - `claudeMdExcludes` on `**/.reference-repos/**`;
  - a committed project settings `env` (only a `--settings` file was tested);
  - Glob with no path on a gitignored directory.
- **Pieces not built yet:** the task script and its `AGENTS.md` listing, the SessionStart hook and the CI check; west's sparse-checkout step.
- **Agent coverage:** whether agents other than Claude Code act on the `AGENTS.md` listing.
- **Other candidates:** agent-reference, packref, shelf and ripvcs on Linux cloud sessions (not run); opensrc's current scope (docs only).
- **Unavailable routes:** PyPI keyword search (see the ledger); Semantic Scholar citations for four papers (throttled; OpenAlex was used instead).

## Papers

No paper studies agents reading pinned, read-only reference clones. The papers below bear on the design: injection through repository files, git's own attack surface, permission approvals, and the value of version-matched docs. Citation data came partly from Semantic Scholar.

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [Workspace Topology as an Attack Vector in Agentic Coding Assistants](https://arxiv.org/abs/2608.14876) | read in part (abstract, 1, 3, 5 headings only, 6.2) | experiment | preprint | borrow ideas | The preprint (accepted at CAMLIS 2026, per the authors) reports that injections in auto-loaded `AGENTS.md` and `CLAUDE.md` succeed most often and root READMEs are almost always read; it recommends scanning context files and default-deny tools (paper-reported) |
| [Names Are Not Objects (ZTAC)](https://arxiv.org/abs/2610.14488) | read in part (threat table, rules, git section) | experiment | preprint | borrow ideas | The preprint reports that git obeys the config, hooks and fsmonitor of any repository it discovers, including an embedded bare repository, and recommends pinning `GIT_DIR` and disabling risky settings (paper-reported) |
| [Manifest-Assisted Retrieval](https://arxiv.org/abs/2610.38361) | read in part (abstract, III, VI, VII-A, VIII, references) | weak experiment | preprint | borrow ideas | The preprint (accepted at IEEE FLLM 2026, per the authors) reports that adversarial `llms.txt` prose was adopted in 21 of 24 responses, while a links-only reading showed no known adoption (paper-reported). Borrowed: keep index prose out of authoritative context; its links-only consumer isn't adopted (question 2) |
| [Authority Is Not a String (CapScope)](https://arxiv.org/abs/2609.08371) | abstract only | weak experiment | peer-reviewed | borrow ideas | The abstract reports that capabilities fixed before repo content is read let injection succeed in 3 of 75 runs, against 33-47 for baselines (paper-reported) |
| [Stale Instruction Files Override the Code](https://arxiv.org/abs/2610.30571) | abstract only | experiment | preprint | borrow ideas | The abstract reports agents following a stale instruction file over the code in 90.1% of choices, and traces it to the instruction channel versus tool output (paper-reported) |
| [One Skill Takes Over (SkillClash)](https://arxiv.org/abs/2610.25064) | abstract only | experiment | preprint | borrow ideas | The abstract reports rule-following dropping from 93-99% to 61-62% when two same-job skills are in context (paper-reported) |
| [Overeager Coding Agents](https://arxiv.org/abs/2605.18583) | abstract only | experiment | preprint | borrow ideas | The abstract reports agents making unrequested edits on benign tasks, with no injection (paper-reported) |
| [From Approval to Abuse](https://arxiv.org/abs/2610.22987) | abstract only | experiment | preprint | borrow ideas | The abstract reports text planted in a repo steering agents (Claude Code, Codex CLI) into proposing broad allow-rules in 58% of cases, after which attacks completed silently in 47 of 58 (paper-reported) |
| [Measuring the Permission Gate](https://arxiv.org/abs/2604.04978) | abstract only | experiment | preprint | borrow ideas | The abstract reports that Claude Code's auto mode never classifies in-project file edits, 36.8% of state-changing actions (paper-reported). Clones inside the repo would count as in-project |
| [Don't Let AI Agents YOLO Your Files](https://arxiv.org/abs/2604.13536) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract argues, from 290 incident reports, for gating agent writes below the agent (paper-reported) |
| [Setup Complete, Now You Are Compromised](https://arxiv.org/abs/2607.15143) | abstract only | experiment | preprint | borrow ideas | The abstract reports that editing a README, requirements file or Makefile redirects the installs agents run (paper-reported) |
| [Supply-Chain Poisoning of Skill Ecosystems (DDIPE)](https://arxiv.org/abs/2604.03081) | abstract only | experiment | preprint | borrow ideas | The abstract reports payloads in documentation code examples being reused by agents (11.6-33.5% bypass) (paper-reported) |
| [NameTrap](https://arxiv.org/abs/2610.34253) | abstract only | experiment | preprint | borrow ideas | The abstract reports that renamed identifiers in third-party files steer agents toward weaknesses with no instructions (paper-reported) |
| [Package Hallucination via Rule Files](https://arxiv.org/abs/2610.09264) | abstract only | experiment | preprint | borrow ideas | The abstract reports injected `AGENTS.md` and `.cursorrules` text making agents swap in attacker packages (paper-reported) |
| [Skill-Inject](https://arxiv.org/abs/2602.20156) | abstract only | experiment | preprint | borrow ideas | The abstract reports skill-file injections succeeding up to 80% of the time (paper-reported) |
| [Prompt Injection on Agentic Coding Assistants (SoK)](https://arxiv.org/abs/2601.17548) | abstract only | qualitative study | preprint | borrow ideas | The abstract reports adaptive attacks exceeding 85% success against defenses, with most defenses mitigating under half (paper-reported) |
| [Spotlighting](https://arxiv.org/abs/2403.14720) | abstract only | experiment | preprint | borrow ideas | The abstract reports provenance marking of untrusted input cutting attack success from over 50% to under 2% on GPT models (paper-reported) |
| [Outside the Prompt](https://zenodo.org/records/23867645) | abstract only | observational study | unreviewed report | borrow ideas | The abstract reports that no client starts a repo-declared MCP server before the user answers, but 5 of 6 pre-select the permissive answer (paper-reported) |
| [Deep Agentic Search](https://arxiv.org/abs/2608.01507) | abstract only | experiment | preprint | borrow ideas | The abstract reports semantic search answering 65.2% correctly against 46.2% for grep by subagents, with 41.8% of the subagent failures at the planner-subagent hand-off (paper-reported) |
| [For Coding Agents, the Repository Matters](https://arxiv.org/abs/2606.28235) | read in part (abstract, I, III-G, III-H, IV-C summary, V-B) | observational study | preprint | borrow ideas | The preprint reports between-repo variance larger for agent PRs than for human PRs, and context files in force in 53.5% of repos (paper-reported) |
| [When LLMs Lag Behind](https://arxiv.org/abs/2604.09515) | abstract only | experiment | preprint | borrow ideas | The abstract reports 42.6% of code running in the target environment without docs and 66.4% with structured docs (paper-reported) |
| [LibEvoBench](https://arxiv.org/abs/2606.25402) | abstract only | experiment | preprint | borrow ideas | The abstract (a workshop paper, per the authors) reports that stating the version doesn't help while relevant docs do (paper-reported) |
| [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) | abstract only | experiment | preprint | borrow ideas | The abstract reports context files not raising success and adding over 20% cost (paper-reported) |
| [WideSWE](https://arxiv.org/abs/2609.33382) | abstract only | experiment | preprint | borrow ideas | The abstract reports cross-repo tasks succeeding 10.8-42.5% of the time, helped by joint access to related repos (paper-reported) |

The other papers found were read as abstracts only, except where a row says otherwise. Each addresses one of the topics above, and none adds a finding beyond the papers in the main table, so each is classed reject for this need:

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [Trojan Horse](https://arxiv.org/abs/2610.23109), [Beyond the Payload](https://arxiv.org/abs/2608.30686), [Security Impact of Coding Agent's Memory Files](https://arxiv.org/abs/2610.38521), [Aletheia](https://arxiv.org/abs/2609.39678), [CodeSentinel](https://arxiv.org/abs/2606.19235), [XOXO](https://arxiv.org/abs/2503.14281), [ImportSnare](https://arxiv.org/abs/2509.07941), [CARI](https://arxiv.org/abs/2610.38799), [QueryIPI](https://arxiv.org/abs/2510.23675), [Agent Skills Enable … Prompt Injections](https://arxiv.org/abs/2510.26328), [The Attacker's Shell](https://arxiv.org/abs/2605.25871), ["Your AI, My Shell"](https://arxiv.org/abs/2509.22040), [Agent Data Injection](https://arxiv.org/abs/2607.05120), [IPI in the Wild](https://arxiv.org/abs/2604.27202), [Deep-Research Agents Poisoned via UGC](https://arxiv.org/abs/2605.24245), [Can It Reach the Generator?](https://arxiv.org/abs/2605.28017), [Step-Zero Attack](https://arxiv.org/abs/2611.01953), [AgentXploit](https://arxiv.org/abs/2609.31318) | abstract only | experiment (The Attacker's Shell: qualitative study; Memory Files and Agent Skills Enable: weak experiment; IPI in the Wild: observational study) | preprint (Beyond the Payload, XOXO, ImportSnare: peer-reviewed) | reject | The abstracts report injection and poisoning through repository files, documentation, tool output and metadata (paper-reported) |
| [Design Patterns for Securing LLM Agents](https://arxiv.org/abs/2506.08837), [CaMeL](https://arxiv.org/abs/2503.18813), [AI Agents May Always Fall for Prompt Injections](https://arxiv.org/abs/2605.17634), [Prismata](https://arxiv.org/abs/2607.08147), [Untrusted Content Masking](https://arxiv.org/abs/2607.05277), [Lingering Authority](https://arxiv.org/abs/2606.22504), [Rethinking Access Control for AI Agents](https://arxiv.org/abs/2611.06764), [Balkanization of Execution-Security Research](https://arxiv.org/abs/2607.05743), [Permission Manifests for Web Agents](https://arxiv.org/abs/2601.02371), [Context Lockfile](https://zenodo.org/records/23629676) | abstract only | Design Patterns, Permission Manifests, Context Lockfile: untested proposal; Rethinking, Balkanization, Always Fall: qualitative study; Lingering Authority: weak experiment; the rest: experiment | preprint (Context Lockfile: unreviewed report) | reject | The abstracts propose or survey defenses by design: capabilities, separation of control and data, redaction, permission manifests (paper-reported) |
| [Agent Approval Laundering](https://arxiv.org/abs/2609.28586), [Approval Laundering: Approval-Execution Binding Failures](https://arxiv.org/abs/2609.38983), [How Agents Ask for Permission](https://arxiv.org/abs/2607.13718), [Do User-Authored Permission Policies Improve Protection Against Overreach?](https://arxiv.org/abs/2608.27443) | abstract only | experiment (How Agents Ask: qualitative study) | preprint | reject | The abstracts study what an approval covers and how permission policies are written and reviewed (paper-reported) |
| [Census of AGENTS.md and CLAUDE.md](https://arxiv.org/abs/2610.31715), [Do Coding Agents Follow AGENTS.md?](https://arxiv.org/abs/2611.04367), [RepoNorm](https://arxiv.org/abs/2610.07757), [Agent READMEs](https://arxiv.org/abs/2511.12884), [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250), [Configuration Smells in AGENTS.md](https://arxiv.org/abs/2606.15828) | abstract only | observational study (Follow AGENTS.md: weak experiment; RepoNorm, Do Context Files Help: experiment) | preprint (Agent READMEs, Do Context Files Help: peer-reviewed) | reject | The abstracts study what context files contain and whether agents follow them (paper-reported) |
| [GitChameleon 2.0](https://arxiv.org/abs/2507.12367), [When LLMs Meet API Documentation](https://arxiv.org/abs/2503.15231), [HTTP Behavioral Signatures in Documentation Portals](https://arxiv.org/abs/2604.02544), [SWE-Chain](https://arxiv.org/abs/2605.14415), [CASE](https://arxiv.org/abs/2610.38800) | abstract only | experiment (HTTP Signatures: observational study; CASE: weak experiment) | preprint (GitChameleon: peer-reviewed; HTTP Signatures: peer review covers only a 2-page workshop abstract) | reject | The abstracts report version-matched documentation improving generated code, and how agents fetch docs (paper-reported) |
| [LLM Agents Can See Code Repositories](https://arxiv.org/abs/2606.14061), [The Code of Theseus](https://arxiv.org/abs/2610.20068), [CrossSWE](https://arxiv.org/abs/2611.01484), [The Mechanics of a Swarm](https://arxiv.org/abs/2609.12748) | abstract only (Code of Theseus: read in part, abstract and introduction) | experiment (Swarm: observational study) | preprint | reject | The abstracts cover repository views, design recovery and cross-repo benchmarks, none about reading pinned clones (paper-reported) |

## Worth retrieving manually

Each of these was read as an abstract only, and its abstract bears on the verdict. Open full text is available legally for each through its arXiv page, linked here:
- [From Approval to Abuse](https://arxiv.org/abs/2610.22987) (no DOI): whether committed deny rules alone hold against allow-rule elicitation.
- [Measuring the Permission Gate](https://arxiv.org/abs/2604.04978) (no DOI): how auto mode treats edits inside the project, which bears on the in-repo layout.
- [Stale Instruction Files Override the Code](https://arxiv.org/abs/2610.30571) (no DOI): the channel finding behind keeping clone text out of the session's opening context.
- [Overeager Coding Agents](https://arxiv.org/abs/2605.18583) (no DOI): the rate of unrequested edits that the deny rule guards against.
- [Authority Is Not a String (CapScope)](https://arxiv.org/abs/2609.08371) (DOI 10.1145/3843750.3843843): capabilities fixed before reading, relevant to a read-only reader subagent. The ACM page or a library is a second route.
- [Deep Agentic Search](https://arxiv.org/abs/2608.01507) (no DOI): the hand-off failure rate behind not making a reader subagent the default.
- RepoGuardBench (no link found; no DOI): a 2026 DL4Code workshop paper on injection through repository files, cited in [From Approval to Abuse](https://arxiv.org/abs/2610.22987). It can be reached through the DL4Code 2026 program page or by asking its author.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Claude Code 2.1.319 docs (memory, skills, permissions, settings, sandboxing, large codebases); apm 0.35.0 pinned in this repo's `mise.toml`, with `apm.lock.yaml`; git 2.53; mise; Renovate managers and the git-refs datasource |
| Earlier notes and decisions | searched | The 2026-10-19 note; the federated knowledge-base note (verdict item 6); the source-calibration leads; no decision records on this topic |
| GitHub repository search | searched | Rounds 1-2, each with a star floor and with only a recent-push filter: "reference repositories", "repos manifest lock", "git vendor lock", "vendir", "clone manifest yaml", "repos lockfile sha", "llms.txt clone", "agent docs repos", "external repos context", "read-only repos mcp", "multi repo workspace", "reference repos", "reference repositories agents", "shelffile". Round 3: "OpenCode-style references", "context routes agents", "packref", "materialize reference repos", "package references agents" (recent-push filter), "references claude code clone repos" (recent-push filter). Round 4: "project references agent", "available_references", "references extension pi/codex", "references plugin claude code", "reference directories agent", "claude code hook references index", plus a forks check of the Pi ports |
| GitHub topics | searched | `multi-repo`, `multirepo`, `repository-management`, `vendoring`, `git-dependencies`, `llms-txt`, `reference-repos`, `agent-context`, `llm-context`, `multi-git` |
| GitHub code search | searched | "reference clones" llms.txt; `vendir.yml` git refs; "west update" and "vcs import" in `mise.toml`; `additionalDirectories` with reference repos; READMEs naming [agent-reference](https://github.com/mutewinter/agent-reference), [devrefs](https://github.com/Blankeos/devrefs), [ingraft](https://github.com/gunta/ingraft) or [vendor-src](https://github.com/KATT/vendor-src); "safe.bareRepository" with agents |
| GitHub topics for agent skills | searched | `agent-skills` with git; `claude-code-skill` with git clone; `agent-skills` with reference |
| GitLab and Codeberg search | searched | GitLab: "multi repo manifest", "reference clones", "repos lock file". Codeberg: "multirepo", "vendoring", "repos", "llms" (single words; the multi-word queries "multi repo", "repos manifest" and "vendoring git" returned nothing) |
| npm | searched | "multi repo manifest", "git repositories lock", "vendor git files", "reference repositories", "git subtree reference", "context routes", "references opencode plugin", "reference lock agents sha", "project references agent"; `keywords:reference-repos`, `keywords:reference,agents`, `keywords:clone,agents`, `keywords:references,opencode`, `keywords:opencode,reference`, `keywords:references,agent`, `keywords:pi-extension,references`, `keywords:claude-code,references`, `keywords:vendir` |
| PyPI | unavailable | Keyword search returns a JavaScript challenge page, and PyPI has no search API. Candidates' PyPI entries were read by name (west, vcs2l, all-repos, metagit-cli, dfetch, apm-cli), and ecosyste.ms covered keywords |
| crates.io | searched | API search "multi repo manifest", "git repositories lock", "reference repositories"; sparse index and crate downloads for gitopolis, ripvcs, repoverse, devrefs |
| Language registries | searched | pkg.go.dev: "multi repo manifest", "git repositories lock", "reference repositories", plus ripvcs, vendir, git-get |
| libraries.io | searched | "reference repositories", "multi repo manifest", "vendor git repositories" (key from the settings file) |
| Homebrew formulae | searched | Regex over names and descriptions (multi-repo, vendir, vendor, manifest, repos, llms, reference); exact names of the candidates |
| nixpkgs | searched | The same regex over `pname` and description; exact names |
| AUR | searched | "multi repo", "multiple git repositories", "repositories manifest", "vendir", "reference repos", "repos sync", candidate names |
| ecosyste.ms | searched | Keywords `multirepo`, `vendoring`, `llms-txt`, `reference-repos`, `multi-repo`, `agent-context` |
| LibHunt | searched | Alternatives pages for [west](https://github.com/zephyrproject-rtos/west), [vcstool](https://github.com/dirk-thomas/vcstool), vcs2l (404) and myrepos (no link found) |
| Cross-language equivalents | searched | vendir alternatives in other languages; vcstool-style tools in Go and Rust; agent reference tools in TypeScript, Rust, Go and Python |
| Awesome lists | searched | "awesome monorepo multi-repo management tools"; awesome-monorepo's repository-management sections |
| alternativeto.net | searched | Through web search only: alternatives to vcstool, to west, and to vendir (no alternativeto.net pages surfaced) |
| aitoolnet.com | searched | Sitemap slugs grepped for repo, clone, codebase context, docs MCP, llms.txt, vendor and dependency source; the Context7 and DeepWiki alternatives pages and ten tool pages read. Only indexers, hosted documentation services and memory tools turned up, none keeping pinned clones |
| General web search | searched | Tools that clone external repos read-only for coding agents; giving Claude Code read access to other repositories; multi-repo manifest with a SHA lock file; "reference repos" for coding agents; OpenCode's references feature; packref and comparisons; prompt injection through repo files |
| Hosted services | searched | Context7 and DeepWiki alternatives with version-specific docs (GitMCP, Ref Tools, Docfork, Nia, Moxie): hosted, so they fail "works offline" |
| Skill directories | searched | skills.sh: "reference repos", "clone repo", "library source", "dependency source", "other repositories", "llms.txt", "cross repo", "shelf", "agent reference", "ingraft", "vendor src", "opensrc", "read-only roots", "packref", "references" |
| Claude Code plugin marketplaces | searched | Anthropic's marketplace file (317 plugins), grepped for clone, source, dependency, reference, multi-repo, llms |
| MCP Registry | searched | clone, repository, repositories, git, docs, llms, filesystem, readonly, workspace, reference, vendor |
| PulseMCP | excluded | Its robots.txt disallows ClaudeBot (fetched 2026-11-06); the MCP Registry and awesome-mcp-servers cover the same MCP servers for this need |
| Anthropic's skills repo | searched | Skill list and frontmatter read; none relevant |
| Awesome lists for agent skills | searched | awesome-mcp-servers (read-only filesystem, git and docs servers; the File Systems section); three awesome lists for Claude skills, grepped for clone and reference |
| arXiv | searched | Unavailable in round 1 (HTTP 429 after a retry). Searched in rounds 2-5 by ID and by `abs:` phrases: "reference repositories", "repository poisoning", "git hooks" with agent, "bare repository", "coding agents" with documentation, "agent-native filesystem", "scope expansion" with agents, "allow rules" with agent. Abstract and HTML pages were read throughout |
| OpenAlex | searched | "prompt injection coding agent repository", "indirect prompt injection code agents", "malicious repository coding assistant attack", "AGENTS.md context files coding agents", "version-specific API code generation library", "reference repositories coding agents", "read-only source code access coding agent MCP"; `cites:` lookups |
| OpenAIRE | searched | "prompt injection coding agents repository", "context lockfile coding agents", "llms.txt agents" |
| Semantic Scholar | searched | Citations of 2608.14876, 2610.14488, 2610.38361 and 2605.18583. 2609.08371 and 2610.30571 stayed throttled after a retry; 2604.13536 and 2610.22987 were throttled on the first call. OpenAlex `cites:` was used for all four |
| papers.cool | searched | "prompt injection coding agent repository", "repository poisoning coding agents", "context files coding agents", "llms.txt" |
| Hugging Face papers | searched | "prompt injection coding agents repository files", "malicious repository coding agent", "AGENTS.md context file security", "documentation retrieval coding agents" |
| Zenodo | searched | Record pages only, by ID, for the replication packages and reports found through other routes (records 23504056, 19229174, 23629675, 23867644); no keyword search |
| Crossref | excluded | Its trigger, a classic software-engineering approach, doesn't match an LLM-agent security question, and no DOI needed resolving beyond OpenAlex's |
| Europe PMC | excluded | A life-sciences index; the need is software security |
| Venue program pages | excluded | The venues met (CAMLIS, IEEE FLLM and DL4Code 2026) were reached through their papers' arXiv pages. DL4Code 2026's program page is the route for the open RepoGuardBench lead, listed under Worth retrieving manually |

## Snowball rounds

The rounds were coordinated. Each subagent searched its own set of services for one round. The main agent then merged every subagent's finds into the next round's seeds, and all subagents ran that round.

- **Round 1** (the queries above, plus the developer's leads):
  - multi-repo tools: [vendir](https://github.com/carvel-dev/vendir), [ripvcs](https://github.com/ErickKramer/ripvcs), [agent-reference](https://github.com/mutewinter/agent-reference), [shelf](https://github.com/Rika-Labs/shelf), [devrefs](https://github.com/Blankeos/devrefs), repoverse (no link found), [vendor-src](https://github.com/KATT/vendor-src), [metagit-cli](https://github.com/metagit-ai/metagit-cli), [ingraft](https://github.com/gunta/ingraft), [graft](https://github.com/min0625/graft), [dotdeps](https://github.com/davidturnbull/dotdeps), [filedist](https://github.com/flaviostutz/filedist), [OpenSpec Stores](https://github.com/Fission-AI/OpenSpec), [momentum](https://github.com/LiminaLabsAI/momentum), [docflow](https://github.com/EvolveHQ/docflow);
  - read-only access and index readers: [local-workspace-mcp](https://github.com/peter4leadson/local-workspace-mcp), the [MCP filesystem server](https://github.com/modelcontextprotocol/servers/tree/36380287ed3b15d115b55f546617d723072b1296/src/filesystem), [filesystem-mcp](https://github.com/j0hanz/filesystem-mcp), [mcpdoc](https://github.com/langchain-ai/mcpdoc);
  - reference skills: [librarian](https://github.com/mitsuhiko/agent-stuff/tree/0865c849befd2021490679f96a8dee58c84ac857/skills/librarian), [explore-repo](https://github.com/sjunepark/agent-scripts/tree/03cfe3258c426f6c67a1ecdb32eac60fb6db64fc/skills/explore-repo), [dependency-docs](https://github.com/juanmarin-co/skills/tree/18988b8f11782c5ba303df03e811de4e1ca42c2f/skills/dependency-docs);
  - 40 papers.
- **Round 2** ("reference repositories", "shelffile", "worktree per version", the `reference-repos` topic, backward and forward citations): [packref](https://github.com/adelrodriguez/packref), [OpenCode references](https://github.com/anomalyco/opencode), [pi-references](https://github.com/alexanderop/pi-references), the [consult-references skill](https://github.com/0x0f0f0f/research-engineering-skills/tree/06e4bd0312385f4d09d731ffb11a4b672eb2629c/skills/consult-references), [depot](https://github.com/acoyfellow/depot), [skillpluck](https://github.com/samettemizer/skillpluck), the [Effect team's post](https://effect.website/blog/the-one-weird-git-trick-that-makes-coding-agents-more-effect-ive/), and 23 papers on repository poisoning and data injection.
- **Round 3** ("OpenCode-style references", "context routes", "package references"):
  - [offworld](https://github.com/oscabriel/offworld);
  - two more Pi ports, [Alurith/pi-references](https://github.com/Alurith/pi-references) and [jeremyosih/pi-references](https://github.com/jeremyosih/pi-references);
  - the packref details;
  - two papers on overeager and filesystem-misusing agents.
- **Round 4** (narrow: "project references", "available_references", forward citations of round 3's papers):
  - no software candidate that could change the shortlist ([refs](https://github.com/kaisers-io/refs), [skill-reference-dirs](https://github.com/kennethfan/skill-reference-dirs), [repo-pattern-miner-plugin](https://github.com/prodm93/repo-pattern-miner-plugin), [pi-references-extension](https://github.com/ethanfritzt/pi-references-extension));
  - three papers on approvals, one of them serious ([From Approval to Abuse](https://arxiv.org/abs/2610.22987)).
- **Round 5** (literature only: references and citations of that paper, "allow rules" with agents):
  - one serious paper ([Measuring the Permission Gate](https://arxiv.org/abs/2604.04978)) and two peripheral ones;
  - one open lead, RepoGuardBench (no link found), listed under Worth retrieving manually.

The software routes converged: rounds 3 and 4 added nothing that could change the shortlist. The literature routes never met the prior-art-search skill's stop condition. Each of rounds 4 and 5 added one serious paper, but on the adjacent topic of permission approvals, and both refine the deny rules rather than the choice of tool. The search stopped there, short of the skill's 10-round cap. That leaves the paper list open at its edges, and it doesn't affect a blend verdict.

## Refresh trigger

The note backs the template's choice of clone manager. Refresh it on the first of these:
- any follow-up check under Could not verify fails;
- vendir:
  - accepts the fix in item 1 or 2 on [the vendir feedback page](../tool-feedback/vendir.md) (then simplify the task script);
  - changes how it sets `remote.origin.tagOpt`, or stops passing its environment to git, which would break the task script's override;
  - changes its submodule default;
  - stops keeping `.git` in a git content;
  - adds parallel sync;
  - stops releasing;
- Renovate's vendir manager changes its datasource or its artifact handling;
- Claude Code:
  - adds a path exclusion for nested skills;
  - changes what `additionalDirectories` loads;
  - changes what its searches skip;
  - changes when it reads `AGENTS.md`, or how a symlinked or importing `CLAUDE.md` counts;
- a west release adds path filtering, a lock file or parallel update;
- exact restore of tracked branches becomes a requirement;
- 2027-11-06.
