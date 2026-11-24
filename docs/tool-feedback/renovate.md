# Renovate

Items found while planning scripts that declare their dependencies in PEP 723 headers ([the harvest pipeline note](../prior-art/2026-11-07-search-harvest-pipeline.md)). All were read in the source of Renovate 44.212.0, the version this repo pins, under `dist/modules/manager/`.

## The `pep723` manager doesn't update script lock files

- **Where:** `pep723/index.js:6-19`. The manager exports `extractPackageFile` but no `updateArtifacts`, unlike `pep621`, which has `artifacts.js`.
- **What:** Renovate bumps a version in a script's inline metadata, but leaves a uv script lock file (`<script>.py.lock`, written by `uv lock --script`) as it was. The bumped header and the stale lock then disagree until someone runs `uv lock --script`. On the hosted app a post-upgrade task can't run it either, since the app's allowlist holds only `git add --all`, `git reset` and `pwd` (as [this repo's HLD](../high-level-design.md) records for `mise lock`).
- **Evidence:** the manager's exports, read in source; a listing of `pep723/` shows no artifacts module.
- **Suggested fix:** an `updateArtifacts` for `pep723` that runs `uv lock --script <file>` when a lock file sits beside the script, as the `pep621` manager does for `uv.lock`.
- **Raised upstream:** not checked; search Renovate's issues and discussions before filing.

## The `pep723` manager can't update a git-pinned dependency

- **Where:** `pep723/schema.js:7-15` parses only `requires-python` and `dependencies`, each dependency through `pep508ToPackageDependency` (`pep621/utils.js:7,33-47`), which always uses the PyPI datasource. Its regular expression takes everything after the name, up to any `;` marker, as the version.
- **What:** a direct reference such as `paper-search-mcp @ git+https://github.com/openags/paper-search-mcp@<sha>` gets the version `@ git+…`, which PyPI can't resolve, so the commit is never bumped. Script metadata's `[tool.uv.sources]` table is ignored too. The `pep621` manager handles git sources there (`pep621/processors/uv.js:49`, `applyGitSource`), but `pep723` never reads it.
- **Evidence:** inferred by reading the code, not by running Renovate. A custom regex manager using the `git-refs` datasource can bump the commit instead.
- **Suggested fix:** read `[tool.uv.sources]` in `pep723` the way the `pep621` uv processor does, and recognize PEP 508 direct references (or skip them with a clear `skipReason`).
- **Raised upstream:** not checked.

The manager is also off unless configured: its `managerFilePatterns` default is empty (`pep723/index.js:18`).

## The `vendir` manager silently skips a git source pinned by commit

Found while choosing how to keep the task tool's vendored YAML parser current (the task-tracker LLD's *Reading YAML*), in Renovate 44.257.5.

- **Where:** `manager/vendir/extract.js` (`extractGitSource`) puts a git content's `ref` in `currentValue`, with no `currentDigest`, and uses the `git-refs` datasource, which sets no default versioning (`datasource/git-refs/index.js`).
- **What:** a `git` content pinned to a full commit SHA, the only exact pin for a repo that publishes no tags, gets no update, and the dependency carries no skip reason or warning. A stale pin goes unnoticed. A branch ref (`origin/main`) is at least skipped visibly, as `invalid-value`, with the debug message "no currentDigest or pinDigests".
- **Evidence:** a local-platform `--dry-run=lookup` on a `vendir.yml` pinning oneyaml-python to a commit two behind `main` returned `updates: []` and `warnings: []` (2026-11-23).
- **Suggested fix:** when `ref` is a 40-hex SHA, extract it as `currentDigest` with the default branch as `currentValue`, as the regex manager's git-refs pattern allows, so digest updates work; failing that, give the dependency a `skipReason`.
- **Workaround here:** `ref: origin/main` with the committed lock, refreshed by lock-file maintenance, whose vendir artifact step runs `vendir sync`.
- **Raised upstream:** not checked.
