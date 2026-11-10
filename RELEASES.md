# Starter Releases

## 1.5.0 — 2026-11-10

Closes two faults found in recipients on the day 1.4.0 shipped. First, a launcher refusal before launch could leave a registered review attempt that nothing accounted for: the next attempt number was registered instead of relaunching, and acceptance refused the run much later with no truthful way to record what had happened. The registrar now refuses a later attempt of an operation while an earlier one was never dispatched and names the relaunch, and `kickoff-evidence record-unlaunched-attempt` records the remaining case, a registration that can never be launched. That record is a third truthful state, not a waiver: it binds the exact registration and a refusal record retained in the run, and it is refused, when written and at every validation, if any dispatch row, execution span or advisory claim exists for the attempt. A run pinned to an earlier tool bundle needs `repin-tools` under its owner's custody before it can use it. Second, parallel test workers could race the first build of a script tool's cached dependency environment and fail unrelated proofs; the supervised runner now builds those environments once before starting workers. A minor release: one new command, no behavior removed. No recipient is inferred upgraded.

Transfers:

- **Never-launched attempts and the registrar's relaunch rule:** `bin/kickoff-evidence` with `tests/test_kickoff_evidence.py`, its recorded defects in `tests/proof-plants.json`, `.claude/skills/kickoff/dispatch.md`, `.claude/skills/kickoff/recovery.md`, `policies/orchestration-evidence.md` and the entry in `bin/README.md`.
- **Script environments built before parallel workers:** `lib/agentic_starter/test_runner.py` with `tests/test_test_governance.py`, its recorded defect, and `policies/build-gates.md`.

## 1.4.0 — 2026-11-10

Makes migrating a recipient from the pre-migration layout a repeatable procedure, from what the first such migration through `teach` found. Two commands are new. `multioperator transfer-ancestry` reports, for each shared file that differs, the source revision nearest the recipient's copy, the recipient lines no source revision ever held, and the conflicts a merge on that ancestor leaves; merging against one assumed base had silently dropped content a recipient never received. `multioperator adopt` records an owner's adoption of a conversion that was committed undeclared, which until now had no route: the staged validator refused every manifest change. The teach procedure now says how to merge edited files, routes a legacy recipient to the first post-migration release as a whole before an ordinary upgrade, and warns that the rehearsal's caller inventory understates a cutover. Test governance gains the operator's ruling on when one planted defect may witness several proofs, and twenty-nine verified defects are recorded for proofs a catching-up recipient inherits. This template's own plan index no longer opens with the rehearsal banner. A minor release: new capability, nothing removed. No recipient is inferred upgraded.

Transfers:

- **Transfer ancestry report and adoption declaration:** `lib/agentic_starter/multioperator.py` with `tests/test_multioperator.py`, their recorded defects in `tests/proof-plants.json`, and the `multioperator` entry in `bin/README.md`.
- **Edited-file merging and the legacy-recipient route:** `.claude/skills/teach/SKILL.md` and `policies/multi-operator-migration.md`.
- **Shared-defect limits:** `policies/test-suite-governance.md`.
- **Recorded defects for inherited proofs:** `tests/proof-plants.json`.

## 1.3.2 — 2026-11-10

Fixes an intermittent false failure in the process supervisor that runs tests, gates and witness commands. Under parallel load a command that had finished normally was occasionally reported as `TEST INCOMPLETE` with `owned group cleanup could not signal`, because for a few milliseconds after a command's last process exits the system refuses a probe of its process group, and the supervisor read one refusal as a child still running. It failed full gates in two repositories in one day and reproduced at about four per thousand short commands. The supervisor now probes again within its cleanup grace before deciding; a group that proves gone is a finished command, and one still unprovable at the deadline is reported incomplete as before. A patch release: one fix, no new capability. No recipient is inferred upgraded.

Transfers:

- **Supervisor liveness probe that settles a refusal:** `lib/agentic_starter/test_runner.py` with `tests/test_test_governance.py` and its recorded defect in `tests/proof-plants.json`.

## 1.3.1 — 2026-11-10

Fixes found by the first transfer of 1.3.0 to a recipient, and one rule learned from that recipient. `./bin/test-governance admit` now checks that its result can be recorded before it plants anything, and refuses with nothing witnessed when it cannot; given part of a batch it previously recorded a witness and then refused. It keeps each planted defect in `tests/proof-plants.json`, which travels with the tests, so a recipient admits an arriving proof by replaying the recorded defect and observing the failure itself instead of rediscovering what to plant. The two gate proofs that need a failing policy check now fail the test-timing check every adopter carries, not the template-only anonymization check, so they travel unchanged. A project adopting parallel test execution now qualifies its existing suite by one full parallel run, not a serial baseline, and labels subtests and parametrized cases with plain text. Nothing here adds work to a gate or test run: a defect is planted once, when a proof is admitted or changed. This is a patch release: fixes and one refinement, no new capability. No recipient is inferred upgraded.

Transfers:

- **Admission that refuses before witnessing, and recorded defects:** `lib/agentic_starter/test_governance.py` with `tests/test_test_governance.py` and `tests/proof-plants.json`; `policies/test-suite-governance.md`; the `teach`, `learn` and `stamp` skills.
- **Gate proofs that fail a universal lane:** `tests/test_check.py`. A recipient that hand-adapted these two proofs may keep its adaptation.
- **Parallel adoption qualified through the worker boundary:** `policies/test-suite-governance.md` and the transfer skills.

## 1.3.0 — 2026-11-10

Less paperwork for the same guarantees. A direct methodology change the operator asked for in the current session now needs one log record, its close, which states what was authorized beside what was delivered; a separate scope record before the work remains for transfers, work spanning sessions and agent-initiated work. A new or changed test is admitted with one command, `./bin/test-governance admit`, which plants the described defect, requires the named failure, restores the tree, and records the witness receipt and the admission together; it records nothing for a test it did not see fail. A stale generated dashboard file, the most frequent record-keeping gate failure in sampled recipients, now names its repair, and `./bin/check-execution-dashboards --regenerate` rewrites the archive from tracked inputs. Every new or changed assertion is still observed failing, every close still carries Lessons, and the gate still refuses a stale file. This is a minor release. No recipient is inferred upgraded.

Transfers:

- **Single-record methodology close:** `policies/review-lanes.md`, `policies/log-discipline.md`.
- **One-step proof admission:** `lib/agentic_starter/test_governance.py` and `bin/test-governance` with `tests/test_test_governance.py`; `policies/test-suite-governance.md`.
- **Dashboard regeneration:** `bin/check-execution-dashboards` with `tests/test_execution_dashboard.py`; `policies/execution-telemetry.md` and the kickoff close resource.

## 1.2.0 — 2026-11-10

The full gate no longer re-runs tests whose inputs have not changed. Its test lane compares the tree with the last tree on which every proof family passed, on the same runtime, and runs only the families the changed-path selection maps to what differs: one family for a new log entry, none when nothing a test covers or reads changed, and every test whenever the comparison cannot be trusted. The push receipt still binds the exact whole tree. `./bin/check all --no-reuse` and a bare `./bin/test` always run everything, and an uncached run that fails a family reuse would have skipped reports `TEST REUSE UNSOUND` and discards the record. A deliverable's own test runner can now be declared as proof families of kind `command`, so a Swift, Rust or Node suite takes part in selection and reuse instead of always running in full. Paths the candidate partition classes as bookkeeping are treated as data in selection and no longer widen a run. Language profiles gain a Swift entry and name each runner's parallel switch. A Starter release is now qualified by the uncached gate. This is a minor release: it adds capabilities and changes which tests the gate executes, not what it certifies. No recipient is inferred upgraded.

Transfers:

- **Test reuse against the last proven tree:** `lib/agentic_starter/test_governance.py`, `bin/test-governance`, `bin/test`, `bin/check` with `tests/test_test_governance.py`, `tests/test_toolchain_entrypoints.py`, `tests/test_check.py`; `policies/build-gates.md`, `policies/test-suite-governance.md`. Requires `bin/kickoff-tree-id`, `bin/check-receipt` and `candidate-partition.yaml`, which the receiver already carries.
- **Native-runner proof families:** the `command` kind in the same engine; the receiver declares its own families.
- **Parallel execution by profile and the Swift profile:** `policies/build-gates.md` and the `stamp` skill; the receiver applies its own runner's switch.

## 1.1.0 — 2026-11-10

The build gate can now say everything that is wrong with a tree in one run, and a checkout that does not hold a project's private evidence can pass it. `./bin/check report` runs every lane to the end, names each failed or incomplete lane, and never stores a receipt; `./bin/check all` is unchanged and still stops at the first failure. Every lane now prints its elapsed seconds. Retained acceptance evidence under the ignored `.kickoff/` directory that is absent from a checkout, as on a fresh clone or a second machine, is reported as `EVIDENCE NOT HELD` and no longer refuses the gate; evidence that is present but altered still refuses, and publishing a new completion still requires the bytes. A methodology close must now be an END or PARK record composed with its Lessons, and can no longer be appended under a bare heading. Receivers carry a machine-readable record of the release they have adopted, and the transfer preflight lists the releases a receiver has not recorded. Repeated tool names in the transfer skills' bundle lists were collapsed. This is a minor release: it adds capabilities and relaxes one refusal, with no change to existing commands. No recipient is inferred upgraded.

Transfers:

- **Gate report mode and lane timing:** `bin/check` with `tests/test_check.py`; `policies/build-gates.md`.
- **Evidence not held, methodology close guard, provenance preflight:** `bin/multioperator` and `lib/agentic_starter/multioperator.py` with `tests/test_multioperator.py`; `policies/phase-status.md`, `policies/log-discipline.md`.
- **Receiver provenance record:** `collaboration/methodology-provenance.json`, written by the receiving transfer; `teach`, `learn` and `stamp` skills; `policies/starter-releases.md`.

## 1.0.2 — 2026-11-10

On macOS the command wrappers now mark the ignored runtime-state directory `.kickoff/` as excluded from Dropbox syncing. The shared toolchain helper creates the directory and writes both Dropbox ignore attributes on every `./bin/setup`, `./bin/test` and `./bin/check` run, whether or not the checkout is currently inside a Dropbox folder, and stops if the marking fails. The rule travels with the helper through `stamp` and `teach`, so a project that receives it is marked on its next wrapper run. Dropbox removes an already-synced `.kickoff/` from its server and other devices once it is marked and keeps the local copy. Other platforms and other sync services are unchanged. Released as a patch at the operator's direction; no recipient upgrade is inferred.

## 1.0.1 — 2026-11-10

Corrected the mini-method's copyable setup and delivery instructions to match the full methodology: agents commit and non-force fast-forward-push approved work without separate human approval after applicable checks, explicit staging and custody verification. Delivery uses only an existing authorized upstream and publication scope, verifies the actual remote result, and preserves task-specific holds, hooks, native permission denials and human subjective acceptance. Setup still never creates or changes a remote. This is a patch refinement, with no new capability or inferred recipient upgrade.

## 1.0.0 — 2026-11-07

First named baseline of the continuously evolving agentic-development methodology hub. The signed annotated tag `v1.0.0` identifies the complete qualified source commit after normal delivery; these notes alone do not establish that the tag exists or that any recipient adopted it.

- Unified teach/learn preconditions and recipient outcomes in both directions, with supported existing-product retrofit, preserved narrative history and no fabricated historical acceptance.
- Preferred available supported cross-harness launch and communication capabilities while retaining direct native/watched-CLI fallback and existing authority, permission, custody, budget and evidence controls.
- Shared identical readiness commands within one preflight while keeping different model, effort, access and tool-capability probes separate. Each real role retains its own authority, registration and work.
- Established feature/minor, fix-or-refinement/patch and rare rewrite-or-breaking/major release numbering, exact source provenance and the distinct outside, pre-1.0.0 and verified named-adoption states.

Earlier verified Starter-derived methodology is designated `pre-1.0.0`; never-adopted repositories are `outside`. No older history is retagged and no receiver upgrade is inferred. See the Starter-only [release policy](policies/starter-releases.md).
