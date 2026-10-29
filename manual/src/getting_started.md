# Get Started

This tutorial creates a small project, checks its initial scaffold, and identifies the first phase. You need Git, a supported coding harness such as Claude Code or Codex, and the language toolchain selected for your project. Starter's own example uses managed Python 3.11 and uv.

## Prepare Starter

Clone the [Starter repository](https://github.com/wolfmcnally/agentic-coding-starter) and open its directory in your coding harness. Run the setup command from a terminal in the checkout:

```sh
./bin/setup
```

Setup succeeds only after the pinned interpreter, locked dependencies, example package, and test tools load. If it refuses, fix the named prerequisite before continuing.

## Describe a small project

Ask the agent to use `stamp` with a new directory and a description. In Claude Code:

```text
/stamp ~/path/to/weather-cli "A Rust command-line app that reports the weather for a named city"
```

In Codex:

```text
$stamp ~/path/to/weather-cli "A Rust command-line app that reports the weather for a named city"
```

For a serious project, write the brief first. A destination may already contain a Markdown brief, an optional Git directory, and a gitignore. `stamp` adopts the brief's body unchanged. It refuses a destination containing source code or unrelated files.

The skill adapts the project instructions, runtime and checks, skill mirrors, initial brief, and phase plan. It verifies the new scaffold and makes its initial local commit. You choose the remote separately.

## Inspect the result

Open the new project in your harness. Read its regular primary `AGENTS.md`, entry-point brief, `plan/INDEX.md` discovery context, and first permanent phase definition/events. Check the inferred name, language, surfaces, dependencies, and acceptance criteria. Correct assumptions before implementation begins.

Run `kickoff` in the new project. In Claude Code:

```text
/kickoff
```

In Codex:

```text
$kickoff
```

The agent selects the next marked phase, loads its authority, plans and implements it, obtains the selected independent advice, and runs the checks. A successful delivery leaves any human demo and product judgment explicit for you.

## Check your understanding

You have completed this tutorial when the new project has an understandable brief, one next phase, working setup/test/check commands, and a clear statement of what the first phase will prove. A live model preflight may still refuse because of authentication, provider availability, or usage limits; that refusal is reported separately from the scaffold's checks.

For a small research folder or knowledge base, the mini-method scaffold offers briefs, policies, pinned references, and deterministic commands without the full phase workflow. Use `teach` later to assess an upgrade.
