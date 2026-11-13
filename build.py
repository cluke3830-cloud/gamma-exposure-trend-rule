#!/usr/bin/env python3
"""Word-document machinery used by build_journal.py, which is the script to run.

What it does, in order:
  1. {{key}}    -> the value in data/numbers.json. A missing key stops the build, so no number is typed by hand.
     {{m:key}}  -> the same value written for LaTeX math (minus sign, percent, powers of ten).
  2. [#fig:x] / [#tab:x] give a figure or table its number, [@fig:x] / [@tab:x] refer to it.
     \\EQ{x} numbers a display equation, [@eq:x] refers to it. [[TOC]] becomes a linked contents list.
  3. pandoc writes the .docx with native Word equations, using the styles in build/reference.docx (made here).
  4. A python-docx pass rules the tables, sets their text style and keeps figures with their captions.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

import paths

HERE = paths.REPO
BUILD = paths.BUILD
V = json.loads((paths.RESULTS / "numbers.json").read_text()) if (paths.RESULTS / "numbers.json").exists() else {}

BODY, HEAD = "Cambria", "Calibri"
NAVY, INK2, RULE, FILL = "1F2A44", "52514E", "8A8984", "F0EFEC"
TEXT_W = 9360                      # text width in twentieths of a point: 8.5 in page less two 1 in margins


# ----------------------------------------------------------------------------------------------- 1. numbers
def tex(v):
    v = v.replace("\u2212", "-").replace("\u00d7", r"\times")
    v = re.sub(r"10\^(-?\d+)", r"10^{\1}", v)
    v = re.sub(r"(?<=\d),(?=\d{3})", "{,}", v)
    return v.replace("%", r"\%").replace("$", r"\$")


def fill_numbers(src):
    missing, used = set(), set()

    def sub(m):
        mode, key = m.group(1), m.group(2)
        used.add(key)
        if key not in V:
            missing.add(key)
            return "??"
        return tex(V[key]) if mode else re.sub(r"10\^(\u2212?\d+)", r"10^\1^", V[key])

    out = re.sub(r"\{\{(m:)?([A-Za-z0-9_]+)\}\}", sub, src)
    if missing:
        sys.exit(f"no value for: {sorted(missing)}")
    print(f"numbers: {len(used)} distinct values substituted")
    return out


# ----------------------------------------------------------------------------------------------- 2. numbering
def number(src):
    names = {"fig": "Figure", "tab": "Table"}
    table = {}
    for kind in ("fig", "tab"):
        for i, m in enumerate(re.finditer(r"\[#%s:([a-z0-9_]+)\]" % kind, src), 1):
            assert (kind, m.group(1)) not in table, f"defined twice: {kind}:{m.group(1)}"
            table[(kind, m.group(1))] = str(i)
    for i, m in enumerate(re.finditer(r"\\EQ\{([a-z0-9_]+)\}", src), 1):
        assert ("eq", m.group(1)) not in table, f"defined twice: eq:{m.group(1)}"
        table[("eq", m.group(1))] = str(i)

    def ref(m):
        key = (m.group(1), m.group(2))
        if key not in table:
            sys.exit(f"reference to an undefined label: {key}")
        return f"({table[key]})" if m.group(1) == "eq" else table[key]

    src = re.sub(r"\[#(fig|tab):([a-z0-9_]+)\]", lambda m: table[(m.group(1), m.group(2))], src)
    src = re.sub(r"\\EQ\{([a-z0-9_]+)\}", lambda m: r"\qquad \text{(%s)}" % table[("eq", m.group(1))], src)
    src = re.sub(r"\[@(fig|tab|eq):([a-z0-9_]+)\]", ref, src)
    n = {k: sum(1 for kk in table if kk[0] == k) for k in ("fig", "tab", "eq")}
    print(f"numbered: {n['fig']} figures, {n['tab']} tables, {n['eq']} equations")
    return src


def contents(src):
    rows = []
    for m in re.finditer(r"^(#{1,2}) (.+?) \{#([a-z0-9-]+)\}\s*$", src, flags=re.M):
        level = len(m.group(1))
        rows.append('::: {custom-style="Contents %d"}\n[%s](#%s)\n:::\n' % (level, m.group(2), m.group(3)))
    assert "[[TOC]]" in src
    return src.replace("[[TOC]]", "\n".join(rows))


# ----------------------------------------------------------------------------------------------- 3. reference styles
# WordprocessingML fixes the order of the children of these elements; Word can refuse a file that breaks it.
ORDER = {
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
            "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
            "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment",
            "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"],
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
              "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"],
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"],
    "trPr": ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit", "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden"],
}


def reorder(el, kind):
    """Put el's children into schema order, keeping the last of any repeated element."""
    rank = {qn("w:" + n): i for i, n in enumerate(ORDER[kind])}
    last = {}
    for k in list(el):
        last[k.tag] = k
        el.remove(k)
    for k in sorted(last.values(), key=lambda k: rank.get(k.tag, 999)):
        el.append(k)


def _fonts(style, name, size=None, bold=None, italic=None, color=None):
    f = style.font
    f.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = RGBColor.from_string(color)


def _para(style, before=None, after=None, line=None, keep_next=None, align=None, left=None):
    pf = style.paragraph_format
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if line is not None:
        pf.line_spacing = line
    if keep_next is not None:
        pf.keep_with_next = keep_next
    if align is not None:
        pf.alignment = align
    if left is not None:
        pf.left_indent = Inches(left)


def _box(style, fill, bar):
    """Shaded paragraph with a coloured bar down its left edge."""
    ppr = style.element.get_or_add_pPr()
    for tag in ("w:pBdr", "w:shd"):
        old = ppr.find(qn(tag))
        if old is not None:
            ppr.remove(old)
    bdr = OxmlElement("w:pBdr")
    for side, sz, col, space in (("w:top", "4", fill, "6"), ("w:left", "24", bar, "8"), ("w:bottom", "4", fill, "6"), ("w:right", "4", fill, "6")):
        e = OxmlElement(side)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), sz)
        e.set(qn("w:space"), space)
        e.set(qn("w:color"), col)
        bdr.append(e)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(bdr)
    ppr.append(shd)
    reorder(ppr, "pPr")


def _page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for kind, text in (("begin", None), (None, " PAGE "), ("end", None)):
        r = p.add_run()
        r.font.size = Pt(9)
        r.font.name = HEAD
        r.font.color.rgb = RGBColor.from_string(INK2)
        if kind:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = text
            r._r.append(it)


def make_reference(path):
    with open(path, "wb") as fh:
        subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], check=True, stdout=fh)
    d = Document(str(path))
    st = d.styles
    from docx.enum.style import WD_STYLE_TYPE

    def get(name, base="Normal"):
        try:
            return st[name]
        except KeyError:
            s = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            s.base_style = st[base]
            return s

    _fonts(st["Normal"], BODY, 11, color="1A1A1A")
    for name in ("Body Text", "First Paragraph"):
        _fonts(st[name], BODY, 11)
        _para(st[name], before=0, after=8, line=1.18)
    _fonts(st["Compact"], BODY, 11)
    _para(st["Compact"], before=0, after=3, line=1.12)
    _fonts(st["Title"], HEAD, 27, bold=True, color=NAVY)
    _para(st["Title"], before=30, after=8, align=WD_ALIGN_PARAGRAPH.LEFT)
    _fonts(st["Subtitle"], HEAD, 14, bold=False, color=INK2)
    _para(st["Subtitle"], before=0, after=16, align=WD_ALIGN_PARAGRAPH.LEFT)
    for style_name in ("Title", "Subtitle"):                       # the default styles letter-space these
        rpr = st[style_name].element.get_or_add_rPr()
        for sp in rpr.findall(qn("w:spacing")):
            rpr.remove(sp)
    for name in ("Author", "Date"):
        _fonts(st[name], HEAD, 11.5, color="1A1A1A")
        _para(st[name], before=0, after=2, align=WD_ALIGN_PARAGRAPH.LEFT)
    _fonts(st["Heading 1"], HEAD, 19, bold=True, color=NAVY)
    _para(st["Heading 1"], before=26, after=9, keep_next=True)
    _fonts(st["Heading 2"], HEAD, 14.5, bold=True, color=NAVY)
    _para(st["Heading 2"], before=18, after=6, keep_next=True)
    _fonts(st["Heading 3"], HEAD, 12, bold=True, color="333333")
    _para(st["Heading 3"], before=14, after=4, keep_next=True)
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        st[name].font.italic = False
    for name in ("Image Caption", "Table Caption"):
        _fonts(st[name], HEAD, 9.5, italic=False, color=INK2)
    _para(st["Image Caption"], before=4, after=14, align=WD_ALIGN_PARAGRAPH.LEFT, line=1.1)
    _para(st["Table Caption"], before=10, after=5, keep_next=True, align=WD_ALIGN_PARAGRAPH.LEFT, line=1.1)
    for name in ("Captioned Figure", "Figure"):
        _para(st[name], before=8, after=0, keep_next=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    t = get("Table Text")
    _fonts(t, HEAD, 9.5, color="1A1A1A")
    _para(t, before=0, after=0, line=1.08)
    for name, fill, bar in (("Plain English", "EAF2FB", "2A78D6"), ("Key Point", "F0EFEC", NAVY), ("Caution", "FDF0E8", "EB6834")):
        b = get(name)
        _fonts(b, HEAD, 10.5, color="1A1A1A")
        _para(b, before=6, after=10, line=1.15, left=0.14)
        b.paragraph_format.right_indent = Inches(0.1)
        _box(b, fill, bar)
    n = get("Draft Note")
    _fonts(n, HEAD, 10, italic=True, color=INK2)
    _para(n, before=10, after=8)
    c1 = get("Contents 1")
    _fonts(c1, HEAD, 11, bold=True, color=NAVY)
    _para(c1, before=5, after=0)
    c2 = get("Contents 2")
    _fonts(c2, HEAD, 10.5, color="1A1A1A")
    _para(c2, before=0, after=0, left=0.25)
    ch = get("Contents Heading")
    _fonts(ch, HEAD, 14.5, bold=True, color=NAVY)
    _para(ch, before=6, after=3)
    r_ = get("Reference")
    _fonts(r_, BODY, 10.5)
    _para(r_, before=0, after=7, line=1.12, left=0.3)
    r_.paragraph_format.first_line_indent = Inches(-0.3)
    try:
        st["Hyperlink"].font.color.rgb = RGBColor.from_string("1C5CAB")
    except KeyError:
        pass

    sec = d.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(1.0)
    sec.top_margin, sec.bottom_margin = Inches(1.0), Inches(0.95)
    sec.header_distance, sec.footer_distance, sec.gutter = Inches(0.5), Inches(0.5), Inches(0)
    _page_number(sec)
    d.save(str(path))


# ----------------------------------------------------------------------------------------------- 4. finishing pass
def _border(el, tag, val="single", sz="4", color=RULE):
    e = OxmlElement(tag)
    e.set(qn("w:val"), val)
    e.set(qn("w:sz"), sz)
    e.set(qn("w:space"), "0")
    e.set(qn("w:color"), color)
    el.append(e)


def finish(path):
    from docx.text.paragraph import Paragraph
    d = Document(str(path))
    for tb in d.tables:
        nxt = tb._tbl.getnext()                                      # air between a table and the text under it
        if nxt is not None and nxt.tag == qn("w:p"):
            Paragraph(nxt, d).paragraph_format.space_before = Pt(11)
        nrows = len(tb.rows)
        tblPr = tb._tbl.tblPr
        for tag in ("w:tblBorders", "w:tblW", "w:tblLayout", "w:tblCellMar", "w:jc"):
            old = tblPr.find(qn(tag))
            if old is not None:
                tblPr.remove(old)
        # exact widths on the table, the grid and every cell (twentieths of a point); auto-fit ignores the grid
        cols = tb._tbl.tblGrid.findall(qn("w:gridCol"))
        raw = [int(c.get(qn("w:w"))) for c in cols]
        widths = [int(round(v * TEXT_W / sum(raw))) for v in raw]
        widths[-1] += TEXT_W - sum(widths)
        for c, wv in zip(cols, widths):
            c.set(qn("w:w"), str(wv))
        w = OxmlElement("w:tblW")
        w.set(qn("w:type"), "dxa")
        w.set(qn("w:w"), str(TEXT_W))
        tblPr.append(w)
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        b = OxmlElement("w:tblBorders")
        _border(b, "w:top", sz="10", color=NAVY)
        _border(b, "w:left", val="nil")
        _border(b, "w:bottom", sz="10", color=NAVY)
        _border(b, "w:right", val="nil")
        _border(b, "w:insideH", sz="4", color="D5D4CE")
        _border(b, "w:insideV", val="nil")
        tblPr.append(b)
        mar = OxmlElement("w:tblCellMar")
        for side, wv in (("w:top", "55"), ("w:left", "80"), ("w:bottom", "55"), ("w:right", "80")):
            e = OxmlElement(side)
            e.set(qn("w:w"), wv)
            e.set(qn("w:type"), "dxa")
            mar.append(e)
        tblPr.append(mar)
        reorder(tblPr, "tblPr")
        for i, row in enumerate(tb.rows):
            trPr = row._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            trPr.append(cs)
            if i == 0:
                th = OxmlElement("w:tblHeader")
                trPr.append(th)
            reorder(trPr, "trPr")
            assert len(row.cells) == len(widths), "merged cells are not handled"
            for j, cell in enumerate(row.cells):
                tcPr = cell._tc.get_or_add_tcPr()
                tcw = OxmlElement("w:tcW")
                tcw.set(qn("w:type"), "dxa")
                tcw.set(qn("w:w"), str(widths[j]))
                tcPr.append(tcw)
                va = OxmlElement("w:vAlign")
                va.set(qn("w:val"), "center" if i == 0 else "top")
                tcPr.append(va)
                if i == 0:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), FILL)
                    tcPr.append(shd)
                    tcb = OxmlElement("w:tcBorders")
                    _border(tcb, "w:bottom", sz="6", color=NAVY)
                    tcPr.append(tcb)
                reorder(tcPr, "tcPr")
                for p in cell.paragraphs:
                    p.style = d.styles["Table Text"]
                    # short tables stay on one page; long ones never leave one or two rows stranded
                    if (nrows <= 8 and i < nrows - 1) or i < 3 or i == nrows - 2:
                        p.paragraph_format.keep_with_next = True
                    for r in p.runs:
                        if i == 0:
                            r.font.bold = True
                        if r.style is not None and r.style.name == "Verbatim Char":
                            r.font.size = Pt(8.5)
    for p in d.paragraphs:
        if p._p.findall(".//" + qn("w:drawing")):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
    # pandoc's equation markup has two schema slips that Word tolerates; put them right so the file validates
    M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    for mc in d.element.iter(M + "mcPr"):
        kids = sorted(list(mc), key=lambda k: 0 if k.tag == M + "count" else 1)
        for k in kids:
            mc.remove(k)
        for k in kids:
            mc.append(k)
    for rp in d.element.iter(M + "rPr"):
        if rp.find(M + "nor") is not None:
            for sty in rp.findall(M + "sty"):
                rp.remove(sty)
    cp = d.core_properties
    cp.title = "Gamma A+C: an option-market signal and a one-month trend on QQQ"
    cp.author = "TC, with Claude"
    cp.subject = "Research draft, November 2026"
    cp.keywords = "gamma exposure, trend, QQQ, deflated Sharpe ratio"
    d.save(str(path))
    return len(d.tables), sum(1 for p in d.paragraphs if p._p.findall(".//" + qn("w:drawing")))


if __name__ == "__main__":
    sys.exit("Run build_journal.py. This module holds the functions it uses.")
