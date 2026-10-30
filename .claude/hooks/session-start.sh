#!/bin/bash
# Installs mise, the skills locked in apm.lock.yaml, and the tools pinned in mise.toml, so
# cloud sessions have the same tools and skills as local ones. Does nothing outside them.
# Stdout carries only the JSON object Claude Code reads; everything else goes to stderr.
# Design: docs/intent/repo-setup/repo-setup-design.md
# @spec SETUP-HOOK-002, SETUP-HOOK-003, SETUP-HOOK-004, SETUP-HOOK-005, SETUP-HOOK-006
# @spec SETUP-HOOK-007, SETUP-HOOK-008, SETUP-HOOK-011
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

finished=false

finish() {
  # $1: empty on success, else a notice for the agent.
  finished=true
  if [ -z "$1" ]; then
    printf '{"hookSpecificOutput": {"hookEventName": "SessionStart", "reloadSkills": true}}\n'
  else
    notice=$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')
    printf '{"hookSpecificOutput": {"hookEventName": "SessionStart", "reloadSkills": true, "additionalContext": "%s"}}\n' "$notice"
  fi
  exit 0
}

fail() {
  finish "Session setup failed at: $1. Missing: $2. Tell the user, and see the hook's stderr (claude --debug) for details."
}

on_exit() {
  # Whatever stops the script, stdout still carries the one object Claude Code reads.
  [ "$finished" = true ] || finish "Session setup stopped unexpectedly. Tools and skills may be missing. Tell the user, and see the hook's stderr (claude --debug) for details."
}
trap on_exit EXIT

# Keep in step with the `version:` input of jdx/mise-action in .github/workflows/; Renovate
# bumps both together.
MISE_VERSION=2026.10.21
bin_dir="$HOME/.local/bin"
mise="$bin_dir/mise"

install_mise() {
  local tmp asset base
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"; trap - RETURN' RETURN
  base="https://github.com/jdx/mise/releases/download/v$MISE_VERSION"
  asset="mise-v$MISE_VERSION-linux-x64.tar.gz"
  curl -fsSL -o "$tmp/$asset" "$base/$asset" || return 1
  curl -fsSL -o "$tmp/SHASUMS256.txt" "$base/SHASUMS256.txt" || return 1
  grep -q "  ./$asset\$" "$tmp/SHASUMS256.txt" || { echo "no checksum line for $asset" >&2; return 1; }
  (cd "$tmp" && grep "  ./$asset\$" SHASUMS256.txt | sha256sum -c --quiet -) || return 1
  tar -xzf "$tmp/$asset" -C "$tmp" || return 1
  install -D -m 0755 "$tmp/mise/bin/mise" "$mise"
}

current=$("$mise" --version 2>/dev/null | awk '{print $1; exit}')
if [ "$current" != "$MISE_VERSION" ]; then
  install_mise >&2 || fail "installing mise $MISE_VERSION" "mise, every pinned tool and the LID skills"
fi

[ -n "${CLAUDE_PROJECT_DIR:-}" ] && CDPATH= cd "$CLAUDE_PROJECT_DIR" >&2 || fail "entering the project directory" "every pinned tool and the LID skills"
"$mise" trust --quiet >&2 || fail "mise trust" "every pinned tool and the LID skills"
"$mise" install apm >&2 || fail "mise install apm" "every pinned tool and the LID skills"
# Without this, `mise run` first installs every missing tool and stops if any fails.
MISE_TASK_RUN_AUTO_INSTALL=false "$mise" run skills >&2 || fail "mise run skills" "every pinned tool and the LID skills"
"$mise" install --quiet >&2 || fail "mise install" "some pinned tools (the LID skills are installed)"

[ -n "${CLAUDE_ENV_FILE:-}" ] || fail "writing PATH (CLAUDE_ENV_FILE is unset)" "PATH entries for mise and the pinned tools"
paths=$("$mise" bin-paths | paste -sd: -) || fail "mise bin-paths" "PATH entries for mise and the pinned tools"
[ -n "$paths" ] || fail "mise bin-paths (it listed no tools)" "PATH entries for mise and the pinned tools"
line="export PATH=\"$bin_dir:$paths:\$PATH\""
if ! grep -qxF "$line" "$CLAUDE_ENV_FILE" 2>/dev/null; then
  echo "$line" >> "$CLAUDE_ENV_FILE" || fail "writing PATH to CLAUDE_ENV_FILE" "PATH entries for mise and the pinned tools"
fi

finish ""
