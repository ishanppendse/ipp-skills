#!/usr/bin/env bash
# Print git-tracked files added/modified on this branch vs its base.
# Usage: scope.sh [base-branch]
set -euo pipefail

base="${1:-}"
if [[ -z "$base" ]]; then
  for c in develop main master; do
    if git show-ref --verify --quiet "refs/heads/$c" || git show-ref --verify --quiet "refs/remotes/origin/$c"; then
      base="$c"; break
    fi
  done
fi
[[ -n "$base" ]] || { echo "no base branch found; pass one explicitly" >&2; exit 1; }

# Prefer the remote ref so a stale local base doesn't widen the diff.
ref="$base"
git show-ref --verify --quiet "refs/remotes/origin/$base" && ref="origin/$base"

merge_base=$(git merge-base "$ref" HEAD)
echo "base: $ref ($merge_base)" >&2

# Committed + staged + unstaged, A/M/R only (drop deletions), tracked only.
{
  git diff --name-only --diff-filter=AMR "$merge_base" HEAD
  git diff --name-only --diff-filter=AMR HEAD
} | sort -u | while read -r f; do
  git ls-files --error-unmatch "$f" >/dev/null 2>&1 && echo "$f"
done
