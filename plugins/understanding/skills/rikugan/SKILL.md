---
name: rikugan
description: Produce an annotated, traced copy of source code so a reader can understand it fast without getting lost in tensor reshapes, transposes, and plumbing. Use this skill whenever the user points at a file, function, or entry script and wants to understand it, read through it, "walk through" it, learn how it works, onboard onto it, or asks "what does this code actually do" — even if they don't say "annotate" or "trace". Also trigger when the user says things like "explain this repo", "help me read this", "I'm lost in this file", "comment this code for me", or names a file and asks what it does. Also trigger on "rikugan" or "six eyes". Named for Gojo's Rikugan (Six Eyes) in Jujutsu Kaisen: eyes that see straight through to the underlying structure and spend zero effort on everything that doesn't matter — which is exactly what this skill does to code, surfacing the principle of each block and tracing one concrete input, while calling plumbing plumbing. It resolves the file's repo-local imports, confirms scope with the user, then writes a sibling copy of each file with a 1–3 line principle-level comment above every block and a one-sentence trace of a concrete anchor input beside every line.
---

# rikugan

## The philosophy this skill encodes

Any piece of code is a handful of simple principles, executed block by block. The
principles are the point; the reshapes, transposes, concats, indexing gymnastics
and boilerplate are the details. Self-attention is one equation, but fifteen lines
of code. A reader who wants to understand the code should get the equation first,
then see how each line moves a concrete example toward it.

So the output is not a summary and not a rewrite. It is the original code, verbatim,
with two layers of explanation woven in:

1. **Block comments** — above every block, at most 3 lines, stating what the block
   *does* in the language of a person who already understands the domain. Equations,
   arrows, state transitions. Never a paraphrase of the code.
2. **Line traces** — beside every line, one sentence tracing a single concrete
   *anchor input* through that line. Shapes, values, state.

The 3-line cap is a forcing function: if a block cannot be explained in 3 lines, it
is two blocks. Split it rather than bloat the comment.

## Workflow

### 1. Resolve scope

Start from the file(s) the user pointed at. Follow its imports, but only the ones
that resolve inside the current repo. Skip anything from site-packages, the standard
library, or vendored third-party code — the user wants to understand *their* code,
not PyTorch.

Follow imports transitively by default, but stop at files that are obviously
utilities the reader already understands (logging setup, argparse config, constants).
Use judgment; the confirmation step is where the user corrects you.

Before writing anything, show the user the planned file list and ask if it looks
right. Something like:

```
Planning to trace these 4 files (repo-local imports of train.py):
  train.py            (entry)
  models/attention.py
  models/block.py
  data/tokenize.py
Skipping: utils/logging.py (setup only), everything under torch/.
Sound good, or should I add/drop any?
```

Wait for the answer. Do not proceed on an unconfirmed scope — tracing the wrong
set of files wastes the user's time and yours.

### 2. Gather context

Read every file in scope before annotating any of them. Blocks in one file are often
only explainable in terms of what a sibling file does.

For files too large to read in one call, read them in successive chunks (offset +
limit) until you have the whole thing. Never annotate a file you have only partly
read — a trace written from the first 500 lines will invent the meaning of the rest.

Also pull in anything that already explains this repo: earlier turns in this
session, memory files about the repo, `CLAUDE.md`, READMEs, docstrings, design
docs. If a previous trace of a sibling file exists, reuse its anchor input so the
traces line up across files.

### 3. Pick the anchor input

Choose one concrete input that exercises the main path. For ML code this is explicit
tensor shapes; for a CLI, one example invocation; for a parser, one short input string.

**Prefer the real thing over a toy.** If the repo, config, docstrings, or the session
already pin down actual values — Qwen's `head_dim=128`, `n_heads=32`, a real
`max_seq_len`, a real batch size from the training script — use those. A reader
learning *this* codebase needs the numbers this codebase actually runs with; inventing
`d=8` throws away real information and hides which dimensions are large, which are
small, and where the memory actually goes.

Invent small numbers only when reality is genuinely unspecified or genuinely
irrelevant (a shape-agnostic utility, a generic example), and even then keep them
plausible. Use judgment: the anchor should be checkable, but correct beats cute.
`B=2` with real `d=128` is often the right compromise — shrink the axes that are
arbitrary, keep the ones the architecture fixes.

Declare it in a comment at the very top of each traced file, before the imports.
Every line trace in that file refers to this anchor.

### 4. Dispatch one agent per file

The main session does the thinking; the agents do the typing. Everything above —
scope, cross-file context, the anchor — is decided **once, in the main session**, and
handed down. Agents must not re-derive the anchor or re-explore the repo; divergent
anchors across files is the failure mode this ordering exists to prevent.

Spawn the agents **in parallel, one per file** (all Agent calls in a single message).
Each writes a different output file, so they never collide — no worktree isolation
needed.

Give each agent a briefing that makes re-exploration unnecessary:

- **Its file**: absolute path in, absolute path out (`<name>.traced.<ext>`).
- **The anchor**, verbatim, exactly as it will appear in the header comment.
- **What this file does** in the system, in two or three sentences — from the reading
  you already did.
- **Sibling context**: what the functions it imports actually do, and what shape or
  value they hand back, so the agent never has to open those files.
- **The rules below**, in full. The agent has not read this skill.

Require a short receipt back — output path, number of blocks commented, and anything
it could not explain — not the file contents. Prose from ten agents will bury the
main session in exactly the context this design is meant to save.

If an agent dies, respawn it for that one file. The others are unaffected.

### 5. How each agent writes its file

The output goes next to the original as `<name>.traced.<ext>` (or, if the user
prefers, mirrored under a `traced/` directory). Same language, same extension, so it
stays a valid, runnable source file, commented in that language's own syntax.

**Copy first, annotate in place.** The agent's first action is to copy the original
to the output path:

```bash
cp path/to/model.py path/to/model.traced.py
```

Then it edits *that copy*, block by block, replacing each block's verbatim lines with
the same lines plus comments. Never regenerate the file from scratch and never
retype the code: a copy that is only ever edited additively is verbatim by
construction, which is the strongest rule this skill has. Retyping a 2000-line file
silently drops lines.

**Work in chunks — always, but especially past ~1000 lines.** Read a slice of the
file (200–400 lines), annotate every block in that slice, then move to the next
slice. Track position by line offset, remembering that every comment line added
pushes the remaining code to higher line numbers — re-read around the boundary rather
than trusting stale line numbers. One chunk fully finished beats three chunks half
done; the file on disk is valid and partially traced at every point in between, so
an agent that dies mid-file leaves resumable work rather than garbage.

Because the copy already exists on disk, an interrupted agent resumes by finding the
first un-annotated block, not by starting over.

Rules for the copy:

- **Code is verbatim.** Do not reorder, rename, reformat, or "clean up". A reader
  should be able to diff the traced file against the original and see only added
  comment lines and trailing comments.
- **Block comment above every block, ≤3 lines.** A block is a coherent unit: a
  function, a loop body, a `with` block, a group of lines that together compute one
  thing. State the principle, not the mechanics. Use equations, `->` arrows for
  state transitions, and shape notation.
- **If it needs more than 3 lines, it's two blocks.** Split and comment each.
- **Line trace beside every line, one sentence.** Trace the anchor: what shape or
  value or state comes out of this line. For tensor code this is almost always a
  shape annotation plus what the dimensions mean.
- **Conditionals:** trace the branch the anchor takes. Note the other branch in one
  short clause (`# anchor: training=True -> takes this branch; eval path skips dropout`).
  Don't fork the whole trace.
- **Loops:** trace one iteration with the anchor, and state how many iterations and
  what accumulates.
- **Skip the trivial honestly.** `import torch` gets no trace. A line that is pure
  plumbing gets a trace that says so (`# plumbing`) rather than an invented insight.
- **Write like someone who already understands the domain.** No "this line calls
  the reshape method". Say what the reshape *is for*.

### 6. Deliver

Collect the agents' receipts and list the files written. Offer to go deeper on any block the user asks about — the
traced file is a map, not the territory.

## Example

Original:

```python
def forward(self, x):
    B, T, C = x.shape
    qkv = self.qkv(x)
    q, k, v = qkv.split(C, dim=2)
    q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
    k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
    v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
    att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
    att = att.masked_fill(self.mask[:, :, :T, :T] == 0, float('-inf'))
    att = F.softmax(att, dim=-1)
    y = att @ v
    y = y.transpose(1, 2).contiguous().view(B, T, C)
    return self.proj(y)
```

Traced:

```python
# ANCHOR: x is (B=2, T=4, C=8), n_head=2, so head dim d=4. Causal mask, training mode.

def forward(self, x):
    B, T, C = x.shape                                   # B=2, T=4, C=8

    # Project x to Q, K, V in one matmul, then split heads:
    #   (B,T,C) -> (B,T,3C) -> 3 x (B,T,C) -> 3 x (B,H,T,d)
    qkv = self.qkv(x)                                   # (2,4,24)
    q, k, v = qkv.split(C, dim=2)                       # each (2,4,8)
    q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)   # (2,2,4,4): heads become a batch dim
    k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)   # (2,2,4,4)
    v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)   # (2,2,4,4)

    # Scaled dot-product attention with causal mask:
    #   att = softmax( QK^T / sqrt(d) + mask ),  shape (B,H,T,T)
    att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))    # (2,2,4,4) scores, /sqrt(4)=0.5
    att = att.masked_fill(self.mask[:, :, :T, :T] == 0, float('-inf'))  # upper triangle -> -inf, so softmax gives 0
    att = F.softmax(att, dim=-1)                                        # each row sums to 1 over the past T positions

    # Weighted sum of values, merge heads back, output projection:
    #   (B,H,T,T) @ (B,H,T,d) -> (B,H,T,d) -> (B,T,C) -> proj -> (B,T,C)
    y = att @ v                                          # (2,2,4,4)
    y = y.transpose(1, 2).contiguous().view(B, T, C)     # (2,4,8): heads concatenated back into C
    return self.proj(y)                                  # (2,4,8)
```

Note what the block comments do: three blocks, three equations. The line traces
carry the shapes. Nobody had to read fifteen lines to find the one idea.

## What this skill is not

- Not a summary. The user gets the full code back.
- Not a refactor. Zero code changes.
- Not a tutorial. The block comments assume the reader knows the domain; they
  explain *this code's* use of it.
