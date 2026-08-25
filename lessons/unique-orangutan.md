---
slug: unique-orangutan
title: A substitution that never took effect, and the completion signal that outran its child
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a `runpy.run_path` copy defeated two test patches, and a double-backgrounded dispatch was reaped at 21 seconds while reporting success"
  - date: 2026-08-20
    ref: "Donor A — a delegated coder launched a gate as a background job in ITS harness, wrote 'holding here until it completes' as its final message, and exited. A child's background job does not outlive the child: when the delegated CLI parent terminated, the job died, and the orchestrator found zero gate processes. The report carried a gate status the role never obtained — the same shape one level down, inside a delegated role rather than the orchestrator"
---

Two failures sharing one shape: **a mechanism that silently did nothing, and
reported the same way as a mechanism that worked.**

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

## The completion signal that outran its child

A dispatch died 21 seconds in with no report, exit code 0, task marked complete.
Cause: `nohup … &` written *inside* a call that was already backgrounded.
Double-backgrounded — the outer call returned immediately, the harness recorded
completion, and the detached child was reaped still working.

**The tell was specific.** The script's own trailing line never printed. The
dispatch script ends by echoing its exit code, and that string was absent from a
14 KB log full of real work. **A log that ends mid-stream without the script's own
terminal marker means the process was killed, not that it finished** — and an exit
code from a wrapper says nothing about the child.

So: one level of backgrounding, chosen deliberately. And **give every detached
script a terminal marker only it can print**, because that marker is the difference
between "completed" and "reaped," which the harness's own status cannot
distinguish.

## Why these are one lesson

Both are silent no-ops that render as success — the inert patch makes a test
report a guarantee it never checked; the reaped child makes a dispatch report a
completion it never reached. Neither surfaces an error anywhere, and both are
caught the same way: **require a positive, specific witness that the mechanism
actually ran**, rather than accepting the absence of a complaint as evidence.
