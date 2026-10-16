# Reading the source material

The transcript (`work/transcript.md`) is the ground truth for everything after phase 1. It must record what is on the page, not what should be on the page.

## Triage before transcribing

For each page, look at the full image and the tiles, and classify it:

- **readable**: every formula and heading can be read, possibly with zoom;
- **partly readable**: a few words or symbols uncertain → `\illegible` / `\missing` marks;
- **unreadable**: stop rule below.

**Stop and ask for a new photo** of a page when a displayed formula or a block heading cannot be read even in the tiles, when more than about a quarter of the page is unreadable (blur, glare, shadow, cut edge, writing showing through), or when the page would need more than 5 `\illegible`/`\missing` marks. `prepare_sources.py` flags images whose longest side is under 1600 px: look at those first. Unattended, transcribe what is readable, mark the rest `\missing`, and put the retake request first among the questions.

Retake tips to give the user: one page per photo, phone held parallel to the page, daylight or even light without flash, no shadow of the phone, the whole page in the frame with a little margin, full camera resolution, a scanner app (document mode) if available, and for a whiteboard a photo per panel.

## General method

1. Read a page once at full size for structure (blocks, figures, reading order), then zoom (tiles in `pNN-tiles/`) for every formula.
2. Transcribe formulas as LaTeX, but in the **source's** notation: if the teacher writes `u→` keep `\vec{u}`; if they write `dx/dt` keep a fraction, not `\dot{x}`.
3. Resolve each formula against its context: dimensions, the variable list of the section, the line before and after. Context may **confirm** a reading; it may not **replace** what is written. If context and ink disagree, it is a `⟦U⟧` item for the user.
4. Number uncertain readings `⟦U1: …⟧` with the alternatives, and note where they are (page, line, tile).
5. One pass per page is not enough for formulas: re-read every formula a second time, right to left, checking signs, indices, exponents and limits.

## Handwriting: glyph pairs to check every time

| Easily confused | How to decide |
|---|---|
| `1` `l` `I` `|` `7` | Serif or crossbar habits of the writer elsewhere on the page |
| `u` `v` `ν` `μ` | Greek letters are usually declared or contextual (frequency, viscosity) |
| `x` `×` `χ` `κ` `k` | Multiplication sign size and position; κ vs k height |
| `ε` `∈` `e` `ϵ` | ∈ appears in set statements (`x ∈ E`); ε as small quantity |
| `φ` `ϕ` `ψ` `Φ` `∅` | Writer's habit; ∅ only with sets |
| `a` `α` `d` `∂` `δ` | ∂ in derivatives with several variables; α open on the right |
| `w` `ω` | ω for angular frequency, often with t |
| `t` `+` `†` | Cross height |
| `z` `2` `ζ` `ξ` | Crossed z in some hands; ξ more loops |
| `5` `S` `s` `§` | |
| `0` `O` `o` `θ` `σ` `δ` | Bar inside θ; σ with a tail on the right |
| `η` `n` `ρ` `p` `γ` `y` `r` `Γ` | Descenders |
| `B` `β` `ß` `13` | |
| `<` `≤` `≺` `∠`, `→` `⇒` `↦` | Underline of ≤; double shaft of ⇒; bar of ↦ |
| `'` (prime) `,` `^1` | Position relative to the baseline |
| `∑` `Σ` `E`, `∏` `Π` | Size and limits |
| `·` (product) `.` (decimal) `,` | French decimal comma |

Subscripts and superscripts: check what is lowered or raised, and whether an index belongs to the letter or to the whole bracket (`x_i^2` vs `(x_i)^2` vs `x_{i^2}`).

## Structures in handwritten notes

- **Boxed, framed or underlined** formulas usually mark key results: note it (`[boxed]`), do not decide alone that it is a theorem.
- **Arrows** between lines: implication, "becomes", or a pointer to a remark. Transcribe the arrow and where it points.
- **Margin notes**: keep them and their anchor point; they become `\aside{}` or a remark, as the user prefers.
- **Colours**: note them (`[red]`); teachers often use colour for definitions or warnings.
- **Crossed-out text**: record it as crossed out. In the LaTeX it becomes `\struck{text}`: not typeset, listed in the report so the user can ask for it back.
- **Abbreviations** (`ssi`, `tq`, `cad`, `ev`, `sev`, `cv`, `DL`, `CNS`): transcribe as written; expansion is a phase 3 decision.
- **"cf. TD", "voir poly"**: references to material you do not have. Keep the reference; never fill it in.
- **Continuation across pages or photos**: mark `→ continues on p05`; check that nothing is lost at the edges of photos (`\missing` if cut).

## Slides and typed PDFs

- Text layers are useful for prose but mangle mathematics (lost sub/superscripts, wrong symbols, broken fractions): always check formulas on the image.
- Slide builds (the same slide repeated with one more line) are one block: transcribe the last state, cite all ids.
- Speaker notes or handwritten annotations on slides are separate items: ask whether to keep them.

## Figures and diagrams

Record every element: axes and their labels, units, tick values, curves and their labels, points, arrows, angles, circuit components with values, tree or graph nodes and edges. If an element cannot be read, say so. This list decides in phase 5 whether the figure can be redrawn (every element known) or must be reproduced from the image.

## Photos of whiteboards

Glare, perspective and partial erasure are frequent: use the tiles; a word half erased is `⟦U⟧`, never reconstructed from what "must" have been there.
