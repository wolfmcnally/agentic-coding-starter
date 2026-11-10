---
title: Diagnostic test labels must survive the parallel worker boundary
scope: methodology
proposed_surface: test
source: learn
slug: steady-perch
status: codified
closed: '2026-11-10'
graduated_to: policies/test-suite-governance.md
filed: '2026-11-06'
occurrences:
- date: '2026-11-06'
  ref: "the donor \u2014 during its first complete adoption of parallel test execution,\
    \ a serial baseline passed every existing product case, and the first parallel\
    \ run failed transporting two passing subtests whose display labels held an exception\
    \ object and a path object"
- date: '2026-11-09'
  ref: "the donor \u2014 a later phase's first changed-selection gate failed serializing\
    \ a subtest label that contained a lone surrogate character"
- date: '2026-11-10'
  ref: "the donor \u2014 a later phase's changed-selection run failed transporting\
    \ a timeout error used only as subtest display text; a string label preserved\
    \ the scenario and its assertions"
---

Harvested from a donor's ledger, where it was filed as a methodology candidate and then recurred twice.

A parallel runner sends each test's result from a worker process to the controller, and everything attached to the result has to be serializable. A subtest's label is attached to it. In the donor the labels were only for display: an exception instance in one, a path object in another, later a string containing a lone surrogate, later a timeout error. Each test passed its assertions and the run still failed, at the transport, with a diagnostic about serialization that names neither the test's subject nor its assertion.

Three things made it expensive. The serial baseline that qualified the suite before adoption could not see it, because nothing crosses a process boundary in a serial run. It surfaced one label at a time, on whichever selection first happened to include the test, so it recurred across three separate days. And the failure reads like a broken test rather than a broken label.

The donor's repair each time was to make the label a string and leave the inputs and assertions alone; it confirmed the cause by restoring the original label, seeing the same failure, and restoring the fix.

**When a project adopts parallel execution, qualify its existing suite by one full run through the actual worker boundary, not by a serial baseline, and give subtests and parametrized cases labels that are plain strings.** A cheap sweep at adoption is to search the suite for subtest labels and parameter identifiers built from objects rather than text.

Not settled, and the reason this is a candidate and not a rule: whether the methodology should carry a mechanical check for non-string labels or only the adoption-time full run. The donor's three occurrences were all in product tests written before parallel execution arrived.

Graduated 2026-11-10 by the operator: the adoption-time full parallel run and plain-text labels became a rule in the test-governance policy and in the transfer guidance for parallel execution. The automatic check for non-text labels was considered and not adopted.
