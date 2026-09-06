---
slug: attentive-dolphin
title: Derive mutation batteries from what the measurement cannot distinguish
status: candidate
scope: methodology
proposed_surface: agent
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — six mutations proved six controls fired, while four different wrong implementations remained indistinguishable to those controls"
  - date: 2026-09-05
    ref: "METHODOLOGY completion — an effectiveness assay counted a test failure caused by dereferencing the copied skill symlinks, without first establishing that the unmodified disposable copy passed"
  - date: 2026-09-05
    ref: "METHODOLOGY independent review R1 — the comparative evaluation fixture accepted an unrelated import-time RuntimeError as a successful wrong-repair rejection because it required only a traceback"
---

An implementation proved its controls with six deliberate mutations. Every
mutation was caught, yet review found four wrong implementations that passed
the same suite.

The mutations came from what each control was designed to catch. They proved
the controls fired in their intended direction, but never probed what each
measurement was unable to distinguish: incomplete enumeration, structured
input reduced to tokens, a state claim represented by a count, or a refusal
verified only by exit status.

**The rule candidate:** for each control, name the property it claims and the
quantity it actually measures. Construct a wrong implementation that preserves
the measured quantity while violating the property. That projection gap, not
the control's happy-path design, supplies the mutation.

Also reconstruct the pre-repair control and show it accepting the mutant. This
inverted run distinguishes a repair that closed the observed gap from one that
merely moved it. Qualify the mutation harness against known-good code first so
its silence cannot masquerade as evidence.

The local recurrence inverted the signal: nonzero exit was the proxy for detecting a seeded defect, but the copying step itself broke a healthy mirror. Complete diagnostics identified the symlink assertion rather than the intended defect. Preserve symlinks in disposable copies and require the same command to pass before applying its mutation; a baseline failure must stop the assay, not increase recall. This correction strengthens the instrument under its existing accuracy contract; it does not graduate this candidate lesson or make the frozen corpus comprehensive.

The independent review found the same projection gap in a new instrument: requiring a traceback rejected successful wrong repairs but accepted unrelated startup crashes. Each fixed control now names its expected exception type and message, and a startup-failure counterexample proves that unrelated errors refuse qualification. This is a distinct observation in the evaluation pack, not another occurrence counted from rerunning the assay incident.
