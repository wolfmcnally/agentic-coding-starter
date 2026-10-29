# Activity records

`entries/` contains immutable Markdown bodies with attributed per-writer sequence and predecessor envelopes. Use `bin/multioperator append --root . --writer <operator> --body <file>` for a new entry, and `bin/multioperator render --root .` for ignored local reading views. The views are disposable; original entries and required evidence are retained.

Imported entries reconstruct the exact committed pre-transition log. Their original body bytes, source offsets and import attribution remain unchanged. Later corrections and preserved uncommitted scope records are new attributed entries, not edits to imported history.
