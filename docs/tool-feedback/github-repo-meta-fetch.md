# github-repo-meta-fetch feedback

[github-repo-meta-fetch](https://github.com/demosdemon/github-repo-meta-fetch) has the design the issue mirror in [the federated knowledge note](../prior-art/2026-11-06-federated-knowledge-and-work-items.md) would borrow; with releases it could be adopted instead. Not yet raised upstream.

## Open items

### 1. No releases or published package

- **What:** the only install route is `cargo install --git`, with no tags, releases or crates.io package (checked at 83df59c).
- **Impact:** it can't be pinned to a version that Renovate updates.
- **Suggested fix:** tagged releases, ideally with binaries or a crates.io publish.

### 2. A generated `CLAUDE.md` in the output tree

- **Where:** `render/mod.rs:211-245` at 83df59c.
- **What:** the render writes a schema guide named `CLAUDE.md` into the output directory. If the mirror is committed inside a repo, Claude Code loads that file as instructions.
- **Suggested fix:** an option to name the guide differently or skip it.

### 3. Deletions are reconciled only by an explicit full sync

- **Where:** `sync/mod.rs:154-165,242-249` at 83df59c.
- **What:** deleted or transferred issues never appear in an incremental listing, so they stay in the mirror until someone runs `--full`.
- **Suggested fix:** an option for a periodic full reconcile (for example, every Nth run or after N days).
