#!/usr/bin/env python3
"""
build_viewer.py — inject a code-boxes JSON tree into the HTML viewer template.

Usage:
    python build_viewer.py BOXES.json OUTPUT.html

JSON schema (validated loosely here; see SKILL.md for full semantics):
{
  "title": str,
  "subtitle": str,                     # e.g. "llama/modeling_llama.py @ abc123"
  "repo_root": str|null,               # optional ABSOLUTE repo path; when set, each node
                                       #   "source" becomes a clickable vscode://file link.
                                       #   Omit for pasted/remote code (source renders as text).
  "root": {
    "id": str,                         # unique across the whole tree
    "name": str,
    "one_liner": str,
    "inputs":  [{"name": str, "shape": str, "meaning": str}],
    "outputs": [{"name": str, "shape": str, "meaning": str}],
    "ops": [str],                      # <=3 equations / bullets
    "source": str,                     # "file.py:L120-180"
    "paper": str|null,                 # optional URL
    "children": {                      # omit or null for leaf
      "nodes": [ <same node schema> ],
      "edges": [{"from": id, "to": id, "label": str|null}]
    }
  }
}
"""
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).parent.parent / "assets" / "viewer_template.html"


def collect_ids(node, seen, errors):
    if node["id"] in seen:
        errors.append(f"duplicate id: {node['id']}")
    seen.add(node["id"])
    ch = node.get("children") or {}
    for sub in ch.get("nodes", []):
        collect_ids(sub, seen, errors)


def validate_edges(node, errors, path="root"):
    ch = node.get("children") or {}
    nodes = ch.get("nodes", [])
    local_ids = {n["id"] for n in nodes}
    for e in ch.get("edges", []):
        for k in ("from", "to"):
            if e[k] not in local_ids:
                errors.append(f"{path}/{node['id']}: edge endpoint '{e[k]}' "
                              f"not among direct children {sorted(local_ids)}")
    for sub in nodes:
        validate_edges(sub, errors, path + "/" + node["id"])


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    data = json.loads(Path(sys.argv[1]).read_text())

    errors = []
    if "root" not in data:
        errors.append("missing 'root'")
    else:
        collect_ids(data["root"], set(), errors)
        validate_edges(data["root"], errors)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(2)

    html = TEMPLATE.read_text()
    html = html.replace("__TITLE__", data.get("title", "Code Boxes"))
    html = html.replace("__DATA__", json.dumps(data))
    Path(sys.argv[2]).write_text(html)
    print(f"wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
