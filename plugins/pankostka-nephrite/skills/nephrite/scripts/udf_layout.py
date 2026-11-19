#!/usr/bin/env python3
"""Rozložení polí formulářové šablony Heliosu (UDF) do mřížky, ze skillu pankostka-nephrite.

Použití:
  udf_layout.py <šablona.xml>                 rozložení všech oddílů
  udf_layout.py <před.xml> <po.xml>           jen oddíly, kde se rozložení změnilo
  udf_layout.py <skript.sql>                  totéž pro skript úpravy: porovná XML z bloku vrácení (před) s novým XML (po)

Oddíl (<tab>) má TableColumns buněk na řádek, pole (<column>) zabere ColSpan buněk (výchozí 1).
Pole se skládají zleva doprava po řádcích. Když se pole do zbytku řádku nevejde, začne na novém řádku
a zbytek řádku zůstane prázdný. ColSpan větší než TableColumns se ořízne na šířku oddílu.
Výpis ukazuje každý řádek mřížky: jméno pole, za ním *N při ColSpan > 1, prázdná buňka je '.'.
Jen standardní knihovna.
"""
import re
import sys
import xml.etree.ElementTree as ET

NS = "{http://tempuri.org/DataForm.Frm.xsd}"


def tag(el):
    return el.tag.replace(NS, "")


def layout(xml_text):
    """Vrátí seznam (popis oddílu, řádky, varování); řádek je seznam buněk."""
    root = ET.fromstring(xml_text.encode("utf-8"))
    default_cols = int(root.get("TableColumns") or 1)
    result = []
    page = ""
    for tab in root:
        if tag(tab) != "tab":
            continue
        if tab.get("TabPageLabel") and not (tab.get("RenderAs") or "").startswith("DesignTab"):
            page = tab.get("TabPageLabel")
        cols = int(tab.get("TableColumns") or default_cols)
        rows, row, warn = [], [], []
        for col in tab:
            if tag(col) != "column":
                continue
            name = col.get("Name") or "?"
            span = int(col.get("ColSpan") or 1)
            if span > cols:
                warn.append(f"{name}: ColSpan {span} > TableColumns {cols}")
                span = cols
            used = sum(s for _, s in row)
            if used + span > cols:
                rows.append(row)
                row = []
            row.append((name, span))
            if sum(s for _, s in row) == cols:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        cells = []
        for r in rows:
            line = [n + (f"*{s}" if s > 1 else "") for n, s in r]
            line += ["."] * (cols - sum(s for _, s in r))
            cells.append(line)
        label = f"{tab.get('Name') or '(bez jména)'} [záložka {page or '-'}, TableColumns={cols}]"
        result.append((tab.get("Name") or str(len(result)), label, cells, warn))
    return result


def show(label, cells, warn, prefix=""):
    print(f"{prefix}{label}")
    for i, line in enumerate(cells, 1):
        print(f"{prefix}  {i:>2}: " + " | ".join(line))
    for w in warn:
        print(f"{prefix}  POZOR {w}")


def from_sql(path):
    text = open(path, encoding="utf-8").read()
    lits = [m.replace("''", "'") for m in re.findall(r"N'(<\?xml.*?)'(?=\s*\r?\n)", text, re.S)]
    if len(lits) < 2:
        sys.exit("Ve skriptu nejsou dva literály XML (nové XML a blok vrácení).")
    return lits[-1], lits[0]


def main():
    args = sys.argv[1:]
    if len(args) == 1 and args[0].lower().endswith(".sql"):
        before, after = from_sql(args[0])
    elif len(args) == 1:
        for _, label, cells, warn in layout(open(args[0], encoding="utf-8").read()):
            if cells:
                show(label, cells, warn)
        return
    elif len(args) == 2:
        before, after = (open(a, encoding="utf-8").read() for a in args)
    else:
        sys.exit(__doc__)
    b = {k: (l, c, w) for k, l, c, w in layout(before)}
    a = {k: (l, c, w) for k, l, c, w in layout(after)}
    changed = 0
    for k in list(b) + [k for k in a if k not in b]:
        if b.get(k, (None, None))[1] == a.get(k, (None, None))[1]:
            continue
        changed += 1
        print("=" * 60)
        if k in b:
            show(*b[k], prefix="PŘED ")
        if k in a:
            show(*a[k], prefix="PO   ")
    print(f"Změněných oddílů: {changed}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
