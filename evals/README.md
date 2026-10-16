# Evaluation set

Each eval gives a prompt and source files to a fresh session that has the skill installed, then scores the produced project against a hand-written ground truth.

## Run one eval

1. Start a new session with the skill, attach the files listed in `evals.json`, send the prompt.
2. When it finishes, score the main file it produced:
   `python3 <skill>/scripts/score_against_truth.py <project>/main.tex --eval-id 1`
3. Grade the `expectations` (process, report, wording) by reading the run and its `fidelity_report.md`.

The scorer is strict on purpose: every truth equation must appear exactly (after normalisation), no output equation may be unmatched (possible invention), every expected mark must be present, forbidden marks and environments must be absent, and every page must be cited.

## Current cases

| id | source | traps |
|---|---|---|
| 1 | `files/oscillateur/source.pdf`, a typed two-page handout | wrong period `T_0 = π/ω_0` (must stay as written, in `\suspect`); crossed-out words (`\struck`); unattended run |
| 2 | `files/oscillateur/photo-p1.jpg`, `photo-p2.jpg`: the same pages photographed (simulated: tilt, perspective, uneven light, blur, noise) | same traps, plus the last line cut off by the photo (`\missing`, never reconstructed) |

These cases test the procedure and the marks. They are **not** handwriting: the simulated photos are of a typed page.

## Add real handwritten cases (recommended)

Handwriting is where the skill is most likely to fail, and only real notes can test it.

1. Photograph 1–3 pages of real handwritten notes (the kind of pages users will send) into `files/<case>/`.
2. Write `truth.tex` by hand, in the stemnotes API, exactly as a perfect run should produce it: the content blocks with `\src{pNN}`, every display equation, and a mark wherever the ink genuinely cannot be read (`\illegible`, `\missing`), where the source is wrong (`\suspect`), where notation is unsettled (`\ambiguous`), and for crossed-out text (`\struck`).
3. Add an entry to `evals.json` with `truth`, `pages`, `must_mark`, `must_not_mark` and `forbidden_envs`.
4. Prefer pages with known traps: a glyph pair that looks alike (ν/v, ε/∈), an exponent or index that is easy to misplace, a crossed-out line, a cut margin.

Run each case several times: a single pass says little about how often the skill misreads.
