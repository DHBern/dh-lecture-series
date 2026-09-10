#!/usr/bin/env python3
"""Generate the pages for past editions and the search index.

Past editions live as data in data/editions.yml; each gets a page under
20XX/. The current edition is prose under 2026/ and is read from there, so
that the search index covers every edition without duplicating content.

Run with:  npm run editions
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "editions.yml"
CURRENT = 2026

LANG = {"de": "Deutsch", "en": "Englisch"}


def esc(text: str) -> str:
    """Escape the pipe, which would otherwise break a Markdown table."""
    return (text or "").replace("|", "\\|")


def page(edition: dict) -> str:
    year = edition["year"]
    rows = []
    for s in edition["sessions"]:
        who = esc(s.get("speaker", ""))
        if s.get("affiliation"):
            who += f" · {esc(s['affiliation'])}"
        title = esc(s.get("title", ""))
        extra = []
        if s.get("workshop"):
            extra.append(f"Workshop: {esc(s['workshop'])}")
        if s.get("note"):
            extra.append(esc(s["note"]))
        if extra:
            title += " — *" + "; ".join(extra) + "*"
        rows.append(f"| **{s['date'][:6]}** | {who} | {title} | {LANG.get(s.get('lang',''),'')} |")

    partners = f"\n{edition['partners']}\n" if edition.get("partners") else ""
    return f"""---
pagetitle: 'Herbstsemester {year}'
lang: de-CH
toc: true
---

# DH Ringvorlesung — Herbstsemester {year}

*DH Lecture Series — Autumn Semester {year}*

**{esc(edition['title'])}**

{edition['time']} · {edition['venue']}
{partners}
::: {{.callout-note title="Vergangene Ausgabe"}}
Diese Ringvorlesung ist abgeschlossen. Das Programm steht hier zur Dokumentation; die
Abstracts und weitere Angaben finden sich im PDF unten.

[**{esc(edition['pdf_label'])}**](/assets/programme/{edition['pdf']})
:::

## Programm

| Datum | Referent:in | Vortrag | Sprache |
|:--|:--|:--|:--|
{chr(10).join(rows)}

: {{tbl-colwidths="[11,26,50,13]"}}

## Weitere Ausgaben

-   [Übersicht aller Ausgaben](/index.qmd)
-   [Aktuelle Ringvorlesung — Herbstsemester {CURRENT}](/{CURRENT}/index.qmd)
"""


def current_edition_entries() -> list:
    """Read the sessions of the current edition out of its own partials."""
    text = (ROOT / str(CURRENT) / "_beitraege.qmd").read_text(encoding="utf-8")
    entries, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        head = re.match(r"^### (?P<date>.+?) — (?P<title>.+?)\s*\{#t-\d+\}\s*$", lines[i])
        if not head:
            i += 1
            continue
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        byline = []
        while i < len(lines) and lines[i].strip():
            byline.append(lines[i].strip())
            i += 1
        raw = " ".join(byline)
        lang = "Deutsch" if "lang-de" in raw else "Englisch" if "lang-en" in raw else ""
        raw = re.sub(r"\[[^\]]*\]\{[^}]*\}", "", raw)
        fields = [f.strip(" ·") for f in raw.split("·") if f.strip(" ·")]
        entries.append({
            "year": CURRENT,
            "date": head.group("date").strip(),
            "speaker": re.sub(r"\*\*", "", fields[0]).strip() if fields else "",
            "affiliation": fields[1] if len(fields) > 1 else "",
            "title": head.group("title").strip(),
            "lang": lang,
            "url": f"{CURRENT}/index.html",
            "current": True,
        })
    return entries


def main() -> int:
    editions = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    index = []

    for e in editions:
        year = e["year"]
        out = ROOT / str(year)
        out.mkdir(exist_ok=True)
        (out / "index.qmd").write_text(page(e), encoding="utf-8")
        print(f"  HS{year}: {len(e['sessions']):>2} sessions -> {year}/index.qmd")
        for s in e["sessions"]:
            index.append({
                "year": year,
                "date": s["date"],
                "speaker": s.get("speaker", ""),
                "affiliation": s.get("affiliation", ""),
                "title": s.get("title", ""),
                "lang": LANG.get(s.get("lang", ""), ""),
                "note": s.get("note", "") or s.get("workshop", ""),
                "url": f"{year}/index.html",
                "current": False,
            })

    index.extend(current_edition_entries())
    index.sort(key=lambda x: (-x["year"], x["date"]))
    (ROOT / "search-index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    years = sorted({x["year"] for x in index}, reverse=True)
    print(f"  search index: {len(index)} sessions across {len(years)} editions {years}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
