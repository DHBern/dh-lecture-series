#!/usr/bin/env python3
"""Build the UniBE handout in two formats from the same source as the website.

Both outputs come from 2026/_programm.qmd, the partial the website page also
includes, so the handout cannot drift from the published programme.

  handout/dh-ringvorlesung-hs2026.md   plain Markdown for the UniBE CMS
  handout/dh-ringvorlesung-hs2026.pdf  printable programme (Typst, no LaTeX needed)

Run with:  npm run handout
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / "programm.qmd"
MD = HERE / "dh-ringvorlesung-hs2026.md"


def render(fmt: str) -> None:
    print(f"  quarto render --to {fmt}")
    subprocess.run(
        ["quarto", "render", str(SRC.relative_to(ROOT)), "--to", fmt],
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
    render("gfm")
    MD.write_text(flatten_for_cms(MD.read_text(encoding="utf-8")), encoding="utf-8")
    render("typst")

    leftovers = {
        "raw <span>": "<span",
        "GitHub alerts": "> [!",
        "in-page anchors": "](#t-",
    }
    md = MD.read_text(encoding="utf-8")
    bad = [name for name, needle in leftovers.items() if needle in md]
    print(f"\n  {MD.name}  {MD.stat().st_size:,} bytes")
    pdf = MD.with_suffix(".pdf")
    print(f"  {pdf.name}  {pdf.stat().st_size:,} bytes")
    if bad:
        print("  ! still present in the Markdown:", ", ".join(bad))
        return 1
    print("  Markdown is clean for the CMS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
