---
slug: unique-orangutan
title: A test double that is never installed is indistinguishable from one that is installed and unused
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a `runpy.run_path` copy defeated two test patches"
---

## The inert substitution

`runpy.run_path` returns a **copy** of the module globals. Functions defined in
that module resolve their globals against the *original* dict, so assigning into
the returned namespace cannot reach them:

```python
ns = runpy.run_path(path, run_name="probe")
ns["helper"] = lambda: "PATCHED"
ns["caller"]()                    # -> "ORIGINAL"
ns is ns["caller"].__globals__    # -> False
```

Two tests patched this way. One was *named* for a failure path and **had never
once exercised it** — every run took the clean path. It failed twice against the
implementation, and both times the disagreement was the inert patch rather than a
defect; the second round nearly consumed a coder cycle "fixing" working code to
satisfy a test that was measuring nothing. A sibling test in the same file
survived only by accident: its control mutated a shared **module object**, which
both dicts point at.

Patch what the running code actually reads:

```python
monkeypatch.setitem(ns["some_function"].__globals__, "target", replacement)
```

**The general rule: a test double that is never installed is indistinguishable
from one that is installed and unused.** Both produce a green test. A substitution
therefore needs a **positive assertion that it took effect** — assert the
failure-path output is *non-empty* under the injected failure and pinned empty
under the clean path. The empty case is what makes the non-empty case mean
something.

This repo's toolchain and evidence tests stub external tools heavily
([`tests/test_toolchain_entrypoints.py`](../tests/test_toolchain_entrypoints.py),
[`tests/test_kickoff_config.py`](../tests/test_kickoff_config.py)), which is
exactly the population this rule guards.

## Ledger note — 2026-10-07 (split)

This lesson was filed together with a second failure of the same shape, a completion signal that outran its child. The two have different remedies, so the operator split them in the 2026-10-07 sweep; the other is `camouflaged-kakapo`. This one keeps its single incident.
