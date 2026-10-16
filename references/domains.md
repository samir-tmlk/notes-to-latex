# Domain packages and figure fidelity

Load extra packages in `main.tex`, after `\usepackage{stemnotes}`. All of these were tested with the three styles, in French, with LuaLaTeX and pdfLaTeX.

| Need | Package | Example |
|---|---|---|
| Chemical formulas and equations | `mhchem` (loaded by stemnotes) | `\ce{CH4 + 2 O2 -> CO2 + 2 H2O}`, `\ce{Cu^2+(aq)}` |
| Structural formulas | `\usepackage{chemfig}` | `\chemfig{H_3C-CH_2-OH}` |
| Electrical circuits | `\usepackage[european,siunitx]{circuitikz}` (or `american`, as the source draws) | `\draw (0,0) to[R, l=$R$] (2,0);` inside `circuitikz` |
| Commutative diagrams | `\usepackage{tikz-cd}` | `\begin{tikzcd} A \arrow[r,"f"] & B \end{tikzcd}` |
| Plots of a given function or data | `pgfplots` (loaded) | `\addplot[domain=0:5] {1-exp(-x)};` |
| Other drawings | `tikz` (loaded, with `arrows.meta`, `calc`, `positioning`, `decorations.markings`, `patterns`) | |
| Code | `listings` (loaded): `\begin{lstlisting}[language=Python]` | Python, C, C++, Java, Matlab, R, SQL, [LaTeX]TeX… |
| Code with Pygments colouring | `minted`: only if the user asks; needs Pygments and `-shell-escape`, which Overleaf allows but many setups do not | |
| Pseudo-code | `algorithm` + `algpseudocode` (loaded, keywords translated in French) | |

Check availability with `check_env.py` (it lists chemfig, circuitikz, tikz-cd, minted).

## Figure fidelity

A redrawn figure is a transcription like any other, and the easiest place to invent.

1. **Inventory first**: from the source, list every element: axes and their labels and units, tick values, curves and their labels, points and their coordinates, arrows, angles, components and their values and orientation, nodes, edges and their labels. Put the list in the transcript (`⟦FIG …⟧`) or as a comment above the figure code.
2. **Draw the inventory, nothing else**: no extra grid, tick, label, legend, colour coding or annotation. A curve drawn by hand in the source may be plotted from its formula only if the source gives the formula; otherwise reproduce the image.
3. **Unknown element → reproduce the image**: if any element cannot be read or its value is unknown, include the cropped source image instead (`\includegraphics`, caption saying it is reproduced from the source, `\src`), and list it under *not verified* if its content was not transcribed.
4. **Check**: render, compare with the source crop element by element, and record the result in the figures table of `work/verification.md` (redrawn or image; inventory matched: none missing, none added).
5. Orientation conventions (current direction, sign of angles, receiver/generator convention) are notation: if the source does not settle them, they are `\ambiguous` questions, not drawing choices.
