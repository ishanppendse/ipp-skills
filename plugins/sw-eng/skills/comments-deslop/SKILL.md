---
name: comments-deslop
description: Rewrite comments and docstrings in files changed on the current branch so they read as finished documentation, not a transcript of an AI session. Use when the user asks to clean, deslop, tighten, or review comments or docstrings, before opening or updating a PR, or after a long agentic session that touched many files. "Clean up before I push" is enough to trigger it.
---

# comments-deslop

Comments written mid-session narrate procedure, restate the code, and refer to the session itself ("added for PR #412", "now handles null"). A reader six months out needs the *why*, the invariant, the data shape — in as few lines as possible.

Target: every comment and docstring in scope looks like it was written once, by whoever understood the design best, for the codebase as it is now.

## 1. Scope

Default: every git-tracked file added or modified on this branch vs its base.

```bash
bash scripts/scope.sh            # base = develop > main > master, prefers origin/
bash scripts/scope.sh feature/x  # explicit base
```

- User names files or a directory → exactly that.
- "The PR" → same as default.
- "Whole repo" → `git ls-files`; confirm first.

Files outside scope with the same problems: flag in the report, don't edit.

## 2. Parallelism

If the scope has more than ~4 files and subagents are available, fan out. Subagents have none of this session's context, so ground them first:

1. Write `/tmp/comments-deslop-context.md` from the main session. Contents, in order:
   - one paragraph: what this branch does and why
   - the base branch and the `scope.sh` file list
   - the file's docstring convention if you've already seen one (Google / NumPy / bare)
   - anything domain-specific a reader would need (units, tensor layout, the paper this implements)
   - the rules in sections 3–4 of this file, verbatim or by path
2. Partition files across agents, roughly equal line counts. Keep a module's files together so voice stays consistent.
3. Each agent: read the context file, then read each assigned file in full, edit, and return a ≤4-line summary (files, deleted/rewritten/added counts, flags).
4. Main session: merge summaries into the report, then `rm /tmp/comments-deslop-context.md`.

No subagents → do the same sequentially.

## 3. What to fix

Read each file in full before editing it. Density and voice are file-level properties: a file with three comments in 400 lines and a file with a comment per function are both fine. Bring the changed comments to *that file's* norm, not a global ideal.

Then, for every comment and docstring:

**Delete** if it:
- restates the code (`# increment i`; `"""Get the user."""` on `get_user`)
- narrates the session: PR/issue numbers, "now", "updated", "previously", "as requested", "fix for"
- describes procedure the code already shows step by step
- is a section banner (`# ---- Helpers ----`) in a file that doesn't already use them
- is commented-out code, a debug print, or an agent TODO (`# TODO: add error handling`)
- restates a type annotation in prose (`x: int` + `"""x: an integer"""`)
- is a closing reassurance (`# This ensures correctness`, `# Safe because validated above`) with no content beyond the reassurance

**Rewrite** if it carries information but is bloated. Keep only:
- motivation: why this exists, why this way and not the obvious way
- invariants and preconditions the code can't express
- non-obvious shape, units, ordering, ownership, lifetime
- the thing that constrains this: paper, RFC, upstream quirk, benchmark result

**Keep** if it already does that in the file's voice.

**Add** only when a non-obvious decision has no explanation. Rare; this is a reduction pass.

## 4. Form

Every line should change what a reader believes.

- Notation over prose: `softmax(q·kᵀ/√d)·v`, `[B,T,H] → [B,H,T]`, `A -> B -> C`, `O(n log n)`.
- Comments ≤ 3–4 lines. Longer only for a subtle invariant, and then say why it's subtle.
- Docstring summary + rationale ≤ 5 lines, hard cap 10. Args/Returns/Raises 1–2 lines each, only where name and type don't already say it.
- No headers, bullets, or bold inside docstrings. No "This function…", "Note that…", "In order to…", "Helper function to…".
- No hedges: "basically", "simply", "just", "essentially", "should", "may or may not".
- No emoji, no exclamation marks.
- Present tense, describing the code as it is. Nothing about how it got there.
- Match the file's docstring style. Don't introduce one.

## 5. Examples

**Before**
```python
def compute_attention(q, k, v, mask=None):
    """
    Computes scaled dot-product attention.

    This function takes query, key, and value tensors and computes the
    attention output. First it computes the dot product of q and k,
    then scales by sqrt(d_k), then applies the optional mask, then
    applies softmax, and finally multiplies by v. Updated in this PR
    to support the mask argument.

    Args:
        q: The query tensor. This should be a tensor of shape
           (batch, heads, seq_len, d_k) containing the queries.
        k: The key tensor, same shape as q.
        v: The value tensor of shape (batch, heads, seq_len, d_v).
        mask: An optional mask tensor. If provided, positions where
              mask is False will be set to -inf before softmax.

    Returns:
        The attention output tensor.
    """
```

**After**
```python
def compute_attention(q, k, v, mask=None):
    """softmax(q·kᵀ/√d_k)·v; masked positions → -inf before softmax.

    √d_k keeps logits O(1) as d_k grows; without it softmax saturates.

    Args:
        q, k: [B, H, T, d_k]
        v:    [B, H, T, d_v]
        mask: [B, 1, T, T] bool, False = blocked
    Returns:
        [B, H, T, d_v]
    """
```

**Before**
```python
# Check if the cache entry is expired. We added this because we were
# seeing stale entries being served after the TTL changed in PR #388.
# If the entry's timestamp plus the TTL is less than now, we evict it.
if entry.ts + ttl < now:
```

**After**
```python
# TTL is read per call, not cached, so a runtime TTL change applies immediately.
if entry.ts + ttl < now:
```

**Before → delete**
```python
# Loop over the batches
for batch in batches:

# ---------- Utility functions ----------

# print(f"debug: {x}")
```

## 6. Process

1. `scripts/scope.sh`; show the file list before editing.
2. Per file: read whole file, edit comments and docstrings only. Never change code, imports, or whitespace outside comments. If a comment is wrong because the code is wrong, leave it and flag it.
3. Run the project's formatter/linter if configured.
4. Report ≤ 6 lines: files touched, deleted/rewritten/added counts, flags. No per-file narration.

## 7. Don't

- Don't strip license headers, shebangs, encoding declarations, lint directives (`# noqa`, `# type: ignore`, `eslint-disable`), `# fmt: off` blocks, or doctest examples.
- Don't touch comments inside string literals, test fixtures, or generated files.
- Don't lengthen a comment that was already good.
- Don't add docstrings for consistency. Absence is fine when the signature is the documentation.
