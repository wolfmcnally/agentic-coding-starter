---
slug: blazing-salmon
title: Verify Codex CLI behavior against the new .agents/skills/ symlinks
status: closed
category: tooling
filed: 2026-05-17
closed: 2026-05-18
---

## Disposition

Resolved by empirical evidence in a sibling project of the author's that had already hit and fixed this (its "Restore Codex skill discovery" change, 2026-05-14), two days before this entry was filed: Codex CLI's [#11314](https://github.com/openai/codex/issues/11314) blocks *file-level* symlinks inside `.agents/skills/<name>/`, but does follow a *directory-level* symlink at `.agents/skills/<name>` → `.claude/skills/<name>`. Starter has been converted to the directory-symlink shape to match that working pattern. The original CLI verification commands in this entry are no longer relevant; the sibling project is the proof.
