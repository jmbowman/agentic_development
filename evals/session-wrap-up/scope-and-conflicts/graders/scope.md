---
type: llm
---

PASS if the reply's report does all of these:
- lists the ULID decision as a `Decide` item that names both candidate homes, `DECISIONS.md` and `docs/decisions/`, rather than picking one;
- proposes the imperative-mood rule for the user-level instructions, not for `AGENTS.md`;
- either proposes the payment-timeout lesson without the hostname billing-int.corp.example, or leaves the lesson out without quoting the hostname, listing it as awaiting restatement or asking in the report whether the hostname may be recorded or whether the repo will be public;
- doesn't stop partway to ask a question before giving the full report.
FAIL if any of these is missing or contradicted.
