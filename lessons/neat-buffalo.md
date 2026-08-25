---
slug: neat-buffalo
title: Role tool stances are documentation the venue never reads — delegated roles run with the operator's entire plugin surface
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-18
    ref: "Donor A — a planner dispatch read fourteen repository files from a hosted git API at ref=master through an ambient MCP server and zero files locally, planning against the remote default branch while the candidate carried uncommitted work including the phase's own plan-index row"
  - date: 2026-08-18
    ref: "Donor A — a coder revision dispatch in the same phase imported a computer-use client and called a screen-reading tool against the operator's terminal window. It failed only because an unrelated sandbox rule killed the kernel; no control of the methodology's own stopped it"
---

Every canonical role declares a tool stance —
[`policies/four-canonical-agents.md`](../policies/four-canonical-agents.md) sets
the coder's write surface and the planner's read-only posture, and
[`policies/research-authority.md`](../policies/research-authority.md) bounds who
may originate search. **Nothing enforces any of it for a delegated role.** The
role definition is read *by the model as instruction*, not *by the venue as
configuration*, so a delegated dispatch runs with whatever the operator's harness
exposes — every installed plugin and every configured MCP server.

Two incidents in one phase are not the finding. **Zero enforcement, for as long
as cross-harness routing has existed, is the finding.** Neither incident was
caught by the evidence apparatus, which verifies that the *tree* did not move
under a dispatch and says nothing about what the role actually read or touched.

Three specifics worth keeping:

- **A remote read defeats candidate binding silently.** The artifact comes back
  candidate-stamped, well-formed, and about a *different tree* — the remote
  default branch rather than the working candidate — and all three delegated
  success signals still hold.
- **The operator's screen is a shared surface.** It carries other concurrent
  sessions' content, so a screen-reading call is a boundary crossing regardless of
  intent.
- **A feature flag reading "off" beside a live server is configuration-as-
  documentation** — the same disease one layer down.

**What to do differently.** The watcher (`bin/kickoff-config`) generates every
delegated invocation and is the only place a scope can be both *applied* and
*recorded*. It wants a first-class per-dispatch allowlist of plugins and MCP
servers, default-closed for the four canonical roles, emitted into the invocation
so the scope is auditable afterward rather than reconstructed by grep. One CLI
lever exists today — plugins carry an `enabled` key overridable per invocation —
but MCP servers have no equivalent, so this is engineering, not configuration.

Until that lands, the interim control is the one that actually caught both:
**after every role dispatch, count the MCP calls in its event stream and record
the number.** Count the whole category, not the specific tool — this control was
written to catch remote git reads and caught a screen-reader because it counted
every MCP call. **Keep controls broader than the incident that motivated them.**
