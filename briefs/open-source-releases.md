---
title: Open-source releases with one canonical history
date: 2026-11-01
status: draft
scope: Design a reviewed first-public-release transition and ongoing release practice with one sanitized history, useful public artifacts, licensing clearance and installed-user continuity.
---

# Open-source releases with one canonical history

## Purpose and present scope

An open-source release should be usable by a stranger without exposing the private context in which the project was developed. This draft works through the first public release and later maintenance. It proposes the contents and evidence of a release plan; it is not an operational runbook, a completed privacy audit or approval to publish. No history reset, purge, archive, repository access change or release tooling is implemented by authoring it.

## Settled owner constraint: one history

The operator reaffirmed on 2026-11-01: “no forked archives. One history only.” The earlier 2026-10-23 direction was to reset history at the first public release and thereafter keep only that history locally and publicly, with no retained private history.

The intended transition replaces the pre-release lineage with a sanitized initial history. From that point, local development and the public repository share that one canonical history. A private fork, archive repository, hidden branch, bundle, exported directory or backup of the discarded project lineage would defeat the decision; none is a proposed fallback. A separately maintained sanitized public mirror of a continuing private project history is also excluded. Subsequent releases extend the canonical history rather than starting a second private chronology.

Until an exact release transition is approved, ordinary development history and evidence remain intact. Recording the intended replacement does not authorize acting on it now. The irreversible action needs a concrete reviewed scope and explicit release approval; the general preference for one history is not that approval.

## Privacy is a surface and reachability question

A clean current source tree is insufficient evidence of a safe public release. The release assessment would cover the following surfaces, with attributable findings and dispositions rather than only a name grep:

| Surface | Questions the release review needs to settle |
|---|---|
| Source, tests, examples and documentation | Are consumer/project references, private engagements, internal terminology, fixtures or quotations identifying something outside the intended public project? Are examples genuinely generic? |
| Host and personal context | Are tailnet/device identities, account identifiers, personal paths, native session IDs, contact details or machine-specific configuration disclosed? |
| Assets and generated output | Do images, media, debug data, maps, generated documentation, archives or package metadata carry private content, embedded paths, provenance, comments or unintended files? |
| Git history and references | What can be reached through the intended branches, tags, other advertised or retained references, local clones and worktrees, reflogs, object stores and remote hosting surfaces? Does discarded lineage remain recoverable anywhere in the approved transition scope? |
| Release and hosting surfaces | What exact source archive, binary/package, documentation site, release attachment and repository metadata will be public? Does each contain only the reviewed intended material? |
| Operational storage | Are ignored evidence, exports, caches or other local records functioning as a recoverable copy of discarded project history rather than current operation state? |

Automated scans can locate candidate paths, strings and object references; they do not establish that all prose, assets or contextual disclosures are safe. An absence of matches is not privacy clearance. The review needs to name what was examined, what was inaccessible and which findings remain unresolved. An existing public copy, third-party fork or external cache also limits any claim about erasure; replacing the controlled repository cannot prove that an uncontrolled copy vanished.

## Public metadata and local private operation records

The public project needs enough sanitized metadata to explain the release: version, license and notices, supported platforms, install/update instructions, artifact identity, relevant changes and known limitations. It does not need private account configuration, secrets, host routing, raw operator conversations or internal consumer history.

Local private operation records serve current execution, not an alternate project chronology. Credentials, active configuration and necessary live service state can remain outside public artifacts, subject to their own custody. This distinction does not permit retaining old commits, raw project logs, source snapshots, qualifying preimages or exported evidence as a private archive of the discarded lineage. Records that would reconstruct that history belong in the proposed purge inventory, not an ignored-folder loophole. Sanitized release-facing evidence would be included in the new canonical record where needed.

Any unresolved conflict between evidence-retention obligations and the intended purge is a concrete release-planning blocker. The plan would resolve the exact records and ongoing work before approval, possibly completing or truthfully interrupting active work and qualifying fresh evidence against the sanitized candidate. It would not silently delete required evidence or preserve it in a contradictory private fork. No such disposition is performed by this draft.

## A usable public release

The README should tell a new reader what the project does, who it is for, its maturity and limitations, supported environments, exact prerequisites, how to install it, and a short successful usage path with expected results. Configuration examples should be safe and portable. Help, troubleshooting, update/uninstall behavior, documentation and contribution/reporting entrypoints should be discoverable. Instructions are useful only when exercised against the actual proposed public artifact in a clean environment with the declared prerequisites.

MIT is the intended license for original work the owner can license that way. A current license file establishes a declaration, not proof that every dependency, copied fragment, asset or contribution is cleared for a future release. A release inventory would establish ownership, provenance and third-party terms, retain required notices and attribution, and identify any unresolved distribution or license conflict. Applying MIT to the project does not replace third-party obligations or confer rights the owner does not have. No license file is changed or third-party work relicensed in this task.

The public artifact review includes package contents and metadata as well as source. Release archives, executable builds, documentation output and hosting allowlists should be inspected as the exact artifacts proposed for distribution, with digests and expected contents recorded. A successful local build alone does not establish that the uploaded archive, generated source download or hosted site contains those same reviewed bytes.

## Shape of the exact reviewed release plan

The later operational plan should resolve these items for a particular release, without turning this draft into standing permission to execute it:

1. **Scope and custody.** Identify the actual repository, current owners, affected checkouts/references and public destinations. Establish terminal boundaries for active commands, reviewers, callbacks and unmerged work. Identify who performs each action and who can approve it; do not infer permissions from a shared directory.
2. **Frozen proposed content.** Name the source candidate, versions, package/site surfaces, inclusion manifest and content digests. Resolve privacy and license findings across the full surface and reachability inventory. No actual private identifier belongs in the portable template's examples.
3. **Evidence and continuity.** Specify acceptance commands, manual inspection, the evidence disposition and installed-user checks. Separate verified facts from missing or unexercised capabilities. Define how fresh qualification binds to the sanitized release candidate rather than assuming old evidence automatically qualifies rewritten content.
4. **Irreversible transition proposal.** Enumerate the precise old histories, references, objects and historical copies to be removed or replaced, the proposed sanitized initial history, affected local/public stores and the verification scope. Explain consequences for collaborators and recovery from partial failure. Explicitly exclude a parallel retained private archive or fork.
5. **Owner approval at the action boundary.** Present the exact reviewed plan and immutable artifact identities, unresolved limits and irreversible effects before any reset, purge, reference replacement or publication. Approval applies to that scope and candidate; a changed public payload or destination needs reconciliation. Draft approval, a standing preference or an ordinary local commit is not release approval.
6. **Execution and inspection record.** Following actual approval, record each terminal operation and read back local and remote state. Verify that the controlled local/public repositories use the same new canonical history, intended refs and artifacts. Independently inspect what an unauthenticated public reader can retrieve, including generated downloads and any hosted output. A queued upload or changed visibility setting is not a verified release.
7. **Subsequent maintenance.** Continue from the sole canonical history, record public changes there and use the project's approved version/compatibility regime. Corrections are made in that history; the discarded private lineage is not restored or kept as a maintenance branch.

The plan's approval point is deliberately later than draft authoring and qualification. Before the irreversible boundary, failed checks leave the current history untouched. After it, there is no promised rollback to a retained private project archive. A partial-failure procedure would reconcile forward to the approved sanitized history or stop and report the exact state; it must not recreate the forbidden second history. No reset/purge commands or new migration framework are supplied here.

## Existing installed users and collaborators

A Git-history transition is separate from changing running software. The release plan should identify existing installations and integrations, supported public interfaces, configuration/data ownership, package or executable identity, launch/service behavior and update paths. The proposed public artifact needs fresh install and relevant existing-install update checks, with an explicit disposition for actual compatibility obligations. An initial public release is not a reason to silently stop an installed service, revoke access, rewrite user data or change startup configuration.

Existing operational installations may continue serving users through a separately qualified update; they are not retained as a mechanism for reconstructing the discarded repository history. Debug metadata, embedded source and packaged assets still need privacy inspection. Collaborators need a concrete transition instruction so a stale checkout or reference cannot republish the discarded lineage. The eventual plan should address how they adopt the same canonical history, rather than relying on an ordinary fast-forward pull after a history replacement.

## Draft acceptance and remaining work

This brief is complete as an initial design when the one-history constraint, privacy/reachability scope, public documentation and licensing needs, installed-user continuity and exact irreversible approval boundary are explicit and its repository catalog/links validate. That is distinct from release readiness.

Release readiness remains unproved: no project-wide privacy or ownership audit, artifact/license inventory, sanitized candidate, reset rehearsal, purge verification, public-surface inspection, install/update qualification or release approval is produced by this draft. The exact future release scope and applicable compatibility decisions remain to be worked out. There is no open archive-versus-no-archive decision: one history and no parallel private archive are already settled.

## Sources and evidence dates

- Operator direction, as of 2026-10-23, reaffirmed 2026-11-01 and recorded in this task's immutable work log: reset at the first public release; thereafter keep only that same history locally/publicly, with no retained private history or forked archive. Retrieved through the authorized task relay on 2026-11-01. Private conversation identifiers and project examples are intentionally absent from this portable text.
- Owner-relayed authoring scope, as of and retrieved 2026-11-01: useful public documentation, MIT subject to ownership and third-party obligations, exact public-artifact inspection and installed-user continuity. This draft contains no external legal opinion or completed third-party clearance.
