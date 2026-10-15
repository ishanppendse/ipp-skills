---
name: polish
description: Polish the user's LaTeX resume (any class or template — moderncv, Jake's/article, awesome-cv, custom) for ML / ML Engineer / Research roles against researched best practices — Google XYZ bullets, quantified ML metrics, strong action verbs, ATS-safe formatting, section order, research-vs-production tailoring — and make every bullet fill exactly one line, measured from the rendered PDF of their own document. Rewrites each bullet into XYZ form, splits bullets that carry two ideas, and writes the result to a new <name>_polished.tex, leaving the original untouched. Finds their .tex, sets up missing TeX tooling with permission, or starts from a bundled template if they have none. Use when the user wants to improve, critique, tighten, or tailor a resume, fix wrapping/overflow/page count, or start a resume.
---

# Resume Polish

The user's only step is installing the plugin. Everything else — finding their resume, setting
up TeX, measuring, editing, verifying — is this skill's job. Adapt to *their* document; never
assume a class, margin, font, or bullet macro.

`SKILL_DIR` below = the directory containing this file.
- `scripts/polish.py env [file.tex]` — tooling check, engine detection, missing packages.
- `scripts/polish.py measure file.tex` — compiles into `.polish_build/` beside the source and
  reports every bullet's rendered line count and fill, with per-context char budgets.
- `references/resume_best_practices.md` — researched ML resume guide (XYZ vs STAR, ML metrics,
  action verbs, ML content, formatting, common mistakes, section order, tailoring, sources).
- `references/latex_layout.md` — generic LaTeX layout pass + per-class notes.
- `assets/template.tex` — default template, used only when the user has no resume.

## What polish changes
1. **Content** — every bullet rewritten into Google XYZ form. Bullets carrying two ideas are
   split, and thin duplicates merged. Missing metrics are asked for, never invented. Verbs,
   tense, pronouns and JD keywords follow the guide.
2. **Fit** — every bullet exactly one line, filling it (no wrap, no orphan, no big trailing gap).
3. **Layout** — the LaTeX itself: page count, overfull boxes, spacing consistency, header
   hierarchy, dates, links, ATS-readable text. See `references/latex_layout.md`.

## 1. Find the resume
- Search the working directory (depth ≤3, skip `.polish_build/`, `node_modules/`, `.git/`) for
  `*.tex` containing `\documentclass`. Prefer files with resume signals (`moderncv`, `\cventry`,
  `\resumeItem`, `awesome-cv`, sections like Experience/Education).
- One candidate → use it, tell the user which. Several → AskUserQuestion. None → ask:
  - "Path to your .tex?" — use it.
  - They have a PDF/DOCX resume → extract its text (`pdftotext -layout`, or the docx skill),
    copy `assets/template.tex` to `./resume.tex`, and port their content into it.
  - No resume → copy `assets/template.tex` to `./resume.tex` and build it with them from scratch.

**Never modify the user's file.** All work happens on a new copy:
- Copy `<name>.tex` → `<name>_polished.tex` **in the same directory**, so relative `\input`,
  images, `.bib` and `.cls` files still resolve. If `<name>_polished.tex` already exists, ask
  whether to continue from it, overwrite it, or write `<name>_polished_2.tex`.
- Multi-file resumes: copy each local `\input`/`\include`/`\import` file you'll edit to
  `<file>_polished.tex`, and point the polished main at those copies. Shared files you don't
  edit (class, style, images) stay as they are.
- Measure, edit and build only the `_polished` copy from here on. The original is the
  baseline for the before/after report.
- Starting from the template is the exception: there is no original, so the new
  `./resume.tex` itself is the working file.

## 2. Set up tooling (ask before installing anything)
Run `python3 SKILL_DIR/scripts/polish.py env <file.tex>`. It reports OS, package manager,
`latexmk`/engines/`tlmgr`/`pdftotext`, the engine the file needs, and `MISSING_FILE x.sty` lines.

If something is missing, say what and why, propose the command, and get permission:
| Missing | macOS (brew) | Debian/Ubuntu | Fedora |
|---|---|---|---|
| TeX + latexmk | `brew install --cask basictex` (~100 MB), then `sudo tlmgr update --self && sudo tlmgr install latexmk`; full: `brew install --cask mactex-no-gui` (~5 GB) | `sudo apt-get install -y texlive-latex-extra texlive-fonts-extra latexmk` | `sudo dnf install -y texlive-scheme-medium latexmk` |
| `pdftotext` | `brew install poppler` | `sudo apt-get install -y poppler-utils` | `sudo dnf install -y poppler-utils` |
| a `.sty`/`.cls` | `tlmgr search --global --file /<name>` → `sudo tlmgr install <pkg>` | `apt-file search <name>` or install `texlive-latex-extra`/`texlive-fonts-extra` | `sudo dnf install 'tex(<name>)'` |

- Run non-sudo installs (e.g. `brew`) yourself once approved. `sudo` needs the user's password:
  ask them to run it as `! <command>` so it executes in-session.
- After BasicTeX, PATH may need `eval "$(/usr/libexec/path_helper)"` or a new shell.
- Re-run `env` until `COMPILE: ok`. If it still fails, read the first `! ` error in
  `.polish_build/<name>.log` and fix or report it — don't guess.

## 3. Baseline
1. Run `python3 SKILL_DIR/scripts/polish.py measure <name>_polished.tex`. Before any edits it
   is identical to the original, so this is the "before" snapshot.
2. Read `references/resume_best_practices.md` in full.
3. Read `references/latex_layout.md`, including the notes for the class in use.
4. Report the baseline to the user: page count, overfull boxes, the budgets, and the
   WRAPS/TIGHT/SHORT/OK counts.

## 4. Polish
Ask before any judgment call — metrics, dates, framing, what to cut — using AskUserQuestion,
batched. If the user says a number wasn't really achieved, remove it; don't soften it. Refill the
line with real descriptive detail.

**Content — XYZ rewrite, bullet by bullet.** For each bullet:
1. Label its parts: **X** (what was accomplished), **Y** (how it was measured: a number with a
   baseline or unit), **Z** (how: the method, model, or tools).
2. Fix the shape:
   - Duty phrasing ("Responsible for…", "Worked on…") → turn it into an accomplishment.
   - A list of tools → keep only the tools that explain the result.
   - Result buried at the end → lead with the verb and the result.
3. Fill the gaps:
   - **Y missing** → don't invent a number or quietly leave it vague. Collect every bullet with
     a missing Y and ask the user in one batched question ("What did this improve, and by how
     much? Latency, accuracy, cost, scale, users, time saved?"). Until they answer, keep the
     bullet with `% TODO metric` above it in the `.tex`.
   - **Z missing** → take the method or tools from the user's notes or the rest of the resume,
     or ask.
4. Rewrite as *Accomplished X, as measured by Y, by doing Z*. The order can flex to "Reduced Y
   by doing Z" when that reads better, but all three parts must be there.

**Content — split big bullets.** A bullet that carries **two or more separate results or
methods** (often joined by "and", ";", "while", "as well as"), or that wraps because it holds
two ideas, becomes **two bullets**. Each one is a full one-line XYZ bullet with its own result.
Splitting keeps content that cutting would throw away; trim only real filler. The reverse also
applies: two thin bullets about the same result merge into one strong one.

**Content — page check.** Splitting adds lines. If the page now overflows, don't silently drop
content. List the weakest bullets (no metric, least relevant to the target role, oldest) and
ask the user which to drop or merge.

**Content — checklist.** Before finalizing, check every version against these:
- [ ] One page (students / <~8 yrs exp).
- [ ] **Every bullet = exactly one line.** No wrap, no 2-word orphan line, no big end-of-line gap.
- [ ] Every bullet leads with a strong **action verb** and carries a **number**.
- [ ] XYZ formula: *Accomplished X, measured by Y, by doing Z.*
- [ ] Reverse-chronological in every section.
- [ ] **No personal pronouns** ("Led team of 8," not "I led…"). Phrases, not sentences.
- [ ] Consistent tense (past for past roles, present for current).
- [ ] Single column, **no tables/text-boxes/images/graphics** for content (ATS-breakers). Submit PDF.
- [ ] Skills section is keyword-rich and matches the job description's exact terms.

**Fit.** `measure` derives everything from the rendered PDF, so it holds for any template:
- `BUDGET A/B/…` — one per list context (line width × font size). Lists inside entries and lists
  directly under a section often differ in font size, so their char limits differ. Draft each
  bullet toward its own context's `target` range; chars are a first guess only.
- Per bullet:
  - `WRAPS` — the bullet runs to 2+ lines; the orphan text is shown. Fix these first:
    - Two ideas → **split** it (see Content).
    - One idea → tighten the wording and cut filler, keeping X, Y and Z.
  - `TIGHT` — gap below ~5pt. TeX squeezed the interword spaces to fit the line. Any edit can
    tip it into a wrap; trim a word if the spacing looks cramped.
  - `SHORT` — fill below 88%. Add a concrete metric, method, or scope; don't pad with filler.
  - `OK` — fills the line.
- Each edit → re-run `measure` (it recompiles). Width is the test. `Overfull \hbox` is not:
  a naturally wrapping bullet raises no warning.
- Short items whose shape is fixed (skills lists, awards) can stay SHORT. Tell the user rather
  than padding them.

**Layout.** Work through `references/latex_layout.md`. Edit the preamble or macros only when
needed, and match the file's existing style.

## 5. Verify and report
- Final `measure`: no WRAPS, page count at target, overfull boxes not increased.
- Render the page and look at it: `pdftoppm -png -r 110 .polish_build/<name>.pdf
  .polish_build/page`, then Read the PNG. Check for orphans, crowding, and misalignment.
- ATS check: run `pdftotext -layout .polish_build/<name>.pdf -` and confirm the text reads in
  order, with nothing garbled.
- Copy the final PDF to `<name>_polished.pdf` next to the source. `.polish_build/` is scratch
  output.
- Report:
  - The files written; the original is untouched.
  - What changed in each pass, before/after counts, and which bullets were split or merged.
  - The `% TODO metric` bullets still waiting on the user, and anything else left for them to
    decide.

## Tailoring to a job
For a pasted job description: copy the resume (the polished one, if it exists) to
`<name>_<company>.tex`. Nothing gets overwritten. Then reorder and reword toward the job description's exact terms, following §9 of
the guide. Never add skills or claims the master doesn't support.
