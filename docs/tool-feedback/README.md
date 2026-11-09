# Tool feedback

Proposed enhancements and bugs for the tools this repo uses or plans to adopt, kept until they're raised upstream. One page per tool. Each item says where the problem is, what's wrong or missing, the evidence, a suggested fix, and whether it has been raised upstream.

- [LID](lid.md): suggestions for decision docs and their tooling.
- [mdbook-lint](mdbook-lint.md): decision-record rules that misfire on LID's decision folders.
- [kontext](kontext.md): the npm package isn't published.
- [github-repo-meta-fetch](github-repo-meta-fetch.md): no releases; a generated `CLAUDE.md`.
- [extant](extant.md): checked documents must be listed one by one.
- [vendir](vendir.md): a locked SHA that isn't a tip can't be fetched shallowly; every tag is fetched; no default-branch ref.
- [paper-search-mcp](paper-search-mcp.md): pacing and retries spread across connectors and limited to one process; a hard-coded Crossref address; retries without TLS verification; a PyPI release far behind main; live-network probes in unit test files.
- [claude plugin eval](claude-plugin-eval.md): gitignored files count toward the plugin's 20,000-entry cap; results can only go inside the plugin directory.
- [Renovate](renovate.md): the `pep723` manager neither updates script lock files nor bumps git-pinned dependencies.
