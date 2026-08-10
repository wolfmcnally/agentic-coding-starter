---
slug: chivalrous-turtle
title: Mechanizing a policy's verification can silently narrow the contract
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-10
source: learn
occurrences:
  - date: 2026-08-10
    ref: "LEARN from Donor A — phase-status verification claimed a check the gate never implemented"
---

When a policy's Verification section is upgraded from documented manual commands to a delegation ("the authoritative gate also rejects X"), the prose can promise a check the mechanical gate never actually implements. The policy then reads as *more* verified than before the mechanization — a reader trusts the gate, stops running the manual commands, and the check quietly ceases to exist anywhere.

Observed in this template: `policies/phase-status.md` asserted that `./bin/check all` rejects status fields and status declarations outside the phase table, but no component of the gate scanned per-phase frontmatter or bodies. A derived project retained the pre-mechanization form — explicit, copy-pasteable `awk`/`grep` commands — which was honest about what actually ran. The cross-repo diff is what exposed the gap: the "less evolved" spoke was correct and the "more evolved" hub was making a false claim.

The generalizable discipline: a prose claim that a gate enforces a rule is itself a verification, and it fails the same test as any other — a verification that can only say "good" is not a verification. When mechanizing, either implement each named check in the gate (with behavioral tests pinning it) in the same change that rewrites the prose, or keep the manual commands until the gate really carries them. Never let the delegation land ahead of the implementation.

## Evidence

- Verified against the gate's source before fixing: the catalog checker validated only the phase table's markers; no component matched `status:` in per-phase files.
- Fixed in the same `learn` pass by implementing the frontmatter and declaration checks in the catalog checker with behavioral tests, then rewriting the policy's Verification section to describe what actually runs.
