---
title: A transfer worker's commit can be refused by its harness's permission layer
  after the gates pass
scope: methodology
proposed_surface: skill
source: teach
slug: sly-sambar
status: candidate
filed: '2026-11-13'
occurrences:
- date: '2026-11-13'
  ref: a recipient's 1.6.0 transfer; the worker's commit of the approved, gated write
    set was denied by the harness's automatic permission check, and the operator settled
    it directly in the worker's session
---

Repository authority, hub approval and a passing gate are not a platform grant. The refused commit differed from earlier workers' commits in two ways: its message came from standard input, a form the operator's allow list did not name, and it carried the harness's default attribution lines, which the operator's rules forbid; the worker reported that the harness's attribution reminder had pulled it into adding them. One refusal cannot say which mattered.

Candidate correction for the teach skill and worker briefs: state the pre-allowed commit form, state that commit messages carry no attribution lines whatever the harness suggests, and have the worker confirm it can commit before running the gates. The hub primary reports the exact refused operation and its unexecuted state and does not perform it from another session.