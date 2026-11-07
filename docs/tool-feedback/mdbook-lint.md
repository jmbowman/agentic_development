# mdbook-lint feedback

Issues found in [mdbook-lint](https://github.com/joshrotenberg/mdbook-lint) source at a1c27e5 while checking it against LID's decision docs. Not yet raised upstream. Other mdbook-lint bugs are kept in [PortaBase's page](https://github.com/jmbowman/portabase/blob/master/docs/wiki/mdbook-lint-bugs.md).

## Open items

### 1. Decision-record rules fire on any `decisions/` folder, on by default

- **Where:** `format.rs:107-147` (path detection), `registry.rs:156-211` (registration).
- **What:** any path segment named `adr`, `adrs`, `decisions` or `architecture-decisions` marks a file as a decision record, and all 17 ADR rules are stable and on by default. A LID decision doc (frontmatter only `node:`, sections Context, Decision Elements, Options in the Domain, Selection) is detected as MADR, and ADR002-ADR005 fail it (no status, no date, missing MADR headings).
- **Impact:** every repo using LID and mdbook-lint fails its build until the rules are disabled one by one.
- **Suggested fix:** make the ADR rules opt-in, or let the decision-record paths be configured.

### 2. Documented rule wildcards and options have no effect

- **Where:** core `config.rs:26-32`; the documentation for rule configuration.
- **What:** the documented `[rules] "ADR*" = true` wildcard and the `[ADR016] min-options` setting have no effect in the source. Rules are disabled only by listing exact IDs under `disabled-rules`. The documentation also says only `/adr/` and `/adrs/` paths are detected, while the code also matches `decisions` and `architecture-decisions`.
- **Suggested fix:** implement the wildcard and the option, or correct the documentation.
