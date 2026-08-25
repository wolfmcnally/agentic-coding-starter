# Policy: Treatises

A treatise is an outward-facing explanation of a repository's principles and
decisions for a named audience. It is derived from live repository authority;
it is not an inventory dump, a transcript, or a substitute for the canonical
briefs and policies.

## Canonical source first

Before rendering a treatise, identify the brief or policy that owns each
material claim. If the repository lacks a canonical explanation, write or
repair that internal brief first. Rendered formats are derivatives; corrections
land in the canonical source and are regenerated outward.

## Intent is recorded beside the brief

Every treatise carries a sidecar, `<brief-name>.yaml`, next to its canonical
brief. It holds the purpose, audience, register, scope, the operator's dated
editorial rulings, the published renderings, and every external fact with its
retrieval date. The prose argues; the sidecar records the instructions that
shaped it, which the prose cannot state about itself.

Read the sidecar before drafting and update it in the same pass that changes the
treatise. Its `directives` list is append-only: a reversal is a new dated entry
naming the one it supersedes, never an edit. A revision that contradicts a
recorded ruling surfaces the conflict to the operator rather than resolving it
silently. A treatise revised without its sidecar re-derives audience and register
from whatever draft is in front of it, which is how a piece drifts from what was
asked for.

## Explain decisions, not files

A treatise answers:

- What problem is this repository solving?
- Which principles govern the solution?
- Which consequential decisions were made, and why?
- What alternatives or limits matter to the audience?
- How can the audience verify the claims?

File paths and implementation details appear only as evidence. A directory
tour is not a treatise.

## Audience and disclosure

Name the audience and the intended venue before writing. Elide secrets,
private paths, external-project identities, unpublished implementation detail,
and internal operational vocabulary while drafting—not as a cleanup pass.
Honor every repository publication, anonymization, and disclosure policy.

Internal generation of a canonical brief is allowed under ordinary repository
write authority. External publication requires both:

1. explicit user authority for the publication action; and
2. a disclosure or release policy governing the receiving project or venue.

If either is absent, produce the internal artifact and stop before publishing.

## Freshness and attribution

Volatile factual claims name both their evidence date (`As of YYYY-MM-DD`) and
retrieval date (`Retrieved YYYY-MM-DD`) when fetched externally. Quote from the
original source, never from an intermediate summary. Keep quotation within the
source's permitted bounds and prefer concise paraphrase.

## Rendered forms

The canonical artifact is normally a repository brief. A user may request a
Markdown article, document, presentation, site, or other rendering. Use the
appropriate artifact workflow for that format, but preserve the same claim
map, audience, disclosure boundary, and source provenance across renderings.

## Review

Review the treatise against its named audience and its canonical authorities.
Confirm that it leads with the governing thesis, distinguishes principles from
implementation details, exposes real limitations, and contains no claim that
cannot be traced to the repository or an identified external source.
