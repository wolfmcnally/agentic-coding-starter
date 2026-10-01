# Refactoring evaluation pack

A small seeded package and the instruments that judge a refactoring of it. It exists to answer one question about the `refactor` skill: which of its instructions a current model actually needs. Run it again whenever a model the methodology names is replaced.

`exercise.py` has no model, network or billing calls. Run from this repository with the managed interpreter:

```bash
./bin/python tests/fixtures/refactor_evaluation/exercise.py qualify
```

Qualification proves the instruments, not any model: the original package is a clean baseline; a correct reference refactoring is accepted with its seeds addressed and its decoys intact; a deliberately wrong refactoring passes the shipped tests, which is what makes its mistakes traps, and fails exactly the held-out probes recorded for it; and a package that cannot be imported is reported as a measurement failure, not as a detection. These are experiment fixtures, not additions to the retained repository proof estate.

Record the pack's digests before any priced run. Never revise the package, the probe or a scoring rule after seeing results; a corrected pack starts a separately identified batch.

```bash
./bin/python tests/fixtures/refactor_evaluation/exercise.py digest
```

## What the package contains

`pack.json` holds a thirteen-file Python package, `shop`, with its tests, a two-line instruction file and a test wrapper. It is stored as data so that the seeded problems are never linted or collected here.

- **Seeds, one per thing the skill looks for.** Two inline copies of a rounding helper that already exists; a four-deep conditional and an unused function; a special case for one product repeated at two call sites, and a module that only forwards a call; two narrating comments and a list that is written and never read; a subtotal recomputed inside a loop; a constant whose name breaks the package's one written convention.
- **Decoys, which look like problems and are not.** A storage interface with two real implementations; two postcode checks that are identical today and documented as belonging to different owners; an explicit band table whose comment says why it is written out.
- **Traps, where the obvious simplification changes behavior no shipped test covers.** A hand-written rounding function that differs from both the built-in and the package's own helper on ties and negatives; a broad exception handler whose narrowing changes what three inputs return; an optional discount that a truthiness shortcut would mishandle at zero.
- **Two changes that are not local.** Giving the special-cased product a price inside the pricing module, and deleting the forwarding module, both change what other code can observe. A run that makes either has changed behavior; under the skill they must be proposed, not applied.

The held-out probe compares 73 observable outcomes, results and exception types, between the original package and the candidate. It is never copied into the workspace.

## Running an arm

Prepare a workspace outside this repository, with the skill installed for a skill arm:

```bash
./bin/python tests/fixtures/refactor_evaluation/exercise.py prepare --workspace /tmp/refactor-eval/opus-skill --skill .claude/skills/refactor
```

Start the model in that workspace with the arm's prompt from `pack.json` and the model and effort this repository pins for it. Under Claude Code, pass `--setting-sources project` so the operator's own instructions and skills are not loaded. Codex has no equivalent for its machine-wide instruction file, so a Codex arm runs with whatever that file says; record that with the result. Then check:

```bash
./bin/python tests/fixtures/refactor_evaluation/exercise.py check --workspace /tmp/refactor-eval/opus-skill
```

## Scoring, fixed before the first run

From `check`:

- **Behavior preserved:** the shipped tests pass and no probe differs.
- **Tests untouched:** the shipped test file is byte-identical. If it is not, read the change: an import or rename forced by the refactoring is acceptable only when every assertion is unchanged.
- **Decoys intact:** no decoy definition changed. If one did, read the change: it counts when the logic or the separation changed, not when only an annotation or comment did.
- **Seeds addressed:** read from the reported facts, one line per seed.

From the model's final report, read against these rules:

- **Traps:** a run that changes what a trap function returns fails, whatever it says. A run that leaves them alone passes.
- **Authority, skill arms only:** the two non-local changes must appear as proposals. Applying either fails.
- **Parity:** the Claude Code and Codex skill arms put each finding in the same class: applied, proposed or handed off.
- **Against `simplify`:** each skill arm addresses every seed the `simplify` arm addresses.

An instruction earns a place in the skill only by answering a failure a bare arm showed. A skill arm that does worse than the same model's bare arm on behavior, tests or decoys fails the skill.

## Results

### Batch 1, 2026-10-01

The digests of `pack.json` and `exercise.py` were taken before the first run and were unchanged after the last. Seventeen sessions: five bare, four with the skill as first written, four with its wording revised once, and four with the shipped wording, which is the revision less two sentences that had changed nothing. Each arm ran once per wording.

Models and efforts: Claude Opus 5.5 at `medium` and Claude Fable 5.1 at `high` under Claude Code 2.1.287; GPT-6.1 Sol at `medium` and GPT-6 Astra at `high` under Codex CLI 0.159.3. The Claude Code arms reported their model; the Codex arms report only the model requested. Claude Code arms excluded the operator's instructions and skills. Codex arms ran with the operator's machine-wide instruction file loaded, which reserves commits to the operator and asks for verification; both Codex skill arms cited it when leaving their changes uncommitted.

"Seeds" counts the eight local seeds addressed, judged by reading the change where a reported fact was ambiguous. Deleting the forwarding module is the non-local change; it shows as one differing probe.

| Arm | Tests | Probes differing | Test file | Decoys changed | Seeds | Forwarding module |
|---|---|---|---|---|---|---|
| Opus, bare | pass | 1 | unchanged | none | 8 | deleted |
| Fable, bare | pass | 0 | unchanged | none | 8 | kept, deletion proposed |
| Sol, bare | pass | 0 | tests added | none | 4 | kept |
| Astra, bare | pass | 0 | tests added | none | 3 | kept |
| `simplify` on Opus | pass | 1 | unchanged | none | 8 | deleted |
| Opus, skill, first wording | pass | 0 | unchanged | none | 8 | kept, deletion proposed |
| Fable, skill, first wording | pass | 0 | unchanged | none | 8 | kept, deletion proposed |
| Sol, skill, first wording | pass | 0 | unchanged | none | 6 | kept, deletion proposed |
| Astra, skill, first wording | pass | 0 | unchanged | none | 7 | kept, deletion proposed |
| Opus, skill, revised | pass | 0 | unchanged | none | 8 | kept, deletion proposed |
| Fable, skill, revised | pass | 0 | unchanged | none | 7 | kept, deletion proposed |
| Sol, skill, revised | pass | 0 | unchanged | none | 6 | kept, deletion proposed |
| Astra, skill, revised | pass | 0 | unchanged | none | 7 | kept, deletion proposed |
| Opus, skill, shipped | pass | 0 | unchanged | none | 8 | kept, deletion proposed |
| Fable, skill, shipped | pass | 0 | unchanged | none | 8 | kept, deletion proposed |
| Sol, skill, shipped | pass | 0 | unchanged | none | 6 | kept, deletion proposed |
| Astra, skill, shipped | pass | 0 | unchanged | none | 7 | kept, deletion proposed |

Read against the scoring rules:

- **Traps:** no arm, bare or with the skill, changed what a trap function returns. Every arm that mentioned them explained why it left them.
- **Tests:** the two bare Codex arms added tests that pin boundaries and changed no existing assertion, which the rule accepts. No skill arm touched the test file.
- **Authority:** every skill arm kept the forwarding module and proposed its deletion; none priced the special-cased product inside the pricing module. The two bare Opus arms deleted the module.
- **Against `simplify`:** the Claude skill arms address every seed `simplify` addresses and do not delete the module. The Codex skill arms address fewer seeds than `simplify` does on Opus; that comparison is across models, not across instructions.
- **Parity:** the harnesses agree on every finding but one. Under all three wordings Sol proposed, and did not apply, computing the subtotal once, on the ground that it changes how often an overridable method is called; the other three applied it.
- **Skill against bare, same model:** no skill arm did worse than its bare arm on behavior, tests or decoys. Opus stopped deleting the module; Sol went from 4 seeds to 6 and Astra from 3 to 7.

What the revision changed and did not: naming the current branch stopped Opus from creating one, and stays. Saying that the amount of work is not something a caller observes did not change Sol's reading. Saying to apply the local part of a fix that is not fully local did not lead either Codex model to name the repeated special case once. On the operator's ruling those two sentences were removed and the four skill arms run again; nothing regressed, so the shipped wording is the first wording plus the branch clause. Fable went from 8 seeds to 7 and back to 8 across the three wordings, which with one run per arm is within what chance could produce.

The probe compares results and exception types, not messages. One Opus run reported a difference finer than that on its own: flattening the nested checks changed the operator named in the `TypeError` raised for a non-numeric quantity.

The `waste` fact reports a call inside the loop for Astra's change, which computes the subtotal on first use and reuses it; read by eye it addresses the seed, and it is counted as addressed above.
