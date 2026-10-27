---
name: docs
description: Build, review, maintain, or publish the project's Markdown/mdBook manual. Supports local browser review, existing Tailnet previews, manual GitHub Pages deployment, and explicitly controlled continuous deployment.
last-reviewed: 2026-10-26
---

# Project documentation

Read the repository's documentation policy and `documentation.toml`. First-party manuals describe this project's product; derived projects acknowledge the Starter methodology briefly and link to its manual. Preserve third-party pins under `docs/` and existing source links.

Run `./bin/docs setup` when pinned tools are absent. It installs exact locked mdBook/plugin versions into ignored repository-local storage; never upgrade global tools or install a global Rust toolchain by inference. If required prerequisites or permissions are unavailable, report the exact blocker.

- No arguments: run `./bin/docs`, which validates the curated input, builds, checks generated links/assets/anchors/search/print, then opens the local book. Browser acceptance is not visual verification; inspect the rendered result using an available browser surface.
- `serve`: run `./bin/docs serve` for a loopback-only foreground preview. An existing approved Tailnet proxy may be supplied with `--url`; do not create routes, Funnel, ACLs or HTTPS configuration. Track the server and stop it before yielding unless the harness supports a persistent tracked background job.
- `build` or `check`: run the corresponding command without opening a browser. Write documentation alongside affected code, use the native test runner for executable examples, and inspect relevant rendered pages after changes.
- `deploy`: run `./bin/docs deploy` after normal commit/push gates. It requires a clean latest pushed release candidate and an already approved workflow. Observe the matching workflow run through its terminal result; then run `./bin/docs verify` and inspect live deep links, anchors, search, 404 and assets before updating or claiming the README link is live.
- `deploy continuous on` or `deploy continuous off`: run the corresponding command only on explicit operator request. It changes the push-deployment switch for the configured release branch (`master` default; existing `main` supported) and leaves manual deployment available. Verify the repository variables after mutation; failure is not success.

The generic Pages workflow template is inert at `manual/github-pages.yml`; Starter's separately approved installation lives at `.github/workflows/docs-pages.yml`. New workflow permissions (`pages: write`, `id-token: write`), Pages source/environment changes, or network/security changes require exact separate approval. Finish the concrete proposal first. Never enable continuous deployment from an ordinary publication request. A dispatch acknowledgment proves only dispatch; no missing or failed state becomes a success.

When transferring this skill, adapt the manual, repository, release branch, URL prefix, preview port, native example tests and local proof inventory as one bundle. Keep this project's manual and publication identity out of another project's scaffold. Follow the repository's normal review, delivery and human-acceptance policies.
