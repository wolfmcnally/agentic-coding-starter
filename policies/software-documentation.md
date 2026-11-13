# Policy: Software Documentation

Projects maintain a Markdown user manual built with pinned mdBook and mdbook-admonish. The design and dated sources are in [Reader-Centered Software Documentation](../briefs/software-documentation.md); renderer/plugin configuration authority is pinned under [mdBook](../docs/mdbook-0.4.50/general.md) and [admonish](../docs/mdbook-admonish-1.19.0/reproducible-builds.md).

## Content and ownership

- Write for the reader's task: tutorials teach, how-to guides accomplish a goal, reference gives exact facts, and explanation supplies understanding. Separate long explanations from task instructions. Short supporting reasons may use standard admonish sidebars.
- Open with the problem. The README and the manual's first page begin with a hook-like problem statement that clearly explains the problem the package is intended to solve, and then explain how the package directly addresses that problem. Only the title and a byline or tagline may come before it. Status, maturity, installation, history and methodology notes follow. Write the statement for a reader who has the problem and should recognise it at once, in concrete terms and without the project's internal vocabulary. Before a release, read both openings against this rule; a section that describes what the package is before saying what problem it solves does not satisfy it.
- Document current behavior. Update affected docs, commands, examples and acceptance in the same change as the software. Preserve old authority documents and links; do not publish historical or operational records by concatenation.
- First-party content lives in `manual/`; `docs/` remains third-party pins governed by [docs.md](docs.md). Starter's manual describes the current methodology, tools and skills. Derived-project manuals describe their products, with only a brief methodology acknowledgment and Starter link.
- Use meaningful headings and link text, clear language, and useful text alternatives for images. Review keyboard navigation, narrow screens, contrast and search in the rendered manual. Mechanical checks do not certify accessibility or product quality.
- Use snake_case chapter filenames, title-case `SUMMARY.md` labels, two spaces for nested summary entries, and one physical line per prose paragraph. Put one executable shell command in each copyable fence.

## Reproducible build and drift

- `documentation.toml` owns exact renderer, plugin and installation-compiler pins and recipient-specific preview/publication settings. `manual/book.toml` owns book configuration. Re-pin compatible tools, generated plugin CSS, licenses and their reference catalog together.
- `docs setup` may install missing exact locked tools under ignored repository-local storage. Never upgrade global tools or install a global compiler implicitly. A missing prerequisite or failed version probe refuses explicitly.
- Set `build.create-missing=false` and disable the external Rust Playground. Never create absent chapters silently. `mdbook test` proves Rust examples only; other languages use native project tests.
- Keep the summary, declared assets, implemented commands, documented skills and links in sync. The docs check validates all curated source paths and generated local links, anchors, assets, search and print. It runs in the repository gate; generated output must not mutate tracked input.
- Test documentation examples at their native executable boundary and inspect affected rendered pages. A browser-open response proves presentation request acceptance, not visual correctness.

## Preview and publication

- Preview on loopback. Reuse an existing approved Tailnet route only; no implicit route, Funnel, ACL, listener-exposure or HTTPS changes. Track foreground preview processes and stop them before yielding when background persistence is unsupported.
- Default-deny publication input: summary-listed chapters and explicitly declared assets only, plus the optional custom 404 page. Reject symlinks, escaping paths, include directives and script/iframe embeds before preprocessing. Publish only fresh validated renderer output, never the repository tree.
- Exclude operational logs/evidence, private-project/client material, credentials, host configuration, private URLs and screenshots. Inspect generated search/print as publication surfaces. The deterministic scanner is a limited secret/local-path proxy; the primary must also review the actual curated content and site artifact for private references it cannot recognize.
- `docs deploy` requires a clean committed candidate equal to the latest pushed configured release branch, a matching publication repository, local validation and an already approved workflow. It does not create permission grants or enable Pages.
- `docs deploy continuous on|off` changes the push-deployment switch only on explicit request. Default off; release branch configurable with `master` default and existing `main` supported. Off leaves manual deployment usable.
- New Pages/OIDC/workflow grants, publishing-source/environment changes and network/security changes require exact separate approval. Prepare the concrete proposal before asking. Never infer live continuous-deployment enablement from a request to publish once.
- Observe the matching workflow through a terminal result. Verify public deep links, anchors, assets, 404, search interaction and excluded operational URLs, then verify the README's live link. Dispatch, completion and live verification are distinct facts; unknown or failed remains unknown or failed.
