# Policy: Third-Party Documentation (`docs/`)

`docs/` at the repo root holds **externally authored reference material the project depends on**, pinned locally: vendor documentation, specifications, RFCs, API references, standards text, license texts. A file under `docs/` is written by someone else about something other than this project. It is never expected to reference the project, and the project's own writing never lands there.

This policy defines what belongs in `docs/`, how a pinned document is recorded, and the one direction in which the rest of the repository may cite it. `bin/check-catalogs` enforces the mechanical half.

## Why a separate directory

Briefs and policies routinely rest on external authority — a wire format, a CLI's flag semantics, a platform's documented limit. Three things go wrong when that authority lives only at a URL:

- **The text moves or changes.** A decision recorded against "the docs" cannot be re-read once the page is revised, and the drift is invisible until something breaks.
- **Retrieval-only roles cannot reach it.** The coder and critic hold no search authority and may be running in a venue with no network at all. A local copy makes the cited authority readable to every role without egress.
- **Analysis and source blur together.** A brief that pastes a vendor page and then reasons about it leaves no clean line between what the vendor said and what the project concluded.

`docs/` separates the source from the reasoning. The vendor's text is pinned verbatim under `docs/`; the project's reading of it is a brief; the rule it produced is a policy.

## What belongs in `docs/`

- Documentation of a dependency, platform, protocol, or tool the project builds on, in the edition the project actually targets.
- Specifications and standards the deliverable must conform to.
- License texts of redistributed third-party material.
- Reference tables the project must match exactly (error codes, enum values, wire-format layouts).

## What does not belong in `docs/`

- **Anything the project wrote about itself.** The deliverable's own API documentation lives with the deliverable; the repository's explanation of itself is a brief or the README; an outward treatise is governed by [`treatise.md`](treatise.md).
- **Commentary on a pinned document.** Observations, comparisons, and conclusions are briefs ([`briefs.md`](briefs.md)); a rule derived from a document is a policy.
- **Material the project may not redistribute.** When a source's terms do not permit a local copy, pin nothing: the citing brief names the URL with `As of` and `Retrieved` dates and quotes only the minimum passage its argument needs.
- **Anything mutable by the project's own work.** A file under `docs/` changes only when the project deliberately re-pins a newer edition.

## Content rules

1. **Verbatim, or a verbatim excerpt.** The pinned file carries the source's text as fetched. No frontmatter is added, no annotations are inserted, no wording is corrected. An excerpt is recorded as such in the catalog with the range it covers. When a document needs commentary, the commentary is a brief that cites the pin.
2. **No outbound references.** A file under `docs/` never links to anything else in this repository. This is the structural expression of "third-party": the material predates the project and cannot know about it. `bin/check-catalogs` fails on any repository-internal link from a file under `docs/` to a path outside `docs/`. The one exception is `docs/README.md`, which is project-owned catalog text and may link to this policy.
3. **Text formats preferred.** Markdown, plain text, or a faithful text rendering of HTML — formats every role can read and every reviewer can diff. A binary format (PDF, image) is pinned only when no text form exists, and the catalog row says so.
4. **Pin what is cited.** A long document is excerpted to the sections the project relies on rather than mirrored whole. A reader who needs the rest follows the source URL in the catalog.
5. **Naming.** Kebab-case, `<origin>-<topic>[-<version>].<ext>` — for example `vendor-api-reference-v2.md` or `rfc-8259.txt`. Unlike briefs, a version or edition belongs in the filename here, because a pin is a specific edition. Re-pinning is a deliberate act: the new edition replaces the old file, the catalog row is updated, and every citation is re-read against the new text in the same change ([`greenfield-until-released.md`](greenfield-until-released.md) applies — no parallel old-and-new editions).
6. **Licensing is recorded.** Every pinned document's catalog row names the basis on which it is redistributed here: a public standard, an open-source project's documentation under its license, a page whose terms permit copying. "Found on the web" is not a basis.

## The catalog: `docs/README.md`

`docs/README.md` is the index of everything under `docs/`. It is required whenever the directory holds anything beyond the README itself, and it is the *only* catalog of pinned documents — `CLAUDE.md` does not list them, because a pinned document is consulted through the brief or policy that cites it, and `CLAUDE.md` is read every turn.

One table row per top-level entry (a file, or a directory holding a multi-file document), carrying:

| Column | Content |
|---|---|
| Document | A link to the file or directory. |
| Source | The URL the material was fetched from. |
| As of | The date or version the source itself carries — when the fact was true. |
| Retrieved | The date the project fetched it. |
| Basis | The license or terms under which it is redistributed here. |
| Pinned for | One line: which brief, policy, or plan concern depends on it, and whether it is an excerpt. |

`As of` and `Retrieved` are deliberately distinct: a fresh retrieval of an old document is still an old document.

`bin/check-catalogs` enforces the mechanical contract: every top-level entry under `docs/` (other than the README and dotfiles) is linked from a catalog row; every catalog link resolves; the README exists whenever the directory is non-empty. What a row *says* is a review matter.

## Citation direction

`docs/` sits beneath every other documentation directory:

- `briefs/`, `policies/`, `plan/`, `CLAUDE.md`, skills, and agent definitions may cite a file under `docs/`.
- A file under `docs/` cites nothing in the repository.

This extends the one-way rule in [`briefs-and-policies.md`](briefs-and-policies.md): docs ← briefs ← policies / plan. When a brief's or policy's claim rests on external text, it cites the local pin — `docs/<file>` with a section — rather than the URL alone, so a reader can verify the claim against the exact text and so a later re-pin surfaces every claim that needs re-reading.

## Research authority

Reading a file under `docs/` is *retrieval*, never *search*, for every role ([`research-authority.md`](research-authority.md)). A pinned document that a brief, policy, or plan cites is a plan- or brief-identified resource for the coder and critic. Adding a new pin is planner or reviewer work — it originates from research — and lands through the same review as any other authority change.

## Freshness

Every catalog row dates its pin. A pin is never silently refreshed: re-pinning is a change with a rationale, and the `sweep` skill's audit includes catalog rows whose `As of` has fallen materially behind the source's current edition for a dependency the project still tracks. Age alone is not staleness — a stable standard pinned years ago is still current; a fast-moving CLI reference pinned last quarter may not be.

## Portability

`docs/README.md` — the catalog shape and its header — is part of the methodology contract and ships with `stamp` and `teach`. Pinned *content* is project state: the template's own pins are never copied into a derived project, and a `learn` pass never absorbs a donor's pins.

## Enforcement

- `bin/check-catalogs` — README presence, catalog completeness, link resolution, and the no-outbound-links rule; runs inside `./bin/check all`.
- The plan reviewer and code critic treat an un-cataloged pin, a pin with an unrecorded basis, or project-authored prose under `docs/` as `REVISE`.
