# Consistency rules (phase 3)

The same thing is always written the same way. On the full track, record each decision in `work/stylesheet.md`; on the express track, apply these rules while writing.

## Terms and wording

- One term per concept across all sources (choose with the user when sources differ).
- Abbreviations (`ssi`, `tq`, `cad`, `ev`, `sev`, `cf.`) are expanded in `edited` and `enriched`, kept in `faithful`. Expand only standard ones; an abbreviation you cannot expand with certainty stays as written and becomes a question.
- Everything else follows the fidelity-level table in SKILL.md.

## Blocks

Map the source's labels, never your own judgement of what a passage "is":

| Source label | Environment |
|---|---|
| Déf., Définition, Def. | `definition` |
| Th., Thm, Théorème | `theorem` |
| Prop. | `proposition`, or `property` if the source calls it "propriété" |
| Lemme | `lemma` |
| Cor., Corollaire | `corollary` |
| Loi, Principe | `law` |
| Rq, Rem., Remarque, N.B. | `remark` |
| Ex., Exemple, Application | `example` |
| Méthode, Méthode : | `method` |
| Exercice, Exo | `exercise` |
| Dém., Preuve | `proof` |
| Solution, Corrigé | `solution` |
| Notation | `notation` |
| unlabelled passage | plain text, even if it states a result |

A passage the source boxes or underlines without a label stays plain text; note the box in the transcript.

## Maths typography

- Upright `\dd`, `\e`, `\ii` (ISO); named functions upright (`\sin`, `\ln`, operators via `\DeclareMathOperator`).
- Delimiters via `\abs`, `\norm`, `\set`, `\inner`; starred forms to auto-size.
- Intervals via `\icc`, `\ioo`, `\ico`, `\ioc` (follow `lang`), integer intervals via `\intint`.
- No `$$`, no `eqnarray`; long equations with `multline` or `split`; alignments with `align`.
- An equation is numbered only if it is referenced, or numbered in the source; reference it with `\eqref`.
- Multiplication: as in the source (`\cdot`, `\times` or juxtaposition).

## Units and numbers

`\qty{9,81}{\metre\per\second\squared}`, `\num{6,022e23}`, `\unit{\kilo\gram}`, `\qtyrange{1}{5}{\milli\metre}`. siunitx follows the language's decimal marker. Keep the number of significant digits of the source.

## References and labels

- Labels `type-shortname` with hyphens (`thm-rolle`, `eq-oh`), never `:` (breaks cleveref with French under pdfLaTeX).
- `\cref` for blocks, figures, tables and algorithms; `\Cref` at the start of a sentence; `\eqref` for equations.
- If the source numbers its results (Th 3.2), keep their order so the numbers match where possible, and tell the user when they cannot.

## Marks

- Every block opens with `\src{pNN}`; captions carry their own `\src`; a code listing has `\src` just before it.
- Marks wrap whole tokens: a full `\qty{}`, a full subscript, a full term. Never inside a siunitx argument or a label, never across an `&` of an alignment.
