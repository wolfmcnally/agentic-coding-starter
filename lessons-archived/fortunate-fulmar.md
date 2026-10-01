---
slug: fortunate-fulmar
title: The leak scan reads only tracked content, so a full gate run before staging never scans the new files it is about to deliver
status: codified
scope: methodology
proposed_surface: bin
filed: 2026-10-01
closed: 2026-10-01
graduated_to: bin/check-anonymization.sh
source: user
occurrences:
  - date: 2026-10-01
    ref: "METHODOLOGY — sol selector moves to GPT-6.1 Sol: the full gate passed while a new user-action file was still untracked, so the anonymization check never read it before it was committed and pushed"
  - date: 2026-10-01
    ref: "METHODOLOGY — universal refactor skill: a standalone anonymization run reported clean with five new paths untracked; the same check failed on one of them once they were staged"
---

The anonymization check searches with `git grep`, which reads tracked content only. A file that is new and not yet staged is invisible to it. The delivery order the methodology describes is checks, then the full gate, then staging and commit, so on that order every newly created file reaches the remote without the leak scan having read it, and the gate's `PASS` line says nothing to distinguish "scanned and clean" from "not scanned".

Both observations were on the same day. In the first, a new file was untracked during the full gate and was then committed and pushed; it happened to contain nothing the scan looks for. In the second, the standalone check printed its clean line over a tree with five new untracked paths, and the staged rerun found a hit in one of them: digest fragments in backticks that the scan reads as commit identifiers. That hit was caught only because the check's own clean line says "tracked files", which prompted staging before the full gate.

What should be done differently: the scan should cover nonignored untracked files as the candidate-identity tooling already does, or refuse while any exist, so that its clean line cannot be vacuous. Until then, stage new files before the full gate.

Graduated on 2026-10-01 at two occurrences by the operator's decision: the scan now searches untracked files as well, a proof covers it, and the policy describing the scan says so.
