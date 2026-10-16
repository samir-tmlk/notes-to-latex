#!/usr/bin/env python3
"""Phase 5 helper: compile a stemnotes document and audit the log.

Usage:
    python3 build.py main.tex [--engine lualatex|pdflatex|xelatex] [--png DIR] [--dpi 80]

Runs latexmk when available (otherwise the engine three times), then reports:
  errors, undefined references, missing glyphs, overfull boxes > 1pt,
  remaining \\illegible / \\missing markers, and fonts that fell back to bitmaps.
With --png, renders every page to DIR for visual inspection.
Exit code 1 if there are errors, undefined references or missing glyphs.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def compile_doc(tex: Path, engine: str):
    cwd = tex.parent
    if shutil.which("latexmk"):
        flag = {"lualatex": "-lualatex", "pdflatex": "-pdf", "xelatex": "-xelatex"}[engine]
        cmd = ["latexmk", flag, "-interaction=nonstopmode", "-halt-on-error", "-f", tex.name]
        subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    else:
        for _ in range(3):
            subprocess.run([engine, "-interaction=nonstopmode", tex.name], cwd=cwd,
                           capture_output=True, text=True)


def audit(log_text: str):
    findings = {"errors": [], "undefined": [], "glyphs": [], "overfull": [], "markers": [], "other": []}
    lines = log_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("! "):
            ctx = " | ".join(l.strip() for l in lines[i + 1:i + 3] if l.strip())
            findings["errors"].append(f"{line[2:]}  [{ctx}]")
        elif re.search(r"(Reference|Citation) .* undefined", line):
            findings["undefined"].append(line.strip())
        elif "Missing character" in line:
            findings["glyphs"].append(line.strip())
        elif line.startswith("Overfull"):
            m = re.search(r"\(([\d.]+)pt too wide\)", line)
            if m and float(m.group(1)) > 1.0:
                findings["overfull"].append(line.strip())
        elif "Package stemnotes Warning" in line:
            findings["markers"].append(line.split(":", 1)[1].strip())
        elif "Label(s) may have changed" in line or "There were multiply-defined labels" in line:
            findings["other"].append(line.strip())
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--engine", default="lualatex", choices=["lualatex", "pdflatex", "xelatex"])
    ap.add_argument("--png", help="directory for page renders")
    ap.add_argument("--dpi", type=int, default=80)
    a = ap.parse_args()

    tex = Path(a.tex).resolve()
    compile_doc(tex, a.engine)
    log = tex.with_suffix(".log")
    pdf = tex.with_suffix(".pdf")
    if not log.exists():
        sys.exit("no log produced: is the engine installed?")
    f = audit(log.read_text(errors="replace"))

    titles = {
        "errors": "Errors", "undefined": "Undefined references", "glyphs": "Missing glyphs (text silently lost)",
        "overfull": "Overfull boxes > 1pt", "markers": "Unresolved fidelity markers", "other": "Other",
    }
    for key, title in titles.items():
        items = list(dict.fromkeys(f[key]))
        if items:
            print(f"\n## {title} ({len(items)})")
            for it in items[:30]:
                print(f"- {it}")
            if len(items) > 30:
                print(f"- ... {len(items) - 30} more")

    if pdf.exists() and shutil.which("pdffonts"):
        fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
        t3 = [l for l in fonts.splitlines() if "Type 3" in l]
        if t3:
            print(f"\n## Bitmap (Type 3) fonts: {len(t3)} — install cm-super/lmodern or the style's fonts")

    if pdf.exists():
        mupdf = None
        if not shutil.which("pdftoppm"):
            for mod in ("pymupdf", "fitz"):
                try:
                    mupdf = __import__(mod)
                    break
                except ImportError:
                    pass
        if shutil.which("pdfinfo"):
            pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
            n = re.search(r"Pages:\s+(\d+)", pages)
            count = n.group(1) if n else "?"
        elif mupdf:
            count = len(mupdf.open(str(pdf)))
        else:
            count = "?"
        print(f"\nPDF: {pdf.name} ({count} pages)")
        if a.png:
            out = Path(a.png)
            out.mkdir(parents=True, exist_ok=True)
            if shutil.which("pdftoppm"):
                subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", str(pdf), str(out / "page")], check=True)
            elif mupdf:
                for k, page in enumerate(mupdf.open(str(pdf)), 1):
                    page.get_pixmap(dpi=a.dpi).save(str(out / f"page-{k}.png"))
            else:
                print("Cannot render pages: install poppler-utils or PyMuPDF. The visual check and the "
                      "blind round-trip are then NOT done: record that in work/verification.md.")
                sys.exit(1)
            print(f"Pages rendered to {out}/")
    else:
        print("\nNo PDF produced.")

    blocking = f["errors"] or f["undefined"] or f["glyphs"] or not pdf.exists()
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
