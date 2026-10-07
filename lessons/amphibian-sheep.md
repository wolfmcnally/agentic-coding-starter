---
slug: amphibian-sheep
title: A byte-exact restore is not a cache-exact restore
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-10-07
source: user
occurrences:
  - date: 2026-10-07
    ref: "this template — a red witness planted a defect the same size as the original and restored it within one second; Python's bytecode cache, keyed on size and whole-second modification time, kept serving the planted code for the restored file, the witness refused, and every later run of that module failed until the file changed again"
---

The witness command plants a defect in a source file, runs a command, and puts the original bytes back. It verified the restore by digest, and the digest matched. The tree was byte-identical to its starting state and still behaved as though the defect were present.

The property checked was the file's content. The property that mattered was what the next process would execute, and a cache stood between the two. Python reuses compiled bytecode when the source's size and modification time, to the second, are what it recorded. Swapping two lines changes neither the size nor, on a fast machine, the second. The digest check could not see this, because it reads the file and the interpreter does not.

It failed in the safe direction: the closing run saw the defect, so no receipt was written, and later baselines were refused. It was still found only by accident, because one planted defect happened to preserve the file's length, and the symptom, a correct file that fails, points everywhere except at the cache.

**When a tool edits a file and restores it, the restore must be distinguishable to every cache that keys on the file's metadata.** Here that means the restored file gets a modification time in a later whole second than the planted version, and a planting never starts in the same second as the version the baseline ran. The wider form: a verification that reads the artifact directly does not cover consumers that read it through a cache; name the cache and its key before trusting the restore.

Correction applied in the same pass, with a proof that fails when the guarantee is removed.
