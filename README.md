# Wolf's Agentic Coding Starter Kit

*An opinionated starting point for building software with AI coding agents.*

**Wolf McNally**

Wolf McNally created and maintains this repository. For a broader guide to agentic methods, terminology, and failure modes, see his [Encyclopedia of Agentic Coding Patterns](https://aipatternbook.com/).

## What this is

This repository is both a working template and a collection of practices for building software with AI coding agents. A project made from it has written briefs, binding policies, a phased plan, independent review roles, repeatable checks, and a durable record of what happened.

The working agreements and evidence live in the repository rather than in one conversation. A new agent session can read the same decisions, rules, and evidence as the previous one.

The kit supports [Claude Code](https://claude.com/claude-code) and [Codex CLI](https://github.com/openai/codex). Claude Code invokes a project skill with a slash, such as `/kickoff`. Codex uses a dollar sign, such as `$kickoff`. The tutorial below uses the Claude Code spelling; Codex users can substitute `$` for `/`.

## Why it exists

Coding agents are good at producing plausible plans, plausible code, and plausible reports that say the work succeeded. Plausible is not the same as correct.

Without a durable project structure, decisions disappear with the conversation, the author grades their own work, and the same mistakes return. This kit moves the important state into files, separates creation from review, and turns failures into lessons that later sessions can use.

## How the methodology works

The complete methodology has [eleven steps](briefs/methodology.md). Four stages are enough to understand the working loop.

### 1. Define

Start with an idea and turn it into a brief. The brief describes what you want to build and why. Architecture notes describe how you intend to build it. Policies state the rules every phase must obey, and the plan divides the work into testable phases.

### 2. Execute

The `kickoff` skill runs one phase at a time. One role plans, another reviews the plan, a third writes the code, and a fourth reviews the result. The author of an artifact does not provide its only judgment.

### 3. Prove and deliver

After review, the repository runs its checks against the exact version that was reviewed. Work that can be checked objectively closes only after independent review and the complete test and policy suite pass. Anything that requires product or other human judgment, a manual inspection, or someone to take custody of an artifact still waits for a person. Once the objective work is complete, `kickoff` commits it and fast-forward pushes it when the repository has a suitable upstream. It does not choose remotes or perform destructive Git operations.

### 4. Learn

The log records what happened. When an assumption is corrected, work fails, or a result is surprising, Rule One diagnoses the cause before turning it into a reusable lesson. Later maintenance passes can fold recurring lessons into the methodology, revise stale guidance, or remove rules that no longer earn their keep.

## Getting started

You need Git, [`uv`](https://docs.astral.sh/uv/), and either Claude Code or Codex CLI.

Clone the kit and open it in your coding harness:

```bash
git clone https://github.com/wolfmcnally/agentic-coding-starter.git
cd agentic-coding-starter
claude
```

Run `codex` instead of `claude` if you use Codex CLI.

### Start with a seed brief (recommended)

A seed brief is a plain Markdown account of the project you want. It does not need to be a formal specification or settle every question. Include the parts that matter to your project:

- the problem or opportunity
- who the project is for
- what the finished project should do
- important constraints and deliberate non-goals
- platforms, languages, frameworks, or dependencies already chosen
- what success would look like
- open questions or tradeoffs that still need work

You do not have to write it alone. Give your idea to an AI chatbot or coding harness and ask it to interview you. For example:

> Help me turn this project idea into a seed brief. Ask me one question at a time about its users, purpose, behavior, constraints, technology, success criteria, and open questions. Then write the result as Markdown.

Put the finished brief in the otherwise-empty destination for the new project. A simple layout is:

```text
my-project/
└── briefs/
    └── BRIEF.md
```

Then, from this Starter Kit session, run:

```text
/stamp ~/path/to/my-project
```

`stamp` adopts the brief, adds any required metadata, and leaves its body unchanged. It reads the project name, language, dependencies, major phases, and whether the project is a CLI, web app, service, library, or something else from what you wrote. If the brief leaves a necessary choice open, `stamp` asks rather than inventing an answer.

The destination may also contain an existing `.git/` directory, a `.gitignore`, and other Markdown briefs. It must not contain source code or unrelated files. The [bootstrap brief](briefs/agentic-bootstrap.md#seed-briefs) gives the complete seed rules.

### Start from a description

For a quick experiment, give `stamp` a destination and a one-line description:

```text
/stamp ~/path/to/weather-cli "A Rust command-line app that reports the weather for a named city"
```

`stamp` infers what it safely can and asks about anything the description does not settle. It creates a starter brief and an initial phase. Review and expand that brief before beginning serious work.

### Run the first phase

`stamp` creates and checks the new repository, makes its initial commit, and leaves remote selection to you. Open the new directory in Claude Code or Codex, then read:

- `briefs/BRIEF.md`, or the entry-point brief you supplied;
- `plan/INDEX.md`, which shows the roadmap and current phase; and
- `plan/phase-1.md`, which describes the first piece of work.

Correct anything `stamp` inferred badly. Then run:

```text
/kickoff
```

With no argument, `kickoff` selects the next phase from the plan. You can also name one:

```text
/kickoff phase 2
```

The orchestrator plans the phase, gets the plan reviewed, implements it, gets the code reviewed, runs the repository's checks, and records the result. If the phase includes something only a person can judge, it stops with a concrete demo or decision instead of claiming success.

## Other useful skills

These are the other commands most users will reach for:

| Skill | What it does |
|---|---|
| `/methodology` | Explains the full methodology or helps scope a new project. |
| `/demo` | Walks through an approved user demo one visible step at a time. |
| `/roles` | Shows or changes which model and harness perform each review role. |
| `/learn` | Assesses another repository for practices worth adopting here. |
| `/teach` | Assesses which practices from this repository should move to another one. |
| `/sweep` | Reviews accumulated policies, briefs, skills, and lessons for maintenance. |

`learn`, `teach`, and `sweep` present their judgments and wait for approval before changing the affected repository. You normally do not invoke Rule One yourself. When work fails or an assumption is corrected, the agent diagnoses what happened and saves any reusable lesson.

The [project guidance](CLAUDE.md#project-specific-skills) lists the full skill set.

## Essential repository map

| Location | Purpose |
|---|---|
| `briefs/` | Product intent, design thinking, research, and methodology. |
| `policies/` | Decisions and rules that every phase must obey. |
| `plan/` | The phase roadmap, dependencies, acceptance criteria, and current status. |
| `project/` | The example deliverable in this repository; a stamped project adapts this to its real software. |
| `.claude/skills/` | Canonical skill definitions used by the supported harnesses. |
| `bin/` | Repeatable setup, test, validation, and methodology commands. |
| `LOG.md` | Append-only record of phase starts, parks, and closes. |
| `CLAUDE.md` and `AGENTS.md` | Complete instructions and catalogs for coding agents. |

## Full documentation

- [Wolf's Agentic Coding Starter Kit: An introduction](briefs/methodology-treatise.md) is the general explanation of the repository and its principles.
- [The product brief](briefs/BRIEF.md) defines what this Starter Kit provides, who it is for, and its acceptance criteria.
- [The methodology](briefs/methodology.md) gives the complete eleven-step process and operating doctrine.
- [The bootstrap brief](briefs/agentic-bootstrap.md) documents how `stamp` creates and adapts a project.
- [The project guidance](CLAUDE.md) contains the complete brief and policy catalogs, project conventions, and agent instructions.
- [The script reference](bin/README.md) documents every deterministic command.
- [The phased plan](plan/INDEX.md) shows the current state of this repository.
- [The EACP pattern map](briefs/eacp-pattern-map.md) connects the repository's structures to patterns in the Encyclopedia of Agentic Coding Patterns.

## License

Released under the MIT License. See [`LICENSE`](LICENSE).
