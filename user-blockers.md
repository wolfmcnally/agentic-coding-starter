# User Blockers

Live queue of action items only the human can perform — deploys, console / dashboard / GUI checks, manual reconciliations, third-party logins, anything outside an agent's reach. Closed items stay in place strikethrough'd as a permanent audit trail.

Full contract — format, slug discipline, lifecycle, agent-vs-human checkoff rules: [`policies/user-blockers.md`](policies/user-blockers.md).

## Pending

*(no open items)*

## Recently closed

### ~~Verify Codex CLI behavior against the new `.agents/skills/` symlinks — `blazing-salmon`~~ ✅ CLOSED

**Disposition:** Resolved by empirical evidence in `~/DevProjects/bartley`, commit `bfe7e03e` ("Restore Codex skill discovery", 2026-05-14). Wolf had already encountered and solved the underlying problem two days before this entry was filed: Codex CLI's [#11314](https://github.com/openai/codex/issues/11314) blocks *file-level* symlinks inside `.agents/skills/<name>/`, but does follow a *directory-level* symlink at `.agents/skills/<name>` → `.claude/skills/<name>`. Starter has been converted to the directory-symlink shape to match bartley's working pattern. The original CLI verification commands in this entry are no longer relevant; bartley is the proof.

### ~~Verify Codex desktop "import settings" prompt is now silent — `dancing-locust`~~ ✅ CLOSED

**Disposition:** Closed alongside `blazing-salmon`. With `.agents/skills/` now populated (as directory symlinks following bartley's working pattern), the Codex desktop "import settings" prompt should treat starter the way it treats bartley — which Wolf has been using without ongoing import-prompt nuisance. If a stray import prompt appears later in a starter-derived project, file under a fresh slug at that time rather than reopening this one.

## Deferred / not currently blocking

*(no deferred items)*
