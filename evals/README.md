# Behavior evals for this repo's skills

Cases for `claude plugin eval`, run by hand from the repo root (the repo root is the plugin). Each skill's cases live in `evals/<skill>/`, one directory per case, and carry the skill's name as a tag; `--eval-dir evals/<skill>` runs one skill's suite. `prior-art-search` and `session-wrap-up` have cases. Each run is a real model call, and the online cases search the web and clone repositories, so a full suite takes a while and costs real usage. Runs are isolated: no user or project instructions load, so a pass shows what the skill itself contributes, and every case also runs without the plugin for comparison.

Cases are also tagged `online` (they need web search and network access) or `offline` (everything they need is in the case's scaffold). `--tag` matches any of the tags given, so combine a skill and a network tag with `--eval-dir` plus `--tag`, not two tags. Every case that seeds a workspace needs `--scaffold`.

```bash
# Offline cases: no network grants.
claude plugin eval . --eval-dir evals/prior-art-search --tag offline --scaffold --allow-tools Bash Write Edit

# Online cases: web tools, plus network for the shell's git and API calls.
claude plugin eval . --eval-dir evals/prior-art-search --tag online --scaffold \
  --allow-tools WebSearch WebFetch Bash Write Edit \
  "WebFetch(domain:github.com)" "WebFetch(domain:api.github.com)" \
  "WebFetch(domain:codeload.github.com)" "WebFetch(domain:raw.githubusercontent.com)" "WebFetch(domain:pypi.org)" \
  "WebFetch(domain:files.pythonhosted.org)" "WebFetch(domain:registry.npmjs.org)" \
  "WebFetch(domain:crates.io)" "WebFetch(domain:static.crates.io)" \
  "WebFetch(domain:gitlab.com)" "WebFetch(domain:codeberg.org)"
```

The runner refuses a plugin that contains hard-linked files, and the plugin here is the whole repo, gitignored directories included. `pyproject.toml` sets uv's `link-mode = "copy"` so `.venv/` has none; if a run fails with "a file in the plugin has more than one name", find the culprit with `find . -path ./.git -prune -o -type f -links +1 -print`.

Cases that grant Bash need Claude Code's sandbox (bubblewrap and socat on Linux). On Ubuntu 24.04 and later, AppArmor restricts unprivileged user namespaces (`sysctl kernel.apparmor_restrict_unprivileged_userns` returns `1`). Claude Code's [sandbox docs](https://code.claude.com/docs/en/sandboxing) give an AppArmor profile for `bwrap`, but Ubuntu 26.04 already ships `/etc/apparmor.d/bwrap-userns-restrict`, which defines a profile with the same name and moves bwrap's children into a confined `unpriv_bwrap` profile; every sandboxed command then fails with `apply-seccomp ... setgroups: Permission denied`, and graders that assert a command was never run pass vacuously. Disabling that profile before adding the documented one (a host-wide security trade-off), or running the evals in a VM without the restriction, are the options. Check that Bash works with one cheap run first: `claude plugin eval . --eval-dir evals/prior-art-search --case no-trigger-bug-fix --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit`; a working run tests its fix instead of reporting a sandbox error.

Add `--case <name> --runs 1 --ablation none` to iterate on one case. Results go to `results/` inside the eval directory, which is gitignored.

Each case's `case.yaml` lists the specs it exercises in `@spec` comments. Each skill's structure tests (`tests/test_prior_art_skill.py`, `tests/test_session_wrap_up_skill.py`) check that every spec its specs file marks *(eval)* has a case in its own suite. `tests/test_evals.py` checks that every case loads in the runner and sits under its skill's directory with its tag.

The session-wrap-up cases are offline, and each gives the skill a record of a session to wrap up inside its prompt, since an eval is a single prompt. Run them with:

```bash
claude plugin eval . --eval-dir evals/session-wrap-up --tag offline --scaffold --allow-tools Bash Write Edit
```

Behavior an eval can't reach (an interactive run, or another live session) is checked by hand from the scripts in `evals/session-wrap-up/manual.md`, which also hold the dated results. Its specs are marked *(manual)*.
