---
slug: zircon-mamba
title: Fixture repositories must not inherit the machine's commit signing
status: codified
closed: '2026-11-11'
graduated_to: tests/conftest.py
scope: methodology
proposed_surface: test
filed: '2026-11-11'
source: user
occurrences:
- date: '2026-11-11'
  ref: three recipients in one batch transfer — fixture commits exited 128 under parallel workers because the machine signs every commit and the signing agent refused some of many simultaneous requests; one recipient measured one to four failures in 64 simultaneous signed commits and none with signing off
---

Test setup turns signing off for every repository a test creates, through git's environment configuration, which is read after every configuration file. The operator's own commits are untouched.
