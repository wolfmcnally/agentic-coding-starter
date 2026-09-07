# Astra-era evaluation pack

As of 2026-09-07: the eight instruction-loading invocations have run. The original workflow batch stopped after three design attempts produced correct code without completing delivery and a fourth was interrupted by the evaluator. A separately identified corrected batch stopped at its first two qualification cells: both implementations were approved on their first code-critic pass and both full implementation gates passed, but neither delivered within the fixed 30-minute budget. One final handoff exposed a remaining generated-log formatting defect; the other run reached close bookkeeping. The remaining 22 cells were not started. These are preserved workflow outcomes, not a general model ranking. This pack implements the [evaluation contract](../../../briefs/astra-era-development.md) and remains insufficient by itself to establish a general model ranking or an optimal phase size.

The corrected pair also exposed an invalid documentation oracle: an exact-string README assertion rejected an accurate description of the new export. The original raw failure is preserved and qualified as a proxy defect, not a code defect; the two candidates' runtime implementation files were identical. Future batches use semantic documentation rubrics for both documented tasks; the analogous currency-keyword assertion is removed too. The design rubric also records which role surfaced the unresolved choice instead of treating safe earlier orchestration as proof or failure of independent planner detection. These corrections change future instruments only; they do not rescore an existing batch.

## Comparative tasks

`tasks.json` fixes four tasks: mechanical symbol rename, required invoice currency across independent inventories, record-import design with an unresolved duplicate policy, and tenant cache repair with ambiguous delimiter keys. Each contains exact public files and prompt, private executable acceptance, a manual review rubric, a correct reference implementation and an intentionally wrong repair. Reference implementations are controls, not mandated implementation shapes. Behavioral checks and independent judgment jointly determine acceptance; keyword presence is never a substitute for the design or documentation rubric. Read complete documentation and distinguish instructions to use a retired interface from accurate discussion of its removal. Qualify manual rubrics against reasonable alternative presentations, since one reference implementation cannot reveal exact-wording false positives.

`exercise.py` has no model, network or billing calls. Run from this repository with the managed interpreter:

```bash
./bin/python tests/fixtures/astra_evaluation/exercise.py qualify
```

Qualification requires all four original fixtures and all four wrong repairs to produce their predeclared exception type and message, and all four references to pass. An unrelated import-time crash must be refused as measurement failure, not counted as a successful rejection. It validates the local instruments, not model behavior. These are experiment fixtures, not additions to the retained repository proof estate; qualification remains an explicit preparation check.

Before a priced batch, record the delivered repository revision and the pack's byte digests in the evaluator's run record. Never revise a task or scoring rule after seeing results; a corrected pack starts a separately identified batch.

Qualify the complete launcher and ordinary workflow through local delivery before scaling the matrix. Static controls and a green host test suite do not witness native process lifetime, review dispatch or close bookkeeping. Use the first predeclared cell in each harness as that witness rather than adding hidden pilot calls. Record any interruption caused by the evaluator separately from model non-convergence. A repaired launcher or methodology starts a new identified batch; preserve the original attempts and do not combine incompatible timing measurements. A deadline reached after correct implementation is a workflow non-completion, not a failed behavioral check.

```bash
./bin/python tests/fixtures/astra_evaluation/exercise.py digest
```

For each cell, prepare a fresh destination outside this repository; the destination must not exist:

```bash
./bin/python tests/fixtures/astra_evaluation/exercise.py prepare --task repair --workspace /tmp/astra-repair-cell
```

Only the selected task's public files and `TASK.md` are written there. The evaluator keeps this pack, checks, reference solutions, negative controls, rubrics and prior runs inaccessible to every implementing/reviewing role. Use a fresh session with no pack-reading history and a verified filesystem boundary granting access only to the disposable workspace and required toolchain. A prompt telling the agent not to read the pack is not that boundary. If the selected harness cannot enforce the boundary, mark held-out qualification unavailable and do not present the run as held-out evidence. Review traces for protected reads; exposure invalidates the run even if the answer is correct. This local preparation tool does not install or claim a sandbox.

In a disposable methodology-equipped checkout, introduce only these public inputs as the product surface, set the approved preset, and give the task prompt unchanged to its ordinary product workflow. Keep the same methodology revision, harness version, permission profile, toolchain and initial context for all twelve cells. Adapt only the fixture's product location and test entry point consistently before freezing the batch; qualify the controls again in that host. Do not transplant private checks or this pack into that checkout. Allow the workflow to choose its phase count, and aggregate all phases to the same accepted outcome. No external deployment or delivery push is part of a fixture task.

Initial matrix: four tasks × quality/balanced/economy = twelve complete outcomes in one operator-selected harness. Predeclare a reproducible randomized cell order in the run record before dispatch. Model versions, efforts and preset expansion must be recorded per role; a missing entitlement is unqualified, never substituted. Existing workflow limits still apply; record non-convergence and failures, do not drop them from the denominator. Cross-vendor and effort comparisons, repetitions, or a second harness are additional priced batches. Any claim about reduced phase count or fewer iterations needs observed data beyond this pack's existence.

For the design task, an independent evaluator reads the workflow's question and any preceding writes before supplying the fixed ruling in its private rubric. Record whether the decision was surfaced before implementation and which role raised it. A question raised before planner dispatch satisfies early escalation but leaves independent planner detection unobserved; final code cannot supply that missing observation or repair a missed decision. The ruling becomes authorized public input only at that point. For every task, answer only factual clarifications, preserve each answer in the run record, and give equivalent questions equivalent answers. An unresolved consequential choice outside the rubric parks the cell instead of inventing a favorable criterion.

After the role workflow terminates, freeze the output snapshot and have the evaluator run acceptance without the implementing agent attached:

```bash
./bin/python tests/fixtures/astra_evaluation/exercise.py check --task repair --workspace /tmp/astra-repair-cell
```

Run candidate code under the separately verified disposable execution boundary; this script itself is not a security boundary. Preserve complete output and exit status. `BEHAVIOR PASS` is only the executable half. Separately record the rubric verdict, escaped defects, review rounds and causes, total elapsed span union, operator parks, and available token/cost measurements from the contract. Unknown measurement stays unknown. Independent review judges the final behavior and scope, including whether changes merely hardcode the samples. Do not feed held-out assertions back into a still-running cell; failures are terminal evaluation findings, and later repair experiments are new cells.

## Instruction-loading pair

`loading.json` defines the exact root instruction, canonical skill entry, linked resource, initial prompt and resumed prompt. The evaluator constructs one new disposable workspace per model using the declared files and symlinks; no private oracle is copied. Native skill discovery must be enabled and observed. Use `/fixture` for Claude Code or `$fixture` for Codex; the requested model and effort use the supported native harness configuration, never prompt text as a claim of identity.

Run the initial prompt once and save its terminal response and provider event stream. Between invocations the evaluator replaces only `resource.md` with the recorded resumed bytes, then resumes the same native session and submits the resumed prompt. Do not paste prior outputs, tokens or resource content into the resume prompt. The root token witnesses effective root instruction delivery; the entry token witnesses skill loading; the resource token witnesses the instructed retrieval. The changed resource token on resume rejects a stale cached answer. These outputs witness behavior, not whether the harness injected bytes automatically versus the model retrieving them; use trace evidence to distinguish that mechanism, or report it unknown.

Each response must be exactly the oracle JSON object for its stage, and the designated workspace file must contain the same object. Missing/unreadable resources or wrong tokens fail behavioral loading. A read-only dry run can demonstrate instruction reading but cannot qualify the write permission posture. Record the actual granted filesystem permissions and trace-observed file write separately from successful prose; permission outside this disposable workspace is unnecessary. Before execution, verify a missing-resource local control would make the oracle impossible to satisfy; never count the mere existence of a symlink as retrieval proof. The local `qualify-loading` command below exercises the physical layout, oracle comparisons and missing/stale resource controls without invoking a model.

```bash
./bin/python tests/fixtures/astra_evaluation/loading.py qualify-loading
```

```bash
./bin/python tests/fixtures/astra_evaluation/loading.py prepare --workspace /tmp/astra-loading-cell
```

```bash
./bin/python tests/fixtures/astra_evaluation/loading.py resume --workspace /tmp/astra-loading-cell
```

```bash
./bin/python tests/fixtures/astra_evaluation/loading.py check --stage initial --workspace /tmp/astra-loading-cell --response /tmp/astra-initial-response.txt
```

Use `--stage resumed` for the second response check. Preserve the initial workspace output before `resume`, which removes the old output so a missing resumed write cannot inherit success.

Live matrix: four models × two invocation stages = **eight invocations in four paired sessions**, not sixteen. Local fixture controls consume no model calls. Repeats or extra control invocations require their own count and budget. Before authorization, price these eight invocations and the separate twelve-outcome comparison using current provider rates and bounded per-role/run allowances, including expected revisions. Present the estimate and spending cap for operator approval; no call begins before that approval. Record actual spend afterward; missing billing data is unknown, not a zero-cost run.

Read identity from provider events and harness version from the invoked binary, preserving requested and reported values separately. Record absent model/effort/version fields as unreported. Resolve explicit aliases against the preflight's dated mapping before comparing provider IDs; do not classify a documented alias expansion as a downgrade. An unexpected reported model is a silent-downgrade finding. No primary identity evidence means unqualified model identity, even when loading passes. No entitlement means an unqualified cell. Synthetic refusal cases remain the offline suite's job; do not induce a paid policy refusal.
