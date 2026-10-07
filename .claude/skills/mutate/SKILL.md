---
name: mutate
description: >-
  Run the mutation survey when the operator chooses to: plant generated faults
  in a disposable copy and report which ones the tests miss. Surveys changed
  code by default; arguments widen it to a revision range or everything, narrow
  it to named paths, or set the time budget. Use when the operator types
  /mutate (Claude Code) or $mutate (Codex), or asks to mutation-test a change,
  check whether the tests would catch faults in some code, or survey the
  suite's blind spots. Operator-invoked only: nothing in the workflow runs a
  survey by default, because one can take minutes to hours.
disable-model-invocation: true
argument-hint: "[all | since <rev> | <path>...] [budget <seconds>]"
allowed-tools: Bash
last-reviewed: 2026-10-07
---

# Mutate — survey what the tests would miss

A mutation survey plants small generated faults in the code and runs the tests against each one. A fault the tests catch is killed; one they miss is a survivor, and each survivor names a line where wrong code would pass. The rules are in [`policies/test-suite-governance.md`](../../../policies/test-suite-governance.md) § Mutation survey; the command's interface is in [`policies/build-gates.md`](../../../policies/build-gates.md) § Language profiles.

The survey is opt-in. It is slow in proportion to the code it covers, so it runs when the operator asks and at no other time. It never gates a commit or a push, and it never changes the live tree: faults are planted in a disposable copy.

## Scope

Translate the arguments into one `./bin/mutate` command.

| The operator says | Command |
|---|---|
| nothing | `./bin/mutate --changed-from '@{upstream}'` |
| `since <rev>` | `./bin/mutate --changed-from <rev>` |
| `all` | `./bin/mutate --all` |
| one or more paths or patterns | add `--path <pattern>` for each, to either form |
| `budget <seconds>` | add `--budget-seconds <seconds>` |

The default is the changed code: every line that differs from the upstream branch, committed or not, plus new files. With no upstream branch, use `HEAD` and say that only uncommitted work is covered. A path alone means that path's changed lines; `all` with a path means the whole of that path.

## Before running

1. Read the `mutation` block in `tests/proof-estate.yaml`. If it declares no tool, report that this repository takes no mutation measurement and give the recorded reason. Stop; do not look for a tool.
2. Tell the operator the scope and the budget in one sentence before starting. The declared budget bounds the run. `all` rarely finishes inside it; say so, and that `budget <seconds>` extends it.

## Run

Run the command with its output captured to a file. A run longer than about two minutes goes in the background; say that it is running and report when it finishes. A non-zero exit means the survey could not be taken, usually because the tests fail before any fault is planted. Report that diagnostic as a failure. It is never a clean result and never "unmeasured".

## Report

Write to the operator in the [plain](../plain/SKILL.md) register, leading with the state.

- **measured**: how many faults were planted and how many the tests missed.
- **partial**: the same, plus which files were not finished. Never present a partial result as covering the scope.
- **unmeasured**: no tool is declared, and why.

List survivors grouped by file, each with its line and what the fault was. A survivor is not automatically a defect in the tests: some faults change nothing observable. Say which survivors look like real gaps and which look equivalent, and give the reason for each judgment.

## Acting on survivors

Do not change tests or code unless the operator asks. When they do:

- Kill a real gap by strengthening the proof that should have caught it, then record a red-witness receipt for that proof with `./bin/test-governance witness`.
- Leave an equivalent fault alone and say why it is equivalent.
- Rerun the survey over the same scope and report the new counts.

When an approved phase names a survey as one of its checks, the phase runs `./bin/mutate` directly and dispositions each survivor on a changed line in its implementation report. That is the plan's decision, not this skill's.
