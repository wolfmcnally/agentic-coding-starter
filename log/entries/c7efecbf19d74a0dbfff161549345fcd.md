---
{"at": "2026-11-10T18:40:30.494410+00:00", "body_sha256": "6574d1dc48284c1c633d6ffce0efa6b3c3af5843d99a7d278b51f33c3a200bed", "id": "c7efecbf19d74a0dbfff161549345fcd", "previous": "76e7cfff38c54621b7d849cdd3b75b83", "sequence": 40, "writer": "starter-maintainer"}
---
## 2026-11-10 18:40 — END — METHODOLOGY — Release 1.5.0: never-launched attempts and script environments before parallel workers

Scope: the operator's authorization of 2026-11-10 to repair and prevent a prelaunch-refusal fault found in two recipients and to fix the parallel first-run hazard, as one release.

Changed: the registrar refuses a later attempt of an operation while an earlier one was never dispatched; `record-unlaunched-attempt` records a registration that can never be launched, on proof that no dispatch, span or advisory claim exists, re-proved at every validation; the supervised runner builds script tool environments once before parallel workers start. The dispatch and recovery procedures, the evidence policy, the gate policy and the tool catalog say so. Two proofs were admitted and one modified, each on a planted defect.

Verification: the full gate without reuse passed on the release tree. The new evidence proof reproduces the real launcher refusal end to end and refuses a forged record for an attempt that actually ran.

Not done: no recipient was changed. A recipient whose blocked run is pinned to the earlier tool bundle still needs a maintenance transfer and a repin under its own owner. Whether `repin-tools` accepts a run that already holds a primary decision was not checked.

Lessons:
- Two lessons were filed and codified in this change, on the prelaunch refusal and on the script-environment race.
- Two candidates were filed: check whether a fault is general before retiring a recipient's own repair for it, and dashboard regeneration cannot cross a payload schema change.
