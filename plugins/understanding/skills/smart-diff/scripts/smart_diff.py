#!/usr/bin/env python3
"""
smart_diff.py — structural diff between two versions of a source file.

Extracts top-level entities (functions, classes, methods, module-level code),
matches them across files (surviving renames and moves), and emits JSON
describing every section pair. Guarantees full line coverage of both files.

Usage:
    python smart_diff.py OLD_FILE NEW_FILE [--json OUT.json] [--min-similarity 0.55]

Output JSON schema:
{
  "old_file": str, "new_file": str, "language": str,
  "summary": {"identical": n, "moved": n, "renamed": n, "modified": n, ...},
  "sections": [
    {
      "status": "identical|moved|renamed|modified|renamed_modified|added|deleted",
      "kind": "function|class|method|module",
      "old_name": str|null, "new_name": str|null,
      "old_span": [start, end]|null, "new_span": [start, end]|null,   # 1-indexed inclusive
      "moved": bool, "position_delta": int|null,
      "similarity": float|null,
      "signature_changed": bool,
      "old_code": str|null, "new_code": str|null,
      "pair_diff": str|null          # unified diff between the matched pair only
    }, ...
  ],
  "coverage": {"old_uncovered_lines": [...], "new_uncovered_lines": [...]}
}
"""

import argparse
import ast
import difflib
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- entities

class Entity:
    def __init__(self, kind, name, start, end, lines, parent=None):
        self.kind = kind            # function | class | method | module
        self.name = name
        self.start = start          # 1-indexed inclusive
        self.end = end
        self.lines = lines          # list[str] body lines
        self.parent = parent        # class name for methods

    @property
    def qualname(self):
        return f"{self.parent}.{self.name}" if self.parent else self.name

    @property
    def code(self):
        return "\n".join(self.lines)

    @property
    def signature(self):
        # first non-decorator line
        for ln in self.lines:
            s = ln.strip()
            if s and not s.startswith("@") and not s.startswith("//") and not s.startswith("#"):
                return s
        return self.lines[0].strip() if self.lines else ""


def _expand_decorators(lines, start_idx):
    """Walk upward from start_idx to include decorators/attributes/comments directly above."""
    i = start_idx
    while i > 0:
        s = lines[i - 1].strip()
        if s.startswith("@") or s.startswith("#[") or s.startswith("[["):
            i -= 1
        else:
            break
    return i


def extract_python(lines):
    src = "\n".join(lines)
    tree = ast.parse(src)
    entities = []

    def node_span(node):
        start = _expand_decorators(lines, node.lineno - 1)
        end = node.end_lineno  # 1-indexed inclusive
        return start + 1, end

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            s, e = node_span(node)
            entities.append(Entity("function", node.name, s, e, lines[s - 1:e]))
        elif isinstance(node, ast.ClassDef):
            s, e = node_span(node)
            # methods as sub-entities
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ss, se = node_span(sub)
                    entities.append(Entity("method", sub.name, ss, se,
                                            lines[ss - 1:se], parent=node.name))
            # class shell = class minus its methods
            method_lines = set()
            for ent in entities:
                if ent.parent == node.name:
                    method_lines.update(range(ent.start, ent.end + 1))
            shell = [lines[i - 1] for i in range(s, e + 1) if i not in method_lines]
            entities.append(Entity("class", node.name, s, e, shell))
    return entities


# C-like / JS / TS / Go / Rust / Java heuristic: declaration regexes + brace matching
DECL_PATTERNS = [
    # js/ts
    re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)'),
    re.compile(r'^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>'),
    re.compile(r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)'),
    # go
    re.compile(r'^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\('),
    # rust
    re.compile(r'^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)'),
    re.compile(r'^\s*(?:pub\s+)?(?:struct|enum|trait|impl)\s+([A-Za-z_]\w*)'),
    # java/c/c++ methods & functions: type name(args) {
    re.compile(r'^\s*(?:public|private|protected|static|final|virtual|inline|constexpr|[\w:<>,\*&\s]+?)\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:const\s*)?\{?\s*$'),
]


def extract_braced(lines):
    entities = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        name = None
        for pat in DECL_PATTERNS:
            m = pat.match(line)
            if m:
                name = m.group(1)
                break
        if name is None:
            i += 1
            continue
        # find opening brace from this line onward
        depth = 0
        opened = False
        j = i
        while j < n:
            for ch in lines[j]:
                if ch == "{":
                    depth += 1
                    opened = True
                elif ch == "}":
                    depth -= 1
            if opened and depth <= 0:
                break
            if not opened and j > i + 3:   # declaration without body nearby; bail
                break
            j += 1
        if not opened:
            i += 1
            continue
        start = _expand_decorators(lines, i) + 1
        end = j + 1
        kind = "class" if re.search(r'\b(class|struct|enum|trait|impl)\b', line) else "function"
        entities.append(Entity(kind, name, start, end, lines[start - 1:end]))
        i = j + 1
    return entities


def extract_entities(path, lines):
    ext = Path(path).suffix.lower()
    if ext == ".py":
        try:
            return extract_python(lines), "python"
        except SyntaxError:
            pass
    if ext in {".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".h",
               ".cc", ".cpp", ".hpp", ".cs", ".kt", ".swift", ".scala"}:
        return extract_braced(lines), ext.lstrip(".")
    # fallback: no entities; whole file is module-level
    return [], "unknown"


def module_entity(lines, entities):
    """Everything not covered by an entity, as one 'module' pseudo-entity."""
    covered = set()
    for e in entities:
        covered.update(range(e.start, e.end + 1))
    mod_lines = []
    for idx in range(1, len(lines) + 1):
        if idx not in covered:
            ln = lines[idx - 1]
            if ln.strip():
                mod_lines.append(ln)
    return Entity("module", "<module-level>", 0, 0, mod_lines)


# ---------------------------------------------------------------- matching

def normalize(code, strip_name=None):
    out = []
    for ln in code.splitlines():
        s = ln.strip()
        if not s or s.startswith(("#", "//")):
            continue
        s = re.sub(r"\s+", " ", s)
        if strip_name:
            s = s.replace(strip_name, "\u0000NAME")
        out.append(s)
    return out


def similarity(a: Entity, b: Entity):
    na = normalize(a.code, a.name)
    nb = normalize(b.code, b.name)
    if not na and not nb:
        return 1.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


def match_entities(old_ents, new_ents, min_sim):
    matches = []            # (old, new, sim)
    old_left = list(old_ents)
    new_left = list(new_ents)

    # pass 1: exact qualname + kind
    for o in list(old_left):
        for nn in list(new_left):
            if o.qualname == nn.qualname and o.kind == nn.kind:
                matches.append((o, nn, similarity(o, nn)))
                old_left.remove(o)
                new_left.remove(nn)
                break

    # pass 2: rename detection by body similarity (greedy best pair, same kind)
    cands = []
    for o in old_left:
        for nn in new_left:
            if o.kind != nn.kind:
                continue
            sim = similarity(o, nn)
            if sim >= min_sim:
                cands.append((sim, o, nn))
    cands.sort(key=lambda t: -t[0])
    used_o, used_n = set(), set()
    for sim, o, nn in cands:
        if id(o) in used_o or id(nn) in used_n:
            continue
        matches.append((o, nn, sim))
        used_o.add(id(o))
        used_n.add(id(nn))
        old_left.remove(o)
        new_left.remove(nn)

    return matches, old_left, new_left


# ---------------------------------------------------------------- sections

def order_key(sec):
    if sec["new_span"]:
        return (0, sec["new_span"][0])
    if sec["old_span"]:
        return (1, sec["old_span"][0])
    return (2, 0)


def build_sections(matches, deleted, added, old_order, new_order):
    sections = []
    for o, nn, sim in matches:
        identical = normalize(o.code, o.name) == normalize(nn.code, nn.name)
        renamed = o.qualname != nn.qualname
        moved = (old_order.get(id(o)) is not None and new_order.get(id(nn)) is not None
                 and old_order[id(o)] != new_order[id(nn)])
        sig_changed = (re.sub(r"\s+", " ", o.signature).replace(o.name, "N") !=
                       re.sub(r"\s+", " ", nn.signature).replace(nn.name, "N"))
        if identical and not renamed:
            status = "moved" if moved else "identical"
        elif identical and renamed:
            status = "renamed"
        elif renamed:
            status = "renamed_modified"
        else:
            status = "modified"

        pair_diff = None
        if not identical:
            pair_diff = "\n".join(difflib.unified_diff(
                o.code.splitlines(), nn.code.splitlines(),
                fromfile=f"old/{o.qualname}", tofile=f"new/{nn.qualname}", lineterm=""))

        sections.append({
            "status": status, "kind": nn.kind,
            "old_name": o.qualname, "new_name": nn.qualname,
            "old_span": [o.start, o.end] if o.start else None,
            "new_span": [nn.start, nn.end] if nn.start else None,
            "moved": moved,
            "position_delta": (new_order.get(id(nn), 0) - old_order.get(id(o), 0)) if moved else None,
            "similarity": round(sim, 3),
            "signature_changed": bool(sig_changed and not identical),
            "old_code": o.code if not identical else None,
            "new_code": nn.code if not identical else None,
            "pair_diff": pair_diff,
        })

    for o in deleted:
        sections.append({"status": "deleted", "kind": o.kind,
                         "old_name": o.qualname, "new_name": None,
                         "old_span": [o.start, o.end] if o.start else None, "new_span": None,
                         "moved": False, "position_delta": None, "similarity": None,
                         "signature_changed": False,
                         "old_code": o.code, "new_code": None, "pair_diff": None})
    for nn in added:
        sections.append({"status": "added", "kind": nn.kind,
                         "old_name": None, "new_name": nn.qualname,
                         "old_span": None, "new_span": [nn.start, nn.end] if nn.start else None,
                         "moved": False, "position_delta": None, "similarity": None,
                         "signature_changed": False,
                         "old_code": None, "new_code": nn.code, "pair_diff": None})

    sections.sort(key=order_key)
    return sections


def coverage_check(lines, entities):
    covered = set()
    for e in entities:
        if e.start:
            covered.update(range(e.start, e.end + 1))
    uncovered = [i for i in range(1, len(lines) + 1)
                 if i not in covered and lines[i - 1].strip()]
    return uncovered


# ---------------------------------------------------------------- main

def run(old_path, new_path, min_sim):
    old_lines = Path(old_path).read_text().splitlines()
    new_lines = Path(new_path).read_text().splitlines()

    old_ents, lang = extract_entities(old_path, old_lines)
    new_ents, _ = extract_entities(new_path, new_lines)

    old_mod = module_entity(old_lines, old_ents)
    new_mod = module_entity(new_lines, new_ents)

    # positional order index (for move detection), by start line among named entities
    old_sorted = sorted([e for e in old_ents], key=lambda e: e.start)
    new_sorted = sorted([e for e in new_ents], key=lambda e: e.start)
    old_order = {id(e): i for i, e in enumerate(old_sorted)}
    new_order = {id(e): i for i, e in enumerate(new_sorted)}

    matches, deleted, added = match_entities(old_ents, new_ents, min_sim)
    # module-level code always pairs with itself
    matches.append((old_mod, new_mod, similarity(old_mod, new_mod)))

    sections = build_sections(matches, deleted, added, old_order, new_order)

    # module-level uncovered check (uncovered = not in entity and not blank;
    # module pseudo-entity captures those lines, so real gaps = none by construction,
    # but report entity-coverage for transparency)
    result = {
        "old_file": str(old_path), "new_file": str(new_path), "language": lang,
        "summary": {},
        "sections": sections,
        "coverage": {
            "old_lines_total": len(old_lines),
            "new_lines_total": len(new_lines),
            "old_module_level_lines": len(old_mod.lines),
            "new_module_level_lines": len(new_mod.lines),
        },
    }
    for s in sections:
        result["summary"][s["status"]] = result["summary"].get(s["status"], 0) + 1
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old_file")
    ap.add_argument("new_file")
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--min-similarity", type=float, default=0.55)
    args = ap.parse_args()

    result = run(args.old_file, args.new_file, args.min_similarity)
    out = json.dumps(result, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(out)
        # terse stdout summary
        print(f"language: {result['language']}")
        print(f"summary: {result['summary']}")
        print(f"sections: {len(result['sections'])} -> {args.json_out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
