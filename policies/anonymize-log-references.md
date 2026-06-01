# Policy: Anonymize External-Repo References in LOG.md (starter-only)

**This policy applies only to this repository** — the agentic-coding-starter-template. Projects derived from this template via `/starter`, and projects retrofitted via `/teach`, do **not** inherit this policy. Their `LOG.md` files are their own business; their references to external work are theirs to disclose or not.

The reason for the asymmetry: **this repository is intended to be public**. Every commit, every `LOG.md` entry, and every committed file will be readable by anyone with the repo URL. A public template's `LOG.md` must not leak the private context of the projects it absorbs patterns from (via `/learn`) or teaches them to (via `/teach`).

## What must be anonymized

When `LOG.md` documents a cross-repo operation, the following must not appear verbatim:

- **Project names** of external repos. Use `Donor A`, `Donor B`, … to distinguish multiple donors in a single entry; use `the donor` or `the target` when there's one and no ambiguity.
- **Commit SHAs** of external repos. Replace with `<sha>` or omit; an mtime fingerprint is acceptable when an audit-trail anchor is needed.
- **Project-specific terminology** that names internal systems, products, daemons, CLI subcommands, MCP tools, or proprietary identifiers unique to the external project. Replace with a generic equivalent (`<a daemon>`, `<a CLI command>`, `<an internal storage path>`).
- **People's names** other than this template's maintainer when the name appears in connection with an external project's design decisions or private discussions. The maintainer's name attached to *this* template is fine; the same name attached to a private downstream project is a leak.
- **Internal repo paths** that reveal directory structure of an external project *beyond* what is structurally identical to this template. `<donor>/.claude/skills/<skill>/SKILL.md` is fine (same structure as ours); `<donor>/<custom-dir>/<custom-subdir>/` reveals a private architectural decision and is not fine.

## What can stay

- **Patterns and ideas** absorbed or taught. The whole point of `LOG.md` is the audit trail. Describing the *shape* of a pattern, framed in terms of what this template now has, preserves the audit value without leaking the donor.
- **Generic characterizations** of the external project: "a single-product repo with a lightweight `user-actions/` queue", "a multi-domain platform repo with two-tier policies". These preserve enough context to make the entry useful to a future maintainer without naming or fingerprinting the donor.
- **References to this template's own files** — `policies/log-discipline.md`, `briefs/methodology.md`, etc. All in-template references are fine.

## Authoring discipline

- Write every `LOG.md` entry **as if a stranger with no other context will read it**. If a stranger could infer the external project's identity, ownership, or proprietary details from the entry, it isn't anonymized.
- When in doubt, generalize. A LOG entry whose audit value depends on naming the external project is suspicious — usually the audit value is in the pattern, not the project.
- Anonymize at write time, **not at commit time**. Don't commit a non-anonymized entry intending to fix it later. Once pushed, the data is leaked even if the entry is later rewritten — the SHA still resolves on remote backups, forks, and caches.

## Plan-reviewer / code-critic enforcement

- Any `LOG.md` change in a phase under review is read against this policy. A reviewer that spots a verbatim project name, SHA, or proprietary identifier returns `REVISE` with a one-line note ("Anonymize the LOG.md reference to `<X>` per `policies/anonymize-log-references.md`").
- The orchestrator (`/kickoff`, `/learn`, `/teach`) writes `LOG.md` entries already anonymized — no rely-on-the-reviewer-to-catch-it pattern.

## Backfill rule

When this policy is first adopted (or revised to broaden), any pre-existing `LOG.md` entries that violate it are retroactively anonymized in the working tree before the next push. Backfill is a single commit titled along the lines of "Anonymize cross-repo references in LOG.md per policy."

## Why this isn't a methodology-universal policy

Private projects have no incentive to anonymize their own `LOG.md` — the audit trail is more valuable when it names what was learned from where. A private repo's `LOG.md` referencing its own donors by name is *exactly* what those private logs should do. The asymmetry is driven by the publicness of *this* repo, not by any methodology principle.

`/teach` and `/starter` exclude this policy from transfer to derived projects. See the Out-of-scope list in `.claude/skills/teach/SKILL.md` and the "Do not copy" carve-outs in `.claude/skills/starter/SKILL.md`.
