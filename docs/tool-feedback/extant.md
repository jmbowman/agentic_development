# extant feedback

[extant](https://github.com/scooter-sensei/extant) is the adopted citation drift check in [the federated knowledge note](../prior-art/2026-11-06-federated-knowledge-and-work-items.md). Not yet raised upstream.

## Open items

### 1. Checked documents must be listed one by one

- **Where:** `extant/config.py:102-104`, `extant/cli.py:640-713` at 7999ce2.
- **What:** `--verify` checks only the documents named in `.extant.toml` (`primary_doc`, default `NEXT_SESSION.md`, plus `extra_docs`). A knowledge base with dozens of pages needs every page listed, and a new page is silently unchecked until someone adds it.
- **Before raising:** check whether `extra_docs` accepts globs; the verification read didn't establish it.
- **Suggested fix:** accept glob patterns (for example, `docs/**/*.md` with excludes).
