---
slug: comical-manticore
title: Construction evidence has no first-class notion of a second repository
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a deliberately cross-repository phase. Two independent surfaces could not express it: finding ingest rejected the critic's sibling-repo paths because relative-path validation refuses any `..` component, and the candidate-id tool hashes the primary tree only, so two rounds of sibling-side edits did not move the candidate id at all"
  - date: 2026-08-22
    ref: "Donor A — a THIRD surface of the same assumption, and the first that is a hard gate rather than a workaround. The final gate refuses unless every required initial role operation has a registered attempt; that phase's implementation and both reviews executed in the sibling repo, so none was dispatched in the primary one and the evidence run could not be sealed as declared. Resolved truthfully by registering all three as rejected/not-dispatched with a cross-reference to the sibling's trace — honest, and pointed at by nothing in any skill or policy"
---

The evidence apparatus assumes **one repository**. A phase whose write set spans a
sibling repository hits that assumption in several places at once, and they fail
in opposite directions:

- **Affected paths fail loudly.** Relative-path validation refuses any path
  containing `..`, so a finding about a sibling-repo file cannot be ingested as
  the critic wrote it. The interim idiom was to requalify as
  `<repo>:relative/path` — no `..`, unambiguous, one field touched, the
  transformation recorded. That is a convention, not a contract.
- **Candidate binding fails silently.** `bin/kickoff-tree-id` hashes one tree, so
  sibling-side work is invisible to the id that plan, review, and gate evidence
  are bound to. Two rounds of contract edits left the candidate unmoved. The
  interim mitigation was telling the critic, in its dispatch brief, that the id
  could not be trusted for the sibling and it must read that tree from disk.
- **Role registration fails at the seal.** When the roles ran in the sibling repo,
  the primary repo's required-operation check had nothing to certify.

**The second is the dangerous one.** An unchanged candidate is normally the
assertion that nothing changed, and here it asserted that falsely about half the
phase.

No design is proposed. The options — a repository-qualified path grammar, a
multi-root candidate, or an explicit declaration that cross-repository phases bind
**per-repository** evidence — differ in cost and in what they promise. What is
certain is that the current apparatus records a cross-repository phase
**incompletely while looking complete**.

This is squarely this repo's business: `learn`, `teach`, and `stamp` are all
cross-repository by construction, and `blazing-cicada` records the ordering
corollary — where a write set spans repositories, every repository's full gate
belongs before the first irreversible step.
