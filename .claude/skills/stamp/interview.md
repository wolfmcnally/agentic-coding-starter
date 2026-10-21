# Stamp interview — invoked with no arguments

With nothing to go on, the stamp asks before it builds. The interview produces two things: a seed brief good enough to enumerate real phases, written where the operator wants it, and a destination the rest of `stamp` can adopt. The operator invoked it, so they are present and want it to be efficient. The practices below and their sources are in [`briefs/agentic-bootstrap.md` § The no-argument interview](../../../briefs/agentic-bootstrap.md#the-no-argument-interview).

## How to ask

- **One question per turn**, each built on the answers so far. Never batch questions, and never show the queue of questions still to come.
- **Offer a recommended answer whenever one is reasonable**, with a one-line reason, so that "yes" settles it. Use the harness's structured question tool for closed choices: `AskUserQuestion` in Claude Code; `request_user_input` in Codex when the active mode offers it, plain text otherwise. Formulate them as [`ask`](../ask/SKILL.md) prescribes. Questions about the problem, the people and past episodes stay open free text.
- **Don't ask what you can infer or what is obvious.** Spend questions on the hard parts the operator may not have considered.
- **Ask about real episodes, not hypotheticals.** "When did you last run into this, and what did you do?" beats "Would you use X?" Do not ask leading or yes/no questions while discovering the problem; save confirmations for the end.
- **When the operator says "you choose"**, choose, give the reason, and record the choice as delegated and revisitable. Never fill in a stack, framework or service nobody named or delegated.

## What to cover

Treat the brief's sections as a coverage checklist and mark each one clear, partial or missing as answers arrive. Choose the next question by how much its answer would change the brief, weighted by how unsure that section still is. Roughly in this order:

1. **The problem and why now.** What it is for, what the operator does today instead, and what made that intolerable. Then who it is for, and what it deliberately is not.
2. **The surface.** CLI, web app, service, library, desktop, TUI or something else, only if it is not already evident. The [*Gather configuration*](SKILL.md#gather-configuration) heuristics then apply to the answers.
3. **Major dependencies already fixed.** Language and runtime, plus the frameworks, libraries, services, data stores, platforms and external APIs the operator has already settled on. Implementation method is out of scope here; that belongs to the phases.
4. **Build order.** First the walking skeleton: the thinnest thing the operator would want to see working end to end, and how they would check that it works. Then each next slice they could see or try, in order. Order the slices by visible outcome, never by layer ("database, then API, then UI"). This list becomes the roadmap that Step 3 turns into Phase 1 and the sketched phases.
5. **Where it lives.** The project name, then the destination directory. Recommend `<parent of this template checkout>/<project-slug>`, which puts it beside this repository. Then the brief's location, recommending `<directory>/briefs/BRIEF.md`; follow any other location the operator gives.

**Stop** when every section is clear, when the operator says "done", or after twelve questions, whichever comes first; the operator can explicitly extend that cap. Anything still unclear becomes an open question in the brief, not a guess.

**Check the destination as soon as it is named.** Apply `stamp`'s destination pre-flight check to it, and if it would be refused, ask for another location while the operator is still present.

## Draft, confirm, write

Keep the draft brief in a scratch file outside every repository, such as the harness's temporary directory. Update it after every answer, in the section the answer belongs to, and replace any text the answer contradicts. That way an interrupted session loses nothing and the draft never disagrees with itself. Write nothing into the destination until the operator has approved the draft.

The brief carries the frontmatter [`policies/briefs.md`](../../../policies/briefs.md) requires: `title`, today's `date`, `status: draft`, and a one-sentence `scope`. Its body has these sections:

- an H1 and an italic one-line tagline;
- `## Thesis` — the problem, why now, and what the project does about it;
- `## Users`;
- `## Scope`, with `### Non-goals`;
- `## Architecture and dependencies` — the surface, language and runtime, every named dependency, and each delegated choice with its reason;
- `## Build order` — the walking skeleton first, then the slices, numbered, each with how the operator will know it works;
- `## Constraints` — only if the operator gave any;
- `## Open questions`.

Use the operator's own words where they gave them. To finish, play back a one-screen summary, then show the full draft, and revise until the operator approves it.

Then create the destination with `mkdir -p` and write the brief to its approved location. When that location is outside the destination, also write a copy to `<directory>/briefs/BRIEF.md` so there is a seed to adopt, and say in the report that the copy is not kept in sync with the original.

## Return to the stamp

Continue from *Pre-flight checks* in [`SKILL.md`](SKILL.md) with the chosen `<directory>` and no `<description>`. The brief is adopted like any other seed: its frontmatter is already complete, its body is not rewritten, and Step 7's byte-identity check covers it. *Gather configuration* reads the answers from the brief and asks nothing it already answered. The final report says the brief came from the interview and gives its path.
