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
