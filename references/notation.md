# Notation: method and conventions

## The notation table (`work/notation.md`)

```
| symbol (as written) | meaning                         | first | macro          | status            |
|---------------------|---------------------------------|-------|----------------|-------------------|
| S                   | solution set of (E)             | p01   | \Sol           | ok                |
| S                   | surface of the plate            | p07   | ?              | CONFLICT: ask     |
| u→ / u (bold) p.4   | velocity vector                 | p02   | \vect{u}       | ask: arrow or bold|
| ⟦U2⟧ ν or v         | frequency?                      | p05   | \nu            | uncertain         |
```

Status values: `ok`, `ask`, `conflict`, `uncertain`, `approved (date of answer)`. Only `ok` and `approved` rows go into `notation.tex`. Rows still `ask`, `conflict` or `uncertain` are typeset as written and marked `\ambiguous{as written}{question}` at their first ambiguous use, so the draft shows them and the report asks about them.

## What to look for

- **One glyph, two meanings** (S for a set and a surface; e for the charge and Euler's number; i for an index and the imaginary unit). Propose a distinction only if the user wants one; otherwise keep both and make sure context always tells them apart.
- **One concept, two glyphs** (a vector written `u→` on one page and bold on another; ℝ and R). Pick one with the user.
- **Implicit conventions** to state or confirm: summation convention, sign conventions (metric signature, work done by/on the system, current direction), Fourier transform normalisation, angle units, logarithm base (log vs ln), indexing (0 or 1), ℕ contains 0 or not (French usage includes 0), inner product linear in which argument, row or column vectors.
- **Definitions given after use**, or never given: flag; do not supply a definition.

## Macros: one per concept

Write `\newcommand\Sol{\mathcal{S}}`, not raw `\mathcal{S}` in the content. If the user later wants script S instead, one line changes. `verify_fidelity.py` reports raw uses of a macro's expansion, which also catches the same glyph used with another meaning.

## Mathematical typography (ISO 80000-2)

| Item | Rule | Write |
|---|---|---|
| Variables, functions named by one letter | italic | `x`, `f(x)` |
| Differential d, constants e, i, π | upright (ISO); keep italic only if the user prefers | `\dd x`, `\e^{x}`, `\ii` |
| Named functions and operators | upright | `\sin`, `\ln`, `\exp`, `\tr`, `\DeclareMathOperator` |
| Units | upright, thin space after the number | `\qty{5}{\newton}` |
| Vectors | arrow (common in French teaching) or bold italic (ISO) | `\vect{u}` + `vectors=` option |
| Matrices | bold upright | `\mat{A}` |
| Sets of numbers | blackboard bold | `\R`, `\N` |
| Subscripts that are words | upright | `T_{\text{ext}}`, `E_{\mathrm{c}}` |
| Subscripts that are indices | italic | `x_i`, `a_{n+1}` |

## French and English conventions

| Item | French (`lang=french`) | English |
|---|---|---|
| Decimal marker | comma: `\num{3,14}` → 3,14 | point |
| Open interval | ]a,b[ via `\ioo{a}{b}` | (a,b) |
| Integer interval | ⟦1,n⟧ via `\intint` | {1,…,n} usually |
| ≤ | `\leqslant` is customary | `\leq` |
| Gradient, divergence, curl | `\grad`→ grad with arrow, `div`, `rot` with arrow | ∇f, ∇·, ∇× |
| Transpose | ᵗA or Aᵀ: follow the source | Aᵀ |
| Punctuation | babel adds the thin spaces before ; : ! ? | — |
| Quotes | `\enquote{}` → « » | “ ” |
| Rank, kernel, image | rg, Ker, Im | rank, ker, im |
| Tangent | tan; arc tangent Arctan or arctan per source | tan, arctan |

Keep what the source uses when it differs from this table; the table is a default for unresolved cases.

## Domain notes

- **Physics**: quantities with units through siunitx; vectors per the source; complex amplitudes often underlined (`\underline{U}`) in French courses; keep the teacher's sign and convention choices, and note them.
- **Computer science**: pseudo-code in `algorithmic` (keywords translated in French), real code in `lstlisting` with the language set; complexity with `\mathcal{O}` via a macro (`\bigO`); keep identifiers exactly as written (case, underscores).
- **Chemistry**: `\ce{}` for formulas and equations, including states and charges (`\ce{Cu^2+(aq)}`); arrows `->`, `<=>`, `<->` as in the source.
- **Probability and statistics**: `\mathbb{P}`, `\mathbb{E}`, `\operatorname{Var}` via macros; distinguish random variables (capital) and values (lower case) only as the source does.
