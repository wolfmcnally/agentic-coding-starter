# Policy: Research Authority

Research authority belongs to the **role**, not to the transport that happens
to run it. A role dispatched through another harness keeps the same authority,
and a tool being installed does not by itself authorize a role to use it.

## Role matrix

| Role | Search | Retrieval | Required disposition |
|---|---|---|---|
| Planner | Yes | Yes | May originate research and write material findings into the plan or an owning brief. |
| Plan reviewer | Yes | Yes | May independently challenge the plan; reports research as review findings and does not rewrite the plan. |
| Coder | No | Yes | May retrieve plan- or brief-identified resources and same-host structural neighbors needed to interpret them. |
| Code critic | No | Yes | May retrieve plan- or brief-identified resources and same-host structural neighbors needed to verify them. |

`Search` means originating a new discovery query. `Retrieval` means fetching a
known resource. A structural neighbor is a predictable document on the same
authority surface, such as an API reference linked from an overview or an RFC
section adjacent to the cited section; it is not permission to begin a new
research topic.

Coder and critic retrieval is **consume-only**. If the approved authorities do
not identify enough material to implement or verify safely, the role reports an
authority-insufficiency advisory to the orchestrator. It does not silently turn
that gap into originating research.

## Installed resources are allow-by-default

Available MCP servers, plugins, local reference stores, and equivalent
retrieval venues are usable by default within the role matrix above. Projects
and phases may narrow that ambient set with an explicit allow or deny rule, but
the template does not ship a global default-deny list. A named optional server
is never assumed to exist, and its absence is not a failure unless the project
or phase explicitly makes it a prerequisite.

The repository's own `docs/` directory is the local reference store that is always present: reading a pinned document there is retrieval for every role, and a pin that a brief, policy, or plan cites is a plan- or brief-identified resource for the coder and critic. Adding or replacing a pin originates from research and is planner or reviewer work under `policies/docs.md`.

Capability and authority are separate checks:

- The role definition and dispatch prompt determine what the role may do.
- The selected venue must actually expose the needed capability.
- Installed availability never widens the role's authority.
- Missing optional capability never implies that the resource was forbidden.

## Egress boundary

External research is read-only and GET-only:

- Use retrieval-equivalent `GET` operations only.
- Never place repository or candidate content in a query string, form field,
  request body, uploaded file, or tool argument sent to an external research
  service.
- A public identifier already named by an approved authority may be sent to
  retrieve that authority.
- Authenticated project data, mutation tools, publication tools, and external
  writes remain outside research authority unless the user separately grants
  them.

When a connector cannot make this boundary legible, do not use it for research.

## Query budgets

`kickoff.yaml` owns per-role originating-query budgets under
`research_budgets`. The shipped defaults are:

- planner: 12
- reviewer: 6
- coder: 0
- critic: 0

A query budget limits discovery searches, not retrieval of already identified
authorities. Zero means the role may not originate a query. A project or phase
may lower a budget; widening it is a deliberate project decision. The runtime
must render the resolved authority and budget into every role dispatch so the
same contract follows cross-harness execution.

## Check consequential facts for freshness

Before planning, identify potentially changing facts whose reversal could invalidate the plan: installed CLI behavior, API contracts, platform defaults, and dependency behavior. Consult existing dated local evidence first, and verify against the authority for the version actually targeted when the fact's age and volatility warrant it. An inability to name a recent dated development is a reason to investigate, not a measurement of correctness; confident recall is not evidence of freshness.

Record the consequential fact, source, and evidence dates concisely in the existing Architecture Decisions section or owning brief. Keep the current query budget and `docs/` pinning contract. Do not add a confidence table or research stable facts merely to populate a section. When the authority is an installed command a read-only role cannot execute, name the exact probe for the orchestrator instead of asserting its result.

The plan reviewer independently challenges assumptions whose staleness could change the design; it may search beyond the planner's bibliography within its role budget. An insufficiency advisory states the unanswered question, the sources consulted, and what evidence would settle it. The planner emits durable brief content and its intended path; the orchestrator lands it outside the read-only dispatch and recomputes the candidate before the next role.

## Evidence and freshness

Research that survives the run names its source and distinguishes the date the
fact was true (`As of YYYY-MM-DD`) from the date it was fetched (`Retrieved
YYYY-MM-DD`). Planner research belongs in the plan or owning brief. Reviewer,
coder, and critic research stays in their evidence or advisory unless the
orchestrator routes an approved correction back to an owning authority.

## Enforcement

The canonical role files, `bin/kickoff-config`, and their behavioral tests form
one contract. Tests must exercise the generated commands and dispatch prompts
for every role and supported venue; source-text assertions alone are not
sufficient. A venue that cannot provide the matrix's required capability fails
preflight rather than silently dispatching a weaker role.
