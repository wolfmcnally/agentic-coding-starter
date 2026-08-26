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
