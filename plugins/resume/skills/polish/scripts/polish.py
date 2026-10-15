#!/usr/bin/env python3
"""Environment check and rendered-layout measurement for a LaTeX resume.

  polish.py env  [file.tex]   report TeX / poppler tooling, engine, and missing packages
  polish.py measure file.tex  compile, then report every bullet's line count and line fill

Measurement reads word boxes from the compiled PDF (pdftotext -bbox), so it works for any
class, margins, font or bullet macro: the line width and per-character budget are derived
from the document itself, never assumed.
"""
import html
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys

BULLET_GLYPHS = set("•◦○●▪▫■□‣∙·–—-*>»▸▹►✓✔")
BUILD_DIR = ".polish_build"


def detect_engine(tex_src):
    m = re.search(r"%\s*!TEX\s+(?:TS-)?program\s*=\s*(\w+)", tex_src, re.I)
    if m:
        return m.group(1).lower()
    if re.search(r"\\usepackage(\[[^\]]*\])?\{(fontspec|unicode-math|polyglossia)\}", tex_src):
        return "xelatex"
    if re.search(r"\\documentclass(\[[^\]]*\])?\{awesome-cv\}", tex_src):
        return "xelatex"
    return "pdflatex"


def compile_tex(tex_path):
    """Compile into BUILD_DIR next to the source; return (pdf_path, log_text, ok)."""
    tex_path = os.path.abspath(tex_path)
    src_dir, name = os.path.split(tex_path)
    engine = detect_engine(open(tex_path, encoding="utf-8", errors="replace").read())
    flag = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}.get(engine, "-pdf")
    cmd = ["latexmk", flag, "-interaction=nonstopmode", "-halt-on-error",
           f"-outdir={BUILD_DIR}", name]
    base = os.path.join(src_dir, BUILD_DIR, os.path.splitext(name)[0])
    if os.path.exists(base + ".pdf"):
        os.unlink(base + ".pdf")  # never measure a stale PDF from an earlier successful build
    subprocess.run(cmd, cwd=src_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open(base + ".log", encoding="utf-8", errors="replace").read() if os.path.exists(base + ".log") else ""
    pdf = base + ".pdf"
    ok = os.path.exists(pdf) and not re.search(r"^! ", log, re.M)
    return pdf, log, ok, engine


def missing_files(log):
    return sorted(set(re.findall(r"File `([^']+)' not found", log)))


def cmd_env(tex_path=None):
    tools = {t: shutil.which(t) for t in ["latexmk", "pdflatex", "xelatex", "lualatex",
                                          "kpsewhich", "tlmgr", "pdftotext", "pdfinfo"]}
    print(f"OS: {platform.system()} {platform.machine()}")
    for pm in ["brew", "apt-get", "dnf", "pacman"]:
        if shutil.which(pm):
            print(f"PACKAGE_MANAGER: {pm}")
            break
    for t, p in tools.items():
        print(f"{'OK     ' if p else 'MISSING'} {t}{'  ' + p if p else ''}")
    if not tex_path:
        return
    src = open(tex_path, encoding="utf-8", errors="replace").read()
    print(f"ENGINE: {detect_engine(src)}")
    if not tools["latexmk"]:
        return
    pdf, log, ok, _ = compile_tex(tex_path)
    miss = missing_files(log)
    for f in miss:
        print(f"MISSING_FILE {f}")
    if ok:
        print("COMPILE: ok")
    else:
        err = re.search(r"^! .*$", log, re.M)
        print(f"COMPILE: failed{'  ' + err.group(0) if err else ''}")


def read_words(pdf):
    """Word boxes per page. -tsv is preferred: -bbox writes an HTML header from the PDF Info
    dict and aborts on some poppler builds when Title is empty (hyperref's default)."""
    r = subprocess.run(["pdftotext", "-tsv", pdf, "-"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.startswith("level"):
        pages = {}
        for line in r.stdout.splitlines()[1:]:
            f = line.split("\t")
            if len(f) < 12 or f[0] != "5":
                continue
            x, y, w, h = map(float, f[6:10])
            pages.setdefault(int(f[1]), []).append(dict(x0=x, y0=y, x1=x + w, y1=y + h, t=f[11]))
        n = max(pages) if pages else 0
        return [pages.get(i, []) for i in range(1, n + 1)]
    r = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True)
    return [[dict(x0=float(a), y0=float(b), x1=float(c), y1=float(d), t=html.unescape(t))
             for a, b, c, d, t in re.findall(
                 r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', page)]
            for page in re.findall(r"<page[^>]*>(.*?)</page>", r.stdout, re.S)]


def build_rows(words):
    """Cluster words into visual rows. Text words define rows by baseline; small glyphs
    (bullet markers sit higher/lower than the text baseline) join the row their centre falls in."""
    glyphs = [w for w in words if w["t"] in BULLET_GLYPHS]
    text = sorted((w for w in words if w["t"] not in BULLET_GLYPHS), key=lambda w: (w["y1"], w["x0"]))
    rows = []
    for w in text:
        for r in rows:
            if abs(r["y1"] - w["y1"]) < 1.5 and not (w["x0"] > r["x1"] + 60 or w["x1"] < r["x0"] - 60):
                r["w"].append(w)
                r["x0"], r["x1"] = min(r["x0"], w["x0"]), max(r["x1"], w["x1"])
                r["y0"] = min(r["y0"], w["y0"])
                break
        else:
            rows.append(dict(w=[w], x0=w["x0"], x1=w["x1"], y0=w["y0"], y1=w["y1"], marker=None))
    for g in glyphs:
        c = (g["y0"] + g["y1"]) / 2
        cands = [r for r in rows if r["y0"] - 1 <= c <= r["y1"] + 1 and 0 <= r["x0"] - g["x1"] < 25]
        if cands:
            min(cands, key=lambda r: r["x0"] - g["x1"])["marker"] = g
    for r in rows:
        r["w"].sort(key=lambda w: w["x0"])
        r["text"] = " ".join(w["t"] for w in r["w"])
    rows.sort(key=lambda r: (r["y1"], r["x0"]))
    return rows


def cmd_measure(tex_path, min_fill=0.88, min_gap=5.0):
    missing = [t for t in ("latexmk", "pdftotext") if not shutil.which(t)]
    if missing:
        print(f"MISSING_TOOL {' '.join(missing)}. Run: polish.py env {tex_path}")
        sys.exit(1)
    pdf, log, ok, engine = compile_tex(tex_path)
    if not ok:
        print(f"COMPILE FAILED ({engine}). Run: polish.py env {tex_path}")
        for f in missing_files(log):
            print(f"MISSING_FILE {f}")
        err = re.search(r"^! .*$", log, re.M)
        if err:
            print(err.group(0))
        sys.exit(1)

    pages = read_words(pdf)
    bullets = []
    for pno, words in enumerate(pages, 1):
        if not words:
            continue
        right = max(w["x1"] for w in words)  # text-block right edge (right-aligned dates, justified lines)
        rows = build_rows(words)
        cur = None
        for r in rows:
            if r["marker"] is not None:
                cur = dict(page=pno, x=r["x0"], rows=[r], right=right)
                bullets.append(cur)
            elif cur and cur["page"] == pno and abs(r["x0"] - cur["x"]) < 2 \
                    and 0 < r["y1"] - cur["rows"][-1]["y1"] < 2.2 * (r["y1"] - r["y0"]):
                cur["rows"].append(r)
            else:
                cur = None

    # A marker beside a one- or two-word row is a header icon or separator, not a bullet.
    bullets = [b for b in bullets if sum(len(r["w"]) for r in b["rows"]) >= 3]
    if not bullets:
        print("No bullet markers found in the PDF; bullets may use an unusual glyph or none.")
        sys.exit(2)

    # Budgets are per context: list width and font size (row height) both change chars/line,
    # e.g. section-level lists often render larger than lists nested in entries.
    for b in bullets:
        size = statistics.median(w["y1"] - w["y0"] for r in b["rows"] for w in r["w"])
        b["ctx"] = (round((b["right"] - b["x"]) / 4) * 4, round(size * 2) / 2)
    budgets = {}
    for ctx in sorted({b["ctx"] for b in bullets}):
        group = [b for b in bullets if b["ctx"] == ctx]
        sample = [b for b in group if len(b["rows"]) == 1 and len(b["rows"][0]["text"]) > 40] or group
        ppc = statistics.median((b["rows"][0]["x1"] - b["x"]) / max(len(b["rows"][0]["text"]), 1)
                                for b in sample)
        budgets[ctx] = (chr(ord("A") + len(budgets)), ppc)

    n_pages = len(pages)
    overfull = len(re.findall(r"^Overfull \\hbox", log, re.M))
    print(f"ENGINE {engine}  PAGES {n_pages}  OVERFULL_HBOX {overfull}  PDF {pdf}")
    for (w, h), (label, ppc) in budgets.items():
        n = sum(1 for b in bullets if b["ctx"] == (w, h))
        print(f"BUDGET {label}: {n} bullets, line {w}pt, text height {h}pt, ~{ppc:.2f}pt/char "
              f"=> ~{int(w / ppc)} chars max; target {int(w * min_fill / ppc)}-{int((w - min_gap) / ppc)} chars")
    print()
    counts = {}
    for i, b in enumerate(bullets, 1):
        avail = b["right"] - b["x"]
        last = b["rows"][-1]
        lines = len(b["rows"])
        fill = (last["x1"] - b["x"]) / avail
        gap = b["right"] - last["x1"]
        if lines > 1:
            status = "WRAPS"
        elif gap < min_gap:
            status = "TIGHT"
        elif fill < min_fill:
            status = "SHORT"
        else:
            status = "OK"
        counts[status] = counts.get(status, 0) + 1
        text = " ".join(r["text"] for r in b["rows"])
        extra = f"  last-line: '{last['text']}'" if lines > 1 else ""
        print(f"#{i:<3} p{b['page']} {budgets[b['ctx']][0]} {status:<5} lines {lines}  fill {fill:5.1%}  gap {gap:6.1f}pt  "
              f"{len(text):>3}ch  | {text[:70]}{'…' if len(text) > 70 else ''}{extra}")
    print("\nSUMMARY " + "  ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("env", "measure"):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "env":
        cmd_env(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        if len(sys.argv) < 3:
            print("usage: polish.py measure file.tex")
            sys.exit(1)
        cmd_measure(sys.argv[2])
