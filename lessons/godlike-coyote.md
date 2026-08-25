---
slug: godlike-coyote
title: Normalize the denominator before comparing throughput numbers — the unnormalized reading skews encouraging
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a published benchmark rate was compared against a live workload rate whose payloads were ~18x larger; normalized, the direction reversed"
  - date: 2026-08-16
    ref: "Donor A — a concurrency probe was compared against an earlier probe of half the concurrency, across runs whose serial baselines differed 35%; normalized to each run's own baseline, the apparent gain became a loss"
---

Two throughput comparisons in one night were arithmetically correct and still
wrong, because each compared a rate against a denominator measured under
different conditions — and **both times the unnormalized reading was the more
encouraging one**, which is exactly when a number is least likely to be
challenged.

1. **Payload-size mismatch.** A published benchmark table said the upstream
   saturates at ~30 inputs/s; a live rebuild ran at ~12 inputs/s, and the gap was
   read as the workload underperforming. The benchmark inputs were ~20-token probe
   strings; the real chunks were ~355 tokens. Normalized to tokens/s, the "slow"
   run had roughly **7×** the benchmark's throughput. The table had been published
   without its payload size, inviting the misread.
2. **Moved baseline.** A concurrency probe aggregated 22.6k tok/s against an
   earlier half-concurrency probe's 19.4k, read as "+17% from doubling." The two
   runs' own serial baselines differed by 35% from hour-to-hour upstream variance.
   Normalized to each run's own baseline, the concurrency multiple *fell* from
   2.72× to 2.36× — doubling made things worse, the opposite of the unnormalized
   reading.

**The rule.** A rate comparison is valid only against a denominator measured under
the same conditions — same payload shape, same session or hour, same instrument.
Before citing any A-vs-B throughput claim, name what one unit *is* on each side
(inputs? tokens? files?) and when and how each baseline was taken; if they differ,
normalize first or re-measure a matched baseline in the same run. Publish
benchmark tables with their payload characteristics, or they will be misread by
the next careful person.

**Corollary that earned the entry: skew is asymmetric in practice.** An
unnormalized comparison that flattered the work survived two careful readers; both
corrections came from the party the number flattered less. **Treat an encouraging
cross-run comparison as unverified until normalized.**

Directly relevant to this repo's human-wall-clock-efficiency invariant
([`CLAUDE.md`](../CLAUDE.md)): every "this is materially faster" claim that
justifies a change to gates, iteration, or reuse is exactly such a comparison, and
[`policies/verification-discipline.md`](../policies/verification-discipline.md)
already requires a material count to carry its reproduction procedure. A rate needs
its denominator on the same terms.
