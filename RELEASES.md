# Starter Releases

## 1.9.0 — 2026-11-20

Adds a mechanical check that a release is cut from the only checkout there is. A product release was tagged from a clean checkout while another registered worktree of the same repository held unexamined tracked and untracked changes; nothing looked at it. `./bin/check-release-worktrees` now passes only when the repository has exactly one registered worktree, the checkout being released, and that checkout has no tracked, staged or untracked change. Any other registered worktree fails it, clean or not, as does a locked, prunable, bare, missing or unreadable registration, a record without its identity fields, and a Git command that fails. It only reads, and never removes, prunes or resets anything. The human-judgment policy requires it at the start of release preparation, before the costly gate, and again immediately before each tag or publication; it is deliberately not part of the ordinary full gate, because a linked worktree is legitimate during development. The same policy now prevents the state earlier: a temporary worktree's owner and purpose are recorded when it is created, the coordinator receiving a lane or phase confirms its unique work is delivered or preserved and retires it with nonforced commands at handback, and a dirty or abandoned handoff keeps a named owner and a precise hold instead of being discarded.

Transfers:

- **One clean checkout before a release:** `bin/check-release-worktrees` with `tests/test_check_release_worktrees.py`, its recorded defects in `tests/proof-plants.json`, the `release-worktrees` family in `tests/proof-estate.yaml`, the delivery-resource and release sections of `policies/human-in-the-loop.md`, the `check-release-worktrees` entry in `bin/README.md`, the handback sentence in the kickoff skill's `close.md`, the cleanup section of `manual/src/workflow.md` and the copy list in `.claude/skills/stamp/SKILL.md`. A recipient adds the two runs of the check to its own release procedure; a recipient with registered worktrees resolves each with its owner before its next release, and nothing is removed for it.

## 1.8.0 — 2026-11-20

Removes turn caps from the methodology. No agent invocation carries a turn quota any more: the per-role `claude_max_turns` setting, the `--max-turns` flag the launcher passed to the Claude CLI, the fixed caps on the sign-in and toolchain probes, the procedure for assessing and continuing a review that hit its cap, the `watch --cap-hit-assessment` option and the `rescue` registration reason are all gone, with their tests and documentation. The first-event, idle and hard clocks are unchanged and are now the only per-invocation guards on every venue; the limits on review passes and loop cycles, research budgets and the watcher's local turn count are also unchanged. **A recipient must delete the `claude_max_turns` lines from its own `kickoff.yaml` when it adopts this release, because the validator now refuses the key.** The release also carries four fixes to bookkeeping checks. The full gate runs the catalog and report checks before lint and tests, so a stale tree stops in about a second instead of after the costly lanes. Report regeneration validates the whole archive as it would stand before it writes anything, and never rewrites a handoff. Registering a document the catalog already lists writes nothing and succeeds. And a run refuses to start on a tree that fails the catalog check.

Transfers:

- **Turn caps removed:** `bin/kickoff-config` and `bin/kickoff-evidence` with `tests/test_kickoff_config.py`, `tests/fixtures/kickoff_config_seed.yaml`, the two retired proofs' removal from `tests/proof-plants.json`, `policies/role-timeouts.md`, `policies/role-models.md`, `policies/four-canonical-agents.md`, the kickoff skill's `preflight.md`, `planning.md`, `implementation.md` and `dispatch.md`, `.claude/skills/teach/SKILL.md`, `briefs/cross-agent-invocation.md`, `briefs/deterministic-orchestration.md`, `briefs/eacp-pattern-map.md`, `manual/src/workflow.md` and the `kickoff-config` entry in `bin/README.md`. The recipient removes `claude_max_turns` from its own `kickoff.yaml`, keeps its clock values, and retires the two cap-hit proofs in its own proof records.
- **Catalog and report checks before the costly lanes:** `bin/check` with `tests/test_check.py` and its recorded defects.
- **Regeneration that validates before it writes:** `bin/check-execution-dashboards` with `tests/test_execution_dashboard.py`, its recorded defect and `policies/execution-telemetry.md`.
- **Repeatable catalog registration:** `bin/check-catalogs` with `tests/test_check_catalogs.py`, its recorded defect and `policies/briefs.md`.
- **Catalog check at run start:** `bin/kickoff-evidence` with `tests/test_kickoff_evidence.py`, its recorded defect and `policies/orchestration-evidence.md`.
- **Tool catalog:** the matching entries in `bin/README.md`.
- **Omitted from the 1.7.0 list:** `briefs/open-source-releases.md` and `briefs/transfer-management.md` changed in 1.7.0 and were not named there. A recipient that adopted 1.7.0 from its list takes them with this release.

## 1.7.0 — 2026-11-14

Fixes the template defects that three layout migrations and five upgrades exposed, so that a full transfer into a project on the earlier layout, or one whose product is not Python, no longer depends on a worker inventing workarounds. Two capabilities are new. A project whose deliverable has its own test suite in another language now declares it with one executable, `bin/test-native`; `./bin/test` then runs it as a second lane after pytest, under the same hang supervision and never inside a pytest worker, and records a tree as proven only when both lanes pass. And `./bin/test-governance admit` now records the retirements and family changes a catch-up needs in the same input as the arriving proofs, since neither half is valid alone. The layout converter reports every line it renames, leaves a Markdown sentence that names both constitution files for a person to settle, repoints a link to a retired tool where it used to leave a link to nothing, and reports the proof families it removed. The record tool reads a relative path from the caller's directory, where it used to validate its own repository and blame the constitution. The route check's refusal of a recipient whose adoption is not declared now names the recorded release and the owner's command that lifts it. A timeout proof that recorded the wrong process, and so could not fail on its subject, is corrected. The transfer skill gains the one-cutover rule for a target whose proof records are current, the call-site check for a changed function signature, gate prerequisites assessed before anything is written, the commit form and no-attribution rule for workers, and the rule that a failed gate is reported, not rerun. The documentation policy now requires the README and the manual's first page to open with the problem the package solves.

Transfers:

- **Native suite as a second supervised lane:** `bin/test` and `lib/agentic_starter/native_suite.py` with `tests/test_toolchain_entrypoints.py`, their recorded defects in `tests/proof-plants.json`, `policies/build-gates.md` and the `bin/test` entry in `bin/README.md`. A recipient that built its own equivalent replaces it with the supplied lane and a `bin/test-native` of its own.
- **Catch-up admission with retirements:** `lib/agentic_starter/test_governance.py` with `tests/test_test_governance.py`, its recorded defect, `policies/test-suite-governance.md` and the `test-governance` entry in `bin/README.md`.
- **Converter report and reference handling:** `lib/agentic_starter/multioperator_transition.py` with `tests/test_multioperator.py` and its recorded defect.
- **Relative paths and the undeclared-cutover refusal:** `bin/multioperator` and `lib/agentic_starter/multioperator.py` with `tests/test_multioperator.py` and its recorded defect.
- **Corrected timeout proof:** `tests/test_kickoff_config.py` with its recorded defect.
- **Transfer skill guidance:** `.claude/skills/teach/SKILL.md`.
- **README and manual open with the problem:** `policies/software-documentation.md`.

## 1.6.0 — 2026-11-12

Lets a run truthfully accept a review the owner directed outside the default launcher. A recipient's owner directed, for one task, a reviewer other than the one the run had frozen, started by a launcher other than the watcher. The review was real, but the evidence tool refused to register it, so nothing after registration could be recorded and the phase could not be accepted. The watcher remains the default and nothing new is required to use it. Two commands are new. `kickoff-evidence record-owner-directed-review` records the owner's verified, task-specific direction; it replaces the frozen reviewer for that review's next attempts and changes nothing else. `kickoff-evidence attest-directed-launch` retains what the launcher reported, with every unobserved value recorded as `unknown`. The attempt is still registered, spends its ordinary pass, is timed, bound to the candidate before and after, ingested and dispositioned; a directed review without its attestation is refused, and `status` reports such reviews as attested by the primary rather than witnessed by the tool. No launcher is named or required.

Transfers:

- **Owner-directed review outside the watcher:** `bin/kickoff-evidence` with `tests/test_kickoff_evidence.py`, its recorded defect in `tests/proof-plants.json`, `policies/orchestration-evidence.md`, `.claude/skills/kickoff/dispatch.md` and the `kickoff-evidence` entry in `bin/README.md`.

## 1.5.1 — 2026-11-11

Fixes three faults in the test setup that a batch transfer of 1.5.0 to four recipients exposed, none of them in the methodology's own rules. Throwaway repositories that tests create inherited the machine's commit signing; on a machine that signs every commit, a signing agent asked for many signatures at once refused some, and fixture commits failed intermittently under parallel workers in three recipients. Test repositories now never sign, whatever the machine configures. Stand-in programs that tests expect to answer were given one or two seconds to speak, which a loaded machine could not always meet; they now get a generous clock, and only the proof that a timeout fires keeps a short one. The script-environment preparation from 1.5.0 can now build into a cache the caller names, for a project that gives each test worker a private cache, where the supervisor's own build is never used. `test-governance validate` now says how many proofs await admission instead of listing the first three as if they were all. The `teach` skill gains the rules for a batch of targets and three limits of the ancestry report.

Transfers:

- **Fixture repositories that never sign:** `tests/conftest.py` with `tests/test_test_governance.py` and its recorded defect in `tests/proof-plants.json`. A recipient with its own `tests/conftest.py` merges the function and its one call.
- **Generous clocks for stand-ins that answer:** `tests/test_kickoff_config.py` and `tests/test_kickoff_evidence.py`.
- **Script environments in a named cache:** `lib/agentic_starter/test_runner.py` with `tests/test_test_governance.py` and its recorded defect.
- **Admission count in validation:** `lib/agentic_starter/test_governance.py`.
- **Batch transfers and ancestry limits:** `.claude/skills/teach/SKILL.md` and `policies/build-gates.md`.

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
