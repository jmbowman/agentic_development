# Behavior evals for this repo's skills

Cases for `claude plugin eval`, run by hand from the repo root (the repo root is the plugin). Each skill's cases live in `evals/<skill>/`, one directory per case, and carry the skill's name as a tag; `--eval-dir evals/<skill>` runs one skill's suite. Only `prior-art-search` has cases so far. Each run is a real model call, and the online cases search the web and clone repositories, so a full suite takes a while and costs real usage. Runs are isolated: no user or project instructions load, so a pass shows what the skill itself contributes, and every case also runs without the plugin for comparison.

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

Add `--case <name> --runs 1 --ablation none` to iterate on one case. Results go to `results/` inside the eval directory, which is gitignored.

Each case's `case.yaml` lists the specs it exercises in `@spec` comments. For prior-art-search, `tests/test_prior_art_skill.py` checks that every spec marked *(eval)* in `docs/intent/prior-art-search/prior-art-search-specs.md` has a case, and that each case sits under its skill's directory with its tag.
