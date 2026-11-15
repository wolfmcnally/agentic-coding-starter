---
title: The transfer ancestry report lists only files both sides hold, so arrivals
  and donor-only files must come from the release difference
scope: methodology
proposed_surface: skill
source: teach
slug: illegal-seal
status: candidate
filed: '2026-11-14'
occurrences:
- date: '2026-11-14'
  ref: a recipient's 1.7.0 transfer; the worker reported that the ancestry report did
    not name a file new in the release or a donor-only test, and that it found both
    from the difference between the two release tags
---

Reported by a transfer worker and not checked by the hub against the report's code. The ancestry report tells a worker which revision each shared file descends from, which is what a merge needs. A worker that takes it for the transfer's file list misses a file the release adds, and never learns that a donor file has no counterpart to merge into. All four workers of this release found the new file anyway, because their brief also gave the tag-to-tag difference.

Candidate correction: where the transfer skill describes the ancestry report, say that it covers shared files only and that the file list comes from the difference between the recorded release and the target release; or have the report add two short sections, arrivals and donor-only paths.
