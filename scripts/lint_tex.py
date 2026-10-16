#!/usr/bin/env python3
"""Static LaTeX lint, for when no TeX engine is available (plan B, NO-TEX).

Usage:
    python3 lint_tex.py main.tex [--sty-dir DIR]

It follows \\input/\\include and checks, without compiling:
  - balanced braces (ignoring \\{ \\} and comments);
  - \\begin/\\end pairs, with the line of the unclosed or mismatched one;
  - math delimiters: $ parity per paragraph, \\[ \\], \\( \\), \\left/\\right per paragraph;
  - argument count of the stemnotes markers (\\suspect, \\ambiguous, \\fixed take two);
  - commands and environments unknown to the lint: defined neither in the stemnotes
    .sty files, nor in notation.tex or the preamble, nor in its list of common packages.
    These are warnings: a correct command from a package it does not know is possible.

This catches typing slips; it does not prove the document compiles. The report must
still say that the LaTeX was not compiled. Exit code 1 on structural errors.
"""
import argparse
import re
import sys
from pathlib import Path

COMMON = set("""
documentclass usepackage begin end input include section subsection subsubsection paragraph
chapter part title author date maketitle tableofcontents label ref eqref cref Cref pageref autoref
caption centering includegraphics textbf textit emph texttt textsf textsc textrm textup textsl
textsuperscript textsubscript underline footnote item newline linebreak pagebreak newpage clearpage
noindent indent par hspace vspace hfill vfill quad qquad smallskip medskip bigskip enspace thinspace
text mathrm mathbf mathit mathsf mathtt mathcal mathbb mathfrak mathscr boldsymbol bm operatorname
frac dfrac tfrac binom sqrt sum prod int iint iiint oint lim limsup liminf sup inf max min arg det
exp log ln lg sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh coth ker dim deg hom Pr gcd
left right middle big Big bigg Bigg bigl bigr Bigl Bigr biggl biggr Biggl Biggr
cdot cdots ldots dots vdots ddots times div pm mp ast star circ bullet oplus otimes odot wedge vee cap
cup setminus subset subseteq supset supseteq in notin ni emptyset varnothing forall exists nexists neg
lnot land lor implies impliedby iff to mapsto rightarrow leftarrow leftrightarrow Rightarrow Leftarrow
Leftrightarrow longrightarrow longleftarrow longmapsto Longrightarrow Longleftrightarrow uparrow
downarrow hookrightarrow twoheadrightarrow rightleftharpoons nearrow searrow
le leq ge geq leqslant geqslant neq ne approx sim simeq cong equiv propto ll gg prec succ preceq succeq
perp parallel mid nmid vert Vert lvert rvert lVert rVert langle rangle lceil rceil lfloor rfloor
infty partial nabla hbar ell Re Im aleph prime angle triangle square Box diamond flat sharp
alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi
rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma
Upsilon Phi Psi Omega
hat widehat tilde widetilde bar overline vec overrightarrow overleftarrow dot ddot acute grave check
breve underbrace overbrace stackrel overset underset substack xrightarrow xleftarrow
tag notag nonumber intertext shortintertext displaystyle textstyle scriptstyle limits nolimits
mathop mathrel mathbin mathopen mathclose mathpunct colon coloneqq eqqcolon
color textcolor colorbox definecolor colorlet
hline toprule midrule bottomrule cmidrule addlinespace multicolumn multirow cline
qty num unit SI si ang qtyrange numrange sisetup
ce chemfig
State Require Ensure If ElsIf Else EndIf For ForAll EndFor While EndWhile Repeat Until Return
Function EndFunction Procedure EndProcedure Call Comment gets
draw node fill path coordinate foreach addplot clip shade filldraw usetikzlibrary tikzset pgfplotsset
newcommand renewcommand providecommand DeclareMathOperator DeclarePairedDelimiter
DeclarePairedDelimiterX newenvironment renewenvironment newtheorem theoremstyle
qedhere qed enquote og fg url href today
lstinline verb
tiny scriptsize footnotesize small normalsize large Large LARGE huge Huge normalfont itshape bfseries
scshape sffamily ttfamily rmfamily upshape mdseries texorpdfstring phantom hphantom vphantom mbox fbox
metre meter second kilogram gram ampere kelvin mole candela hertz newton pascal joule watt coulomb volt
farad ohm siemens weber tesla henry degreeCelsius degree radian steradian becquerel gray sievert litre
liter minute hour day electronvolt percent bar bel decibel neper astronomicalunit atomicmassunit dalton
femto pico nano micro milli centi deci deca hecto kilo mega giga tera peta per square cubic squared
cubed tothe raiseto of
""".split())
COMMON_ENVS = set("""
document equation equation* align align* gather gather* multline multline* flalign flalign* split
aligned gathered cases dcases pmatrix bmatrix vmatrix Vmatrix matrix smallmatrix array subequations
figure figure* table table* tabular tabular* center flushleft flushright itemize enumerate description
minipage quote quotation verbatim lstlisting algorithm algorithmic tikzpicture axis circuitikz tikzcd
proof abstract subfigure thebibliography
""".split())
VERBATIM = ("lstlisting", "verbatim", "minted")


def strip_comment(line):
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2]); i += 2; continue
        if c == "%":
            break
        out.append(c); i += 1
    return "".join(out)


def load(path, seen):
    path = path.resolve()
    if path in seen or not path.exists():
        return []
    seen.add(path)
    rows, in_verb = [], None
    for n, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if in_verb:
            if re.search(r"\\end\{" + re.escape(in_verb) + r"\}", raw):
                in_verb = None
                rows.append((path, n, r"\end{" + raw.split(r"\end{", 1)[1].split("}")[0] + "}"))
            continue
        code = strip_comment(raw)
        m = re.search(r"\\begin\{(" + "|".join(VERBATIM) + r")\}", code)
        if m and not re.search(r"\\end\{" + m.group(1) + r"\}", code):
            in_verb = m.group(1)
            code = code[:m.end()]
        code = re.sub(r"\\verb(.).*?\1", "", code)
        code = re.sub(r"\\lstinline(.).*?\1", "", code)
        rows.append((path, n, code))
        for inc in re.finditer(r"\\(?:input|include)\{([^}]+)\}", code):
            child = path.parent / inc.group(1)
            if child.suffix != ".tex":
                child = child.with_suffix(".tex")
            rows.extend(load(child, seen))
    return rows


def defined_names(texts):
    cmds, envs = set(), set()
    for t in texts:
        cmds |= set(re.findall(r"\\(?:new|renew|provide)command\*?\s*\{?\\([A-Za-z@]+)", t))
        cmds |= set(re.findall(r"\\(?:DeclareRobustCommand|DeclareMathOperator\*?|DeclarePairedDelimiterX?)\s*\{?\\([A-Za-z@]+)", t))
        cmds |= set(re.findall(r"\\def\\([A-Za-z@]+)", t))
        cmds |= set(re.findall(r"\\let\\([A-Za-z@]+)", t))
        envs |= set(re.findall(r"\\(?:new|renew)environment\*?\{([^}]+)\}", t))
        envs |= set(re.findall(r"\\newtheorem\*?\{([^}]+)\}", t))
        envs |= set(re.findall(r"\\sn@thm\{([^}]+)\}", t))
        envs |= set(re.findall(r"\\ifcsundef\{([^}]+)\}\{\\newtheorem", t))
    return cmds, envs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--sty-dir", help="folder with stemnotes*.sty (default: next to main.tex)")
    a = ap.parse_args()
    main_tex = Path(a.tex)
    rows = load(main_tex, set())
    if not rows:
        sys.exit(f"cannot read {main_tex}")
    sty_dir = Path(a.sty_dir) if a.sty_dir else main_tex.resolve().parent
    sty_texts = [p.read_text(errors="replace") for p in sty_dir.glob("stemnotes*.sty")]
    if not sty_texts:
        print(f"warning: no stemnotes*.sty in {sty_dir}; unknown-command check will be noisy")
    all_code = "\n".join(r[2] for r in rows)
    cmds, envs = defined_names(sty_texts + [all_code])
    known_cmds = COMMON | cmds | {"src", "illegible", "missing", "suspect", "ambiguous", "fixed", "struck",
                                  "accepted", "omitted",
                                  "aside", "vect", "mat", "vv", "subtitle", "basedon", "runningtitle"}
    known_envs = COMMON_ENVS | envs | {"added", "wide", "marginfigure", "solution", "notation"}

    errors, warnings = [], []
    rel = lambda p: p.name
    # braces and environments
    depth_by_file, stack = {}, []
    for f, n, code in rows:
        d = depth_by_file.get(f, 0)
        for m in re.finditer(r"\\[{}]|[{}]|\\(begin|end)\{([^}]*)\}", code):
            tok = m.group(0)
            if tok in ("\\{", "\\}"):
                continue
            if tok == "{":
                d += 1
            elif tok == "}":
                d -= 1
                if d < 0:
                    errors.append(f"{rel(f)}:{n} closing brace without opening brace"); d = 0
            if m.group(1) == "begin":
                stack.append((m.group(2), f, n))
                if m.group(2) not in known_envs:
                    warnings.append(f"{rel(f)}:{n} environment `{m.group(2)}` unknown to the lint")
            elif m.group(1) == "end":
                if not stack:
                    errors.append(f"{rel(f)}:{n} \\end{{{m.group(2)}}} without \\begin")
                elif stack[-1][0] != m.group(2):
                    b = stack[-1]
                    errors.append(f"{rel(f)}:{n} \\end{{{m.group(2)}}} closes \\begin{{{b[0]}}} "
                                  f"opened at {rel(b[1])}:{b[2]}")
                    stack.pop()
                else:
                    stack.pop()
        depth_by_file[f] = d
    for f, d in depth_by_file.items():
        if d > 0:
            errors.append(f"{rel(f)}: {d} unclosed brace(s)")
    for name, f, n in stack:
        errors.append(f"{rel(f)}:{n} \\begin{{{name}}} never closed")

    # math delimiters, per paragraph
    by_file = {}
    for f, n, code in rows:
        by_file.setdefault(f, []).append((n, code))
    for f, lines in by_file.items():
        para, start = [], None
        for n, code in lines + [(10**9, "")]:
            if code.strip() == "" and para:
                text = " ".join(para)
                t = text.replace(r"\$", "")
                if t.count("$") % 2:
                    errors.append(f"{rel(f)}:{start} odd number of $ in this paragraph")
                if t.count(r"\[") != t.count(r"\]"):
                    errors.append(f"{rel(f)}:{start} \\[ and \\] do not pair up in this paragraph")
                if t.count(r"\(") != t.count(r"\)"):
                    errors.append(f"{rel(f)}:{start} \\( and \\) do not pair up in this paragraph")
                nl = len(re.findall(r"\\left(?![a-zA-Z])", t)); nr = len(re.findall(r"\\right(?![a-zA-Z])", t))
                if nl != nr:
                    errors.append(f"{rel(f)}:{start} {nl} \\left for {nr} \\right in this paragraph")
                para, start = [], None
            elif code.strip():
                if start is None:
                    start = n
                para.append(code)

    # marker arity and unknown commands
    two_args = ("suspect", "ambiguous", "fixed")
    for f, n, code in rows:
        for m in re.finditer(r"\\(" + "|".join(two_args) + r")(?![A-Za-z])", code):
            rest = re.sub(r"^\s*\[[^\]]*\]", "", code[m.end():]).lstrip()  # optional [region]
            if not re.match(r"\{(?:[^{}]|\{[^{}]*\})*\}\s*\{", rest):
                warnings.append(f"{rel(f)}:{n} \\{m.group(1)} needs two arguments "
                                f"(check if the second is on the next line)")
        for m in re.finditer(r"\\([A-Za-z]+)\*?", code):
            name = m.group(1)
            if name not in known_cmds:
                warnings.append(f"{rel(f)}:{n} command \\{name} unknown to the lint")

    warnings = list(dict.fromkeys(warnings))
    print(f"## Structural errors ({len(errors)})")
    print("\n".join(f"- {e}" for e in errors) or "- none")
    print(f"\n## Warnings ({len(warnings)})")
    print("\n".join(f"- {w}" for w in warnings[:60]) or "- none")
    if len(warnings) > 60:
        print(f"- ... {len(warnings) - 60} more")
    print("\nStatic lint only: the document has NOT been compiled.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
