# vendir feedback

[vendir](https://github.com/carvel-dev/vendir) is the clone manager chosen in [the reference-clones note](../prior-art/2026-11-06-agent-reference-clones.md). These items come from reading vendir 0.46.3's source and running it on Linux, on 2026-11-07. The runs used throwaway local repos (branches, tags, a submodule and agent-instruction files) and public GitHub repos (pytest, qtbase and six smaller tools). Not yet raised upstream.

## Open items

### 1. A locked or pinned SHA that isn't a branch or tag tip can't be fetched at a shallow depth

- **Where:** at v0.46.3 (43e80d11):
  - `pkg/vendir/cmd/sync.go:100-111` applies the lock;
  - `pkg/vendir/config/directory.go:349-358` sets `ref` to the bare SHA;
  - `pkg/vendir/fetch/git/git.go:186-197,236-241` fetches;
  - `pkg/vendir/fetch/git/git.go:219` checks out.
- **What:**
  - `vendir sync --locked` replaces `ref` with the lock's SHA. The fetch is then `git fetch origin --depth N`, which brings only the last N commits of each branch and tag, so at depth 1 only the tips.
  - `git checkout <sha>` then fails with "unable to read tree" once the SHA is out of that range. A `ref` set to such a commit fails the same way on a first sync.
  - So with `depth: 1`, a lock restores exactly only until a tracked branch moves upstream. With `depth: 0` it works, at the cost of every branch's full history.
- **Evidence:** at `depth: 1`, a commit pin one commit behind `main` failed, and a `--locked` restore failed after upstream advanced a tracked branch. Both passed at `depth: 0`.
- **Suggested fix:** when `ref` is a full SHA, fetch it directly (`git fetch origin <sha> --depth N`). GitHub and most hosts allow fetching a reachable SHA. Fall back to the current fetch if the server refuses.

### 2. Every tag is fetched, even for a branch or SHA ref

- **Where:** `pkg/vendir/fetch/git/git.go:181` (`config remote.origin.tagOpt --tags`) at v0.46.3 (43e80d11).
- **What:** with `ref: origin/main` and `depth: 1`, the fetch still brings the tip of every tag.
  - pytest through vendir: 226 commits, 20 MB and 3.8 s, against 12 MB and 0.65 s for a plain `git clone --depth 1 --single-branch --no-tags`.
  - qt/qtbase: git running vendir's fetch sequence (init, `tagOpt --tags`, `fetch origin dev --depth 1`) took 63 s and 426 MB with its 294 tags, and 8.4 s and 68 MB with `--no-tags`.
- **Workaround (tested):** vendir passes its environment to git, so `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.tagOpt GIT_CONFIG_VALUE_0=--no-tags` overrides the setting.
  - With it, vendir took 1.0 s for pytest and 9.9 s for qtbase, and the lock recorded no `tags` for those entries.
  - It breaks tag pins, whose tag is then never fetched, so it can only be used for branch entries synced one at a time.
- **Suggested fix:** skip tags when `ref` is `origin/<branch>` or a SHA, and fetch only the named tag for a tag ref (`git fetch origin refs/tags/<t>:refs/tags/<t> --depth N`). An option such as `fetchTags: false` would also do. The `tags` field in the lock would then come from the fetched tag, from `git ls-remote --tags`, or be left empty.

### 3. A branch ref must be named; there is no "default branch"

- **Where:** `pkg/vendir/fetch/git/git.go:186-197,236-241` at v0.46.3.
- **What:** `ref: origin/HEAD` and `ref: HEAD` both fail at checkout. An entry that should follow a repo's default branch therefore has to name it, and breaks if upstream renames it.
- **Suggested fix:** accept `origin/HEAD` by resolving the remote's default branch (`git ls-remote --symref origin HEAD`) before the fetch.

### 4. The kept `.git/config` points at a deleted credentials file

- **Where:** `pkg/vendir/fetch/git/git.go:95,149-155` at v0.46.3: the helper is configured at 149-155, and the credentials directory is removed at 95.
- **What:** each synced directory's `.git/config` keeps `credential.helper = store --file <staging dir>/…/.git-credentials`, a path vendir deletes after the sync. It is harmless, but it is surprising config to leave in a kept `.git`.
- **Evidence:** a synced clone's `credential.helper` named a file under `.vendir-tmp-<n>/incoming/git-auth/`, and no staging directory was left after the sync.
- **Suggested fix:** remove the helper setting before moving the clone out of staging, or keep the credentials file outside the repo's config.
