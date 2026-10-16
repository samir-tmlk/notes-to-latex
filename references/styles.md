# The styles

All share the same content API; only `style=` changes. Previews: `assets/previews/`.

## classic — AMS journal / arXiv preprint

- Inspiration: AMS journals (amsart), arXiv preprints, Springer monographs.
- Fonts: Latin Modern (Computer Modern) for text and maths.
- Page: A4, 140 mm text block, centred; running head in small caps.
- Headings: sections centred in small caps (`1. Introduction`), subsections bold, subsubsections run-in italic.
- Blocks: amsthm. Results in bold head + italic statement; definitions, examples, methods upright; remarks with italic head.
- Colour: none except dark navy links.
- Best for: pure maths, theoretical physics, anything printed in black and white or archived.

## tufte — Tufte-LaTeX handout

- Inspiration: Edward Tufte's books and the Tufte-LaTeX classes; Feynman-style lecture handouts.
- Fonts: Palatino (TeX Gyre Pagella + Pagella Math, or newpx with pdfLaTeX), Inconsolata for code.
- Page: A4, 113 mm text block plus a 48 mm margin column; header and page number span the margin.
- Headings: italic, no bold; small caps letter-spaced running head and author.
- Blocks: small-caps heads, italic statements for results.
- Margin: `\aside{}` numbered sidenotes, `marginfigure` for small plots and diagrams, `wide` for content that needs the full width.
- Best for: physics and applied courses with many remarks, figures and side comments.

## boxed — modern lecture notes

- Inspiration: contemporary university lecture notes and revision sheets using coloured theorem boxes.
- Fonts: XCharter (text and XCharter Math), Source Sans Pro headings, Inconsolata code.
- Page: A4, 150 mm text block, no paragraph indent, spaced paragraphs.
- Headings: sans bold, coloured numbers, thin rule under sections; running head shows the current section.
- Blocks: a coloured left bar and a 6 % tint per family (results burgundy, definitions blue, examples green, methods amber, exercises slate, remarks grey rule only). Every box keeps its printed label (Définition, Théorème…), so nothing relies on colour alone.
- Best for: revision, computer science and engineering, readers who scan for definitions and results.

## none — imposed class or preamble

No layout at all: the class's fonts, page, headings and title stay. Only the marks, anchors, notation macros and missing block environments are added. See `api.md`, *Imposed class or preamble*.

## Customising

Put overrides in the preamble after `\usepackage{stemnotes}`:

```latex
\definecolor{sn@thm}{HTML}{7A1F5C}          % boxed: change the results colour
\definecolor{sn@link}{HTML}{000000}         % black links for printing
\geometry{letterpaper}                      % US letter instead of A4
\setmainfont{Libertinus Serif}              % LuaLaTeX: another text font…
\setmathfont{Libertinus Math}               % …with its matching maths font
```

`\makeatletter … \makeatother` is needed around overrides that use `@` in a `.tex` file.

Two-sided printing: `\documentclass[11pt,twoside]{article}` works with `classic` and `boxed`; keep `tufte` one-sided (its margin column is on the right).

## Choosing quickly

| Need | Style |
|---|---|
| Looks like a research paper; black and white printing | classic |
| Lots of remarks, small figures, physics intuition | tufte |
| Quick revision, colour-coded definitions and results | boxed |
