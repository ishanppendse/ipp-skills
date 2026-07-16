---
name: smart-diff
description: Produce a semantic, structure-aware diff between two versions of a source file. Use this skill whenever the user asks to compare two files, review what changed between file versions, diff code, understand a refactor, or complains that a normal diff is unreadable. Trigger on phrases like "smart diff", "compare these two files", "what changed between", "diff this against", "review this refactor", or any request to explain differences between two versions of code. Unlike plain line diff, this skill matches functions across renames and moves, so a renamed or relocated function shows as one modified section instead of a giant delete+add.
---

# Smart Diff

Plain `diff` compares files line-by-line in order. It has three classic failure modes:

1. **Renamed function** → shows as full delete + full add, hiding that only the name changed.
2. **Moved function** (top of file → bottom) → never compared against its old self; diff is garbage.
3. **Interleaved changes** → hunks span unrelated functions, so the reader can't tell which logical unit changed.

Smart diff fixes this by matching *entities* (functions, classes, methods, module-level code) across the two files first, then diffing only within matched pairs. Every line of both files is accounted for — nothing is silently skipped.

## Workflow

### Step 1: Run the matcher

```bash
python <skill-path>/scripts/smart_diff.py OLD_FILE NEW_FILE --json /tmp/smartdiff.json
```

The script:
- Extracts entities (Python via `ast`; JS/TS/Go/Rust/Java/C-like via declaration + brace heuristics; unknown languages fall back to one module-level section).
- Matches entities: first by exact name+kind (survives moves), then by normalized body similarity (detects renames; default threshold 0.55, tune with `--min-similarity`).
- Classifies each pair: `identical`, `moved`, `renamed`, `modified`, `renamed_modified`, `added`, `deleted`. Also flags `signature_changed` and `position_delta`.
- Pairs module-level code (imports, constants, top-level statements) as its own section.
- Emits a unified `pair_diff` for every non-identical match.

Read the JSON. If the language is exotic and the script fell back to a single module section, do the entity matching yourself by reading both files.

### Step 2: Sanity-check the matching

Before writing the report, scan the JSON for suspicious results:
- A `deleted` + `added` pair with similar signatures or purpose → the similarity threshold probably missed a heavy rewrite-rename. Merge them into one `renamed_modified` section manually in your report and say so.
- A `renamed` match that looks wrong (two unrelated functions paired) → split them back into deleted/added.

You are the second-pass matcher; the script is only the first pass.

### Step 3: Write the report

The report is ONE annotated diff. Code-centric: the diff IS the report, commentary lives inside it as annotation lines. No prose paragraphs, no tables, no emoji, no markdown headers around each entity.

Output a single fenced ```diff block using this exact grammar:

```diff
==== ENTITY_NAME  [status flags]           <- section header per entity
      unchanged context line                # (B, S, D)  <- shape annotation, only when relevant
-     removed line
+     added line
#? annotation: what changed / why it matters, one line each
#? shapes explicitly when they change: (B, S, D) -> (B*S, D)

==== old_name -> new_name  [renamed, moved down, body identical]
#? pure rename. callers break.

==== unchanged: foo, bar (moved), baz     <- single trailing line, no code
```

Grammar rules:
- `====` prefix = entity section header. Format: `==== name  [status]`. Status flags in plain words: `modified`, `renamed`, `moved up/down`, `sig changed`, `added`, `deleted`, `body identical` — combine as needed.
- `-` / `+` prefixed lines = the actual pair_diff hunks (these render red/green). Trim to hunks that matter; keep 1-3 context lines around each hunk.
- `#?` prefixed lines = your commentary. Placed directly under the hunk they explain, plus optionally 1-2 at section end for overall verdict. Terse fragments, not sentences.
- Inline trailing comments (`# (B, S, H, d)`) on code lines: shape annotations for Python/tensor code. ONLY when shapes are relevant to the change — do not annotate shapes on code where nothing shape-related happened.
- Entities that are `identical` or purely `moved`: collapse into ONE final `==== unchanged:` line listing names. Never dump their code.
- For `added`/`deleted` entities: show the code as all-`+`/all-`-` if short (<20 lines); if long, show signature + key lines with `...` elision, plus `#?` gist.
- First line of the whole report: `==== SUMMARY  old.py -> new.py` followed by 1-3 `#?` lines: refactor vs behavior change, the one thing a reviewer must check.

Content rules for `#?` annotations:
- Semantic, not mechanical — the red/green already shows the mechanics. Say WHY: rename-for-clarity vs semantics changed; bug fix vs refactor; O(n^2) -> O(n log n); dropped error handling; changed default; caller breakage.
- Shapes: whenever Python/tensor code changes shape behavior, state old -> new explicitly: `(B, S, D) -> (B*S, D)`.
- Order sections by new-file position; deleted entities after; unchanged line last.
- Never omit a changed entity. Every non-identical section in the JSON must appear.

### Step 4: Deliver

In Claude Code / terminal contexts, print the report directly or write it to a file if the user asks. In Claude.ai, save as a `.md` file and present it when the report is long.

## Notes

- Two directories instead of two files: run the script per file pair (match files by name), and add a top-level file-rename check (a deleted file and an added file with similar content = renamed file). Roll per-file summaries into one master summary.
- Git refs instead of files: `git show REF:path > /tmp/old.py` first, then run normally.
- The script's similarity matching is O(deleted × added) per file — fine for normal files, slow only if hundreds of unmatched entities. If that happens, raise `--min-similarity`.
