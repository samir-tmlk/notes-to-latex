---
name: notes-to-latex
description: Converts STEM course material (PDF lecture notes, slides, scans, photos of handwritten notes) into a faithful LaTeX document for maths, physics, computer science, chemistry or engineering. Use when the user wants LaTeX, or a clean PDF typeset with LaTeX, from course notes or exercise sheets ("fais le LaTeX de ces photos", "mets mon cours au propre en LaTeX", "typeset my lecture notes"). Keeps the source's content and notation, marks every doubt in the document and delivers a fidelity report. Not for editing or debugging existing LaTeX, humanities or non-technical texts, text extraction or other PDF operations (pdf skill), Word output (docx skill), or clarifying questions before unrelated tasks (zero-hallucination-clarification).
---

# Notes to LaTeX

Produce a LaTeX document that says **exactly what the source says**, in a consistent notation, with professional typography. Beauty comes last and never at the expense of fidelity.

**Output check.** If the user asks to "clean up" or "put my course in order" without naming LaTeX, ask in one question whether they want a LaTeX/PDF document, a Word file or something else, and hand over to the matching skill if it is not LaTeX.

## Fidelity contract

These rules hold on every track and override any wish to make the result "better".

1. **Nothing is invented.** No statement, hypothesis, step, value, unit, figure, reference or example that is not in the source. The fidelity levels below list the only edits allowed. Content the user explicitly asks to add goes only in an `added` block.
2. **Nothing is silently fixed.** A suspected error in the source is typeset **as written** inside `\suspect{as written}{reason}`. Two conditions before using it:
   - **The reading is certain.** On handwriting, an apparent error is usually a misreading: re-read the tiles of the passage first. If the reading itself is in doubt, use `\illegible`, not `\suspect`.
   - **The reason names concrete evidence**: what contradicts it (another page or equation, a computation, units). A style preference or a hunch is not a reason.

   The mark becomes a question; after the answer, a correction becomes `\fixed{original}{corrected}`, and "the source is right" removes the mark.
3. **Nothing is silently guessed.** An uncertain reading goes in `\illegible{best reading}`; an unreadable or cut passage in `\missing{what is missing}`; a symbol whose meaning or convention is not settled in `\ambiguous{as written}{question}`.
4. **Nothing is silently dropped.** Crossed-out text goes in `\struck{text}`: not typeset, tagged in the draft, listed in the report.
5. **Everything is traceable.** Every block carries `\src{pNN}`, the id of the source page it comes from.
6. **Questions are batched and shown with their evidence.** Structuring questions use the question tool (plain text when it is not available), at most 4 per round; marks to resolve go in an answer sheet with a crop of the passage (see *Questions and answers*). "I don't know" is always an allowed answer and has defined outcomes.
7. **Claims stay within what was checked.** Never write or say "100 % faithful", "error-free", "fully verified" or an equivalent (see *Reporting*).

**Draft and final.** `mode=draft` shows every mark, with a legend under the title. `mode=final` compiles only when no `\illegible`, `\missing`, `\suspect` or `\ambiguous` remains: stemnotes stops with an error otherwise, and `verify_fidelity.py --final` fails. A mark disappears only through an answer handled as described in *Questions and answers*, "I don't know" included; no mark is removed on the model's own initiative. In `final`, only `added` blocks stay visibly marked; `\fixed` prints the corrected text (the trace lives in the report), `\src` and `\struck` print nothing.

**Fidelity levels.** Chosen once per document; `edited` is the default. Examples below are French; apply the same logic to the document's language.

| Level | Allowed | Not allowed |
|---|---|---|
| `faithful` | Typography only: maths typesetting, notation macros, units, spacing, list layout. Wording kept word for word, abbreviations included. | Any change of wording. |
| `edited` | Everything in `faithful`, plus: expanding standard abbreviations when the context settles the meaning (`ssi`, `tq`, `cad`, `cf.`), and `\ambiguous` for those it does not (`ev`, `cv`…); spelling, agreement and punctuation; adding the articles, prepositions and the copula (`est`, `sont`) that a telegraphic note leaves out; in prose only, writing a quantifier symbol in words (`∀` → "pour tout", `∃` → "il existe"). | Adding or completing a hypothesis, quantifier, step, justification, conclusion, example or explanation; completing an "etc.", a "…" or a truncated sentence; adding any logical connective (`donc`, `car`, `alors`…) the source does not write in words; turning `⇒`, `→` or `⇔` into words (between formulas or in prose they stay symbols); reordering an argument. |
| `enriched` | Everything in `edited`, plus additions the user asked for, only inside `added` blocks. | Additions outside `added` blocks. |

**Other skills.** The track and supervision rules below take precedence over `zero-hallucination-clarification` when both are installed: that skill asks before starting any task, whereas the express track starts without questions and unattended runs never wait. Borrow from it only the format of the questions.

## Paths and files

`<skill>` is the folder containing this SKILL.md; every path below is relative to it (run `python3 <skill>/scripts/build.py …`). The project is a separate folder in the working directory; copy into it what it needs, never edit files inside `<skill>`.

| Path in `<skill>` | Use |
|---|---|
| `assets/latex/stemnotes.sty` + `stemnotes-{classic,tufte,boxed,none}.sty` | Shared API and the looks (`none`: imposed class or preamble). Copy all into the project. |
| `assets/latex/template/` | Project skeleton: `main.tex`, `notation.tex`, `content/01.tex`. |
| `assets/latex/example/` | Demo of every feature, marks in text and in maths included. Read once before writing LaTeX. |
| `assets/previews/{classic,tufte,boxed}.png` | Style previews to show the user. |
| `scripts/check_env.py` | Engines, poppler/PyMuPDF, Pillow, packages, fonts, test build of the skeleton. |
| `scripts/prepare_sources.py` | PDFs and photos → page images, zoom tiles, grid overlays (to locate marks), text layers, resolution hints, `manifest.json`. |
| `scripts/verify_fidelity.py` | Provenance, open marks, notation consistency, labels, equation checklist, text layer vs LaTeX numbers on typed pages, answer sheet with crops (`--crops`), verification scope. |
| `scripts/build.py` | Compile, audit the log, render pages to PNG. |
| `scripts/lint_tex.py` | Static lint when nothing can compile (braces, environments, maths delimiters, unknown commands). |
| `scripts/score_against_truth.py` | Scores a run against the evaluation set (ground-truth cases, kept outside the installed skill in `evals/`; see its README). Development tool, not used in a normal run. |
| `references/api.md` | Options, environments, macros, marks, imposed templates. |
| `references/transcription.md` | Reading handwriting, slides and scans; glyph confusions; photo triage. |
| `references/notation.md` | Notation table, ISO 80000-2, French and English conventions. |
| `references/consistency.md` | Phase 3 rules: terms, block mapping, maths typography, units, references. |
| `references/domains.md` | Chemistry, circuits, diagrams, code; figure fidelity. |
| `references/styles.md` | The styles in detail, customisation. |

Project layout:

```
project/
  sources/               pNN.png, pNN-tiles/, pNN-grid.png, pNN-text.txt, manifest.json
  work/state.md          progress, decisions, open questions (for resuming)
  work/transcript.md     faithful reading of every page          (full track)
  work/notation.md       notation table                          (full track)
  work/stylesheet.md     consistency decisions                   (full track)
  work/blind_reading.md  blind re-transcription of the source
  work/verification.md   verification log (template created by verify_fidelity.py)
  work/questions.md      answer sheet: one entry per open mark, with crop (generated)
  build/crops/           crops of the passages behind each open mark (generated)
  main.tex  notation.tex  content/*.tex  figures/  stemnotes*.sty
  fidelity_report.md
```

Keep `work/state.md` current (track, style, level, language, pages done per step, open questions, last command) so that an interrupted run can resume: on resuming, read it, `verification.md` and the report before anything else.

## Track and supervision

**Track.** The **express** track is the default. Use the **full** track when any of these holds, or when the user asks for it: more than 10 source pages; dense handwriting (handwritten pages that are mostly formulas, small writing); high stakes (published, distributed to a class, reference material where an error matters, or the user says it must be exact); several sources covering the same content. Switch from express to full mid-way if reading reveals **more than 5 uncertain readings in total over the pages read so far**, or any notation conflict, and say so in one line. (The per-page stop rule of Phase 0 is separate: it concerns a single page.)

**Supervision.** The session is **unattended** only when the user explicitly said to proceed without them ("fais au mieux", "je regarde demain", "don't wait for me"), when it was started by a schedule or automation with no user message, or when the environment offers no way to ask. Otherwise it is attended: ask and wait. Unattended, never wait:

- take the defaults (`classic`, `edited`, the source's language) and state them at the top of the report;
- mark every doubt in the document: `\illegible`, `\missing`, `\suspect` (never `\fixed`), `\ambiguous`;
- leave `mode=draft`; the answer sheet and the report's *Questions for the user* carry every question;
- deliver the draft PDF and the report, saying that answers are awaited.

## Phase 0: Environment, preparation and triage (both tracks)

1. Run `python3 <skill>/scripts/check_env.py --style all`. It tests the engines, latexmk, poppler or PyMuPDF, Pillow, packages and fonts, and compiles the skeleton in each style, with French (which needs the most packages; English needs nothing more). Once the style is known, rerun with `--style <style>` (and `--lang english` if relevant) to confirm the engine.
   - `READY`: use the engine it names (LuaLaTeX first).
   - `DEGRADED`: it compiles, but fonts fall back or a tool is missing. Continue and note the limitation in the report.
   - `NO-TEX`: **plan B**. Do every phase except compilation: run `lint_tex.py` instead, keep `mode=draft` (the final-mode guard cannot be checked without compiling), record compilation, render check and visual check as **not done**, and still do the blind re-transcription. Deliver the `.tex` project and the report, saying plainly that no PDF was compiled and that the LaTeX was only linted. Suggest Overleaf (upload the folder, compiler LuaLaTeX) or a local TeX distribution.
2. Check that every source file opens. A file mentioned but missing is a question.
3. **Prepare the pages**: `python3 <skill>/scripts/prepare_sources.py sources <files in course order>`. Page ids `p01, p02…` are the `\src` anchors; keep them stable. PDFs are rasterised with poppler, or PyMuPDF when poppler is missing (`pip install pymupdf` if neither is there). If neither can be installed, ask for page images and note it; pages then cannot be rendered either, so proceed as for `NO-TEX` for the render check.
4. **Triage every page** from its image, tiles and resolution hints (`references/transcription.md`): readable, partly readable or unreadable. A page needs a **new photo** when a displayed formula or a block heading cannot be read even in the tiles, when more than about a quarter of the page is unreadable (blur, glare, shadow, cut edge), or when that **single page** would need more than 5 `\illegible`/`\missing` marks. Give the retake tips from the reference.
   - Attended: retake requests join the first round of questions (the intake on the full track, the first message on the express track), so the user answers once. Start on the pages that are fine in the meantime.
   - Unattended: transcribe what is readable, mark the rest `\missing`, and put the retake request first in the answer sheet.
   - Never reconstruct what the image does not show.
5. Read images with the image-viewing tool; no OCR engine is used (their output on formulas is unreliable).

## Questions and answers

**Structuring questions** (style, level, language, scope, notation conflicts, source conflicts, retakes, permission for a reviewer agent) go through the question tool, **at most 4 per round**, the most structuring first; use further rounds only if the answers change what comes next, otherwise carry the rest into the answer sheet.

**Marks** (`\illegible`, `\missing`, `\suspect`, `\ambiguous`) go into the answer sheet, not through the question tool:

0. When placing a mark, give the passage's region on the source page as its optional first argument, read off `sources/pNN-grid.png`: `\illegible[p02@0.42,0.22,0.56,0.29]{t_0}` (fractions of the page, top left = 0,0; `[p02]` alone for the whole page).
1. `verify_fidelity.py --crops` writes `work/questions.md` and one crop per mark in `build/crops/`: for each mark an id (`I1` illegible, `M1` missing, `S1` suspect, `A1` ambiguous), its page, the crop to look at, the best reading or the question, and the options.
2. Open every crop: if one does not show its passage, correct the region and rerun. Then show the sheet and the crops to the user and let them answer **in one free-text message**, in any order and partially ("I1: t_a, I2: ?, S1: source right, A1: bold").
3. Apply the answers using the table below, rerun the script, and put what is still open in the next sheet.

| Answer | Outcome |
|---|---|
| A reading, a value or a convention | The mark is removed, the text set as given. |
| "The source is right" (on `S`) | The mark is removed, nothing changes. |
| A correction approved (on `S`) | `\fixed{original}{corrected}`. |
| "I don't know" or no answer, and the user wants a `final` anyway | Ask them to choose one: **(a) accept the best reading**: the mark becomes `\accepted{reading}`, typeset plainly in `final` and listed by the report as *uncertain reading accepted by the user*, with its page, because the PDF will then show it as certain; **(b) omit the passage**: it becomes `\omitted{what}`, which prints nothing in `final` and is listed under *omitted on purpose, unresolved*; **(c) stay in `draft`**, marks visible. |
| Anything else | Ask again, or keep the mark. |

The model never picks (a), (b) or (c) for the user. Unattended, the answer is (c) by default.

## Building and layout (both tracks)

1. Assemble `main.tex` from the template with the chosen `style`, `lang`, `vectors`; fill title, author, date and `\basedon` only with what the source states. With an imposed class or preamble, use `style=none` (see `references/api.md`).
2. **Figures** (`references/domains.md`): before drawing, list every element of the figure from the source (axes, labels, ticks, points, curves, components and values, nodes and edges). Redraw with TikZ, pgfplots, circuitikz, chemfig or tikz-cd only if every element is known; draw exactly that list, nothing more. Otherwise include the cropped source image, captioned as reproduced from the source, with its `\src`. Never invent data points, labels or decorations.
3. Build: `build.py main.tex --png build/png`. Fix every error, undefined reference and missing glyph.
4. **Render check**: read every rendered page and compare it with what the LaTeX is meant to show: a mark, a sign, an index or a symbol rendered differently from the code (wrong macro, lost argument, missing glyph). This finds typesetting errors only; it says nothing about fidelity to the source. In the same pass, check the layout: overfull lines, equations in the margin, boxes split after one line, figures far from their reference, headings alone at a page bottom, tables wider than the text.
5. **Figure check**: compare each redrawn figure, rendered, with the source crop, element by element against the list; record it in the figures table of `verification.md`.
6. Switch to `mode=final` only when `verify_fidelity.py --final` passes and every mark has been resolved through *Questions and answers*.

## Verification (both tracks)

The goal is to find where the LaTeX departs from the source and to record exactly how far the checks went.

1. **Side by side**, every page: the source image (and tiles) next to the LaTeX blocks anchored to it, item by item: hypotheses and quantifiers, inequality directions, signs, indices, exponents, bounds, constants, numbers and units, figure labels, every line of code. Tick the equation checklist of the report; check inline maths in the same pass.
2. **Blind re-transcription of the source**, by default on every handwritten or dense page (all of it) and on the displayed equations of every other page. In a separate step, **without opening** `content/*.tex`, `notation.tex` or the transcript, re-read the source image and tiles and write what they say in `work/blind_reading.md`, page by page. Only then compare it with the LaTeX. For each difference, go back to the image: if the ink settles it, correct the LaTeX; if not, mark `\illegible` and add it to the answer sheet. This is the check that catches **reading** errors. To lower the correlation with the first reading:
   - **Independent reader.** On the full track, ask at the intake whether a separate reviewer agent may be used. If it may and one is available, give it the source images only (never the LaTeX or the transcript) for this step, and record who did it. On the express track, use one only if the user already agreed.
   - **Same session, no agent.** Change the conditions: read the pages in reverse order, from the tiles rather than the full page, and write each formula before looking at the context around it. Say in the report that this reduces but does not exclude a repeated misreading.
   - **Typed PDFs.** Compare the text layer with the image reading, since the two readings are independent: `verify_fidelity.py --manifest …` lists, per typed page, the numbers found in only one of the text layer and the LaTeX; check signs and symbols of displayed equations by eye against the text layer. A mismatch is read again on the image.
3. **Additions audit**: anything not traceable to a page is deleted, or moved to an `added` block if the user asked for it.
4. **Omission audit**, on both tracks, by **counting blocks directly on each source image** (definitions, results, proofs, examples, displayed equations, figures, code) and comparing with the LaTeX blocks anchored to that page. On the full track, also compare with the transcript, but the image count is the one that counts: an omission made while transcribing is repeated in the transcript and in the LaTeX, so a comparison between those two cannot reveal it. The script checks that every page is cited.
5. **Sanity checks** (dimensions, a short re-derivation, a numerical example) only produce `\suspect` marks with their evidence, never corrections.
6. **Re-verify what changes.** Any block modified after its check, whether by an answer, a `\fixed`, a changed reading, or a content edit made during layout, is checked again side by side, and its displayed equations again by blind re-transcription. Record the re-check in `verification.md` (column *rechecked after changes*) and in the report. A change of style alone does not invalidate the content checks; it does require the render check and the visual check again.
7. **Record** everything in `work/verification.md` (per page: kind, side by side, blind re-transcription or n.a., render check, block counts, discrepancies, rechecks; the figures table; what was not verified), update `work/state.md`, rerun `verify_fidelity.py`, which embeds the log in the report.

Cost: a handwritten page is read up to four times (transcription, side by side, re-transcription, render check). Restricting the re-transcription to handwritten or dense pages and displayed equations keeps typed pages to three.

## Express track

For short, clear material: same contract and marks, fewer artefacts, one round of answers at the end.

1. **No upfront questions** unless the scope is ambiguous (which files, which pages) or a page needs a retake (Phase 0, step 4). Use `classic` and `edited` unless the user said otherwise, and say so in one line when starting.
2. **Phase 0** (environment, preparation, triage); copy the template and the `.sty` files into the project.
3. **Read and write in one pass** (phases 1–3 merged): read each page from its image (tiles for handwriting, `references/transcription.md`) and write the LaTeX directly in `content/01.tex`, each block opening with `\src{pNN}`, applying `references/notation.md` and `references/consistency.md` as you go. Doubts become marks, crossed-out text `\struck`, never choices. Course-specific macros go in `notation.tex`.
4. **Building and layout**, then **Verification**.
5. **One round of answers** with the draft PDF: the structuring questions (the 4 most important; the rest goes to the report), the style if the user may want another (show the previews), and the answer sheet. Apply the answers, then re-verify what changed (Verification, step 6). If the style changes, rerun `check_env.py --style <new>` if it was not `READY` for it, rebuild, and redo the render check and visual check. Switch to `mode=final` when nothing is open or the user has chosen (a) or (b) for what remains, rebuild, deliver.

## Full track

### Phase 1: Intake, then consolidation

**Intake**, one round of questions (at most 4; retake requests from the triage and the answers sheet come with it):

1. **Style**: show the previews. `classic` (AMS / arXiv look) for pure maths and anything printed; `tufte` (wide margin for notes and small figures) for physics and annotated notes; `boxed` (colour-coded blocks) for revision, CS and engineering; `none` when a university or journal imposes its own class or preamble (ask for it). Details: `references/styles.md`.
2. **Fidelity level**: `faithful`, `edited` (default) or `enriched`, as defined in the table of the contract.
3. **Scope and language**: which files and pages, in which order; one document or one per lecture; language (default: the source's), and anything the user already knows is wrong or missing.
4. **Reviewer agent**: may a separate agent be used for the independent blind re-transcription and, on long courses, for chunked transcription? (Yes / no / only for the check.)

For more than 10 pages, agree on a **pilot** of 2–3 pages through every phase first (see *Long courses*).

**Consolidation**: one faithful, ordered reading of all the material, before any LaTeX.

1. Read every page from its **image**. For typed PDFs, the text layer may supply the prose (spot-checked against the image), but formulas, tables and figures are always read from the image.
2. Write `work/transcript.md`, one section per page (`## p03 — cours.pdf p.3, photo`), in the source's words and notation: block types as the source labels them (never promote a remark to a theorem or name a result the source does not name); `⟦U1: t_0 or t_a?⟧` for each uncertain reading; `⟦FIG: every element⟧` for figures; margin notes, arrows, boxes, colours; crossed-out text marked as such.
3. Merge sources by course chronology; when two sources cover the same content, keep the clearest reading and cite both ids. **When they disagree, ask**; never average or pick silently.
4. Build the outline: sections, then blocks with type and anchor.

Checkpoint: source conflicts as structuring questions, uncertain readings in the answer sheet.

### Phase 2: Notation

One meaning per symbol, one symbol per meaning, decided with the user (`references/notation.md`). Build `work/notation.md`; detect glyphs with two meanings, concepts with two glyphs, inconsistent styles, implicit conventions, handwriting ambiguities; ask about what the material does not settle and mark it `\ambiguous` until answered. Keep the source's notation; modernise only with approval. Write `notation.tex`: one macro per concept, commented with meaning and first anchor.

### Phase 3: Consistency

The same thing is always written the same way. Apply `references/consistency.md` (terms, block mapping, maths typography, units, references, source numbering) and record decisions in `work/stylesheet.md`. Write `content/*.tex`, every block opening with `\src{pNN}`. Run `verify_fidelity.py main.tex --manifest sources/manifest.json` and fix every consistency and label finding.

Then **Building and layout**, then **Verification**, then the answer sheet as in the express track, step 5.

## Long courses

- **Chunks**: lectures of 5–10 pages, one `content/NN.tex` each, sharing `notation.tex` and `work/stylesheet.md`; the pilot chunk goes through every step before the others start. Notation found in a later chunk is added to the shared table, never redefined locally.
- **Sub-agents**, only when available and the user agreed: one per chunk for transcription, given its page images, the notation table, the stylesheet and the references; each returns its content file and its uncertain readings. The main session harmonises, runs the scripts and the checks. The blind re-transcription of a chunk is never done by the agent that transcribed it.
- **Typed PDFs**: prose from the text layer, spot-checked; formulas, tables and figures from the image; blind re-transcription on displayed equations only.
- After each chunk, update `work/state.md` so a later session can resume.

## Reporting

`fidelity_report.md` and the final message say what was done, never more:

- **Checked, and how**: e.g. "side by side on p01–p06; blind re-transcription of p02–p05 (handwritten) and of the displayed equations of p01 and p06, reverse order from tiles, by the same model; block counts on the images; render check of all pages; automated checks: anchors, page coverage, notation, references".
- **Not checked**: e.g. "figure p04 included as an image; inline formulas checked only side by side; no independent reviewer, so a misreading repeated in both readings cannot be excluded"; with `NO-TEX`, "not compiled: syntax only linted, no render check, no visual check".
- **Rechecked after changes**: blocks modified after their check, and their re-check.
- **Still open**: remaining marks and unanswered questions.
- **Resolved by the user without certainty**: readings accepted under "I don't know" (option a) and passages omitted as unresolved (option b), each with its page.
- **Omitted on purpose**: crossed-out text (`\struck`), listed with its page.

`verify_fidelity.py` checks provenance and consistency, not meaning: never present its clean output as proof of fidelity. Wording to avoid in any language: "100 % fidèle", "sans erreur", "entièrement vérifié", "identical to the source".

## Delivery

- The project folder as a zip (`main.tex`, `notation.tex`, `content/`, `figures/`, the `.sty` files, `fidelity_report.md`, `work/`, and `sources/` with at least `manifest.json`, plus the page images when the total stays under about 50 MB, so the `\src` anchors can be resolved) and the compiled PDF.
- A short summary: track, style, level, pages covered, corrections applied (with anchors), additions, crossed-out text omitted, what was checked and what was not, readings accepted or passages omitted at the user's choice, anything still open.
- `NO-TEX`: the zip without PDF, in draft mode, with one sentence saying it was not compiled and how to compile it.
- Unattended: the draft PDF and the report, questions first.

## Pitfalls

- Starting to typeset before notation is settled on the full track: errors multiply across the document.
- Opening the LaTeX or the transcript during the blind re-transcription: it then checks nothing.
- Treating the render check as a fidelity check: it only compares the PDF with the LaTeX.
- Counting blocks against the transcript only: an omission made while transcribing stays invisible.
- Applying an answer or a `\fixed` and delivering without re-checking the changed block.
- "Improving" a proof, completing a step, or adding an example outside an `added` block.
- A `\suspect` placed on a passage whose reading is uncertain, or with a vague reason ("looks odd"): re-read the tiles, then use `\illegible`, or name the contradicting page, equation or computation.
- Removing a mark because the user said "I don't know", without their choice between (a), (b) and (c); or applying (a) or (b) without `\accepted` / `\omitted`, which leaves no trace in the report.
- Sending crops without opening them: a wrong region shows the user a blank patch of paper.
- Normalising notation the user did not approve (e.g. turning the teacher's `$\vec u$` into bold).
- Putting a mark inside a siunitx argument, a label or across an `&` of an alignment: wrap whole tokens, e.g. `\fixed{\qty{100}{\micro\farad}}{\qty{10}{\micro\farad}}`.
- Starting a block with a list without `\src` first: the list would run into the heading.
- Typing Unicode maths (`α`, `≤`) in the source: use commands, so every engine works.