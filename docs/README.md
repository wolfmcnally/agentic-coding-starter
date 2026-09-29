# `docs/` — Third-Party Documentation

This directory holds externally authored reference material the project depends on — vendor documentation, specifications, RFCs, API references, standards text, license texts — pinned locally so that briefs and policies can cite exact wording and every role can read the cited authority without leaving the repository.

Nothing here is written by the project about the project. A file under `docs/` is verbatim third-party text (or a verbatim excerpt) and never links to anything else in this repository; commentary on a pinned document is a brief, and a rule derived from one is a policy. The full contract — what belongs here, naming, licensing, the citation direction, and what `bin/check-catalogs` enforces — is [`policies/docs.md`](../policies/docs.md).

## Catalog

Every top-level entry in this directory has one row here. `As of` is the date or version the source itself carries; `Retrieved` is when the project fetched it. `Basis` names the license or terms under which the material is redistributed here. `Pinned for` names the brief, policy, or plan concern that depends on it and says whether the pin is an excerpt.

| Document | Source | As of | Retrieved | Basis | Pinned for |
|---|---|---|---|---|---|
| [OpenAI Astra model settings](openai-astra-model-settings.md) | https://developers.openai.com/api/docs/models/gpt-6-astra | 2026-09-04 (living-page observation) | 2026-09-04 | Minimal factual identifiers and enumerated settings; no expressive guide prose | Astra identifier and API effort enum; excerpt of Model ID line and reasoning.effort sentence (source lines 3 and 11). |
| [Anthropic Opus 5.5 model and effort guidance](anthropic-opus-5-5-model-effort.md) | https://platform.claude.com/docs/en/about-claude/models/overview and https://platform.claude.com/docs/en/build-with-claude/effort | 2026-09-22 (Opus 5.5 release; living pages) | 2026-09-23 | Minimal excerpt of vendor model-selection and effort recommendations, quoted for citation; no guide prose beyond the cited sentences | Lead-model and starting-effort choice in the Astra-era brief; excerpt of the overview's model-choice sentences and the Opus 5.5 and Fable 5.1 effort recommendations. |
| [OpenAI Codex model selection](openai-codex-model-selection.md) | https://learn.chatgpt.com/docs/models | 2026-09-23 (living-page observation; page carries no date) | 2026-09-23 | Minimal excerpt of vendor model-selection and reasoning-effort recommendations, text-rendered from HTML, quoted for citation | Lead-model and starting-effort choice in the Astra-era brief; excerpt of the Astra/Sol/Luna selection and reasoning-effort sentences and the GPT-6 Sol replacement line. |
