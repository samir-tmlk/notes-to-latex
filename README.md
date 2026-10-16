# notes-to-latex

A Claude skill that turns STEM course material (PDF lecture notes, slides, scans, photos of handwritten notes) into a faithful, carefully typeset LaTeX document, for maths, physics, computer science, chemistry or engineering.

Fidelity comes first: nothing is invented, corrected or guessed silently. Every doubt stays visible in the draft PDF, every block points back to its source page, and a fidelity report says what was checked, how, and what was not.

## Install

The skill is the repository root: `SKILL.md`, `assets/`, `scripts/`, `references/`. Zip a folder named `notes-to-latex` containing those four items (leave out `evals/`) and add it to Claude as a custom skill.

## Use

Attach your course (PDF, slides or photos) and ask, for example:

- « Fais le LaTeX de ces photos de mon cours »
- « Mets ce poly au propre en LaTeX, style tufte »
- "Typeset my lecture notes in LaTeX"

Short, clear material goes through an express track (no questions upfront, one round of answers at the end). Long, dense or high-stakes material goes through the full five-phase track: consolidation, notation, consistency, verification against the source, layout.

## Styles

All styles share one content API, so switching is a single option: `\usepackage[style=…]{stemnotes}`.

| Style | Look | Best for |
|---|---|---|
| `classic` | AMS journal / arXiv preprint, Latin Modern | Pure maths, printed or archived notes |
| `tufte` | Tufte handout, Palatino, wide margin for sidenotes and figures | Physics, annotated notes |
| `boxed` | Modern lecture notes, Charter, colour-coded blocks | Revision, CS, engineering |
| `none` | Keeps an imposed university or journal class | Imposed templates |

Previews: [`assets/previews/`](assets/previews).

## Marks in the draft

| Mark | Meaning |
|---|---|
| `\src{p03}` | Source page of the block |
| `\illegible{…}` `[?]` | Uncertain reading |
| `\missing{…}` | Unreadable or cut passage |
| `\suspect{…}{evidence}` `[!]` | Probable error in the source, typeset as written |
| `\ambiguous{…}{question}` `[n?]` | Notation to confirm |
| `\fixed{original}{corrected}` | Correction approved by the user |
| `\struck{…}` | Crossed-out text, not typeset, listed in the report |
| `added` environment | Content not in the source, asked for by the user |

The final mode refuses to compile while any uncertain mark remains.

## Contents

- `SKILL.md`: the workflow the model follows.
- `assets/latex/`: `stemnotes.sty` and the style files, a project template, a complete example.
- `scripts/`: environment check, source preparation (page images, zoom tiles, grids), fidelity checker and answer sheet with crops, build and log audit, static lint, scorer for the evaluation set.
- `references/`: transcription guide, notation conventions, consistency rules, domain packages and figure fidelity, styles.
- `evals/`: evaluation cases with ground truth (not part of the installed skill). Real handwritten cases are the most useful addition; see `evals/README.md`.

## Requirements

LuaLaTeX (recommended), pdfLaTeX or XeLaTeX with a recent TeX Live or MiKTeX, or Overleaf; Python 3; poppler-utils or PyMuPDF; Pillow. `scripts/check_env.py` tests all of it and compiles the template.
