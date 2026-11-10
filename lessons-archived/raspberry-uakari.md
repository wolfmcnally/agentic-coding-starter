---
slug: raspberry-uakari
title: The process supervisor can report a finished short command as incomplete under
  heavy parallel load
status: codified
closed: 2026-11-10
graduated_to: lib/agentic_starter/test_runner.py
scope: methodology
proposed_surface: bin
filed: 2026-11-10
source: user
occurrences:
- date: 2026-11-10
  ref: "this template \u2014 during an operator-approved change, one full parallel\
    \ run of 188 tests failed a new witness test with 'TEST INCOMPLETE: hang, interruption\
    \ or outstanding child' and 'owned group cleanup could not signal 15: Operation\
    \ not permitted' for a two-line shell script whose last command was an external\
    \ program; the same test passed in 24 further runs alone and under load, and in\
    \ two later full runs after the script was made to end with a shell builtin"
- date: '2026-11-10'
  ref: "a recipient \u2014 the first full run of its gate after a transfer failed\
    \ a different proof with the same two diagnostic lines, for a script that ends\
    \ with a shell builtin; an unchanged rerun passed"
---

The witness command was a shell script that ran one external program and exited. The supervisor that runs it treats a process group that still has members after its leader exits as an outstanding child, tries to signal the group, and reports the run as incomplete when the signal is refused. On this platform a signal to a group whose only remaining member has already exited but has not yet been collected is refused with a permission error, so a child that is finishing normally can look like one that cannot be stopped.

I could not reproduce it, so the mechanism above is a reading of the two diagnostic lines, not an observed sequence. What would settle it: run a script of that shape many times under full parallel load with the supervisor's group-membership check logged, and see whether the refused signal coincides with a member that is already dead.

The fixture now ends with a builtin, as the older witness fixture does. That removes the trigger from the test and leaves the supervisor as it was. **If this recurs anywhere, in a witness, a gate or a test, treat it as a supervisor defect: a refused signal to a group with no live member is a finished run, not an incomplete one.**

Codified 2026-11-10 on the operator's direction to fix the supervisor. The second occurrence disproved the first reading above: the script that failed ended with a builtin, so the shape of the script was never the trigger. The fault was then reproduced on demand, at about four per thousand short commands under parallel load, and measured: for up to twenty milliseconds after a command's last process exits, a probe of its process group is refused, and the refusal always cleared by itself. The supervisor read one refusal as a live child. It now probes again within its cleanup grace and still reports an unprovable group as incomplete at the deadline. The same reproduction after the fix reported none in over seven thousand commands.

What the first filing got wrong is worth keeping: it named a mechanism from two diagnostic lines and changed a test fixture to avoid the supposed trigger, which removed nothing. The honest part of that filing was the sentence saying the mechanism was unobserved and what would settle it; a stress loop of a few minutes settled it.
