---
slug: smoky-jackrabbit
title: Resolve discovered configuration dependencies before closing a learning shortlist
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-09-04
source: learn
occurrences:
  - date: 2026-09-04
    ref: "LEARN assessment — the operator identified a root candidate declaration omitted from the proposed transfer shortlist"
---

The assessment inspected candidate-identity code but did not follow its new root declaration before presenting the shortlist. The operator's correction exposed the omission. File-name novelty was an incomplete proxy for behavioral novelty: an existing script can change its governing contract by loading a new configuration file.

The proposed improvement is to resolve configuration dependencies found in an inspected mechanism before declaring that mechanism assessed. A future assessment should be able to name the owning declaration and its consumers, or explicitly record why they could not be inspected. This is a candidate lesson, not a new binding instruction.
