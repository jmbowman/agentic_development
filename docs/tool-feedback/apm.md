# APM feedback

Bugs and proposed enhancements for [APM](https://github.com/microsoft/apm), which installs this repo's pinned LID skills (`mise run skills`, [repo setup](../intent/repo-setup/repo-setup-design.md)).

None of the items below has been raised upstream.

## Bugs

### 1. Skills deployed by APM 0.33.0 block a dependency bump under 0.35.1

- **Where:** `apm install --frozen`, after the manifest and lock file move a dependency to a new version.
- **What:** when the dependency's deployed files were written by APM 0.33.0, APM 0.35.1 refuses to replace them. It reports, for each file, "no trustworthy local deployment baseline. Move the conflicting file aside and retry; use --force only to intentionally overwrite it", and installs nothing. Every deployed file still matched the hash the old lock file recorded, so there was nothing local to protect.
- **Evidence (2026-11-14):** in a scratch copy of this repo at the LID 1.4.0 lock, `apm install --frozen` with APM 0.33.0, then the LID 1.4.5 manifest and lock file and `apm install --frozen` with 0.35.1, failed with 17 errors (one per deployed file). The same steps with the first install done by APM 0.35.0, or with no first install, succeeded. Moving the three deployed skill directories aside let 0.35.1 install 1.4.5.
- **Suggested fix:** when no baseline exists from the installing version, accept a deployed file whose content matches the hash the current lock file records for it, and replace it as usual.
- **Who it affects:** this repo pins APM 0.35.1 (`mise.toml`), so a clone whose skills were first installed by 0.33.0 hits it on its next LID bump; a clone installed by 0.35.0 or later doesn't.
- **Workaround:** move the dependency's deployed skill directories out of `.claude/skills/`, then run `mise run skills`. They're gitignored and reinstalled from the lock file.
