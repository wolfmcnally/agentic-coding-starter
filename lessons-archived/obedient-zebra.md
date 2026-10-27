---
slug: obedient-zebra
title: Qualify full gates inside every delegated execution environment
status: rejected
scope: methodology
proposed_surface: test
filed: 2026-08-25
closed: 2026-10-26
source: learn
occurrences:
  - date: 2026-08-25
    ref: "Donor A — delegation markers made methodology tests fail only inside the delegated coder, preventing a clean full-suite signal there"
---

An environment distinction supplied by the role watcher is real even when the
same suite passes in the orchestrator. Tests whose semantics depend on a
delegation marker must declare and test their delegated behavior explicitly.
Either make the test valid under the marker or skip it for a narrow, covered
reason. Qualify the full gate in both environments before phase work relies on
the signal.

**Closed 2026-10-26 by sweep:** no new occurrence in sixty days. A new occurrence appended here reopens it.
