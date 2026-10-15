# Renovate preset specs

Design: [renovate-preset-design.md](renovate-preset-design.md). The preset is `renovate/default.json` in this repo. Consumer repos extend it as `github>jmbowman/agentic_development//renovate/default#<tag>`. "Resolved config" means the preset after Renovate applies its `extends` chain, as computed by the Renovate version pinned in this repo's mise config.

## Validity and base

- [x] **PRESET-001**: The Renovate preset (`renovate/default.json`) shall pass the config validator of the pinned Renovate version.
- [x] **PRESET-002**: The Renovate preset shall extend `config:best-practices`.

## Automerge

- [x] **PRESET-AUTO-001**: In the Renovate preset's resolved config, automerge shall be enabled for every update type (tested at least for `major`, `minor`, `patch`, `pin`, `pinDigest`, `digest`, `lockFileMaintenance` and `replacement`), except where PRESET-AUTO-003 disables it.
- [x] **PRESET-AUTO-002**: The Renovate preset shall use `automergeType` `pr` with `platformAutomerge` enabled.
- [x] **PRESET-AUTO-003**: The Renovate preset shall disable automerge for dependencies from Renovate's built-in `apm` manager whose `packageName` is `jszmajda/lid` (LID plugin pins in `apm.yml`, which need a manual `/update-lid` walk after merging), and Renovate's extraction of an `apm.yml` fixture shall produce a dependency that this rule matches.

## Supply-chain delay

- [x] **PRESET-AGE-001**: The Renovate preset shall set `minimumReleaseAge` to 3 days for every dependency not exempted by PRESET-AGE-002 to PRESET-AGE-004.
- [x] **PRESET-AGE-002**: The Renovate preset shall exempt from `minimumReleaseAge` every dependency handled by the copier manager (template versions come from the git-tags datasource, which has no release timestamps).
- [x] **PRESET-AGE-003**: The Renovate preset shall exempt from `minimumReleaseAge` every dependency from the `github-runners` datasource (runner images listed inside Renovate, with no release timestamps).
- [x] **PRESET-AGE-004**: The Renovate preset shall exempt from `minimumReleaseAge` the dependencies whose package name is `jmbowman/agentic_development` or matches the case-sensitive regex `^jmbowman/copier-[a-z]`.
- [x] **PRESET-AGE-005**: The Renovate preset shall not exempt any dependency from `minimumReleaseAge` by matching its owner alone (for example, `jmbowman/other`, `jmbowman/copierx`, `jmbowman/copier-1x` and `jmbowman/copier-X` wait the full delay).

## Ignored paths

- [x] **PRESET-PATH-001**: The Renovate preset's `ignorePaths` shall include each of Renovate's default ignore patterns: `**/node_modules/**`, `**/bower_components/**`, `**/vendor/**`, `**/examples/**`, `**/__tests__/**`, `**/test/**`, `**/tests/**` and `**/__fixtures__/**`.
- [x] **PRESET-PATH-002**: The Renovate preset's `ignorePaths` shall cause Renovate to ignore a consumer's `.config/copier-<name>/**` files at the repository root and every `.config/mise/conf.d/**` file at any depth, and shall not ignore a template repo's `template/.config/copier-<name>/**` sources.
- [x] **PRESET-PATH-003**: The Renovate preset's `ignorePaths` shall cause Renovate to ignore every file under a `.mise/locks/` or `.config/mise/locks/` directory at any depth, the dependency sidecars that `mise lock` writes.

## Lock-refresh commits

- [x] **PRESET-LOCK-001**: The Renovate preset's `gitIgnoredAuthors` shall be exactly `["lock-refresh@agentic-development.invalid"]`, the author of the lock-refresh workflow's commits.
