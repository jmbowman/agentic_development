# Proposal: a SessionStart hook that installs mise in cloud sessions (2026-10-22)

A draft for review, not yet part of the repo's setup. It installs mise and the tools `mise.toml` pins at the start of each Claude Code cloud session, so `mise run check` works there as it does locally and in CI. Adding it changes how the repo is set up, so it should pass the LID HLD check (the HLD's process and tooling sections) before it is committed as `.claude/` files. Background: [cloud-session readiness report, section 4](2026-10-22-cloud-session-readiness.md#4-running-the-repos-checks-in-a-cloud-session).

## What was verified

In a cloud session on 2026-10-22, with the environment's widened network policy:
- **Installing by hand:** downloading mise 2026.10.14 from its GitHub release and running `mise install` installed all eight pinned tools in about 14 seconds. `mise run check` then passed in full: lint, typecheck, 333 tests, `lidc` with no findings, and conflicts.
- **The draft script below, run with an empty home directory:**
  - a fresh install took about 32 seconds;
  - a second run took about 1 second and changed nothing;
  - with a corrupted checksum file it exited 1 and installed nothing;
  - outside a cloud session it exited 0 without doing anything.
- **The environment file:** with the PATH line it writes sourced, `mise`, `ruff` and `lidc` resolved to the installed versions, and `mise run lid` and a sample pytest run passed.

**Not yet verified:**
- running as a registered hook, from a fresh session;
- whether Claude Code's Bash tool picks up the `CLAUDE_ENV_FILE` line;
- how the hook interacts with the environment's container cache.

## Draft files

`.claude/hooks/session-start.sh`:

```bash
#!/bin/bash
# Installs mise and the tools pinned in mise.toml, so `mise run check` works
# in Claude Code cloud sessions. Does nothing outside them.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Keep in step with the `version:` input of jdx/mise-action in .github/workflows/.
MISE_VERSION=2026.10.14
bin_dir="$HOME/.local/bin"

if ! "$bin_dir/mise" --version 2>/dev/null | grep -q "^$MISE_VERSION "; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  base="https://github.com/jdx/mise/releases/download/v$MISE_VERSION"
  asset="mise-v$MISE_VERSION-linux-x64.tar.gz"
  curl -fsSL -o "$tmp/$asset" "$base/$asset"
  curl -fsSL -o "$tmp/SHASUMS256.txt" "$base/SHASUMS256.txt"
  (cd "$tmp" && grep "  ./$asset\$" SHASUMS256.txt | sha256sum -c --quiet -)
  tar -xzf "$tmp/$asset" -C "$tmp"
  install -D -m 0755 "$tmp/mise/bin/mise" "$bin_dir/mise"
fi

cd "$CLAUDE_PROJECT_DIR"
"$bin_dir/mise" trust --quiet
"$bin_dir/mise" install --quiet

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$bin_dir:$("$bin_dir/mise" bin-paths | paste -sd: -):\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
```

`.claude/settings.json` (new file):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

## Design choices in the draft

- **Cloud only.** The script exits at once unless `CLAUDE_CODE_REMOTE` is `true`, so local sessions keep using the developer's own mise.
- **Synchronous.** The session starts only after the tools are installed, so no check can run before they exist. The cost is about 30 seconds on a fresh container. Async mode would hide that, but adds a race with the first check.
- **Idempotent.** It skips the download when the right mise version is already present, and `mise install` skips installed tools. A resumed or cached container pays about a second.
- **The same mise version as CI.** The pin matches the `version:` input of `jdx/mise-action` in `.github/workflows/`, so local, CI and cloud sessions run one mise.
- **Integrity check.** The archive is verified against the release's own `SHASUMS256.txt`. That catches corruption in transit, but not a compromised release, since both files come from the same place.
- **PATH for later commands.** The hook writes mise and every pinned tool's bin directory to `CLAUDE_ENV_FILE`, so direct calls such as `ruff` or `lidc` work as well as `mise run`.

## Alternatives

- **The environment's setup script** instead of a repo hook. The container state is cached when it finishes in about five minutes, so later sessions start warm. But it lives in the cloud environment's settings, outside the repo, so it isn't reviewed, versioned or shared with other people's environments, and Renovate can't update it.
- **mise's install script** (`curl https://mise.run | sh`). Shorter, but it runs a remote script unpinned, and it installs the latest mise rather than CI's version.
- **A checksum pinned in the script** instead of the release's checksum file. This defends against a compromised release, but every mise bump would also need a new hash. Renovate's regex manager can update the version but not a hash in the same line without extra configuration.
- **Template delivery.** Ship the hook to consumer repos through the copier template, since any consumer has the same gap in cloud sessions. This is the long-term home if the HLD check agrees; this repo would get it first.

## Open questions

1. **Hook or setup script?** A repo hook (reviewed and versioned; pays about 30 seconds on a fresh container) or the environment setup script (cached, but outside the repo)? This is the readiness report's open question 4.
2. **Keeping the version in step.** Should the shared Renovate preset gain a regex manager for `MISE_VERSION` in the hook, grouped with the `jdx/mise-action` `version:` bumps? Or should the hook read the version from somewhere Renovate already updates?
3. **Checksum source.** Is checking against the release's own checksum file enough, or should the hash be pinned in the repo?
4. **Template scope.** Should this ship to consumers through the copier template, and if so, as a template-owned file?
5. **Network domains.** What does the environment's network policy need to allow, as a documented requirement? This session used GitHub releases, `nodejs.org`, npm and PyPI.
