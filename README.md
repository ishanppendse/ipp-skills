# ipp-skills

A growing collection of [Claude Code](https://claude.com/claude-code) skills for **understanding code and concepts deeply, learning faster, and doing better research.**

This repo is a Claude Code **plugin marketplace**. Skills are grouped into plugins by category. Install the whole marketplace once, then install whichever categories you want.

## Install

```
/plugin marketplace add ishanppendse/ipp-skills
/plugin install understanding@ipp-skills
/plugin install sw-eng@ipp-skills
```

Update later with `/plugin marketplace update ipp-skills`.

## Categories

### `understanding`
Turn dense code and concepts into structured, navigable explanations — for when you want to *understand*, not just read.

| Skill | What it does |
| ----- | ------------ |
| **code-boxes** | Explains a code file or module as an interactive flowchart of collapsible black boxes — each showing inputs (shapes/types), outputs, and the core operations/equations inside. Renders a single self-contained HTML viewer. When run inside a real repo, box source labels become clickable `vscode://` links that jump to the exact file+line in your local VS Code. |
| **rikugan** | *(Gojo's Six Eyes, JJK — see through to the structure, spend nothing on the rest.)* Writes an annotated, traced copy of your code: a ≤3-line principle-level comment above every block (the equation, not a paraphrase) and a one-sentence trace of one concrete anchor input beside every line. Code stays verbatim — diff the traced copy against the original and you see only added comments. Resolves repo-local imports and confirms scope before writing, then fans out one agent per file, each annotating a copy in place chunk by chunk so large files don't blow up. |
| **smart-diff** | Produces a semantic, structure-aware diff between two versions of a file. Matches functions across renames and moves, so a renamed/relocated function shows as one modified section instead of a giant delete+add. |

### `sw-eng`
Everyday software-engineering passes you run on real code before it ships.

| Skill | What it does |
| ----- | ------------ |
| **comments-deslop** | Rewrites comments and docstrings in the files your branch touched so they read as finished documentation instead of a transcript of the session that produced them. Deletes code restatements, PR-number narration and agent TODOs; compresses the rest to motivation, invariants and shapes. Comments only — never touches code. Fans out across subagents on large diffs. |

*More categories (e.g. `learning`, `research`) will be added as separate plugins over time.*

## Repo layout

```
.claude-plugin/marketplace.json      # marketplace catalog (lists plugins)
plugins/
  understanding/
    .claude-plugin/plugin.json       # plugin manifest
    skills/
      code-boxes/    SKILL.md + scripts/ + assets/
      smart-diff/    SKILL.md + scripts/
      rikugan/       SKILL.md
  sw-eng/
    .claude-plugin/plugin.json
    skills/
      comments-deslop/   SKILL.md + scripts/
```

Adding a new category = a new directory under `plugins/` with its own `plugin.json` and `skills/`, plus one entry in `marketplace.json`.

## License

[MIT](./LICENSE) © Ishan Pendse
