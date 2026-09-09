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
