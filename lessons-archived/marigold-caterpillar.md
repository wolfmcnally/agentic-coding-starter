---
slug: marigold-caterpillar
title: Stamp's acceptance list contains items its own procedure makes unsatisfiable
status: codified
scope: methodology
proposed_surface: skill
filed: 2026-10-01
closed: 2026-10-01
graduated_to: .claude/skills/stamp/SKILL.md
source: user
occurrences:
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the config manager's reset, which the skill requires, drops thirteen of the seeded file's twenty-four comment lines, while the acceptance list expects the section comments to be there to preserve"
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the acceptance list says no destination file names the template-only anonymization members, but five files the skill copies verbatim name them in plain text"
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the acceptance list asks for proof that staged, unstaged and untracked format failures are each rejected, and the template carries no behavioral test of that for the destination to inherit"
---

`stamp` Step 7 is the bootstrap's acceptance check. Three of its items cannot be met by an agent that follows Steps 1 through 6 exactly.

Step 2 says to seed both configuration sections with `kickoff-config reset all`. Run against the template's own `kickoff.yaml`, that command leaves eleven of twenty-four comment lines: the explanations above the research budgets, the role timeouts and the self-resume budget are gone. Step 7 then expects a scoped model edit to preserve the timeout and research comments, which no longer exist.

Step 7 says no file in the destination links or names the anonymization policy, its checker or its contract test. The `teach` and `sweep-planning` skills, `briefs/agentic-bootstrap.md`, `policies/lessons.md` and `policies/repo-relative-paths.md` all name at least one of them, and all five are on the verbatim list. No link is broken, so no gate fails, and the item is simply false of every stamp.

Step 7 asks that staged, unstaged and nonignored untracked format failures each be rejected without rewriting the candidate. The adapted `tests/test_check.py` and `tests/test_toolchain_entrypoints.py` contain no test of it. The agent proved it by hand in a disposable copy.

In each case the agent reported the item as not met or as proved outside the suite, which is the honest outcome and also means the acceptance check cannot come back clean. A list that cannot be satisfied teaches its reader that unmet items are normal, and the next genuinely unmet item will look the same.

What should be done differently: an acceptance list is checked against the procedure it accepts before it ships. For each item, either the procedure produces it, or a test in the copied suite proves it, or the item is reworded to what is actually true, here "no link to" rather than "no mention of". Kin to `magenta-ferret`, where a policy's own verification block escaped the rules the corpus states.

Ratified 2026-10-01. The three items are now satisfiable: `stamp` no longer resets a copied configuration, since the reset changed no value and removed the comments; the anonymization item asks for no links and no mention in the files the skill adapts, which is what is true; and `tests/test_check.py` carries a format-failure proof that runs the real formatter, for every destination to inherit. The general rule, that an acceptance list is checked against the procedure it accepts before it ships, is not written into a policy; it was applied here by hand.
