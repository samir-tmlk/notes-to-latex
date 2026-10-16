#!/usr/bin/env python3
"""Phase 0 helper: check that this machine can build a stemnotes document.

Usage:
    python3 <skill>/scripts/check_env.py [--style classic|tufte|boxed|all] [--lang french|english]

Checks the TeX engines, latexmk, poppler (pdftoppm, pdfinfo, pdftotext, pdffonts), Pillow,
the LaTeX packages stemnotes needs and the fonts each style prefers, then compiles the
project skeleton from assets/latex/template in a temporary folder.

Verdict and exit code:
  0 READY     an engine compiles the skeleton in the requested style(s)
  1 DEGRADED  it compiles, but something is missing (fonts fall back, no poppler, no Pillow)
  2 NO-TEX    no engine can compile: deliver the .tex project and say clearly that the PDF
              was not built (plan B in SKILL.md)
"""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
LATEX = SKILL / "assets" / "latex"

PACKAGES = ["kvoptions", "etoolbox", "iftex", "babel", "csquotes", "amsmath", "mathtools", "amsthm",
            "xcolor", "graphicx", "tikz", "pgfplots", "tcolorbox", "booktabs", "enumitem", "caption",
            "subcaption", "float", "changepage", "marginnote", "titlesec", "fancyhdr", "siunitx",
            "mhchem", "listings", "algorithm", "algpseudocode", "hyperref", "cleveref", "microtype",
            "geometry"]
UNICODE_PACKAGES = ["fontspec", "unicode-math", "lualatex-math"]
FONTS = {  # style -> (unicode-engine files, pdfLaTeX packages); missing ones fall back
    "classic": (["latinmodern-math.otf"], ["lmodern.sty"]),
    "tufte": (["texgyrepagella-regular.otf", "texgyrepagella-math.otf"], ["newpxtext.sty", "newpxmath.sty"]),
    "boxed": (["XCharter-Roman.otf", "XCharter-Math.otf", "SourceSansPro-Regular.otf"],
              ["XCharter.sty", "newtxmath.sty", "sourcesanspro.sty"]),
}


def which(cmd):
    return shutil.which(cmd) is not None


def kpse(name):
    if not which("kpsewhich"):
        return False
    r = subprocess.run(["kpsewhich", name], capture_output=True, text=True)
    return bool(r.stdout.strip())


def try_compile(engine, style, lang):
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        shutil.copytree(LATEX / "template", t, dirs_exist_ok=True)
        for sty in LATEX.glob("stemnotes*.sty"):
            shutil.copy(sty, t)
        main = t / "main.tex"
        text = main.read_text()
        text = text.replace("style=classic", f"style={style}").replace("lang=french", f"lang={lang}")
        main.write_text(text)
        for _ in range(2):
            subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                           cwd=t, capture_output=True, text=True, timeout=300)
        log = (t / "main.log").read_text(errors="replace") if (t / "main.log").exists() else ""
        ok = (t / "main.pdf").exists()
        first_error = next((l for l in log.splitlines() if l.startswith("! ")), "")
        return ok, first_error


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="all", choices=["classic", "tufte", "boxed", "all"])
    ap.add_argument("--lang", default="french", choices=["french", "english"],
                    help="french (default) needs the most packages; english needs nothing more")
    a = ap.parse_args()
    styles = ["classic", "tufte", "boxed"] if a.style == "all" else [a.style]
    degraded, notes = False, []

    print("## Tools")
    engines = [e for e in ("lualatex", "pdflatex", "xelatex") if which(e)]
    for tool in ("lualatex", "pdflatex", "xelatex", "latexmk", "kpsewhich",
                 "pdftoppm", "pdfinfo", "pdftotext", "pdffonts"):
        print(f"- {tool}: {'yes' if which(tool) else 'MISSING'}")
    mupdf = None
    for mod in ("pymupdf", "fitz"):
        try:
            __import__(mod)
            mupdf = mod
            break
        except ImportError:
            pass
    print(f"- PyMuPDF: {'yes' if mupdf else 'no'}")
    if not all(which(t) for t in ("pdftoppm", "pdfinfo", "pdftotext")):
        degraded = True
        if mupdf:
            notes.append("poppler-utils missing: the scripts use PyMuPDF instead (no pdffonts check).")
        else:
            notes.append("poppler-utils and PyMuPDF both missing: PDFs cannot be rasterised and the PDF "
                         "cannot be rendered. Try `pip install pymupdf`; otherwise ask the user for page "
                         "images, and record the visual check and blind round-trip as NOT done.")
    try:
        import PIL  # noqa: F401
        print("- Pillow: yes")
    except ImportError:
        print("- Pillow: MISSING (photos are copied without auto-orientation, no zoom tiles)")
        degraded = True

    if not engines:
        print("\nVERDICT: NO-TEX — no LaTeX engine found. Plan B: deliver the .tex project and the "
              "fidelity report, state that the PDF was not compiled, suggest Overleaf.")
        raise SystemExit(2)

    print("\n## LaTeX packages")
    missing = [p for p in PACKAGES if not kpse(p + ".sty")]
    if a.lang == "french" and not kpse("french.ldf"):
        missing.append("babel-french (french.ldf)")
    print("- all present" if not missing else "- MISSING: " + ", ".join(missing))

    optional = ["chemfig", "circuitikz", "tikz-cd", "minted"]
    print("- optional domain packages: " + ", ".join(f"{p} {'yes' if kpse(p + '.sty') else 'no'}" for p in optional))
    if kpse("minted.sty") and not which("pygmentize"):
        print("  (minted also needs Pygments and -shell-escape: prefer listings)")

    print("\n## Fonts (missing ones fall back to Latin Modern or base PostScript fonts)")
    for s in styles:
        otf, sty = FONTS[s]
        miss = [f for f in otf + sty if not kpse(f)]
        print(f"- {s}: {'preferred fonts present' if not miss else 'fallback for ' + ', '.join(miss)}")
        degraded |= bool(miss)

    print("\n## Compilation test of the project skeleton")
    usable = {}
    for s in styles:  # engines in order of preference; stop at the first that works
        for e in engines:
            if e in ("lualatex", "xelatex") and not all(kpse(p + ".sty") for p in UNICODE_PACKAGES[:2]):
                print(f"- {e} / {s}: skipped (fontspec/unicode-math missing)")
                continue
            ok, err = try_compile(e, s, a.lang)
            print(f"- {e} / {s}: {'OK' if ok else 'FAILED ' + err}")
            if ok:
                usable[s] = e
                break
    failed = [s for s in styles if s not in usable]
    if not usable:
        print("\nVERDICT: NO-TEX — engines exist but the skeleton does not compile "
              f"(missing: {', '.join(missing) or 'see errors above'}). Plan B as in SKILL.md.")
        raise SystemExit(2)
    if failed or missing:
        degraded = True
    for n in notes:
        print(f"\nNote: {n}")
    best = ", ".join(f"{s} → {e}" for s, e in usable.items())
    print(f"\nVERDICT: {'DEGRADED' if degraded else 'READY'} — use: {best}"
          + (f"; styles that do not compile here: {', '.join(failed)}" if failed else ""))
    raise SystemExit(1 if degraded else 0)


if __name__ == "__main__":
    main()
