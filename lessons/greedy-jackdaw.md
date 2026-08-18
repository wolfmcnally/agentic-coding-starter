---
slug: greedy-jackdaw
title: A gate's wrapper is where its preconditions live — never invoke the inner implementation directly
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-17
    ref: "Donor A phase close — the operator invoked a gate's inner test harness directly with a hand-supplied interpreter flag, bypassing the wrapper preamble that resolves the interpreter once to an absolute executable; every mutated child re-entered the package manager and the single-row proof hung reproducibly to its timeout cap, consuming a full diagnostic cycle across two threads before a controlled re-run isolated the one variable"
---

A gate's wrapper script is not a convenience layer over the "real"
implementation — it is where the gate's preconditions are established. In the
donor incident, every gate script sourced a shared preamble precisely to
resolve the repository interpreter once to an absolute executable path and
refuse anything else; invoking the inner implementation directly with a
hand-supplied interpreter flag silently re-introduced the exact hazard the
preamble exists to prevent, and produced a failure mode (reproducible hangs at
the timeout cap) that read as a defect in the code under test.

The trap's shape: the inner tool's `--help` advertises exactly the flag you
want, so reaching past the wrapper feels like precision rather than bypass.
The wrapper's work is invisible when it is doing its job — which is what makes
skipping it feel free.

Two corollaries earned by the incident:

- **A hand-built invocation of gate machinery is itself an unvalidated
  instrument.** Before spending diagnostic cycles on a failure only your
  invocation produces, reproduce it through the gate's own entry point; a
  symptom that vanishes there is an invocation artifact, not a finding.
- **Do not bank a pass against an unexplained hang.** One hang plus one pass
  is a variable you haven't found yet. The operator's cost caveat belongs
  beside the credit: the isolating re-run happened because it was cheap
  (~2 minutes); at twenty minutes a shot the convenient "flaky-environmental"
  verdict was the likely permanent record. Where reproduction is expensive,
  the discipline must be structural: no transient or environmental
  classification enters a permanent record without a reproduction attempt
  through the canonical entry point.
