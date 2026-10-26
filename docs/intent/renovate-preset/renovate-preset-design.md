---
parent: high-level-design
prefix: PRESET
---

# Renovate preset

## Context and Design Philosophy

Each consumer's Renovate config file (`.github/renovate.json` on GitHub) holds one line that extends this repo's preset at a pinned tag. The preset carries the shared update policy: automerge everything once CI passes, except changes that need a human step before they can merge. It also delays third-party releases long enough for bad ones to be pulled, and keeps Renovate out of files that a template owns.

The preset file is `renovate/default.json`. Consumers extend it as `github>jmbowman/agentic_development//renovate/default#vX.Y.Z`, and Renovate's renovate-config manager bumps that tag.

## Policy

**Base.** Extends `config:best-practices`:
- Renovate's recommended defaults;
- GitHub Actions and reusable-workflow references pinned by digest, with the tag as a comment (consumer CI stubs end up as `check.yml@<sha> # vX.Y.Z`);
- automatic migration of deprecated config;
- weekly lock-file maintenance.

**Automerge.**
- All update types automerge, majors included.
- The automerge type is `pr` with platform-native automerge (Renovate's defaults). Every update gets a PR, and GitHub merges it as soon as the required checks pass. A PR left open means its update needs attention.
- **Consumer repo settings** that this needs:
  - "Allow auto-merge" enabled;
  - a branch rule on the default branch that requires the CI check to pass.

  Without a required check, GitHub would merge an automerge-enabled PR before CI finishes. Applying these settings is part of onboarding a repo.
- A copier update that conflicts is reported by Renovate as an artifact error, which blocks automerge. The conflict-marker check in each repo's `check` task is a second guard, which also covers updates run by hand.

**Exceptions to automerge.**
- **LID pins.** APM dependencies from the `jszmajda/lid` repository never automerge (`matchManagers: ["apm"]`, `matchPackageNames: ["jszmajda/lid"]`; Renovate's apm manager sets `packageName` to the repository and `depName` to the plugin path). Such an update needs a `/update-lid` walk of the project's design docs, which a bot can't do. A person runs it on the update's branch and pushes the result, and the repo's LID version check fails until they do (HLD: *LID pin bumps are the one exception to automerge*).
- **APM lock files.** `config:best-practices` turns on Renovate's weekly lock-file maintenance, and the apm manager supports it: it deletes `apm.lock.yaml`, reruns `apm install` beside the manifest, and opens a PR only if the lock file changed (verified in Renovate 44.167.7's `modules/manager/apm/`). Tag pins re-resolve to the same commits, so such a PR is rare, and it automerges like any other. Consumers' template-owned lock files sit under the ignored `.config/copier-*/**`, so maintenance runs only where a repo owns its manifest: this repo and the template repos. It needs `apm` in Renovate's environment, as an apm pin bump does.

**Supply-chain delay.**
- `minimumReleaseAge` is 3 days, so third-party releases wait before Renovate proposes them.
- **Untimed datasources are exempt.** Renovate holds an update with no release time forever under a minimum age, so the delay can't apply to these:
  - GitHub runner images (`matchDatasources: ["github-runners"]`), whose versions come from a list built into Renovate;
  - copier templates, as below.
- **Copier templates are exempt** (`matchManagers: ["copier"]`). Renovate tracks template versions through the git-tags datasource, which reports no release time, and Renovate holds untimed updates under a minimum age forever. The delay can't apply to them, whoever publishes the template.
- **This system's own repos are exempt**, so a fix released here reaches consumers without waiting. The rule matches `jmbowman/agentic_development` and `jmbowman/copier-*` by package name, which is how the renovate-config and github-actions managers name them.
- Lock-file maintenance isn't covered by `minimumReleaseAge`. Python lock files get the same delay from uv's own `exclude-newer = "3 days"`, which each Python template renders in a template-owned `uv.toml`.

**Ignored paths.** `ignorePaths` replaces Renovate's defaults rather than adding to them, so the preset lists:
- Renovate's defaults: `**/node_modules/**`, `**/bower_components/**`, `**/vendor/**`, `**/examples/**`, `**/__tests__/**`, `**/test/**`, `**/tests/**`, `**/__fixtures__/**`;
- `.config/copier-*/**`, anchored at the repo root, and `**/.config/mise/conf.d/**` at any depth. In a consumer, a template's directory and the `conf.d` links into it are template-owned and change only through template releases. In a template repo, the fragment under `template/.config/copier-<name>/` doesn't match and gets updated normally, while the template's own `conf.d` link is ignored, so Renovate never sees the same pins twice. A template release then carries the new pins to consumers.
- `**/.mise/locks/**` and `**/.config/mise/locks/**`, where `mise lock` writes the dependency sidecars for npm and Python tools (for an npm tool, a `package.json` and an `aube-lock.yaml`). Renovate's npm manager would otherwise extract a sidecar's `package.json` as a project and bump the tool separately from its mise pin, breaking the digest `mise.lock` records (verified with Renovate 44.149.1 and mise 2026.10.8). Renovate's mise manager rewrites sidecars itself when it updates `mise.lock`.

**Commits from the lock-refresh workflow.** `gitIgnoredAuthors` lists `lock-refresh@agentic-development.invalid`, the fixed author of the lock-refresh workflow's commits ([lock-refresh LLD](../lock-refresh/lock-refresh-design.md)). Renovate otherwise treats a PR with another author's commit as edited, and stops updating or rebasing it, so a later template release would leave the PR stale. When Renovate rebases, it drops the lock commit, and the workflow makes it again. `gitIgnoredAuthors` isn't a mergeable option, so a consumer that sets its own list replaces the preset's and must repeat this address (verified in Renovate 44.151.0's option definitions). The address is unique to that workflow, as Renovate requires: if another bot or person shared it, Renovate could force-push over their changes.

## Testing a release

Tests share the check workflow's pytest harness. Renovate runs as a command-line tool pinned in this repo's mise config (`npm:renovate`, with the Node version it requires), so the tests drive the real Renovate rather than reimplementing its matching. The repo contains no JavaScript of its own. Tests that run the Renovate CLI are marked `renovate`.

- **Offline:** `renovate --platform=local --dry-run=extract` on committed fixture repos, with the preset as each repo's `renovate.json`, as consumers use it. (Supplied as a global config file instead, its own `ignorePaths` would be replaced by those of the presets it extends.) Its debug log lists the package files Renovate extracted, which shows the ignore rules in effect (verified with Renovate 44.149.1 on Node 24).
- **Resolved config:** with `--print-config`, the log includes the fully resolved config, so rules from `config:best-practices` are checked together with the preset's own. Renovate decides automerge per branch after lookup, and its log doesn't record that decision per update, so the tests check the resolved rules and the dependency names the managers extract rather than lookup output.

This repo's CI, before a tag:
- runs Renovate's config validator on `renovate/default.json`;
- runs Renovate itself against fixture directories and checks its decisions:
  - `.config/copier-python/mise.toml` and `.config/mise/conf.d/copier-python.toml` are ignored;
  - `template/.config/copier-python/mise.toml` is not ignored, and `tests/fixtures/x/mise.toml` is ignored (this repo's fixtures keep fixed pins on purpose);
  - any copier dependency, and any `github-runners` dependency, is exempt from the delay;
  - `jmbowman/agentic_development` from the renovate-config and github-actions managers and `jmbowman/copier-python` are exempt, while `jmbowman/other`, `jmbowman/copierx` and an unrelated `github-tags` dependency are not;
  - the resolved config, after `config:best-practices` is applied, still automerges every update type except LID pins;
  - an APM dependency with `depName` `jszmajda/lid/plugins/linked-intent-dev` and `packageName` `jszmajda/lid`, as the apm manager sets them, doesn't automerge.

## Decisions & Alternatives

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Automerge scope | Everything, majors included, except LID pins | Patch and minor only | Tenet 5. Majors are where breakage shows up, and CI catches it before merge |
| Automerge type | `pr` with platform automerge | `branch` (Renovate pushes passing updates straight to the default branch); `pr` merged by Renovate on its next run | Every update leaves a reviewable PR, and the default branch can require PRs. Platform automerge merges as soon as checks pass instead of waiting for Renovate's next run. It needs two repo settings, applied at onboarding |
| Supply-chain delay | 3 days for third-party releases, plus uv's `exclude-newer` for lock files | None; 7 or 14 days | Unreviewed automerge makes a malicious release the main risk. Most are pulled within days, and 3 days keeps tools close to current |
| Test harness | pytest driving the Renovate CLI (pinned through mise) in local-platform dry runs | Node tests importing Renovate's internal functions | Keeps the repo's code in one language, and tests Renovate's real behavior through its supported CLI rather than internal functions that can change between releases |
| Delay exemptions | All copier templates, plus this system's repos by name | Exempt every dependency of the repo owner | Copier versions carry no release time, so the delay can't apply to any template. Matching on the owner would exempt a consumer's unrelated dependencies and assume one owner for every consumer |
| Renovate and the lock-refresh commit | List the workflow's fixed author in `gitIgnoredAuthors` | Leave it out; have each consumer list its own App's bot address | Left out, Renovate stops maintaining every template-update PR the workflow touches. A fixed author shared by all adopters keeps this in the preset |
| Keeping Renovate out of template-owned pins | Ignore consumer `.config/copier-*/**`, and `conf.d` links at any depth | Let Renovate bump them, relying on copier's merge of identical changes | A Renovate bump that runs ahead of the template conflicts on the next copier update |
| LID pin handling | Never automerge | Automerge and walk later | A merged LID bump leaves the project's `- Version:` stale until someone walks it, which LID treats as drift |

## Open Questions & Future Decisions

### Deferred
1. Grouping related updates (for example all Astral tools) into one branch. Add it if update volume becomes noisy.
2. Automated tagging of releases after a merge. Slice 2's commit tooling (cocogitto) can derive versions from commit messages. Until then, the maintainer tags releases by hand.

## References

- [Renovate automerge](https://docs.renovatebot.com/key-concepts/automerge/); [minimum release age](https://docs.renovatebot.com/key-concepts/minimum-release-age/); [shareable presets](https://docs.renovatebot.com/config-presets/); [`ignorePaths`](https://docs.renovatebot.com/configuration-options/#ignorepaths); [mise manager](https://docs.renovatebot.com/modules/manager/mise/); [uv `exclude-newer`](https://docs.astral.sh/uv/reference/settings/#exclude-newer).
