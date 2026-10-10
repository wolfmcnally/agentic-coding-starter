---
slug: dazzling-hippogriff
title: Verify a presentation through the path the reader takes, not the one that is convenient to automate
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-10-09
source: user
occurrences:
  - date: 2026-10-09
    ref: "this template — the phase report's new color-mode icons were checked in a browser against a local server, passed, and were committed and pushed; the report is normally opened as a local file, where the browser refused the icons' mask images and the control showed no icon. It was found only because the operator asked for the report to be opened and the file path was tried first"
---

The report gained a control whose icons were loaded as CSS mask images. The change was inspected in a real browser, at two widths and in every color mode, and it was right every time. All of that inspection went through a local server, because the automated browser refuses file addresses and a server was one command away.

A reader does not use a server. The tool opens the report as a file, and a browser treats every local file as its own origin, so an asset that loads when served can be refused when opened. The inspection was thorough and it examined a different thing from the one that ships.

The proxy was "renders correctly in a browser"; the property was "renders correctly the way it is opened". The two differ only in how the page is loaded, which is why the difference is easy to step over: the automated path and the real path look like the same check.

**Before judging a rendered artifact, name how its reader opens it, and make at least one observation through that path.** Where the convenient instrument cannot take that path, say so as an unchecked item, or find one that can. Here a second browser run from the command line could load the file, and one screenshot showed the gap.

Correction applied: the icons are plain image elements, which load from files; the checker forbids mask images in the report; and the policy's inspection steps begin with opening a page as a file.
