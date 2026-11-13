#!/usr/bin/env python3
"""Build paper/Gamma_AC_Journal_Paper.docx from paper_journal.md.       python3 build_journal.py

Uses the machinery of build.py (number substitution, numbering of figures, tables and equations, Word styling).
  {{key}}          a value from results/numbers.json, results/numbers_journal.json or declarations.json; a missing key stops the build
  [[table:name]]   a table written by journal_numbers.py
After the build it prints every number typed in the text that no script produced (dates, labels and constants are
expected). If an earlier Word draft is available (paths.py, optional), it also checks that every display equation of
that draft is still present, character for character.
"""
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import paths  # noqa: E402
import build as B  # noqa: E402

HERE = paths.REPO
from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

BUILD = paths.BUILD
OUT = paths.PAPER / "Gamma_AC_Journal_Paper.docx"
RECEIVED = paths.RECEIVED
MM = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


def journal_reference(path):
    B.make_reference(path)
    d = Document(str(path))
    st = d.styles
    B._fonts(st["Title"], B.HEAD, 20, bold=True, color=B.NAVY)
    B._para(st["Title"], before=18, after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    for name in ("Author", "Date"):
        B._fonts(st[name], B.HEAD, 11.5, color="1A1A1A")
        B._para(st[name], before=0, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    for name, size, bold in (("Abstract Title", 11, True), ("Abstract", 10, False)):
        try:
            s = st[name]
        except KeyError:
            continue
        B._fonts(s, B.BODY if name == "Abstract" else B.HEAD, size, bold=bold, italic=False, color="1A1A1A")
        B._para(s, before=14 if bold else 0, after=4 if bold else 8, line=1.15, left=0.45,
                align=WD_ALIGN_PARAGRAPH.CENTER if bold else WD_ALIGN_PARAGRAPH.LEFT)
        s.paragraph_format.right_indent = Inches(0.45)
    B._fonts(st["Heading 1"], B.HEAD, 15, bold=True, color=B.NAVY)
    B._para(st["Heading 1"], before=20, after=7, keep_next=True)
    B._fonts(st["Heading 2"], B.HEAD, 12.5, bold=True, color=B.NAVY)
    B._para(st["Heading 2"], before=14, after=5, keep_next=True)
    d.save(str(path))


WIDTHS = {   # caption phrase -> relative column widths
    "The two datasets": [16, 46, 38],
    "Fields saved for each option contract": [21, 53, 26],
    "Filters applied to the option quotes": [7, 25, 42, 13, 13],
    "Notation used in Section 4": [10, 18, 52, 20],
    "The eight cases of the rule": [7, 20, 11, 22, 9, 9, 12, 10],
    "Performance over": [34, 22, 22, 22],
    "Calendar-year returns and the rule": [19, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    "Concentration of the result": [27, 7, 11, 11, 11, 11, 11, 11],
    "random filters that hold the trend position": [40, 11, 17, 20, 12],
    "rules that use the day's move without the option reading": [42, 14, 15, 15, 14],
    "Differences in annualized Sharpe ratio": [34, 11, 13, 11, 10, 10, 11],
    "Threats to the validity": [15, 27, 29, 29],
    "Total return in four stress periods": [26, 30, 8, 20, 16],
    "Baseline and full return accounting": [28, 12, 12, 12, 12, 12, 12],
    "days of the preregistered holdout": [24, 19, 19, 19, 19],
    "Inputs to the deflated Sharpe ratio": [10, 21, 52, 17],
    "for different numbers of trials": [37, 9, 9, 9, 9, 9, 9, 9],
    "Newton's method for the example contract": [10, 15, 20, 18, 19, 18],
}


def apply_widths(path):
    """Set the widths in WIDTHS on the table that follows each matching caption. Returns the captions that matched nothing."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    d = Document(str(path))
    body = d.element.body
    used = set()
    for tbl in body.iter(qn("w:tbl")):
        prev = tbl.getprevious()
        cap = "".join(t.text or "" for t in prev.iter(qn("w:t"))) if prev is not None else ""
        cap = cap.replace("\u2019", "'")
        key = next((k for k in WIDTHS if k in cap), None)
        cols = tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol"))
        if key is None:
            print("   no width rule for table:", cap[:70])
            continue
        rel = WIDTHS[key]
        assert len(rel) == len(cols), (key, len(rel), len(cols))
        used.add(key)
        widths = [int(round(v * B.TEXT_W / sum(rel))) for v in rel]
        widths[-1] += B.TEXT_W - sum(widths)
        for c, wv in zip(cols, widths):
            c.set(qn("w:w"), str(wv))
        for tr in tbl.findall(qn("w:tr")):
            for tc, wv in zip(tr.findall(qn("w:tc")), widths):
                tcw = tc.find(qn("w:tcPr")).find(qn("w:tcW"))
                tcw.set(qn("w:w"), str(wv))
    d.save(str(path))
    return sorted(set(WIDTHS) - used)


def linear(el):
    """The characters of an equation without spacing, invisible characters, brackets or its (n) tag. Brackets are left out
    because Word stores them either as text or as a delimiter object, and the two look the same on the page."""
    import unicodedata
    txt = "".join(t.text or "" for t in el.iter(MM + "t"))
    txt = "".join(ch for ch in txt if not ch.isspace() and unicodedata.category(ch) not in ("Cf", "Zs"))
    return re.sub(r"[()\[\]]", "", re.sub(r"\(\d+\)$", "", txt))


def display_equations(docx):
    from lxml import etree
    root = etree.fromstring(zipfile.ZipFile(docx).read("word/document.xml"))
    return [linear(e) for e in root.iter(MM + "oMathPara")]


def audit_numbers(src, values):
    """Numbers typed in the source that no script produced. Dates, section and equation labels and small integers are expected."""
    text = re.sub(r"\{\{[^}]*\}\}|\[\[[^\]]*\]\]|\[[#@][^\]]*\]|\\EQ\{[^}]*\}|\(figs/[^)]*\)\{[^}]*\}|https?://\S+", " ", src)
    known = set()
    for v in values:
        for tok in re.findall(r"\d[\d,]*\.?\d*", v):
            known.add(tok.replace(",", "").rstrip("."))
    unknown = {}
    for tok in re.findall(r"(?<![\w.])\d[\d,]*\.?\d*%?", text):
        raw = tok.rstrip("%").replace(",", "").rstrip(".")
        if raw in known or re.fullmatch(r"(19|20)\d\d", raw) or (raw.isdigit() and int(raw) <= 31):
            continue
        unknown[raw] = unknown.get(raw, 0) + 1
    return unknown


def main():
    values = json.loads((paths.RESULTS / "numbers.json").read_text())
    jv = json.loads((paths.RESULTS / "numbers_journal.json").read_text())
    decl = json.loads((HERE / "declarations.json").read_text())
    clash = set(values) & set(jv)
    assert not clash, clash
    values.update(jv)
    values.update({k: v for k, v in decl.items() if k.startswith("decl_")})
    B.V = values
    tables = json.loads((paths.RESULTS / "tables_journal.json").read_text())

    src = (HERE / "paper_journal.md").read_text()
    assert "<<YELLOW" not in src, "a yellow note is still unresolved"
    src = re.sub(r"\[\[table:([a-z0-9]+)\]\]", lambda m: tables[m.group(1)], src)
    unknown = audit_numbers(src, list(values.values()) + list(tables.values()))
    src = B.number(B.fill_numbers(src))
    left = re.findall(r"\{\{[^}]*\}\}|\[[#@](?:fig|tab|eq):[^\]]*\]|\\EQ\{|\[\[", src)
    assert not left, left[:5]
    (BUILD / "paper_built.md").write_text(src)
    ref = BUILD / "reference_journal.docx"
    journal_reference(ref)
    cmd = ["pandoc", str(BUILD / "paper_built.md"), "-f", "markdown+smart+pipe_tables+multiline_tables+fenced_divs+bracketed_spans+tex_math_dollars+implicit_figures+link_attributes+raw_attribute",
           "-t", "docx", "--reference-doc", str(ref), "--resource-path", str(HERE), "--columns", "72", "-o", str(OUT)]
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    if r.stderr.strip():
        print("pandoc:", r.stderr.strip()[:3000])
    if r.returncode != 0:
        sys.exit("pandoc failed")
    nt, nf = B.finish(OUT)
    unused = apply_widths(OUT)
    if unused:
        print("   width rules that matched no table:", unused)
    d = Document(str(OUT))
    cp = d.core_properties
    cp.title = "Does option gamma exposure add anything to a trend rule? A daily test on QQQ, 2018 to 2026"
    cp.author = decl.get("author", "TC")
    cp.subject = "Working paper, November 2026"
    cp.keywords = "gamma exposure, dealer hedging, trend following, backtest overfitting, deflated Sharpe ratio, QQQ"
    d.save(str(OUT))
    subprocess.run(["zip", "-q", "-d", str(OUT), "*/"], capture_output=True)
    print(f"wrote {OUT.name}: {nt} tables, {nf} figures, {OUT.stat().st_size / 1e6:.2f} MB")

    if RECEIVED is not None:
        old, new = display_equations(RECEIVED), display_equations(OUT)
        missing = [e for e in old if e not in new]
        print(f"equations: {len(old)} in the earlier draft, {len(old) - len(missing)} reproduced exactly, {len(new) - len(old) + len(missing)} new")
        for e in missing:
            print("   CHANGED:", e[:110])
    print(f"numbers typed in the text that no script produced: {len(unknown)} distinct")
    if unknown:
        print("  ", ", ".join(sorted(unknown, key=lambda x: (len(x), x))[:80]))


if __name__ == "__main__":
    main()
