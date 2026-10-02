---
slug: overjoyed-angelfish
title: A freshly seeded role configuration cannot pass kickoff preflight on an account that reports an additional usage group
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-10-01
source: user
occurrences:
  - date: 2026-10-01
    ref: "stamp of a Python command-line target, 2026-10-01 — the first kickoff preflight in the new repository refused with an ambiguous-additional-usage-group message until a custom target mapping that group's window was added to the seeded configuration by hand"
---

The seeded `kickoff.yaml` declares no custom targets. The built-in cross-provider review target therefore has an empty `usage_windows` list. `preflight` consults the usage tool, finds that the provider reports an additional named usage group, and refuses because it cannot tell whether that group's limit applies: "ambiguous additional usage group …; configure usage_windows". Refusing is the documented rule in `policies/role-models.md` and is sound. The consequence is that a repository stamped on such an account cannot start its first phase.

The fix is a dozen lines of YAML: a custom target that restates the built-in one and names the group's window. Three other derived repositories on the same machine already carry that block, each added by hand, and they do not agree with each other. Two include the additional group's window. One lists only the shared window, with a comment that this deliberately excludes additional groups. A new repository has no way to learn which reading the operator intends.

The stamp's acceptance check runs `kickoff-config show`, which validates the file and does not consult usage. Nothing in the bootstrap runs `preflight`, so the stamp reports success on a repository whose first `kickoff` is certain to stop.

What should be done differently: the answer to "does this additional group count against this target" is an operator decision about an account, not about a repository, so it should be made once and reach every repository on that account rather than being re-derived per stamp. Short of that, the refusal should print the exact block to add, and the bootstrap's acceptance should run the preflight so the gap surfaces at the stamp and not at the first phase.
