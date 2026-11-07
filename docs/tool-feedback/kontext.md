# kontext feedback

[kontext](https://github.com/patkusch/kontext) is the optional staleness check in [the federated knowledge note](../prior-art/2026-11-06-federated-knowledge-and-work-items.md). Not yet raised upstream.

## Open items

### 1. The npm package isn't published

- **Where:** `package.json:41` at 0f34cf0 declares `@patkusch/kontext` 0.1.0.
- **What:** the npm registry returns 404 for that name (checked 2026-11-06), and the README says to install with a git clone plus `npm link`.
- **Impact:** it can't be installed or version-pinned through mise or updated by Renovate.
- **Suggested fix:** publish the package, or tag releases with built artifacts.
