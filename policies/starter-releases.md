# Policy: Starter Releases and Adoption Provenance

Starter-only. Operator-ratified 2026-11-07. Starter is a continuously evolving knowledge and best-practice hub for agentic development. Named releases identify qualified snapshots that projects can deliberately adopt; they do not replace the repository's continuous history or require a product overhaul at each release.

## Version and tag contract

The first named baseline is **1.0.0**, tagged **`v1.0.0`** on the complete qualified state containing the authorized changes of 2026-11-07. Earlier history remains intact and receives no retroactive release tags. `RELEASES.md` records release notes; immutable annotated Git tags identify their exact commits. Use `v<major>.<minor>.<patch>` consistently.

Choose the next release number from the latest delivered named release and the complete release batch:

- **Minor:** a new methodology capability or feature; increment minor and reset patch to zero.
- **Patch:** small fixes or refinements without a new capability; increment patch.
- **Major:** a complete rewrite or breaking change to an externally consumed contract; increment major and reset minor and patch. These are expected to be rare, not the normal response to incremental learning.

A batch with several kinds of change takes the highest required bump. Explain consequential classification in its normal scope/close record rather than guessing from changed-file count. Policies have no independent version counters; their changes contribute to the hub's next release. Numbering does not automatically release the isolated example package, add compatibility machinery or waive the greenfield policy.

## Qualification and delivery

Apply ordinary methodology ownership, explicit-path staging, focused/changed-path checks and the complete final full gate to the actual release candidate. Record notes, scope, lessons and all tracked bookkeeping before that gate. After success, commit the exact qualified tree with the configured signing conventions; create an annotated tag on that commit using the existing signing identity and verify its signature, annotation and peeled commit. Verify branch and tag delivery through the existing configured remote and visibility, then confirm aligned tips and a clean tree. A gate failure, unknown custody, conflicting existing tag, missing signer or rejected push is a blocker; never bypass checks, recreate/move a published tag, rewrite history, change remotes or alter access to finish a release.

The operator expressly authorized creation and existing-remote delivery of `v1.0.0` for this batch after qualification. This grant is exhausted by that release. Future tag creation/publication remains operator-owned unless separately authorized; routine commit/push authority is unchanged. A release tag does not authorize hosted release assets, package publication, visibility changes, history replacement or new credentials.

## Recipient taxonomy and factual provenance

- **`outside`:** a repository established to have never adopted the Starter methodology. It can enter through `teach <recipient>` from Starter or the equivalent `learn <starter>` from that recipient, under the same concrete plan approval and adoption procedure.
- **`pre-1.0.0`:** a repository with verified historical Starter derivation or adoption, including repositories stamped before the first named baseline, whose adopted methodology is not tied to a completed transfer from a named release. Do not apply this label to outside repositories.
- **Named adopted baseline:** a recipient with retained evidence of an actual completed methodology adoption from an exact named Starter release and revision. Report the adopted release, tag/commit, scope and subsequent local adaptations, not an unsupported assertion that every file equals the donor.
- **Unknown:** provenance not yet established. Missing records, filenames, a layout detector, an assessment or a declaration alone do not prove derivation, non-adoption or upgrade.

A tag existing in the donor, reading new files or approving a plan never upgrades a recipient. A partial capability transfer records its precise imported items and donor release separately from the recipient's overall baseline; it does not silently advance that baseline. Preserve prior provenance and report gaps explicitly. No recipient is relabeled or written as a side effect of releasing Starter.

## Transfer boundary

`teach`, `learn` and initial stamping record exact donor revision plus a verified declared release/tag when available, or honest unversioned/unknown provenance for other sources. For Starter, the taxonomy above determines whether historical adoption is `pre-1.0.0` or the receiver remains `outside`. Concrete plans record proposed source provenance; completed receiving records distinguish actual application from assessment, partial transfer and whole-methodology adoption. Receiving publication/anonymization rules still govern those records. Tag/signature facts are checked from Git, never invented from a README or copied donor receipt.

The receiving repository carries its own machine-readable record, `collaboration/methodology-provenance.json`, written by the transfer that it describes and read by `bin/multioperator transfer-preflight`, which reports the declared releases the receiver has not recorded. Its `release` field is the named adopted baseline of the taxonomy above and advances only on a completed adoption of everything that release names; individually transferred capabilities are listed separately and never advance it. Each release entry in `RELEASES.md` therefore ends with a `Transfers:` list naming its capabilities and the members that travel together, so a transfer plans from the release gap. Starter carries no such record of its own: it is the source.

This policy and Starter's `RELEASES.md` are template-specific and do not become a derived project's own release policy or release notes. The generic obligation to preserve truthful source provenance travels through the universal skills and bootstrap guidance. Receivers own their product release numbers, tags and authorities.
