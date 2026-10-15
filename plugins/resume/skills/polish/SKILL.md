---
name: polish
description: Polish a one-page LaTeX (moderncv banking) resume for ML / ML Engineer / Research roles against researched best practices — Google XYZ bullets, quantified ML metrics (accuracy/latency/throughput/scale/$), strong action verbs, ATS-safe single-column formatting, reverse-chronological section order, and research-vs-production tailoring. Use when the user wants to write, critique, or tighten resume bullets, tailor a version to a job description, fix wrapping/overflow/page-count issues, or set up a versioned resume repo. Every bullet must fit exactly one line, verified by rendered width, not character count.
---

# Resume Polish (moderncv, ML roles)

Goal: tight, quantified, ATS-friendly one-page resume. **One line per bullet, no awkward
end-of-line whitespace, margins respected.**

## Files in this skill
- `assets/template.tex` — moderncv `banking`/`grey`, 10pt, A4, tuned margins + name-gap patch. Placeholder content.
- `scripts/build.sh` — `./build.sh path/to/main.tex` → `latexmk -pdf`.
- `scripts/probe.sh` — measures rendered bullet widths (see LINE-WIDTH BUDGET).
- `references/resume_best_practices.md` — researched ML resume guide: XYZ vs STAR, quantifying ML
  impact, action verbs, ML-specific content (skills, end-to-end ownership, publications), formatting,
  common ML-candidate mistakes, section ordering, research vs production tailoring, sources.
  **Read it in full before writing or critiquing any bullet** (Workflow step 1).

Requires a TeX install with `latexmk` + `pdflatex` and the `moderncv` package (TeX Live / MacTeX).

## Recommended repo layout
```
resume/
├── CLAUDE.md              # owner-specific notes (name, roles, honesty constraints)
├── superset.tex           # MASTER pool — every entry/bullet ever; never trimmed
├── PROJECTS.md            # deep, detailed account of each project — bullets are distilled from it
├── build.sh
└── versions/<tag>/        # one self-contained folder per tailored version (main.tex + assets)
```
- **Superset convention:** add any new project/bullet to `superset.tex` first, then pull a subset
  into the active version. Nothing is ever lost when a version is trimmed.
- **Versioning:** new version = copy latest `versions/<tag>/` to a new date/company tag, then edit.
- Post-graduation versions drop Coursework and student-only entries (e.g. Teaching Assistant).

## Non-negotiables (check every version against these)
- [ ] One page (students / <~8 yrs exp).
- [ ] **Every bullet = exactly one line.** No wrap, no 2-word orphan line, no big end-of-line gap.
- [ ] Every bullet leads with a strong **action verb** and carries a **number**.
- [ ] XYZ formula: *Accomplished X, measured by Y, by doing Z.*
- [ ] Reverse-chronological in every section.
- [ ] **No personal pronouns** ("Led team of 8," not "I led…"). Phrases, not sentences.
- [ ] Consistent tense (past for past roles, present for current).
- [ ] Single column, **no tables/text-boxes/images/graphics** (ATS-breakers). Submit PDF.
- [ ] Skills section is keyword-rich and matches the job description's exact terms.

## Workflow
1. Read `references/resume_best_practices.md` in full. Apply it, not just the checklist above.
2. Gather facts: read `PROJECTS.md`/source notes; ask the owner about anything ambiguous —
   metrics, dates, framing — **before** editing (use AskUserQuestion for judgment calls).
3. Draft bullets in XYZ form: *Accomplished X, measured by Y, by doing Z*. Strong past-tense
   verb (present for current role), a number in nearly every bullet, no pronouns.
4. Width-probe every new/edited bullet (`scripts/probe.sh`). Adjust until each lands in the band.
5. Build, then check `pdfinfo main.pdf | grep Pages` = 1 and no `Overfull \hbox` in the log.
6. Render to PNG (`pdftoppm -png -r 110 main.pdf out`) and eyeball spacing/orphans; re-run the
   non-negotiables checklist.

**Honesty rule:** if the owner says a number wasn't actually achieved, remove it — don't soften
it. Refill the freed width with real descriptive detail.

## cventry header — bold vs italic
`\cventry{dates}{B}{C}{city}{}{body}` in moderncv **banking** renders:
- **C (3rd arg) = BOLD top line** (city on right) — the headline.
- **B (2nd arg) = italic line below** (dates on right) — the subtitle.

Put the highest-signal identifier in C:
- **Brand present** (company, lab, known advisor): `C = Role, Brand`; `B = project topic`.
- **No brand** (personal/course project): `C = project title`; `B = "Personal Project"` /
  `"Course Project, <course>, <school>"`.

## LINE-WIDTH BUDGET — the optimization target
Margins `left=right=1.6cm, top=bottom=0.8cm` → itemize text width **496.46pt** in both contexts:
- **cventry bullets** (Experience/Projects) render in `\small` → ~123 char ceiling.
- **section-level bullets** (Skills, Achievements — itemize directly under `\section`) render in
  `\normalsize` → wider glyphs, wrap at FEWER chars. Probe these in `section` mode or you'll
  under-estimate and get a stray word on a second line.

| | chars (avg prose, `\small`) | notes |
|---|---|---|
| Hard ceiling | ~123 | beyond → wraps, 2–3 word orphan |
| **Sweet spot** | **115–120** | fills line, small gap |
| Too short | < ~100 | wasted line — add a metric/method |

Character mix matters (digits, i/l/t pack tight; m/w wide), so **char count is only a first
guess. Width is the rule.**

### Verifying a bullet fits one line
`grep "Overfull \hbox"` is **NOT** a wrap test — a bullet that wraps naturally produces zero
overfull warnings. Measure rendered width:
```bash
# bullets.txt: one LaTeX-escaped bullet per line (\%, \&, $\times$, etc.)
scripts/probe.sh bullets.txt            # Experience/Projects bullets
scripts/probe.sh skills.txt section     # Skills/Achievements lines
```
Output per line: width, gap to 496.46pt, status. **WRAPS** (>496.46pt) → cut. **RISKY**
(<5pt gap; font rounding can tip it) → trim a word. **OK** → target 15–25pt gap. **SHORT**
(>60pt gap) → add concrete detail.

If you change margins/font size, the 496.46pt constant in `probe.sh` must change too — measure
`\linewidth` inside the itemize with `\typeout{\the\linewidth}`.

## Vertical spacing knobs
- Section gaps: `\vspace{1mm}` before each `\section` (avoid stacking negative vspaces — headers hug the section above).
- Inter-entry gaps: `\vspace{3pt}` between `\cventry` blocks.
- Name ↔ contact gap: moderncv hardcodes a bare `\\` in `\makehead`; the template patches it:
  ```latex
  \usepackage{etoolbox}
  \makeatletter
  \patchcmd{\makehead}{\\\addressfont}{\\[4pt]\addressfont}{}{}
  \makeatother
  ```
  `\patchcmd` search args must be brace-balanced (can't match across a `{`).

## Gotchas
- **Don't** `\usepackage{hyperref}` — moderncv already loads it → "Option clash" fatal error.
  Use `\PassOptionsToPackage` / `\hypersetup` if needed.
- Layout is space-constrained both ways: one long Skills line wrapping can push the last line to
  page 2; adding >~1 line of vertical space can too. **Re-check page count after every edit.**
