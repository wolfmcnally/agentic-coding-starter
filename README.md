# Agentic Coding Starter Template

A repository template for building software with AI coding agents under a structured, multi-agent methodology. It encodes a workflow that turns a vague idea into shippable software through a planner → reviewer → coder → critic loop, with humans deciding what "done" means.

This template is harness-agnostic. It works with [Claude Code](https://claude.com/claude-code), with [Codex CLI](https://github.com/openai/codex), and with any other agent host that reads project-level instructions and agent definitions from `.claude/`, `.codex/`, `.agents/`, or `AGENTS.md`. The same files drive both — never edit a harness-specific mirror by hand.

---

## What this is

A starter template — a *master template* — for projects that use agent-driven development. Clone it, invoke the `stamp` skill to spin up a new project from it, or open it directly and invoke `kickoff` to start building.

Skill invocation is harness-specific:

| Harness | Syntax | Example |
|---|---|---|
| Claude Code | `/name [arguments]` | `/kickoff` |
| Codex | `$name [arguments]` | `$kickoff` |

The rest of this README uses bare names such as `kickoff` when discussing a skill and shows both forms when giving a command to type.

The template ships with:

- A **methodology** (eleven-step pipeline, see [`briefs/methodology.md`](briefs/methodology.md)) that takes you from idea to shipped code.
- A **`kickoff` skill** that orchestrates one phase of work end-to-end: plan → plan-review → code → code-review → build → log.
- Four **canonical agent roles** (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`) defined once and mirrored to every supported harness.
- A **`stamp` skill** (starter-template-only) for stamping out new repos from this one.
- **`learn` and `teach` skills** (universal — carried into every derived project) for moving patterns *between* methodology-following repos. `learn` absorbs patterns from another repo into the current one; `teach` sends patterns from the current repo out to a target. Both work one decision at a time, then present one complete plan for approval before any file changes.
- Universal **`demo` and `treatise` skills** for walking a human through an approved demo one visible action at a time and producing an audience-specific outward explanation from canonical repository authority.
- **Human-editable kickoff configuration.** One `kickoff.yaml` contains harness-aware role routing, execution budgets, and per-role originating-search budgets. Model and effort are separate fields. Edit it directly or use the `roles` skill; the round-trip-safe manager rejects schema typos while preserving comments and project-specific data under `extensions`.
- **Role-based research authority.** Planner and plan reviewer may search and retrieve; coder and code critic may retrieve plan- or brief-identified resources plus same-host structural neighbors but may not originate searches. Installed MCP servers and plugins are allow-by-default, never assumed present, and external research is GET-only without repository-content egress.
- **Fail-fast readiness and progress-aware timeouts.** `kickoff` live-validates every required non-orchestrator CLI/model/auth path before it mutates phase state. Production role calls then use per-role first-event, idle, and hard deadlines from the same config; local gitignored telemetry supports evidence-based recalibration. See [`policies/role-models.md`](policies/role-models.md) and [`policies/role-timeouts.md`](policies/role-timeouts.md).
- **Candidate-bound incremental assurance.** Complete first reviews produce
  stable findings; later rounds receive causal revision packets and widen when
  authority, scope, risk, or continuity changes. Focused checks accelerate
  convergence. A complete implementation-candidate gate proves the unchanged
  approved candidate; after evidence and tracked close bookkeeping, a second
  bare handoff gate proves the actual tree delivered to the user. See
  [`briefs/incremental-orchestration.md`](briefs/incremental-orchestration.md).
- **Exact operator-wait telemetry.** Execution traces measure active work;
  a separate phase ledger records every interval parked for user input and an
  overlap-safe total. Same-boot spans are exact; cross-boot calendar spans are
  clearly marked non-exact in the offline dashboard.
- **No implicit background worktrees.** The shipped `.claude/settings.json`
  sets `worktree.bgIsolation` to `none`; explicit worktrees remain available
  when the user chooses one.
- A **`plan/` ledger** (status table, dependency graph, cross-cutting concerns) where work is tracked phase by phase.
- A **`briefs/` library** for durable design decisions and methodology notes.
- A **`policies/` library** for the rules every phase must respect.
- A **`LOG.md`** activity log written by `kickoff` on phase open and close.
- A minimal Python example project so the toolchain contract has a real target
  from the first checkout.

---

## Why this exists

Coding with agents is high-leverage but easy to do badly. Without structure, you get:

- Agents that re-derive the same decisions every session.
- Plans nobody reviewed and code nobody checked.
- "Done" that means "the agent stopped talking" rather than "the human accepted the work."
- A directory whose state is impossible to reconstruct from its files.

This template solves those problems by externalizing the parts of the work that *must* persist across sessions: the brief (what), the architecture (how), the plan (in what order), the log (what actually happened), and the policies (what's off-limits). Each session starts from those artifacts and ends by updating them.

The result is a workflow where each phase is incremental, testable, and reviewed by a human before the next one begins.

---

## How to use this template

There are two ways to start.

### Option A — Stamp out a new project (recommended)

From inside this repo, invoke `stamp` with the destination and description.

Claude Code:

```
/stamp ~/path/to/new-project "one-line description of what to build"
```

Codex:

```
$stamp ~/path/to/new-project "one-line description of what to build"
```

The `stamp` skill copies this repo's structural files into the new directory, asks a few configuration questions (project name, primary language, build commands) when the description doesn't make them obvious, and leaves you with a project ready for `kickoff`.

### Option B — Use this repo directly

If you're trying it out or learning the workflow, open this repo and invoke `kickoff`.

Claude Code:

```
/kickoff
```

Codex:

```
$kickoff
```

The first `kickoff` run will pick up Phase 1 (currently a placeholder for
"decide what you're building"), walk through the planner → reviewer → coder →
critic loop, and write a START/END pair to `LOG.md`. Edit the brief and plan,
then invoke `/kickoff` again in Claude Code or `$kickoff` again in Codex. The
example under `project/example/` gives the toolchain a real target immediately.

### Verify the checkout

Every repository stamped from this template owns a cwd-independent toolchain
contract:

```bash
./bin/setup                 # provision the pinned, locked environment
./bin/test                  # run every test
./bin/test tests/test_check.py -q  # focused repo-relative selection
./bin/check all             # authoritative lint/format/test/policy suite
./bin/python --version      # Python profile: selected project interpreter
```

The host only needs `uv`; Starter selects a managed Python from
`project/.python-version`, uses `project/uv.lock`, and verifies the real
project/test/lint dependency chain before each entry point proceeds. For a
deliberate compatibility check,
`TOOLCHAIN_PYTHON=/absolute/path/to/python ./bin/check all` makes that
base interpreter authoritative; it must live outside `project/.venv`, and
failure never falls back to the managed default.
Each full gate stores a complete durable log and a receipt bound to the exact
candidate and environment. Optional tracked Git hooks reuse that receipt only
for the clean current `HEAD`; every miss or error runs the same full-gate entry
point. Opt in for the current checkout with:

```bash
./bin/install-hooks
```

---

## The eleven-step methodology

The full version lives in [`briefs/methodology.md`](briefs/methodology.md). The short version:

1. **Vague ideas → insights.** Surface what's actually being asked for. Do competitive analysis.
2. **Insights → brief.** Write down *what* you're building. Lives under `briefs/`.
3. **Brief → architecture.** Research Best Current Practices. Decide *how*.
4. **Repo-level policies.** Codify the non-negotiables. Lives under `policies/`.
5. **Brief + architecture → phased plan.** Break the work into incremental, testable phases.
6. **Sub-phase breakdown at phase start.** Decompose each major phase only when you start it.
7. **Orchestrator-driven sub-phase execution.** `kickoff` runs initial work through planner → reviewer → coder → critic. Complete first reviews establish stable findings; bounded revision rounds receive candidate-bound causal packets. Small low-risk follow-ups may be fixed directly; only high-risk or large/cross-cutting corrections require another full coder → critic cycle.
8. **Acceptance check.** Focused checks run while work converges. After critic approval, the orchestrator runs the complete phase-prescribed sequence and one authoritative full gate against the unchanged approved candidate.
9. **Append-only phase log.** `LOG.md` records open and close with evidence.
10. **Human evaluation.** *You* decide whether each sub-phase is done. The agent does not.
11. **Stay agile.** Add or split phases as the problem gets clearer.

---

## Repository layout

```
.
├── README.md                       ← this file
├── CLAUDE.md                       ← top-level guidance for agents
├── AGENTS.md                       ← symlink → CLAUDE.md (for Codex/aider)
├── LOG.md                          ← append-only activity log
├── kickoff.yaml                    ← human-editable role models/efforts/timeouts
├── project/                        ← the deliverable (self-contained per
│   │                                  policies/project-isolation.md)
│   ├── .python-version             ←   managed interpreter selection
│   ├── pyproject.toml              ←   package metadata
│   ├── uv.lock                     ←   exact dependency resolution
│   ├── example/                    ←   source code
│   │   ├── __init__.py
│   │   └── cli.py
│   ├── tests/                      ←   pytest suite
│   │   └── test_cli.py
│   └── README.md                   ←   the artifact's own quickstart
├── briefs/                         ← durable design + methodology library
│   ├── BRIEF.md                    ←   entry-point brief for *this* repo
│   ├── methodology.md              ←   the eleven-step methodology
│   ├── agentic-bootstrap.md        ←   how to stand up a new project
│   ├── cross-agent-invocation.md   ←   cross-CLI invocation BCPs
│   ├── incremental-orchestration.md ← candidate-bound incremental assurance
│   ├── deterministic-orchestration.md ← draft: deterministic kickoff loop
│   └── harness-self-improvement.md ← lessons, sweep, and cross-repo flywheel
├── policies/                       ← non-negotiable rules every phase honors
│   ├── README.md
│   ├── briefs-and-policies.md
│   ├── cross-harness-parity.md
│   ├── phase-status.md
│   ├── acceptance-empirical.md
│   ├── repo-relative-paths.md
│   ├── log-discipline.md
│   ├── human-in-the-loop.md
│   ├── four-canonical-agents.md
│   ├── role-models.md              ← role routing and fail-closed preflight
│   ├── role-timeouts.md            ← first-event/idle/hard execution budgets
│   ├── orchestration-evidence.md   ← candidate/revision/gate evidence
│   ├── review-lanes.md             ← review intensity + proportional follow-ups
│   ├── lessons.md                  ← candidate process-lessons lifecycle
│   ├── build-gates.md              ← atomic repository toolchain contract
│   ├── project-isolation.md        ← isolate deliverable under project/
│   └── greenfield-until-released.md ← no backward-compat shims pre-release
├── bin/                            ← deterministic methodology executables
│   ├── setup                       ← provision pinned + locked environment
│   ├── test                        ← full/focused canonical test runner
│   ├── check                       ← authoritative lint/format/test/policy gate
│   ├── check-receipt               ← durable exact-candidate gate receipts
│   ├── python                      ← selected managed Python interpreter
│   ├── install-hooks               ← opt in to tracked lifecycle hooks
│   ├── kickoff-config              ← round-trip config, preflight, watchdog
│   ├── kickoff-tree-id             ← complete review candidate identity
│   ├── kickoff-evidence            ← authority/change/finding/gate records
│   ├── lessons                     ← validate and query the lessons ledger
│   ├── check-catalogs              ← document and phase-ledger fitness
│   └── check-anonymization.sh      ← starter-only public-repo leak guard
├── .githooks/
│   └── pre-push                    ← exact receipt hit or canonical full gate
├── tests/                          ← universal methodology machinery tests
│   ├── test_toolchain_entrypoints.py ← setup/test/runtime behavior
│   ├── test_check.py               ← canonical gate behavioral coverage
│   ├── test_check_receipt.py       ← receipt integrity/fail-closed coverage
│   ├── test_install_hooks.py       ← opt-in hook installer coverage
│   ├── test_kickoff_config.py      ← config/watchdog behavioral coverage
│   ├── test_kickoff_tree_id.py     ← candidate identity coverage
│   ├── test_kickoff_evidence.py    ← evidence/packet/gate coverage
│   ├── test_lessons.py             ← lessons-ledger coverage
│   └── test_check_catalogs.py      ← document and phase-ledger coverage
├── lessons/                        ← open candidate process lessons
├── lessons-archived/               ← codified/rejected lesson audit trail
├── plan/                           ← phased execution plan
│   ├── INDEX.md                    ←   phase ledger (status lives ONLY here)
│   └── phase-1.md                  ←   first phase (a stub you replace)
├── .claude/                        ← Claude Code agent definitions
│   ├── skills/
│   │   ├── kickoff/SKILL.md        ←   phase orchestrator
│   │   ├── methodology/SKILL.md    ←   the eleven steps (self-contained)
│   │   ├── learn/SKILL.md          ←   absorb patterns FROM another repo (universal)
│   │   ├── teach/SKILL.md          ←   send patterns TO another repo (universal)
│   │   ├── roles/SKILL.md          ←   pin a model/harness to a role (universal)
│   │   ├── sweep/SKILL.md          ←   prune and graduate rule surfaces (universal)
│   │   └── stamp/SKILL.md          ←   new-project bootstrapper (starter-only)
│   └── agents/
│       ├── phase-planner.md
│       ├── plan-reviewer.md
│       ├── phase-coder.md
│       └── code-critic.md
├── .codex/                         ← Codex CLI agent mirrors
│   └── agents/
│       ├── phase-planner.toml
│       ├── plan-reviewer.toml
│       ├── phase-coder.toml
│       └── code-critic.toml
└── .agents/                        ← Codex CLI's native project-skill discovery
    └── skills/                     ←   (developers.openai.com/codex/skills)
        ├── kickoff                 ←   each is a directory symlink → ../../.claude/skills/<name>
        ├── methodology             ←     (directory-level because Codex doesn't follow
        ├── learn                   ←      file-level symlinks inside skill dirs — issue #11314)
        ├── teach
        ├── roles
        ├── sweep
        └── stamp                   ←   present only in this template repo
```

---

## Status markers

Phase status lives in **`plan/INDEX.md`** and nowhere else. The legend is:

- ⏳ Not Started
- ⬅️ Next — at most one phase; required while idle and incomplete
- 🚧 In Progress
- ✅ Completed

`kickoff` flips `⬅️` → `🚧` on start, `🚧` → `✅` on completion, and advances the next `⏳` row to `⬅️`. Status does not live in per-phase frontmatter; `id`, `title`, `depends_on`, `informs`, and the optional `review_lane` (see `policies/review-lanes.md`) are the only frontmatter fields.

Every phase row carries exactly one recognized status. Zero next rows is valid
while work is active and after the project completes; more than one is always
invalid.

---

## The four canonical agents

Every initial implementation uses the four canonical roles, subject to the declared review lane; proportional follow-ups may invoke only the roles their risk and size justify. The role names are load-bearing — `kickoff` calls them by name.

| Role | Tools | Writes code | Job |
|---|---|---|---|
| `phase-planner` | Read, Grep, Glob, WebSearch, WebFetch | No | Turn one phase into a concrete, file-level plan |
| `plan-reviewer` | Read, Grep, Glob, WebSearch, WebFetch | No | Approve the plan or send it back for revision |
| `phase-coder` | Read, Write, Edit, Grep, Glob, Bash, WebFetch | Yes | Implement the approved plan and retrieve its named references |
| `code-critic` | Read, Grep, Glob, WebFetch | No | Approve the code or send it back for revision, retrieving named references as needed |

`kickoff` normally delegates implementation; it may directly apply only an
eligible small, low-risk follow-up correction. It owns candidate identity,
evidence validation, both close gates, status, and `LOG.md`.

---

## Briefs vs. policies vs. plan

These three directories look similar at a glance. The distinction is load-bearing.

- **`briefs/`** — *what* you're building and why. Durable design decisions, methodology, research notes, glossaries. A brief informs every phase that references it.
- **`policies/`** — non-negotiable *rules* every phase honors. Cross-cutting invariants ("repo-relative paths only", "tests must hit a real database", "every phase produces a START/END log entry"). Policies are short and prescriptive.
- **`plan/`** — *in what order* you're building it. Phase files, dependency graph, status ledger.

When the plan and a brief disagree, the plan wins — it is the refinement. When code and a policy disagree, the policy wins — it is the law.

See [`policies/briefs-and-policies.md`](policies/briefs-and-policies.md) for the full contract.

---

## Cross-harness parity

The same workflow runs in Claude Code, Codex CLI, and other agent hosts. The contract:

- **Canonical sources** live under `.claude/` (skills, agents) and at the repo root (`CLAUDE.md`).
- **Harness mirrors** are either symlinks (`AGENTS.md` → `CLAUDE.md`; `.agents/skills/<name>` → `.claude/skills/<name>` as a *directory* symlink) or thin wrapper files (`.codex/agents/*.toml`) that point at the canonical content.
- **`.agents/skills/`** feeds Codex's native skill loader ([documented contract](https://developers.openai.com/codex/skills)). Repo skills are invoked with `$name` in Codex. The mirror uses *directory* symlinks because Codex doesn't follow file-level symlinks inside a skill directory ([openai/codex#11314](https://github.com/openai/codex/issues/11314)), but does traverse a symlinked skill directory.
- **Never edit a mirror by hand.** Update the canonical file; refresh the mirror.

See [`policies/cross-harness-parity.md`](policies/cross-harness-parity.md) for the rules and the onboarding procedure for adding a third harness.

---

## Cross-repo knowledge transfer: `learn` and `teach`

Once you have more than one methodology-following project, patterns evolve in one and stop in another. Two universal skills handle the round trip:

- **`learn <donor-dir> [<desc>]`** — Invoke as `/learn ...` in Claude Code or `$learn ...` in Codex. Explores `<donor-dir>` for patterns (skills, policies, briefs, agent refinements, build-gate idioms, even domain specializations) and proposes which to absorb. The donor stays read-only. Nothing is written here until you approve. After application, it captures methodology defects exposed by adapting the donor so a later return pass can harvest them.
- **`teach <target-dir> [<desc>]`** — Invoke as `/teach ...` in Claude Code or `$teach ...` in Codex. Proposes which of *this* repo's patterns to apply to `<target-dir>`. This repo stays read-only, and the target's custom work is preserved by default.

Both skills are carried into every project that `stamp` creates, so any methodology-following project can learn from or teach another.

Every derived project also carries the `lessons/` ledger and `sweep` skill.
Phase work records candidate process lessons; `sweep` proposes graduation,
rejection, consolidation, and rule-surface maintenance for human approval.

The `<desc>` argument narrows intent. Omit it for a broad assessment that defaults to general-purpose improvements; supply it to focus on a specific surface ("focus on the testing setup", "Unity specialization", "just the policies").

## First-time setup

1. Pick a harness:
   - **Claude Code**: `claude` in this directory.
   - **Codex CLI**: `codex` in this directory.
2. Read [`briefs/BRIEF.md`](briefs/BRIEF.md), [`briefs/methodology.md`](briefs/methodology.md), and [`plan/INDEX.md`](plan/INDEX.md) to ground yourself in what this repo expects.
3. Either invoke `kickoff` (`/kickoff` in Claude Code; `$kickoff` in Codex) to use this repo directly, or invoke `stamp` (`/stamp ...` in Claude Code; `$stamp ...` in Codex) to create a new project.

---

## License

Released under the MIT License. See [`LICENSE`](LICENSE).
