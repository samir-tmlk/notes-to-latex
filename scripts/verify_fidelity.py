#!/usr/bin/env python3
"""Phase 3-4 helper: static fidelity and consistency audit of a stemnotes project.

Usage:
    python3 verify_fidelity.py main.tex [--manifest sources/manifest.json]
                               [--notation notation.tex] [--report fidelity_report.md] [--final]

What it checks (it reads the .tex sources, it does not judge the mathematics):
  1. Provenance: every block (theorem-like, proof, solution, figure, table, algorithm, code)
     carries a \\src{...} anchor; with --manifest, every source page is cited at least once
     and no anchor points to a page that does not exist.
  2. Open items: \\illegible, \\missing, \\suspect, \\ambiguous, \\fixed (original -> corrected),
     added blocks, TODO/FIXME comments; crossed-out text omitted with \\struck is listed apart.
  3. Consistency: raw notation that bypasses a macro from notation.tex or the core
     (e.g. \\mathbb{R} instead of \\R), unused notation macros, duplicate or undefined labels,
     labels containing ':' (breaks cleveref with French babel under pdfLaTeX),
     $$...$$ and eqnarray, raw Unicode math symbols.
  4. Equation inventory: every display equation with its file:line and source anchor,
     written as a checklist for the side-by-side comparison of phase 4.
  5. Questions for the user: one per open mark, with an id (I1 illegible, M1 missing,
     S1 suspect, A1 ambiguous) and its page. With --crops, also work/questions.md (the
     answer sheet) and build/crops/<id>.png, cut from sources/pNN.png using the mark's
     optional region [pNN@x0,y0,x1,y1] (fractions of the page; whole page without it).
  7. Typed pages (manifest kind pdf-text): numbers in the text layer vs numbers in the
     LaTeX anchored to that page, an independent check of digits.
  6. Verification scope: what was checked automatically, what this script cannot check, and
     the manual verification log (work/verification.md, created from a template on first run
     and embedded in the report on every run; edit that file, not the report).
It never checks that a formula or a sentence matches the source: that is the manual part.
With --final, exits 1 while any \\illegible, \\missing, \\suspect or \\ambiguous remains
(stemnotes also refuses to compile them in mode=final).
"""
import argparse
import json
import re
import sys
from pathlib import Path

BLOCK_ENVS = ["theorem", "proposition", "lemma", "corollary", "property", "law", "definition",
              "example", "exercise", "method", "remark", "notation", "proof", "solution",
              "figure", "table", "algorithm", "marginfigure"]
VERBATIM_ENVS = ["lstlisting", "verbatim"]
DISPLAY_ENVS = ["equation", "equation*", "align", "align*", "gather", "gather*", "multline",
                "multline*", "flalign", "flalign*"]
CORE_NOTATION = {  # macro -> raw form it replaces (from stemnotes.sty)
    r"\N": r"\mathbb{N}", r"\Z": r"\mathbb{Z}", r"\Q": r"\mathbb{Q}", r"\R": r"\mathbb{R}",
    r"\C": r"\mathbb{C}", r"\K": r"\mathbb{K}", r"\dd": r"\mathrm{d}", r"\e": r"\mathrm{e}",
    r"\ii": r"\mathrm{i}", r"\eqdef": r"\coloneqq", r"\transp": r"^{\mathsf{T}}",
}
UNICODE_MATH = "αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩ∞∑∏∫∂∇≤≥≠≈≡∈∉⊂⊆∪∩→⇒⇔∀∃±×÷√"


# ------------------------------------------------------------------ reading
def strip_comment(line: str) -> str:
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2]); i += 2; continue
        if c == "%":
            break
        out.append(c); i += 1
    return "".join(out)


def load_project(main: Path, seen=None):
    """Return list of (file, lineno, raw_line, code_line) following \\input/\\include."""
    seen = seen if seen is not None else set()
    main = main.resolve()
    if main in seen or not main.exists():
        return []
    seen.add(main)
    rows = []
    for n, raw in enumerate(main.read_text(errors="replace").splitlines(), 1):
        code = strip_comment(raw)
        rows.append((main, n, raw, code))
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", code):
            child = (main.parent / m.group(1))
            if child.suffix != ".tex":
                child = child.with_suffix(".tex")
            rows.extend(load_project(child, seen))
    return rows


MARKS = [("I", "illegible", 1), ("M", "missing", 1), ("S", "suspect", 2), ("A", "ambiguous", 2)]


def mark_args(text, pos, nargs):
    """After a mark's name: optional [region], then nargs braced arguments."""
    region = None
    i = pos
    while i < len(text) and text[i] in " \t":
        i += 1
    if i < len(text) and text[i] == "[":
        j = text.find("]", i)
        region = text[i + 1:j].strip()
        i = j + 1
    args = []
    for _ in range(nargs):
        while i < len(text) and text[i].isspace():
            i += 1
        a, i = balanced_arg(text, i)
        args.append(a or "")
    return region, args, i


def parse_region(region, fallback_page):
    """'p02@0.1,0.2,0.5,0.4' -> ('p02', (0.1,0.2,0.5,0.4)); 'p02' -> ('p02', None)."""
    if region:
        m = re.fullmatch(r"\s*([A-Za-z.]*\d+)\s*(?:@\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+))?\s*", region)
        if m:
            box = tuple(float(m.group(k)) for k in range(2, 6)) if m.group(2) else None
            return m.group(1), box
    page = re.split(r"[,;\s-]", fallback_page.strip())[0] if fallback_page else None
    return page, None


def balanced_arg(text: str, start: int):
    """text[start] must be '{'. Returns (content, index after closing brace)."""
    if start >= len(text) or text[start] != "{":
        return None, start
    depth, i = 0, start
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    return text[start + 1:], len(text)


def expand_ids(spec: str):
    ids = []
    for part in re.split(r"[,;]\s*", spec.strip()):
        m = re.fullmatch(r"([A-Za-z.]*)(\d+)\s*-{1,2}\s*([A-Za-z.]*)(\d+)", part)
        if m and (m.group(3) in ("", m.group(1))):
            a, b, width = int(m.group(2)), int(m.group(4)), len(m.group(2))
            ids += [f"{m.group(1)}{k:0{width}d}" for k in range(a, b + 1)]
        elif part:
            ids.append(part)
    return ids


# ------------------------------------------------------------------ checks
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--manifest")
    ap.add_argument("--notation", action="append", default=[])
    ap.add_argument("--report", default="fidelity_report.md")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--verification", help="manual verification log (default: work/verification.md)")
    ap.add_argument("--crops", action="store_true",
                    help="write work/questions.md and one crop per open mark in build/crops/")
    ap.add_argument("--sources", help="folder of page images and text layers (default: sources/)")
    a = ap.parse_args()

    main_tex = Path(a.tex)
    rows = load_project(main_tex)
    if not rows:
        sys.exit(f"cannot read {main_tex}")
    notation_files = [Path(p).resolve() for p in a.notation] or \
        [f for f in dict.fromkeys(r[0] for r in rows) if f.name.startswith("notation")]
    content_rows = [r for r in rows if r[0] not in notation_files]
    rel = lambda f: f.name

    # one long text per file, plus a map from offset to line number
    by_file = {}
    for f, n, raw, code in content_rows:
        by_file.setdefault(f, []).append((n, code))
    texts = {}
    for f, lines in by_file.items():
        offsets, buf, pos = [], [], 0
        for n, code in lines:
            offsets.append((pos, n)); buf.append(code); pos += len(code) + 1
        texts[f] = ("\n".join(buf), offsets)

    def line_of(f, off):
        ln = 1
        for start, n in texts[f][1]:
            if start <= off:
                ln = n
            else:
                break
        return ln

    issues = {k: [] for k in ["provenance", "open", "consistency", "labels"]}
    struck, records = [], []  # records: approved corrections and additions (not questions)
    uncertain, marks, latex_numbers = [], [], {}
    src_tags, equations, questions = [], [], []

    def nearest_src(f, off):
        best = "no anchor"
        for g, ln, spec, o in src_tags:
            if g == f and o <= off:
                best = spec
        return best

    for f, (text, _) in texts.items():
        # source anchors
        for m in re.finditer(r"\\src\{([^}]*)\}", text):
            src_tags.append((f, line_of(f, m.start()), m.group(1), m.start()))
        # blocks without anchor
        for env in BLOCK_ENVS:
            for m in re.finditer(r"\\begin\{" + re.escape(env) + r"\}", text):
                end = text.find(r"\end{" + env + "}", m.end())
                body = text[m.end(): end if end > 0 else len(text)]
                if r"\src{" not in body:
                    issues["provenance"].append(
                        f"{rel(f)}:{line_of(f, m.start())} `{env}` has no \\src anchor")
        for env in VERBATIM_ENVS:
            for m in re.finditer(r"\\begin\{" + env + r"\}", text):
                before = text[max(0, m.start() - 400):m.start()]
                if r"\src{" not in before.split(r"\end{")[-1]:
                    issues["provenance"].append(
                        f"{rel(f)}:{line_of(f, m.start())} `{env}` has no \\src just before it")
        # open marks: \name[region]{arg}{arg}, collected in document order
        for kind, name, nargs in MARKS:
            for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", text):
                region, args, _ = mark_args(text, m.end(), nargs)
                marks.append({"kind": kind, "name": name, "file": f, "off": m.start(),
                              "line": line_of(f, m.start()), "src": nearest_src(f, m.start()),
                              "region": region, "args": args})
        for m in re.finditer(r"\\struck\s*", text):
            arg, _ = balanced_arg(text, m.end())
            struck.append(f"[{nearest_src(f, m.start())}, {rel(f)}:{line_of(f, m.start())}] `{arg}`")
        for m in re.finditer(r"\\accepted\s*", text):
            arg, _ = balanced_arg(text, m.end())
            uncertain.append(f"[{nearest_src(f, m.start())}, {rel(f)}:{line_of(f, m.start())}] "
                             f"reading accepted by the user without certainty: `{arg}`")
        for m in re.finditer(r"\\omitted\s*", text):
            arg, _ = balanced_arg(text, m.end())
            uncertain.append(f"[{nearest_src(f, m.start())}, {rel(f)}:{line_of(f, m.start())}] "
                             f"passage omitted as unresolved, at the user's choice: {arg}")
        for m in re.finditer(r"\\fixed\s*", text):
            orig, nxt = balanced_arg(text, m.end())
            corr, _ = balanced_arg(text, nxt)
            records.append(f"[{nearest_src(f, m.start())}, {rel(f)}:{line_of(f, m.start())}] "
                           f"correction: `{orig}` -> `{corr}`")
        # numbers, for the text-layer comparison of typed pages
        for m in re.finditer(r"(?<![A-Za-z\\{])\d+(?:[.,]\d+)?", text):
            latex_numbers.setdefault(nearest_src(f, m.start()), []).append(m.group(0).replace(",", "."))
        for m in re.finditer(r"\\begin\{added\}", text):
            records.append(f"[{rel(f)}:{line_of(f, m.start())}] added block (not in the source)")
        # display equations
        for env in DISPLAY_ENVS:
            for m in re.finditer(r"\\begin\{" + re.escape(env) + r"\}", text):
                end = text.find(r"\end{" + env + "}", m.end())
                equations.append((f, m.start(), text[m.end():end]))
        for m in re.finditer(r"\\\[(.*?)\\\]", text, re.S):
            equations.append((f, m.start(), m.group(1)))
        # consistency
        if "$$" in text:
            issues["consistency"].append(f"{rel(f)}: uses $$...$$ — use \\[...\\] or equation")
        if "eqnarray" in text:
            issues["consistency"].append(f"{rel(f)}: uses eqnarray — use align")
        for ch in sorted(set(c for c in text if c in UNICODE_MATH)):
            off = text.find(ch)
            issues["consistency"].append(
                f"{rel(f)}:{line_of(f, off)} raw Unicode symbol `{ch}` — use the LaTeX command")

    for f, n, raw, code in content_rows:
        for kw in ("TODO", "FIXME", "XXX"):
            if kw in raw[len(code):]:
                issues["open"].append(f"{rel(f)}:{n} {raw.strip()}")

    # ids and questions for the open marks, in document order
    file_order = {f: k for k, f in enumerate(texts)}
    marks.sort(key=lambda mk: (file_order[mk["file"]], mk["off"]))
    counters = {}
    for mk in marks:
        counters[mk["kind"]] = counters.get(mk["kind"], 0) + 1
        mk["id"] = f"{mk['kind']}{counters[mk['kind']]}"
        mk["page"], mk["box"] = parse_region(mk["region"], mk["src"])
        loc = f"{rel(mk['file'])}:{mk['line']}"
        a0 = mk["args"][0]
        a1 = mk["args"][1] if len(mk["args"]) > 1 else ""
        if mk["kind"] == "I":
            issues["open"].append(f"{mk['id']} {loc} uncertain reading: `{a0}`")
            mk["question"] = f"Is `{a0}` the right reading? If not, what is written?"
            mk["options"] = "the reading as written in the source · `?` (I don't know)"
        elif mk["kind"] == "M":
            issues["open"].append(f"{mk['id']} {loc} missing passage: {a0}")
            mk["question"] = f"Missing passage ({a0}): what does it say?"
            mk["options"] = "the text · a better photo of the page · `?` (I don't know)"
        elif mk["kind"] == "S":
            issues["open"].append(f"{mk['id']} {loc} suspected source error: `{a0}` ({a1})")
            if len(a1.split()) < 4:
                issues["consistency"].append(
                    f"{mk['id']} {loc} \\suspect without a concrete reason: say what contradicts it "
                    f"(page or equation, computation, units), or remove the mark")
            mk["question"] = f"The source writes `{a0}`, which looks wrong: {a1}."
            mk["options"] = "source right · correct to … · `?` (I don't know)"
        else:
            issues["open"].append(f"{mk['id']} {loc} notation to confirm: `{a0}` ({a1})")
            mk["question"] = f"Notation `{a0}`: {a1}"
            mk["options"] = "the meaning or convention · `?` (I don't know)"
        if mk["region"] is None:
            issues["consistency"].append(f"{mk['id']} {loc} has no [pNN@x0,y0,x1,y1] region: "
                                         f"its crop will be the whole page")
        questions.append(f"**{mk['id']}** [{mk['page'] or 'no page'}, {loc}] {mk['question']}")

    # notation
    macros = dict(CORE_NOTATION)
    defined_here = {}
    for nf in notation_files:
        if not nf.exists():
            continue
        ntext = "\n".join(strip_comment(l) for l in nf.read_text().splitlines())
        for m in re.finditer(r"\\(?:re)?newcommand\*?\s*\{?(\\[A-Za-z]+)\}?\s*(\[\d\])?\s*", ntext):
            if m.group(2):  # macros with arguments: no raw-form check
                defined_here[m.group(1)] = None
                continue
            body, _ = balanced_arg(ntext, m.end())
            if body:
                macros[m.group(1)] = body.strip()
                defined_here[m.group(1)] = body.strip()
        for m in re.finditer(r"\\DeclareMathOperator\*?\s*\{?(\\[A-Za-z]+)\}?", ntext):
            defined_here[m.group(1)] = None
    all_text = "\n".join(t for t, _ in texts.values())
    for name, body in macros.items():
        if not body or len(body) < 3:
            continue
        for f, (text, _) in texts.items():
            off = text.find(body)
            if off >= 0:
                issues["consistency"].append(
                    f"{rel(f)}:{line_of(f, off)} raw `{body}` — use `{name}`, or if it means "
                    f"something else here, the glyph has two meanings: resolve in the notation table")
    for name in defined_here:
        if not re.search(re.escape(name) + r"(?![A-Za-z])", all_text):
            issues["consistency"].append(f"notation macro `{name}` is never used")

    # labels and references
    labels = {}
    for f, (text, _) in texts.items():
        for m in re.finditer(r"\\label\{([^}]*)\}", text):
            labels.setdefault(m.group(1), []).append(f"{rel(f)}:{line_of(f, m.start())}")
    for lab, locs in labels.items():
        if len(locs) > 1:
            issues["labels"].append(f"duplicate label `{lab}` at {', '.join(locs)}")
        if ":" in lab:
            issues["labels"].append(f"label `{lab}` contains ':' — use '-' (French babel + pdfLaTeX)")
    for f, (text, _) in texts.items():
        for m in re.finditer(r"\\(?:ref|eqref|cref|Cref|pageref|autoref)\{([^}]*)\}", text):
            for lab in m.group(1).split(","):
                if lab.strip() and lab.strip() not in labels:
                    issues["labels"].append(
                        f"{rel(f)}:{line_of(f, m.start())} reference to undefined label `{lab.strip()}`")

    # coverage against the manifest
    cited = set()
    for f, ln, spec, _ in src_tags:
        cited.update(expand_ids(spec))
    if a.manifest:
        expected = [p["id"] for p in json.loads(Path(a.manifest).read_text())]
        for pid in expected:
            if pid not in cited:
                issues["provenance"].append(f"source page `{pid}` is never cited: content may be missing")
        for pid in sorted(cited - set(expected)):
            issues["provenance"].append(f"anchor `{pid}` does not match any source page")

    # manual verification log: created once from a template, then only read
    vpath = Path(a.verification) if a.verification else main_tex.resolve().parent / "work" / "verification.md"
    pages = [p["id"] for p in json.loads(Path(a.manifest).read_text())] if a.manifest else sorted(cited)
    if not vpath.exists():
        vpath.parent.mkdir(parents=True, exist_ok=True)
        rows = "\n".join(f"| {pid} | | [ ] | [ ] / n.a. | [ ] / n.a. | / | | |" for pid in pages)
        vpath.write_text(
            "<!-- Manual verification log. Fill it in during verification; verify_fidelity.py embeds it in the report. -->\n"
            "Track: express | full · Engine: … · Blind re-transcription done by: same model | separate agent | user\n\n"
            "| page | kind (typed / handwritten / dense) | side-by-side (source image vs LaTeX) "
            "| blind re-transcription (source re-read without the LaTeX) | render check (PDF page vs LaTeX intent) "
            "| blocks counted on image / in LaTeX | discrepancies and resolution | rechecked after changes |\n"
            "|---|---|---|---|---|---|---|---|\n" + rows + "\n\n"
            "Figures (one row per figure):\n\n"
            "| figure | anchor | redrawn or source image | element inventory matched (none missing, none added) |\n"
            "|---|---|---|---|\n\n"
            "Not verified (what and why, e.g. figure p05 included as an image, page p07 blurry, no PDF compiled):\n- \n")
        print(f"Verification log template created: {vpath}")
    vtext = vpath.read_text().strip()

    # answer sheet with crops
    sources = Path(a.sources) if a.sources else main_tex.resolve().parent / "sources"
    if a.crops:
        crop_dir = main_tex.resolve().parent / "build" / "crops"
        crop_dir.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import Image
        except ImportError:
            Image = None
            print("Pillow missing: the answer sheet lists regions but no crop images.")
        sheet = ["# Answer sheet", "",
                 "Answer in one message, in any order, partially if you like: "
                 "`I1: t_a, I2: ?, S1: source right, A1: bold`. `?` means \"I don't know\".", ""]
        for mk in marks:
            crop_note = "no crop"
            img = sources / f"{mk['page']}.png" if mk["page"] else None
            if Image and img and img.exists():
                im = Image.open(img)
                W, H = im.size
                if mk["box"]:
                    x0, y0, x1, y1 = mk["box"]
                    pad = 0.03
                    box = (max(0, int((x0 - pad) * W)), max(0, int((y0 - pad) * H)),
                           min(W, int((x1 + pad) * W)), min(H, int((y1 + pad) * H)))
                    im = im.crop(box)
                elif max(W, H) > 1600:
                    im = im.resize((W * 1600 // max(W, H), H * 1600 // max(W, H)))
                out_img = crop_dir / f"{mk['id']}.png"
                im.save(out_img)
                crop_note = f"build/crops/{mk['id']}.png" + ("" if mk["box"] else " (whole page: no region given)")
            elif img:
                crop_note = f"no crop ({img.name} not found)"
            sheet += [f"## {mk['id']} · page {mk['page'] or '?'} · {rel(mk['file'])}:{mk['line']}", "",
                      f"- Look at: {crop_note}", f"- Question: {mk['question']}",
                      f"- Answer with: {mk['options']}", ""]
        sheet += ["If you answer `?` and still want a final document, choose for each such mark: "
                  "(a) accept the best reading (listed in the report as uncertain), (b) omit the passage "
                  "(listed in the report), or (c) keep the draft with the marks visible.", ""]
        qpath = main_tex.resolve().parent / "work" / "questions.md"
        qpath.parent.mkdir(parents=True, exist_ok=True)
        qpath.write_text("\n".join(sheet))
        print(f"Answer sheet: {qpath} ({len(marks)} marks, crops in {crop_dir})")

    # typed pages: numbers in the text layer vs numbers in the LaTeX anchored to that page
    textlayer = []
    if a.manifest:
        for pg in json.loads(Path(a.manifest).read_text()):
            tl = sources / f"{pg['id']}-text.txt"
            if pg.get("kind") != "pdf-text" or not tl.exists():
                continue
            src_nums = [n.replace(",", ".") for n in re.findall(r"\d+(?:[.,]\d+)?", tl.read_text())]
            tex_nums = [n for spec, nums in latex_numbers.items() if pg["id"] in expand_ids(spec) for n in nums]
            only_src = sorted(set(src_nums) - set(tex_nums), key=lambda x: float(x))
            only_tex = sorted(set(tex_nums) - set(src_nums), key=lambda x: float(x))
            if only_src or only_tex:
                textlayer.append(f"{pg['id']}: in the text layer only: {', '.join(only_src) or '—'} · "
                                 f"in the LaTeX only: {', '.join(only_tex) or '—'}")

    out = ["# Fidelity report", ""]
    n_illegible, n_missing, n_suspect, n_ambiguous = (
        sum(mk["kind"] == k for mk in marks) for k in ("I", "M", "S", "A"))
    out.append(f"- Source anchors: {len(src_tags)} (pages cited: {', '.join(sorted(cited)) or 'none'})")
    out.append(f"- Display equations to check: {len(equations)}")
    out.append(f"- Uncertain readings: {n_illegible} · missing passages: {n_missing} · "
               f"suspected source errors: {n_suspect} · notations to confirm: {n_ambiguous}")
    out.append(f"- Crossed-out text omitted: {len(struck)}")
    out.append("")
    out.append("## Verification scope")
    out.append("")
    out.append("Checked automatically by verify_fidelity.py: every block has a source anchor; every source "
               "page is cited" + ("" if a.manifest else " (no manifest given: page coverage NOT checked)") +
               "; open markers are listed; notation macros are used consistently; labels and references resolve.")
    out.append("")
    out.append("Not checked by the script: whether any sentence, formula, number or figure matches the source. "
               "That is only covered by the manual checks below, page by page. The blind re-transcription "
               "catches reading slips, but a misreading that the same reader repeats in both readings cannot be "
               "excluded; only a separate reviewer or the user can rule it out. The render check only finds "
               "typesetting errors.")
    out.append("")
    out.append(f"### Manual checks ({vpath.name})")
    out.append("")
    out.append(vtext)
    out.append("")
    out.append(f"## Approved corrections and additions ({len(records)})")
    out.append("")
    out.append("Each one must match an explicit answer from the user; otherwise turn it back into \\suspect.")
    out.append("")
    out += [f"- {x}" for x in records] or ["- none"]
    out.append("")
    out.append(f"## Resolved by the user without certainty ({len(uncertain)})")
    out.append("")
    out.append("The PDF shows these as certain, or leaves them out, at the user's choice after an \"I don't know\".")
    out.append("")
    out += [f"- {x}" for x in uncertain] or ["- none"]
    out.append("")
    if textlayer:
        out.append(f"## Text layer vs LaTeX, numbers per typed page ({len(textlayer)})")
        out.append("")
        out.append("Independent of the image reading. Page numbers and equation numbers are expected here; "
                   "any other difference is read again on the image.")
        out.append("")
        out += [f"- {x}" for x in textlayer]
        out.append("")
    out.append(f"## Crossed-out text omitted ({len(struck)})")
    out.append("")
    out.append("Crossed out in the source and therefore not typeset. Tell us if any of it should be kept.")
    out.append("")
    out += [f"- {x}" for x in struck] or ["- none"]
    out.append("")
    out.append(f"## Questions for the user ({len(questions)})")
    out.append("")
    out += [f"{k}. {q}" for k, q in enumerate(questions, 1)] or ["- none"]
    out.append("")
    titles = {"open": "Open items (need a decision from the user)", "provenance": "Provenance",
              "consistency": "Consistency", "labels": "Labels and references"}
    for key, title in titles.items():
        out.append(f"## {title} ({len(issues[key])})")
        out += [f"- {i}" for i in issues[key]] or ["- none"]
        out.append("")
    out.append("## Equation checklist (compare each one with the source image)")
    out.append("")
    out.append("| # | location | source | equation | ok |")
    out.append("|---|---|---|---|---|")
    for k, (f, off, body) in enumerate(sorted(equations, key=lambda e: (str(e[0]), e[1])), 1):
        eq = " ".join(body.split()).replace("|", r"\|")
        out.append(f"| {k} | {rel(f)}:{line_of(f, off)} | {nearest_src(f, off)} | `{eq}` | [ ] |")
    Path(a.report).write_text("\n".join(out) + "\n")

    print("\n".join(out[:5]))
    for key, title in titles.items():
        print(f"{title}: {len(issues[key])}")
    print(f"Report written to {a.report}")
    if a.final and (n_illegible or n_missing or n_suspect or n_ambiguous):
        print("Not ready for mode=final: resolve every \\illegible, \\missing, \\suspect and "
              "\\ambiguous with the user first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
