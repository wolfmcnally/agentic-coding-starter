---
slug: cute-aardwolf
title: A coordinator verifies that each instruction reached its worker before reporting the work as moving
status: candidate
scope: methodology
proposed_surface: skill
filed: '2026-11-11'
source: user
occurrences:
- date: '2026-11-11'
  ref: a batch transfer to four recipients — the coordinator told two background workers to hold for a ruling and, hours later, sent them instructions. The message service accepted the instructions and left them pending, reporting that the identity it held for each worker no longer matched. The coordinator had read the delivery state of its first messages but not of these, reported the work as under way, and nothing moved for about five hours. It then explained the failure with a claim about the messaging system that it had not read anywhere
---

Accepted is not delivered, and delivered is not done. After sending an instruction that work depends on, read its delivery state before saying anything about progress. When a delivery is refused, report the reason the system gave and stop there; an explanation of why belongs to that system's owner or its documentation, not to inference.
