#!/usr/bin/env bash
# Measure rendered width of candidate bullets. One bullet per line in the input file (LaTeX-escaped).
# Usage: ./probe.sh bullets.txt [cventry|section]
#   cventry (default): Experience/Projects bullets (\small)
#   section:           Skills/Achievements bullets (\normalsize, itemize directly under \section)
# Linewidth = 496.46pt. Width > 496.46pt => WRAPS. Target gap 15-25pt.
set -euo pipefail
IN="${1:?Usage: ./probe.sh bullets.txt [cventry|section]}"; MODE="${2:-cventry}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
{
  echo '\documentclass[10pt,a4paper,serif]{moderncv}\moderncvstyle{banking}\moderncvcolor{grey}'
  echo '\usepackage[utf8]{inputenc}\usepackage[left=1.6cm,right=1.6cm,top=0.8cm,bottom=0.8cm]{geometry}'
  echo '\name{I}{P}\begin{document}\makecvtitle\newlength{\probew}'
  echo '\def\test#1#2{\settowidth{\probew}{#2}\typeout{PROBEROW #1 \the\probew}}'
  if [ "$MODE" = section ]; then echo '\section{S}\begin{itemize}\item'; else echo '\cventry{2025}{P}{R}{L}{}{\begin{itemize}\item'; fi
  n=0; while IFS= read -r line || [ -n "$line" ]; do [ -z "$line" ] && continue; n=$((n+1)); echo "\\test{$n}{$line}"; done < "$IN"
  if [ "$MODE" = section ]; then echo 'probe\end{itemize}'; else echo 'probe\end{itemize}}'; fi
  echo '\end{document}'
} > "$TMP/_probe.tex"
(cd "$TMP" && pdflatex -interaction=nonstopmode _probe.tex >/dev/null || true)
grep -o "PROBEROW [0-9]* [0-9.]*pt" "$TMP/_probe.log" | awk '{w=$3; sub(/pt/,"",w); gap=496.46-w;
  s=(gap<0)?"WRAPS":(gap<5)?"RISKY":(gap>60)?"SHORT":"OK"; printf "#%s  %8.2fpt  gap %7.2fpt  %s\n",$2,w,gap,s}'
