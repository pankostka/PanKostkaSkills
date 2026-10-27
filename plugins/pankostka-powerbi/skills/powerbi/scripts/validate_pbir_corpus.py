# -*- coding: utf-8 -*-
"""Diferencni kontrola PBIR reportu a TMDL modelu proti korpusu existujicich souboru.

Doplnek k validate_pbir.py. Ten kontroluje odkazy do modelu, tenhle kontroluje TVAR
souboru - tedy prave to, co validate_pbir.py ve svem README uvadi jako "co nehlasi":
nazvy vlastnosti formatovani v objects / visualContainerObjects.

Princip: neznalost objektoveho modelu Power BI se nahradi empirii. Vsechny ostatni
reporty v repu (a volitelne dalsi adresare) jsou Desktopem overene, takze plati:
kdyz se nejaka konstrukce nevyskytuje ANI JEDNOU nikde jinde, je to skoro jiste
vymyslena vec, kterou Desktop bud odmitne, nebo tiste ignoruje.

Chyta napriklad:
  - "visibility": "None" na strance (klic se ve skutecnosti neuvadi vubec)
  - vymyslene property typu grid.rowPadding, values.banded, total.bold
  - sloupec field parametru zapsany jako projekce vizualu (spravne se do projections
    pisou skutecna pole a parametr se uvadi zvlast v bloku fieldParameters)
  - prazdny radek za /// v TMDL (popis musi prilehat k objektu, jinak
    "TMDL Format Error: Unexpected line type: Empty")

Nehlasi, jestli je vec spravne pouzita - jen jestli je vubec nekde doloziteľna.
Nova konstrukce nemusi byt chyba; musi ale byt vedome overena proti dokumentaci.

Navratovy kod: 0 = nic noveho, 1 = nalezena nedolozitelna konstrukce, 2 = spatne parametry.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

# Vse od /solid nebo /expr dal je forma hodnoty, ne struktura. Bez teto normalizace
# by kazda barva zapsana jako Literal misto ThemeDataColor vyrobila falesny poplach.
_TRIM = re.compile(r"/(solid|expr)/.*$")

# U techto klicu se porovnava i konkretni hodnota, ne jen existence klice.
ENUM_KEYS = {"visibility", "type", "displayOption", "howCreated", "visualType",
             "direction", "acceptsFilterContext", "mode", "position", "preset",
             "horizontalTextAlignment", "fontWeight", "fontStyle"}

PBIR_FILES = ("page.json", "visual.json", "report.json")
_TMDL_TOK = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(:|=|$)")


def _norm(path):
    return _TRIM.sub("/<value>", path)


def _walk(node, path, paths, vals):
    if isinstance(node, dict):
        for k, v in node.items():
            p = path + "/" + k
            paths.add(_norm(p))
            if k in ENUM_KEYS and isinstance(v, str):
                vals.add((k, v))
            _walk(v, p, paths, vals)
    elif isinstance(node, list):
        for v in node:
            _walk(v, path + "/[]", paths, vals)


def _read_json(path):
    try:
        return json.load(io.open(path, encoding="utf-8"))
    except Exception:
        return None


def collect_pbir(roots, skip=()):
    skip = set(os.path.normcase(os.path.abspath(p)) for p in skip)
    paths, vals, n = set(), set(), 0
    for root in roots:
        for dirpath, _, files in os.walk(root):
            if any(os.path.normcase(os.path.abspath(dirpath)).startswith(s) for s in skip):
                continue
            for f in files:
                if f not in PBIR_FILES:
                    continue
                j = _read_json(os.path.join(dirpath, f))
                if j is None:
                    continue
                _walk(j, f[:-5], paths, vals)
                n += 1
    return paths, vals, n


def collect_tmdl(roots, skip=()):
    """Konstrukce TMDL = prvni token radku pred : nebo =, tedy blokove klicove slovo
    nebo nazev vlastnosti."""
    skip = set(os.path.normcase(os.path.abspath(p)) for p in skip)
    out, n = set(), 0
    for root in roots:
        for dirpath, _, files in os.walk(root):
            for f in files:
                if not f.endswith(".tmdl"):
                    continue
                p = os.path.join(dirpath, f)
                if os.path.normcase(os.path.abspath(p)) in skip:
                    continue
                try:
                    src = io.open(p, encoding="utf-8").read()
                except Exception:
                    continue
                for ln in src.split("\n"):
                    st = ln.strip()
                    if not st or st.startswith("///") or st.startswith("--"):
                        continue
                    m = _TMDL_TOK.match(ln)
                    if m:
                        out.add(m.group(1) + (m.group(2) if m.group(2) in (":", "=") else ""))
                n += 1
    return out, n


def dangling_descriptions(root):
    """/// je POPIS objektu a musi byt bezprostredne nad nim. Prazdny radek mezi tim
    je TMDL Format Error: Unexpected line type: Empty."""
    bad = []
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if not f.endswith(".tmdl"):
                continue
            p = os.path.join(dirpath, f)
            try:
                lines = io.open(p, encoding="utf-8").read().split("\n")
            except Exception:
                continue
            for i, ln in enumerate(lines):
                if ln.strip().startswith("///"):
                    if i + 1 >= len(lines) or lines[i + 1].strip() == "":
                        bad.append((os.path.relpath(p, root), i + 1))
    return bad


def field_parameter_tables(roots):
    """Tabulky s ParameterMetadata = field parametry."""
    found = set()
    for root in roots:
        for dirpath, _, files in os.walk(root):
            for f in files:
                if not f.endswith(".tmdl"):
                    continue
                try:
                    src = io.open(os.path.join(dirpath, f), encoding="utf-8").read()
                except Exception:
                    continue
                if "ParameterMetadata" in src:
                    m = re.search(r"^table '?([^'\n]+?)'?\s*$", src, re.M)
                    if m:
                        found.add(m.group(1).strip())
    return found


def field_parameter_misuse(report_root, fp_tables):
    """Sloupec field parametru se nesmi zapsat jako projekce vizualu - Desktop pak hlasi
    "Can't determine relationships between the fields". Ve vizualu (mimo slicer) se do
    projections pisou skutecna pole a parametr se uvadi zvlast v bloku fieldParameters,
    takze korektne pouzity parametr tahle kontrola nezachyti."""
    bad = []
    for dirpath, _, files in os.walk(report_root):
        if "visual.json" not in files:
            continue
        j = _read_json(os.path.join(dirpath, "visual.json"))
        if not j:
            continue
        v = j.get("visual", {})
        if v.get("visualType") == "slicer":
            continue
        for well, cont in v.get("query", {}).get("queryState", {}).items():
            for pr in cont.get("projections", []):
                col = pr.get("field", {}).get("Column")
                if not col:
                    continue
                ent = col.get("Expression", {}).get("SourceRef", {}).get("Entity")
                if ent in fp_tables:
                    bad.append((os.path.basename(dirpath), ent, well, v.get("visualType")))
    return bad


def repo_root():
    """Koren git repa aktualniho adresare, mimo git aktualni adresar. Skript lezi ve skillu, ne v repu."""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    except OSError:
        return os.getcwd()
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else os.getcwd()


def main():
    ap = argparse.ArgumentParser(
        description="Diferencni kontrola PBIR/TMDL proti korpusu overenych souboru.")
    ap.add_argument("--report", help="kontrolovany *.Report adresar")
    ap.add_argument("--model", help="kontrolovany *.SemanticModel adresar")
    ap.add_argument("--corpus", action="append", default=[],
                    help="adresar s overenymi soubory; lze zopakovat. "
                         "Vychozi je koren git repa aktualniho adresare.")
    ap.add_argument("--verbose", action="store_true", help="vypsat vse, ne jen prvnich 20")
    args = ap.parse_args()

    if not args.report and not args.model:
        ap.error("zadej aspon --report nebo --model")

    corpus_roots = args.corpus or [repo_root()]

    problems = 0
    cap = None if args.verbose else 20

    def show(title, items, fmt=str):
        print("\n--- %s (%d) ---" % (title, len(items)))
        for it in (items if cap is None else items[:cap]):
            print("   ", fmt(it))
        if cap is not None and len(items) > cap:
            print("    ... a dalsich %d (--verbose)" % (len(items) - cap))

    if args.report:
        cp, cv, cn = collect_pbir(corpus_roots, skip=[args.report])
        tp, tv, tn = collect_pbir([args.report])
        print("PBIR korpus: %d souboru, %d konstrukci | kontrolovano: %d souboru"
              % (cn, len(cp), tn))
        novel = sorted(p for p in tp if p not in cp)
        novel_v = sorted(v for v in tv if v not in cv)
        fp = field_parameter_tables(corpus_roots)
        misuse = field_parameter_misuse(args.report, fp)
        show("nedolozitelne struktury", novel)
        show("nedolozitelne hodnoty", novel_v, lambda kv: "%s = %r" % kv)
        show("field parametr mimo slicer", misuse,
             lambda t: "%s: %s ve wellu %s vizualu %s" % t)
        problems += len(novel) + len(novel_v) + len(misuse)

    if args.model:
        skip = [os.path.join(dp, f) for dp, _, fs in os.walk(args.model)
                for f in fs if f.endswith(".tmdl")]
        cm, cmn = collect_tmdl(corpus_roots, skip=skip)
        tm, tmn = collect_tmdl([args.model])
        print("\nTMDL korpus: %d souboru, %d konstrukci | kontrolovano: %d souboru"
              % (cmn, len(cm), tmn))
        novel_t = sorted(t for t in tm if t not in cm)
        dangling = dangling_descriptions(args.model)
        show("nedolozitelne konstrukce TMDL", novel_t)
        show("popis /// bez navazujiciho objektu", dangling,
             lambda t: "%s radek %d" % t)
        problems += len(novel_t) + len(dangling)

    print("\n" + "=" * 78)
    if problems:
        print("Nalezeno %d veci, ktere nejsou nikde jinde dolozene. Kazdou bud dolozit"
              % problems)
        print("proti dokumentaci, nebo nahradit variantou, ktera dolozena je.")
        return 1
    print("OK - vsechny pouzite konstrukce se vyskytuji i jinde v korpusu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
