---
title: A stand-in that records `$$` from a subshell makes its proof watch the wrong
  process
scope: methodology
proposed_surface: test
source: teach
slug: ambrosial-wapiti
status: candidate
filed: '2026-11-13'
occurrences:
- date: '2026-11-13'
  ref: a recipient's 1.6.0 transfer stopped on a template timeout proof under load;
    examining it showed the stand-in wrote the parent shell's process id from a subshell,
    so the proof passed with the behavior it guards removed
---

In a POSIX shell `$$` inside `( ... )` is the parent's process id. A stand-in that means to record a background descendant this way records the leader. The proof then asserts something about a process that exits by itself and cannot fail on its subject.

The same proof also let its shortest clock cover the stand-in's own start, so it failed on a loaded machine before reaching its subject. Both were corrected in that one proof. Not yet done: an audit of the other stand-ins in the kickoff configuration and evidence tests for a recorded `$$` in a subshell, and for any short clock that also bounds fixture setup. A proof whose red witness was never observed is the common cause; the corrected proof now has one.