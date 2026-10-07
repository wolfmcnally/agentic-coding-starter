---
slug: berserk-cassowary
title: A plan that promises a guard's consequence must check the guard is armed in this checkout
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-10-07
source: user
occurrences:
  - date: 2026-10-06
    ref: "this template — an operator-approved plan stated that commits would be refused while a red witness was pending, on the strength of the pre-commit hook calling validation; the hooks are opt-in and were not installed in the checkout, which the hook witness reported in one line when it was finally run during verification"
---

The plan told the operator what a new guard would cost: for as long as a witness was open, commits in that checkout would be refused. The reasoning was sound as far as it went. The hook script runs validation, and validation would refuse. What the plan never checked was whether the hook runs. In this repository hooks are opted into per checkout, and this one had not opted in, so the stated consequence did not hold here; only the full gate that qualifies a push was guaranteed to refuse.

The claim was written from reading the hook file. Reading a configuration shows what would happen if it were live, and the repository carries a command whose whole purpose is to say whether it is. The error was caught only because the verification step tried to trip the guard for real, and by then the consequence had already been presented to the operator as a cost of approval.

**Before a plan states what a guard will do, run the guard's liveness witness and say which checkouts the statement covers.** A consequence that depends on opt-in machinery is conditional, and the condition belongs in the sentence that states it.

Correction applied in the same pass: the policy now says the commit hook refuses where a checkout has opted in and that the full gate always refuses, and the operator was told the plan's sentence had been wrong.
