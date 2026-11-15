---
title: The provenance record's date names no convention, so a transfer near midnight
  can be dated two ways
scope: methodology
proposed_surface: skill
source: teach
slug: colorful-camel
status: candidate
filed: '2026-11-14'
occurrences:
- date: '2026-11-14'
  ref: a recipient's 1.7.0 transfer ran after midnight UTC while the local date was
    still the previous day; the worker found that every earlier value in the file fell
    on a day where both dates agree, chose the local date, and reported the choice as
    inferred
---

The provenance record carries a `recorded` date and nothing says whether it is the operator's local date or the UTC date. Log entries are stamped in UTC by the record tool; commits carry local time. For most transfers the two agree and the question never arises. When they differ, two careful workers can record different dates for the same event, and the file's history cannot settle which is right.

Nothing depends on the field to the day today, so the cost so far is an inferred choice a worker had to report. It becomes a real defect the first time a tool compares that date with a log entry or a release date.

Candidate correction: the transfer skill, or the record's schema, states one convention. UTC matches the log entries the same transfer writes and needs no knowledge of where the operator is.
