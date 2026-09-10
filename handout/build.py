#!/usr/bin/env python3
"""Build the UniBE handout in two formats from the same source as the website.

All outputs come from the partials in 2026/, which the website page also
includes, so the handouts cannot drift from the published programme.

  handout/dh-ringvorlesung-hs2026.md        full programme, Markdown for the UniBE CMS
  handout/dh-ringvorlesung-hs2026.pdf       full programme, printable (Typst, no LaTeX)
  handout/dh-ringvorlesung-hs2026-kurz.md   short version: table and speakers only
  handout/dh-ringvorlesung-hs2026-kurz.pdf  short version, printable

Run with:  npm run handout
"""
import re
from datetime import date
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / "programm.qmd"
MD = HERE / "dh-ringvorlesung-hs2026.md"
SRC_SHORT = HERE / "programm-kurz.qmd"
MD_SHORT = HERE / "dh-ringvorlesung-hs2026-kurz.md"


MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]


def build_date_line() -> Path:
    """Write the 'Stand:' line.

    The date cannot come from the front matter: any date there makes Quarto
    render its own title block above our logos.
    """
    today = date.today()
    line = (f"Digital Humanities, Universität Bern · "
            f"Stand: {today.day}. {MONTHS_DE[today.month - 1]} {today.year}")
    target = HERE / "_stand.qmd"
    target.write_text(line + "\n", encoding="utf-8")
    return target


def stage_logos() -> None:
    """Copy the logos beside the Typst source.

    Typst refuses to read files above the directory it compiles in, so the
    handout cannot reference ../logo.png. The repo root keeps the originals;
    these copies are refreshed on every build.
    """
    for name in ("logo-unibe.png", "logo.png"):
        shutil.copyfile(ROOT / name, HERE / name)
    print("  logos staged for Typst")


def build_speaker_list() -> Path:
    """Derive a compact speaker list from the contributions partial.

    Generated rather than written by hand so the short handout cannot drift
    from the full programme.
    """
    src = ROOT / "2026" / "_beitraege.qmd"
    lines = src.read_text(encoding="utf-8").split("\n")
    entries = []
    i = 0
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

        # a contribution may carry its title in the other language on the next line
        other_title = ""
        while i < len(lines) and not lines[i].strip():
            i += 1
        alt = re.match(r"^\[(?P<t>.+?)\]\{\.title-(en|de)\}\s*$", lines[i].strip() if i < len(lines) else "")
        if alt:
            other_title = alt.group("t")
            i += 1

        raw = re.sub(r"\[[^\]]*\]\{[^}]*\}", "", raw)          # drop the badge spans
        fields = [f.strip(" ·") for f in raw.split("·")]
        fields = [f for f in fields if f]
        name = re.sub(r"\*\*", "", fields[0]).strip() if fields else ""
        affiliation = fields[1] if len(fields) > 1 else ""
        entries.append({
            "date": head.group("date").strip(),
            "title": head.group("title").strip(),
            "name": name,
            "affiliation": affiliation,
            "lang": lang,
            "other_title": other_title,
        })

    out = ["## Referentinnen und Referenten", ""]
    for e in entries:
        who = f"**{e['name']}**"
        if e["affiliation"]:
            who += f" · {e['affiliation']}"
        out.append(who + "  ")
        detail = f"*{e['title']}*"
        if e["other_title"]:
            detail += f" / *{e['other_title']}*"
        detail += f" — {e['date']}"
        if e["lang"]:
            detail += f", Vortragssprache: {e['lang']}"
        out.append(detail)
        out.append("")

    target = HERE / "_referierende.qmd"
    target.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"  speaker list: {len(entries)} entries -> {target.name}")
    return target


def build_short_table() -> Path:
    """Copy the programme table with its in-page links removed.

    The short handout leaves out the contributions, so links to their
    anchors would dangle (and Typst refuses to compile them).
    """
    src = (ROOT / "2026" / "_tabelle.qmd").read_text(encoding="utf-8")
    src = re.sub(r"\[([^\]]+)\]\(#t-\d+\)", r"\1", src)
    target = HERE / "_tabelle-kurz.qmd"
    target.write_text(src, encoding="utf-8")
    print(f"  programme table without anchors -> {target.name}")
    return target


def render(source: Path, fmt: str) -> None:
    print(f"  quarto render {source.name} --to {fmt}")
    subprocess.run(
        ["quarto", "render", str(source.relative_to(ROOT)), "--to", fmt],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )


def flatten_for_cms(text: str) -> str:
    """Turn Quarto's GFM niceties into markdown a plain CMS will accept."""

    def alert(match: re.Match) -> str:
        """> [!NOTE] blocks -> a plain blockquote led by a bold title."""
        lines = []
        for raw in match.group(2).split("\n"):
            line = re.sub(r"^>\s?", "", raw)
            heading = re.match(r"^#{1,6}\s+(.*)$", line)
            if heading:
                line = f"**{heading.group(1).strip()}**"
            lines.append(("> " + line).rstrip())
        while lines and lines[0] == ">":
            lines.pop(0)
        while lines and lines[-1] == ">":
            lines.pop()
        return "\n".join(lines) + "\n"

    text = re.sub(r"^> \[!(\w+)\]\n((?:>.*\n?)*)", alert, text, flags=re.M)
    # in-page anchors mean nothing once pasted elsewhere
    text = re.sub(r"\[([^\]]+)\]\(#t-\d+\)", r"\1", text)
    # any stray inline HTML
    text = re.sub(r"</?span[^>]*>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def main() -> int:
    stage_logos()
    build_date_line()
    build_speaker_list()
    build_short_table()

    docs = [(SRC, MD), (SRC_SHORT, MD_SHORT)]
    for source, md in docs:
        render(source, "gfm")
        md.write_text(flatten_for_cms(md.read_text(encoding="utf-8")), encoding="utf-8")
        render(source, "typst")

    hostile = {"raw <span>": "<span", "GitHub alerts": "> [!", "in-page anchors": "](#t-"}
    failed = False
    print()
    for _, md in docs:
        pdf = md.with_suffix(".pdf")
        print(f"  {md.name:<38} {md.stat().st_size:>8,} bytes")
        print(f"  {pdf.name:<38} {pdf.stat().st_size:>8,} bytes")
        text = md.read_text(encoding="utf-8")
        bad = [name for name, needle in hostile.items() if needle in text]
        if bad:
            print(f"  ! {md.name}: still present -> {', '.join(bad)}")
            failed = True
    if failed:
        return 1
    print("\n  Both Markdown files are clean for the CMS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
