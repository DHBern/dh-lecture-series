# DH Ringvorlesung

Website of the **DH Ringvorlesung** (lecture series) at the University of Bern, Walter Benjamin
Kolleg / Digital Humanities.

🌐 <https://dhbern.github.io/dh-lecture-series/>

|                   |                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------- |
| Semester          | Herbstsemester 2026 (HS 2026)                                                             |
| Day               | Mondays                                                                                   |
| Lecture           | 14:00–16:00                                                                               |
| Workshop          | 16:00–18:00, on selected dates; attendance expected                                       |
| First / last      | 14 September 2026 / 7 December 2026                                                       |
| Languages         | German and English                                                                        |
| Also published at | [dh.unibe.ch](https://www.dh.unibe.ch/studium/lehrveranstaltungen/aktuell/index_ger.html) |

Single-page site: everything lives in `index.qmd`, with anchors per date. There are no
sub-pages by design.

## Handout for the UniBE website

The programme is also published as plain Markdown (for the UniBE CMS) and as a PDF, in a full
and a short variant:

|                                | Markdown                                  | PDF                                                |
| ------------------------------ | ----------------------------------------- | -------------------------------------------------- |
| Full programme, all abstracts  | `handout/dh-ringvorlesung-hs2026.md`      | `handout/dh-ringvorlesung-hs2026.pdf` (11 pp.)     |
| Short: table and speakers only | `handout/dh-ringvorlesung-hs2026-kurz.md` | `handout/dh-ringvorlesung-hs2026-kurz.pdf` (3 pp.) |

All four are generated from the partials in `2026/` that the website page also includes, so they
cannot drift from the published programme. The speaker list and the link-free programme table
used by the short variant are themselves derived at build time. Regenerate after any change:

```bash
npm run handout
```

That renders GFM and Typst (no LaTeX needed), flattens the Markdown for a plain CMS (GitHub
alert blocks become ordinary blockquotes, in-page anchors are unlinked, inline HTML removed) and
fails if anything CMS-hostile survives. Both files are copied into the published site, so they
also have stable URLs:

- <https://dhbern.github.io/dh-lecture-series/handout/dh-ringvorlesung-hs2026.pdf>
- <https://dhbern.github.io/dh-lecture-series/handout/dh-ringvorlesung-hs2026.md>

## Local development

Requires [Quarto](https://quarto.org/docs/get-started/).

```bash
quarto preview      # live preview
quarto render       # build to _site/
npm install         # dev tooling
npm run format      # format sources before pushing (CI lints with Prettier)
```

## Deployment

Pushing to `main` triggers `.github/workflows/quarto-publish.yml`: lint, render, optimise,
dead-link check, deploy to GitHub Pages.

## Related course sites

- [Introduction to Digital Humanities](https://github.com/DHBern/introduction-to-dh)
- [DH Lab](https://github.com/DHBern/dh-lab)

## Licence

- Text: [CC BY-SA 4.0](LICENSE-CCBYSA.md) — abstracts remain with their authors
- Code: [AGPL-3.0](LICENSE-AGPL.md)
