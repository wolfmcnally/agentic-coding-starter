---
slug: gleeful-whippet
title: A witness's expected text can match the assertion's echoed source instead of its failure
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-10-26
source: user
occurrences:
  - date: 2026-10-26
    ref: "this template, full sweep — a red witness for a new resume-forwarding assertion planted a defect that made the test fail with a ValueError before the assertion ran; the expected text was the assertion's message, which pytest printed as part of the failing source line, so the witness tool accepted the receipt. The author noticed, recorded a second witness whose defect reached the assertion with the expected text prefixed by the exception type, and marked the first receipt as not relied on"
---

The witness tool requires the failing output to contain the expected text. Pytest's failure report reprints the source lines around the failure, including the assertion and its message, so a message string can appear in the output of a run that never reached the assertion. The check meant "this assertion fired" and measured "this text appears anywhere", which a different failure can satisfy.

**Expect the exception-qualified failure line (`AssertionError: <message>`), not the bare message, and prefer a defect that leaves every earlier statement in the test working.** A tool-side remedy would match only pytest's `E ` failure lines, or reject a receipt whose output names a different exception type first; that is a `bin` change, not adopted here.

Second instance this would catch: an expected text that is also a literal in a fixture or a log line the test prints before failing for an unrelated reason.
