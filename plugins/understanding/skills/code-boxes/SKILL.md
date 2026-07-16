---
name: code-boxes
description: "Explain a code file or module as an interactive flowchart of collapsible black boxes, each showing inputs (with shapes/types), outputs, and the core operations or equations inside — instead of line-by-line prose. Use this skill whenever the user wants to understand, study, or get an overview of nontrivial code (especially ML modeling files, but any code — algorithms, networking, data pipelines), or says things like 'explain this file', 'help me understand this code', 'what does this module do', 'break down this modeling file', 'code boxes', or 'make a diagram of this code'. Prefer this over prose walkthroughs for any file longer than ~100 lines."
---

# Code Boxes

Line-by-line code reading doesn't scale. Any code can be represented as a directed graph of black boxes: each box has inputs (name, shape/type, meaning), outputs, and the core operation inside (1-3 equations or bullets). Understanding = reading boxes at the right depth, unfolding only where needed.

The deliverable is a single self-contained HTML file: an interactive nested flowchart. Boxes collapse/expand on click; children render inside their parent as a layered DAG with edges (residual/skip connections included). No dependencies, works offline.

Token-efficiency rule: you only write a JSON tree. Never handwrite HTML — the bundled template + script do all rendering.

## Workflow

### Step 1: Scope the code

- Identify the entry file(s) the user cares about.
- Follow **repo-internal imports**: if the file imports from elsewhere in the same repo (utils, submodules), read those files too and box their relevant functions as part of the graph. Resolve imports by path; grep for the definitions.
- **External libraries** (torch, numpy, stdlib, pip packages) are always leaves — never expand into their source. `nn.Linear` is a box with in/out shapes and `y = xW^T + b`, nothing more.

### Step 2: Build the box tree

Write a JSON file matching this schema (full reference in `scripts/build_viewer.py` docstring):

```json
{
  "title": "LlamaDecoderLayer",
  "subtitle": "modeling_llama.py",
  "repo_root": "/abs/path/to/repo",
  "root": {
    "id": "decoder_layer",
    "name": "LlamaDecoderLayer",
    "one_liner": "one transformer block: attn + MLP, pre-norm, residual",
    "inputs":  [{"name": "hidden_states", "shape": "(B, S, D)", "meaning": "token embeddings"}],
    "outputs": [{"name": "hidden_states", "shape": "(B, S, D)", "meaning": "updated embeddings"}],
    "ops": ["h = h + Attn(RMSNorm(h))", "h = h + MLP(RMSNorm(h))"],
    "source": "modeling_llama.py:L305-360",
    "paper": null,
    "children": {
      "nodes": [ "...same node schema, recursively..." ],
      "edges": [
        {"from": "input_norm", "to": "attn", "label": "(B, S, D)"},
        {"from": "attn", "to": "residual_1", "label": null}
      ]
    }
  }
}
```

Rules for building the tree:

- **Leaf rule**: a box is a leaf when its ops fit in ≤3 equations/bullets AND it makes no repo-internal calls. External lib calls are always leaves. When in doubt, make it a leaf with good ops — depth can mislead more than it helps.
- **Ops are the payload**: ≤3 lines per box. Prefer a math equation (`attn = softmax(qk^T/√d_h)·v`) over words. If no natural equation, terse bullets: the invariant, the recurrence, the complexity. Never paragraphs.
- **Shapes/types adapt to domain**:
  - Tensor code: symbolic shapes always — `(B, S, H_kv, d_h)`. Define symbols once in the root's one_liner or ops if not obvious. Symbols, not numbers.
  - General code: types + key invariants — `heap: list[(dist, node)]`, `graph: adj list (V, E)`. Add complexity to ops where meaningful: `O((V+E) log V)`.
- **Edges = dataflow between sibling boxes**, labeled with the variable/shape flowing. Include residual and skip connections — they're just edges (the layout handles non-sequential graphs). Edges only connect direct siblings within the same parent; the injector validates this.
- **ids** must be unique across the whole tree (prefix by parent, e.g. `attn.rope`).
- **source**: `path:Lstart-Lend` so the user can jump to code. See the clickable-links rule below for how `path` and `repo_root` combine.
- **paper**: link when the box implements a known technique (RoPE, GQA, flash attention). Optional.
- Generate the FULL tree in one pass — expansion is client-side, no regeneration on click.
- Every meaningful piece of the file should land in some box. Trivial glue (arg parsing, logging) can be one shallow box or noted in a parent's ops; don't silently drop real logic.

### Clickable source links (when working inside a real codebase)

If you are running this skill **inside an actual repo on the user's machine** (not just explaining a pasted snippet), make every box's `source` a link that opens the exact file+line in the user's local VS Code. This lets them jump from any box straight to the code.

To enable it:

1. Set the top-level **`repo_root`** field to the **absolute** path of the repo on this machine (e.g. run `pwd` / `git rev-parse --show-toplevel`). Example: `/Users/alice/code/transformers`.
2. Make each node's **`source`** a **repo-root-relative** path plus line range: `src/models/llama/modeling_llama.py:L305-360`. Not a bare basename, not an absolute path — relative to `repo_root`.

The viewer then renders each `source` as a link to:

```
vscode://file/<repo_root>/<source-path>:<start-line>:1
```

Clicking it opens that file at that line in the user's local VS Code (the `vscode://file/...` URI scheme; VS Code registers it as its handler). The start line is parsed from `Lstart` (the `-Lend` and any `L` prefix are ignored for the jump target).

When to **omit `repo_root`**: pasted snippets, remote/hypothetical code, or any case where no local file exists (like a generic explanation). With no `repo_root`, `source` renders as plain text — same as before, links off. Never guess an absolute path; only set `repo_root` when you actually know the real on-disk location.

Note: `vscode://` links require VS Code installed and its URI handler registered (default on install). Cursor uses `cursor://file/...`; if the user is in Cursor and asks, swap the scheme in the template's `vscodeUri` helper.

### Step 3: Render

```bash
python <skill-path>/scripts/build_viewer.py boxes.json output.html
```

The script validates ids and edge endpoints, injects the JSON into `assets/viewer_template.html`, and writes a standalone HTML file. If validation fails, fix the JSON — do not edit the template.

### Step 4: Deliver

Present the HTML file. Default state: root expanded one level, everything deeper collapsed. Tell the user in one line what the top-level flow is; no prose summary beyond that — the boxes are the explanation.

## Notes

- Model/token cost: this skill is token-lean by design (JSON only). The hard part is semantic extraction — shapes, meanings, the right equations. For unfamiliar or subtle code, a stronger model produces noticeably better boxes; for routine files a smaller model is fine.
- Multiple files / whole subsystem: one root box per subsystem with files as first-level children, or ask the user which entry point matters.
- If the user asks for a specific depth ("just the top-level flow"), still build the full tree — the viewer's collapse-all handles presentation.
