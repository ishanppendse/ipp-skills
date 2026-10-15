#!/usr/bin/env bash
# Compile a .tex file to PDF. Usage: ./build.sh resume.tex
set -euo pipefail
TEX="${1:?Usage: ./build.sh <file.tex>}"
latexmk -pdf -interaction=nonstopmode -halt-on-error "$TEX"
echo "Built: ${TEX%.tex}.pdf"
