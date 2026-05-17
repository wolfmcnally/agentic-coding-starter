# Activity Log

This log is **append-only** and owned by `/kickoff`. Do not hand-edit historical entries.

`/kickoff` writes a `## <YYYY-MM-DD HH:MM> — START` block when a phase enters `🚧 In Progress`, and a `## <YYYY-MM-DD HH:MM> — END` block when it leaves `🚧` (either `✅ Completed` or a paused-state END block that documents why).

If a phase pauses mid-way, leave its row in `plan/INDEX.md` at `🚧` and note the pause reason in the END block. The next `/kickoff` resumes it.

See [`policies/log-discipline.md`](policies/log-discipline.md) for the full contract.
