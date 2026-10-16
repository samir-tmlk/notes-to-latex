# stemnotes API

The content files use only this API, so changing `style=` changes the look without touching the content.

## Loading

```latex
\documentclass[11pt]{article}   % report or book also work (theorems stay numbered by section)
\usepackage[style=classic, lang=french, vectors=arrow, mode=draft]{stemnotes}
\input{notation}
```

| Option | Values | Effect |
|---|---|---|
| `style` | `classic` (default), `tufte`, `boxed`, `none` | Fonts, page geometry, headings, theorem look; `none` changes nothing in the layout (imposed class or preamble) |
| `theorems` | `true` (default), `false` | `false`: declare no block environment, the class or preamble provides them |
| `lang` | `french` (default), `english` | babel, environment names, cleveref names, intervals, siunitx locale, algorithm keywords, vector calculus operators |
| `vectors` | `arrow` (default), `bold` | Rendering of `\vect{}` |
| `mode` | `draft` (default), `final` | `draft` shows `\src` anchors and highlights `\fixed` corrections |

Engines: LuaLaTeX (recommended), XeLaTeX, pdfLaTeX. Each style falls back to available fonts on minimal installations.

Loaded for you: amsmath, mathtools, amsthm, babel, csquotes, xcolor, graphicx, tikz (+ arrows.meta, calc, positioning, decorations.markings, patterns), pgfplots (compat 1.18), tcolorbox, booktabs, enumitem, caption, subcaption, float, siunitx, mhchem, listings, algorithm + algpseudocode, hyperref, cleveref, microtype, titlesec, fancyhdr. Do not load `physics` (spacing problems; the core provides `\dv`, `\pdv`, `\abs`, `\norm`).

## Title block

`\title{}`, `\author{}` (`\and` works), `\date{}`, plus `\subtitle{}`, `\basedon{provenance}` (printed as "D'après : …" / "Based on: …") and `\runningtitle{short title}`. Leave a field empty rather than inventing it.

## Block environments

All numbered blocks share one counter, numbered within sections (Définition 2.1, Théorème 2.2, …). Each takes an optional title: `\begin{theorem}[Rolle]`.

| Family (boxed colour) | Environments | French names |
|---|---|---|
| Results (burgundy) | `theorem`, `proposition`, `lemma`, `corollary`, `property`, `law` | Théorème, Proposition, Lemme, Corollaire, Propriété, Loi |
| Definitions (blue) | `definition`, `notation` (unnumbered) | Définition, Notation |
| Examples (green) | `example` | Exemple |
| Methods (amber) | `method` | Méthode |
| Exercises (slate) | `exercise` | Exercice |
| Remarks (grey rule) | `remark` | Remarque |
| Unboxed | `proof`, `proof[Title]`, `solution` | Démonstration, Solution |

`\cref{thm-rolle}` prints "théorème 2.2" in French (lower case, correct mid-sentence), "Theorem 2.2" in English; `\Cref` capitalises at the start of a sentence.

Other: `algorithm` + `algorithmic` (keywords translated in French), `lstlisting` (`[language=Python, caption=…]`), `figure`, `table` with booktabs and siunitx `S` columns.

## Layout helpers (style-aware)

| Command | tufte | classic, boxed |
|---|---|---|
| `\aside{text}` | numbered sidenote in the margin | footnote |
| `\begin{marginfigure} … \caption{} \end{marginfigure}` | figure in the margin column | ordinary `figure[htbp]` |
| `\begin{wide} … \end{wide}` | extends over the margin column | no effect |

## Fidelity markers

| Marker | Use | draft | final |
|---|---|---|---|
| `\src{p03}` | Source anchor at the start of every block, caption, and before code listings. Accepts `p03,p05` and `p03-p05`. | grey tag `[p03]` | hidden |
| `\illegible[region]{best reading}` | Uncertain reading (text or maths) | orange + `[?]` | compile error |
| `\missing[region]{description}` | Unreadable, cut or absent passage | orange bracket note | compile error |
| `\suspect[region]{as written}{evidence}` | Probable error in the source, typeset as written; the evidence (what contradicts it) goes to the report, not the PDF | red + `[!]` | compile error |
| `\ambiguous[region]{as written}{question}` | Symbol whose meaning or convention is not settled; the question goes to the report | blue + `[n?]` | compile error |
| `\fixed{original}{corrected}` | Correction approved by the user | corrected text in teal | corrected text, plain |
| `\accepted{reading}` | After "I don't know", option (a): the user accepts the best reading | grey + `[acc.]` | plain; listed in the report |
| `\omitted{what}` | After "I don't know", option (b): the user omits the unresolved passage | grey tag `[omis]` | nothing; listed in the report |
| `\struck{text}` | Crossed-out text in the source, not typeset | grey tag `[barré]` | nothing; listed in the report |
| `\begin{added} … \end{added}` | Content not in the source, asked for by the user | violet rule + label | same |

**Region.** The optional first argument of the four open marks locates the passage on the source page for the answer sheet's crops: `[p02@x0,y0,x1,y1]`, fractions of the page image with 0,0 at the top left, read off `sources/p02-grid.png`; `[p02]` for the whole page. It is never typeset. Without it, the crop is the whole page of the nearest `\src`.

In maths, a marked span is underlined and its sign is bracketed and set in sans serif, so `x^{2}` marked `[!]` cannot be read as a factorial. Marks work inside `align`, fractions and sub- or superscripts; amsmath's double pass is counted once.

In `draft`, a legend of the marks is printed under the title. `final` is only for a document with no open mark: the four "compile error" marks stop compilation there.

Rules: wrap whole tokens (a full `\qty{}`, a full subscript), never put a mark inside a siunitx argument, a label or a verbatim block, never across an `&`. `verify_fidelity.py` lists every mark with its line and turns the open ones into questions; with `--crops` it writes the answer sheet `work/questions.md` and the crops `build/crops/<id>.png`.

## Notation macros (core)

| Macro | Output | Note |
|---|---|---|
| `\N \Z \Q \R \C \K` | ℕ ℤ ℚ ℝ ℂ 𝕂 | |
| `\dd` | upright d with correct spacing | `\int f(x) \dd x` |
| `\e`, `\ii`, `\jj` | upright e, i, j | `\jj` for electrical engineering |
| `\dv[n]{f}{x}`, `\pdv[n]{f}{x}` | d^n f / dx^n, ∂^n f / ∂x^n | |
| `\abs{x}`, `\norm{x}`, `\ceil{x}`, `\floor{x}`, `\inner{u}{v}`, `\set{…}` | paired delimiters | starred forms auto-size: `\abs*{…}`; `\set*{x \;\middle|\; P(x)}` |
| `\icc{a}{b}`, `\ioo`, `\ico`, `\ioc` | [a,b], ]a,b[ or (a,b)… | follows `lang` |
| `\intint{1}{n}` | ⟦1,n⟧ | integer interval |
| `\vect{u}` | arrow or bold per `vectors=` | |
| `\vv{AB}` | long arrow over AB | |
| `\mat{A}` | bold upright | |
| `\transp` | ^T | `A\transp` |
| `\eqdef` | ≔ | definitions |
| `\grad \divg \rot \lapl` | French: grad→, div, rot→, Δ · English: ∇, ∇·, ∇×, ∇² | follows `lang`; override in `notation.tex` |
| `\tr`, `\rank` (rg in French), `\Vect`, `\sgn` | operators | |

Override any of them in `notation.tex` with `\renewcommand` when the source writes it differently.

## Chemistry, units, code

- `\ce{H2SO4 + 2 NaOH -> Na2SO4 + 2 H2O}` (mhchem).
- `\qty{3,0e8}{\metre\per\second}`, `\num{6,022e23}`, `\unit{\kilo\gram}`, `\qtyrange{1}{5}{\milli\metre}`.
- `\begin{lstlisting}[language=Python]` (also C, Java, [LaTeX]TeX, Matlab, R, SQL…). Accented letters work in code with both engines.

## Imposed class or preamble

When a university or journal imposes its class or preamble:

```latex
\documentclass{their-class}      % or \documentclass{article} + \input{their-preamble}
\usepackage[style=none,lang=french]{stemnotes}
```

- `style=none` loads no font, page geometry, heading or title style: the class keeps its look. Marks, `\src`, notation macros and the report work as usual.
- Block environments the class already defines (`theorem`, `definition`…) are kept as they are; stemnotes only adds the missing ones, sharing the class's `theorem` counter. With `theorems=false` it adds none: map the source's blocks to the class's environments instead, and tell the user which ones are missing.
- babel, hyperref and cleveref are not reloaded if the class already loads them; equation numbering is left to the class.
- Tested with `article` + a preamble defining its own theorems, `amsart` and `scrartcl` (KOMA keeps its own `\subtitle`). If a class still clashes (an option clash on a package), load that package with the class's options before stemnotes, and report it.
- Check the imposed class with the skeleton before transcribing (`build.py` on the template with the class swapped in).

## Long documents

Use `\documentclass[11pt]{report}` with `\chapter` for a full course; keep one `content/NN.tex` per chapter or lecture. Add `\tableofcontents` after `\maketitle`.
