# LaTeX layout pass

Work through the generic checks for any resume, then the notes for the class in use. Change the
fewest lines possible and match the file's existing macros. Don't restyle a template the user
chose. After any spacing or preamble change, re-run `polish.py measure` and recheck the page count.

## Generic checks (any class)
- **Page count.** One page for students / <~8 yrs experience. Over by a few lines → first shorten
  WRAPS bullets, then cut the weakest bullet, then trim spacing. Shrinking the font or margins
  is the last resort, and only with the user's OK.
  - Floors: body text ≥10pt, margins ≥~0.5in (1.27cm).
- **Overfull `\hbox`.** Each one in the log is something sticking into the margin, often a long
  URL or unbreakable token. Fix every new one.
- **Vertical rhythm.** The gaps between entries should be equal, and so should the gaps before
  sections.
  - Look for stacked `\vspace{-..}` (two negatives in a row), which makes a header hug the
    content above it.
  - Look for one-off spacing that differs from the rest.
  - Prefer one named length or macro over scattered literal values.
- **Header hierarchy.** Every entry should give organization, role, dates and location the same
  weight (bold/italic) and the same position.
  - Lead with the highest-signal name: a known brand if there is one, otherwise the project title.
  - Don't let a generic label like "Personal Project" sit in the bold slot.
- **Dates.** One format throughout (`MM/YYYY`, or `Mon YYYY`).
  - Use an en dash for ranges (`--` in LaTeX).
  - "Present" for current roles.
- **Links.** Use `\href` with readable text. Check that every link resolves (open the PDF, or
  `pdftotext` the URL).
  - If the class already loads `hyperref`, don't load it again: that causes an option clash.
    Pass options with `\hypersetup`.
- **Special characters.** `%`, `&`, `#`, `_`, `$` must be escaped.
  - Use `$\times$` for ×, `$\sim$` for ~, `--` for ranges.
  - Check the `pdftotext -layout` output: anything garbled there is garbled for ATS too.
- **ATS readability.** Content stays in a single column.
  - No tables or minipages holding *body content*. Two-column headers for dates are fine when
    the extracted text still reads in order.
  - No text inside images, and no icon-only contact info: the text must be there too.
- **Dead code.** Leave the user's commented-out blocks alone; they're often a personal archive.

## moderncv (`\documentclass{moderncv}`, styles casual/classic/banking/oldstyle/fancy)
- `\cventry{dates}{B}{C}{city}{grade}{body}`. In **banking**, C (3rd arg) renders **bold on
  the top line** and B (2nd arg) renders *italic below*. Other styles put arg 2 (title) in
  bold. Check the rendered page before deciding which slot gets the brand.
- Bullets inside a `\cventry` body render in `\small`; an itemize directly under `\section`
  renders in `\normalsize`. That's why `measure` reports two budgets.
- moderncv loads `hyperref` itself, so a second `\usepackage{hyperref}` is a fatal option clash.
- The name-to-contact gap is a bare `\\` hardcoded in `\makehead` (banking/moderncvheadiii).
  Widen it from the preamble:
  ```latex
  \usepackage{etoolbox}
  \makeatletter
  \patchcmd{\makehead}{\\\addressfont}{\\[4pt]\addressfont}{}{}
  \makeatother
  ```
  `\patchcmd`'s search text must be brace-balanced. It can't match across a `{`.
- Entry spacing: a `\vspace{..pt}` between `\cventry` blocks. Section spacing: `\vspace` before
  `\section`.

## Jake's resume / article-based (`\resumeSubheading`, `\resumeItem`, `\resumeItemListStart`)
- Bullets come from `\resumeItem{...}` (usually `\item\small{...}`). Edit the text inside the
  braces.
- Spacing lives in the macro definitions as negative `\vspace`s. Change it there once, not per
  entry.
- Subheadings use `tabular*` for the right-aligned dates. Keep the content inside the cells
  short, or the line overflows.
- Usually loads `hyperref` itself, plus `\pagestyle{fancy}` with emptied headers.

## awesome-cv (`\documentclass{awesome-cv}`)
- Needs **xelatex** (fontspec); `polish.py` detects this. Missing fonts show up as fontspec
  errors in the log.
- `\cventry{position}{organization}{location}{date}{\begin{cvitems}\item ...\end{cvitems}}`.
- Section content is often split into `\input{}`/`\import{}` files. Edit those files, and
  measure the main file.

## Anything else
Find where the bullets come from (`\item`, a custom macro, an `enumitem` list) and where spacing
is set. Follow the existing pattern. `measure` reads the PDF, so it works whatever the macros are.
