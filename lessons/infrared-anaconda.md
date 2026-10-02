---
slug: infrared-anaconda
title: A skill that names a template detail by value goes stale when the template moves
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the skill says to move the test's failure-injection stub onto the last policy gate and names it as the shell-syntax check; the last gate once the template-only one is removed is now the test-time check, so the named target no longer proves what the instruction says it must"
---

`stamp` Step 5 explains that `tests/test_check.py` injects a failure into the last policy gate to prove a later gate's output cannot mask it, and that the stub must move when the template-only anonymization gate is removed. It then names the destination's last gate: `check-shell-syntax`. In `bin/check` today four gates run after that one, ending in `policy-test-time`. An agent that followed the named value would have moved the stub to a gate in the middle of the sequence, and the test would have kept passing while no longer proving the property.

The stamping agent followed the stated principle instead of the stated name and got it right. That worked because the paragraph happens to explain why. An instruction that had given only the name would have been obeyed into a test that passes for the wrong reason, which is the outcome the paragraph was written to prevent.

The gates were added by changes to `bin/check` that had no reason to open the stamp skill. Nothing connects the two.

What should be done differently: where a skill needs a value the repository already holds, such as the last gate in a sequence, the number of universal skills, or the list of required executables, it should say how to read that value from its source rather than quote it. Where quoting is unavoidable, the quoted value needs a check that fails when the source moves. Kin to `traditional-prawn`: both are hand-kept copies of facts the template owns, with no witness.
