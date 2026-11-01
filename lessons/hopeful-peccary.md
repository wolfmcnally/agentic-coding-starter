---
slug: hopeful-peccary
title: The seed rule refuses a destination for Finder's own metadata
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-10-31
source: user
occurrences:
  - date: 2026-10-31
    ref: "a seed stamp of a TypeScript project — the destination held one written brief and a .DS_Store that Finder created when the directory was opened"
---

The stamp skill and the bootstrap brief list what a seed destination may contain and refuse anything else, naming the file. Read literally, a `.DS_Store` disqualifies the destination, and the operator is told to move aside a file Finder will recreate the next time the folder is open.

The refusal protects against stamping over unrelated work. Operating-system metadata is not work, and the template's own `.gitignore` already ignores it. The run adopted the seed, left the file in place and untracked, and reported the deviation.

**Name operating-system metadata as permitted in the seed definition, at both the skill and the brief, so an agent neither refuses a real seed nor quietly reads a strict rule loosely.**
