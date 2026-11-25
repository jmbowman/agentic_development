# oneyaml

Feedback for [oneyaml-python](https://github.com/recursive-ai-oss/oneyaml-python), whose pure-Python backend the task tool vendors (the task-tracker LLD's *Reading YAML*). Read in source at f41c222 (2026-11-11). None of these has been raised upstream. The project page says the Python version is paused, so these may wait until it resumes.

## No releases or tags

- **Where:** the repository: `git ls-remote --tags` lists nothing; `pyproject.toml` has `version = "0.1.0.dev0"`, and `CHANGELOG.md` has only an `[Unreleased]` section.
- **What:** with no tags, a consumer can pin only a commit. Dependency bots then can't propose updates by version: Renovate's vendir manager finds no update for a commit pin ([Renovate feedback](renovate.md)), so this repo follows `main` through a vendir lock refreshed by lock-file maintenance instead, and every upstream commit reaches it, finished or not.
- **Evidence:** the listing and files above; a Renovate dry run on a commit pin (2026-11-23).
- **Suggested fix:** tag releases, even `0.x` ones, at points meant for use; a GitHub release per tag would also let tools read a release date.

## An invalid `ONEYAML_BACKEND` stops the import

- **Where:** `src/oneyaml/__init__.py:63-69` (`_select`).
- **What:** a value other than `auto`, `native` or `pure` raises `ValueError` at import time, so a stray or misspelled variable in a shell breaks every program that imports oneyaml, including ones that never chose a backend. This repo's tool sets the variable itself before importing to stay clear of it.
- **Evidence:** read in source.
- **Suggested fix:** warn and fall back to `auto` for an unknown value, keeping the error for an explicit `native` that can't load; or document that the variable is read at import and must be valid.

## The published conformance results are empty

- **Where:** `docs/conformance.md`, *Results*: the generated block between `<!-- generated:conformance-line -->` and `<!-- end generated -->` holds nothing.
- **What:** the README says each backend is scored against the yaml-test-suite, but no pass rate is published, so a consumer can't see how the pure backend does without running the suite.
- **Evidence:** read at f41c222.
- **Suggested fix:** commit the generated results with each release, or link the CI run that produces them.
