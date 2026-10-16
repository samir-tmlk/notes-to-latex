#!/usr/bin/env python3
"""Score a produced project against a ground-truth transcription (evaluation set).

Usage:
    python3 score_against_truth.py OUTPUT_MAIN.tex --eval-id 1 [--evals <skill>/evals/evals.json]

Reads the eval entry (truth file, expected marks, forbidden environments) and reports:
  - display equations: how many truth equations appear in the output, exactly after
    normalisation, or nearly (similarity >= 0.9, listed for a human to judge);
  - extra display equations in the output that match nothing in the truth (possible inventions);
  - block sequence: similarity of the sequence of block environments;
  - marks: each expected mark present (\\suspect, \\struck, \\missing…), and no forbidden mark;
  - forbidden environments (e.g. added) absent;
  - page coverage: every expected page cited by \\src.
Normalisation ignores spacing commands, labels, \\left/\\right sizes, marker wrappers and
equivalent macros (\\dd = \\mathrm{d}, \\R = \\mathbb{R}, \\e = \\mathrm{e}).
Exit code 0 if every hard criterion passes (all equations exact, no extra equation, all
marks, no forbidden item, full coverage), 1 otherwise.
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
BLOCKS = ["theorem", "proposition", "lemma", "corollary", "property", "law", "definition", "example",
          "exercise", "method", "remark", "notation", "proof", "solution", "algorithm", "figure",
          "table", "lstlisting", "added"]
DISPLAY = r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}|\\\[(.*?)\\\]"


def load(path: Path, seen=None) -> str:
    seen = seen if seen is not None else set()
    path = path.resolve()
    if path in seen or not path.exists():
        return ""
    seen.add(path)
    out = []
    for line in path.read_text(errors="replace").splitlines():
        code = re.sub(r"(?<!\\)%.*", "", line)
        out.append(code)
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", code):
            child = path.parent / m.group(1)
            if child.suffix != ".tex":
                child = child.with_suffix(".tex")
            if child.name.startswith("notation"):
                continue
            out.append(load(child, seen))
    return "\n".join(out)


def arg(text, i):
    """Balanced {...} starting at text[i] (after optional spaces and an optional [..]).
    Returns (content, end)."""
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] == "[":
        i = text.find("]", i) + 1
        while i < len(text) and text[i].isspace():
            i += 1
    if i >= len(text) or text[i] != "{":
        return "", i
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return text[i + 1:], len(text)


def unwrap(text):
    """Replace marker calls by the content a reader of the source would see."""
    keep_first = {"illegible": 1, "suspect": 2, "ambiguous": 2, "accepted": 1}
    drop = {"src": 1, "struck": 1, "missing": 1, "label": 1, "omitted": 1}
    changed = True
    while changed:
        changed = False
        for name, n in list(keep_first.items()) + list(drop.items()):
            m = re.search(r"\\" + name + r"(?![A-Za-z])", text)
            if not m:
                continue
            first, end = arg(text, m.end())
            for _ in range(n - 1):
                _, end = arg(text, end)
            text = text[:m.start()] + (first if name in keep_first else "") + text[end:]
            changed = True
    m = re.search(r"\\fixed(?![A-Za-z])", text)
    while m:
        _, end = arg(text, m.end())
        second, end2 = arg(text, end)
        text = text[:m.start()] + second + text[end2:]
        m = re.search(r"\\fixed(?![A-Za-z])", text)
    return text


def norm(eq: str) -> str:
    eq = unwrap(eq)
    for a, b in [(r"\dd", r"\mathrm{d}"), (r"\R", r"\mathbb{R}"), (r"\N", r"\mathbb{N}"),
                 (r"\Z", r"\mathbb{Z}"), (r"\C", r"\mathbb{C}"), (r"\e", r"\mathrm{e}"),
                 (r"\geqslant", r"\geq"), (r"\leqslant", r"\leq"), (r"\ge", r"\geq"), (r"\le", r"\leq"),
                 (r"\tfrac", r"\frac"), (r"\dfrac", r"\frac")]:
        eq = re.sub(re.escape(a) + r"(?![A-Za-z])", lambda _: b, eq)
    eq = re.sub(r"\\(?:,|;|!|:|quad|qquad|enspace|thinspace)(?![A-Za-z])|~", "", eq)
    eq = re.sub(r"\\(?:left|right|big|Big|bigg|Bigg)[lr]?(?![A-Za-z])", "", eq)
    eq = re.sub(r"\\(?:notag|nonumber)(?![A-Za-z])|&|\\\\", "", eq)
    eq = re.sub(r"\\tag\{[^}]*\}", "", eq)
    eq = re.sub(r"\s+", "", eq)
    eq = eq.rstrip(".,;")
    eq = re.sub(r"\{([^{}\\])\}", r"\1", eq)  # x^{2} == x^2
    return eq


def equations(text):
    return [norm(m.group(2) if m.group(2) is not None else m.group(3)) for m in re.finditer(DISPLAY, text, re.S)]


def blocks(text):
    return re.findall(r"\\begin\{(" + "|".join(BLOCKS) + r")\}", text)


def marker_args(text, name):
    found = []
    for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", text):
        a, _ = arg(text, m.end())
        found.append(a)
    if name == "added":
        found = re.findall(r"\\begin\{added\}", text)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output")
    ap.add_argument("--eval-id", type=int, required=True)
    ap.add_argument("--evals", default=str(SKILL / "evals" / "evals.json"))
    a = ap.parse_args()
    ev = next(e for e in json.loads(Path(a.evals).read_text())["evals"] if e["id"] == a.eval_id)
    truth = load(SKILL / ev["truth"])
    out = load(Path(a.output))
    if not out:
        sys.exit(f"cannot read {a.output}")
    hard_fail = []

    te, oe = equations(truth), equations(out)
    exact = [e for e in te if e in oe]
    near = []
    for e in te:
        if e in oe:
            continue
        best = max(oe, key=lambda o: SequenceMatcher(None, e, o).ratio(), default="")
        r = SequenceMatcher(None, e, best).ratio() if best else 0
        near.append((e, best, r))
    extra = [o for o in oe if o not in te and max((SequenceMatcher(None, o, t).ratio() for t in te), default=0) < 0.9]
    print(f"## Display equations: {len(exact)}/{len(te)} exact")
    for e, b, r in near:
        print(f"- not exact (best similarity {r:.2f}):\n    truth:  {e}\n    output: {b}")
    if near:
        hard_fail.append("equations")
    if extra:
        print(f"- {len(extra)} output equation(s) match nothing in the truth (possible invention):")
        for x in extra:
            print(f"    {x}")
        hard_fail.append("extra equations")

    tb, ob = blocks(truth), blocks(out)
    sim = SequenceMatcher(None, tb, ob).ratio()
    print(f"\n## Block sequence similarity: {sim:.2f}\n- truth:  {' '.join(tb)}\n- output: {' '.join(ob)}")

    print("\n## Marks")
    for want in ev.get("must_mark", []):
        args = marker_args(out, want["marker"])
        ok = any(want.get("contains", "") in x for x in args)
        print(f"- {want['marker']} containing `{want.get('contains', '')}`: {'present' if ok else 'MISSING'}")
        if not ok:
            hard_fail.append(f"mark {want['marker']}")
    for bad in ev.get("must_not_mark", []):
        n = len(marker_args(out, bad))
        print(f"- no {bad}: {'ok' if n == 0 else f'FOUND {n}'}")
        if n:
            hard_fail.append(f"forbidden mark {bad}")
    for env in ev.get("forbidden_envs", []):
        n = len(re.findall(r"\\begin\{" + env + r"\}", out))
        print(f"- no {env} environment: {'ok' if n == 0 else f'FOUND {n}'}")
        if n:
            hard_fail.append(f"forbidden env {env}")

    cited = set()
    for m in re.finditer(r"\\src\{([^}]*)\}", out):
        cited.update(x.strip() for x in re.split(r"[,;]", m.group(1)))
    missing_pages = [p for p in ev.get("pages", []) if p not in cited]
    print(f"\n## Page coverage: {'complete' if not missing_pages else 'MISSING ' + ', '.join(missing_pages)}")
    if missing_pages:
        hard_fail.append("coverage")

    print(f"\nRESULT: {'PASS' if not hard_fail else 'FAIL (' + ', '.join(hard_fail) + ')'}")
    print("The 'expectations' in evals.json (process, report, wording) are graded by reading the run.")
    sys.exit(0 if not hard_fail else 1)


if __name__ == "__main__":
    main()
