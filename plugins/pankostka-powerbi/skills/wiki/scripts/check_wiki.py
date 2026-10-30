#!/usr/bin/env python3
"""Kontrola wiki kostky proti modelu ze skillu pankostka-powerbi-wiki.

Použití: check_wiki.py <Kostka | adresář kostky>
Výstup: jedna řádka na nález ve tvaru soubor:řádek: [identifikátor] zpráva.
Návratový kód: 0 bez nálezů, 1 s nálezy, 2 chybné použití.

Nic nezapisuje. Nález s výjimkou <!-- pankostka: allow <identifikátor>, <důvod> --> na řádku nebo nad ním se nehlásí. Kostka zadaná názvem se hledá jako adresář Wiki<Kostka> v aktuálním git repu, adresář kostky je jeho nadřazený a obsahuje <Kostka>.SemanticModel.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measures_table  # noqa: E402
import tmdl  # noqa: E402

SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__"}
SECTIONS = {
    "kostka": ["Vazby", "Reporty", "Aktuálnost dat"],
    "fakt": ["Dimenze", "Ukazatele", "Zdroj dat"],
    "dim": ["Kde se vyskytuje", "Zdroj dat"],
    "report": ["Stránky", "Z čeho čerpá"],
    "udrzba": ["Postup", "Na co si dát pozor"],
}
RE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RE_WIKILINK = re.compile(r"(!?)\[\[([^\]|#]+)(#[^\]|]*)?(\|[^\]]*)?\]\]")
RE_ALLOW = re.compile(r"pankostka:\s*allow\s+([a-z]+/[a-z0-9-]+(?:\s*,\s*[a-z]+/[a-z0-9-]+)*)\s*,\s*[^\s-]", re.IGNORECASE)


def is_tmp(name):
    return re.search(r"-(TMP|VZOR)(\.[^.]*)?$", name) is not None


def git(cwd, *args):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def locate(arg):
    """Vrátí (kostka, adresář kostky, adresář wiki, definition modelu) nebo ukončí skript."""
    if os.path.isdir(arg):
        kostka_dir = os.path.abspath(arg)
        kostka = os.path.basename(kostka_dir.rstrip("\\/"))
        if kostka.startswith("Wiki"):
            kostka_dir, kostka = os.path.dirname(kostka_dir), kostka[4:]
    else:
        kostka = arg
        top = git(os.getcwd(), "rev-parse", "--show-toplevel") or os.getcwd()
        kostka_dir = None
        for root, dirs, _ in os.walk(top):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_tmp(d)]
            if "Wiki" + kostka in dirs:
                kostka_dir = root
                break
        if not kostka_dir:
            sys.exit(f"adresář Wiki{kostka} v repu není")
    wiki = os.path.join(kostka_dir, "Wiki" + kostka)
    definition = measures_table.najdi_model(kostka_dir, kostka)
    if not definition:
        sys.exit(f"pod {kostka_dir} není {kostka}.SemanticModel")
    return kostka, kostka_dir, wiki, definition


def find_reports(kostka_dir, kostka):
    """Uživatelské reporty kostky: adresáře *.Report kromě testovacího <Kostka>.Report a vzorů."""
    out = {}
    for root, dirs, _ in os.walk(kostka_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for d in dirs:
            if d.endswith(".Report"):
                name = d[:-7]
                if name != kostka and not is_tmp(name):
                    out[name] = os.path.join(root, d)
    return out


def read_article(path):
    """Vrátí (řádky, frontmatter {klíč: (řádek, hodnota)}, tagy [(řádek, tag)], konec frontmatteru)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    fm, tags, end = {}, [], 0
    if lines and lines[0].strip() == "---":
        key = None
        for i in range(1, len(lines)):
            s = lines[i]
            if s.strip() in ("---", "..."):
                end = i + 1
                break
            m = re.match(r"([A-Za-z_]\w*)\s*:(.*)$", s)
            if m:
                key, value = m.group(1), m.group(2).strip()
                fm[key] = (i + 1, value.strip("'\""))
                if key == "tags" and value:
                    tags += [(i + 1, t.strip().strip("'\"").lstrip("#")) for t in value.strip("[]").split(",") if t.strip()]
            elif key == "tags" and s.strip().startswith("- "):
                tags.append((i + 1, s.strip()[2:].strip().strip("'\"").lstrip("#")))
    return lines, fm, tags, end


def last_commit(top, path):
    out = git(top, "log", "-1", "--format=%cs", "--", path)
    return out or None


def check(arg):
    kostka, kostka_dir, wiki, definition = locate(arg)
    tables, rels = tmdl.load_model(definition)
    visible = {n: t for n, t in tables.items() if not t["hidden"] and not t["param"]}
    facts = {n for n in visible if n.startswith("Fact")}
    reports = find_reports(kostka_dir, kostka)
    top = git(kostka_dir, "rev-parse", "--show-toplevel")
    findings = []
    texts = {}

    def add(path, line, rule, msg):
        findings.append((path, line, rule, msg))

    # rozcestník leží v kořeni wiki, ostatní články v adresáři svého jména (umístění hlídá pankostka-md)
    articles = {}
    if os.path.isdir(wiki):
        for n in os.listdir(wiki):
            path = os.path.join(wiki, n)
            if is_tmp(n):
                continue
            if n.endswith(".md"):
                articles[n[:-3]] = path
            elif os.path.isfile(os.path.join(path, n + ".md")):
                articles[n] = os.path.join(path, n + ".md")

    # chybějící články
    expected = {kostka: ("kostka", None)}
    for n in visible:
        expected[f"{kostka} {n}"] = ("fakt" if n in facts else "dim", n)
    for n in reports:
        expected[f"{kostka} {n}"] = ("report", n)
    for name, (kind, _) in sorted(expected.items()):
        if name not in articles:
            what = {"kostka": "rozcestník", "fakt": "faktovka", "dim": "dimenze", "report": "report"}[kind]
            add(os.path.join(wiki, name + ".md") if kind == "kostka" else os.path.join(wiki, name, name + ".md"), 1, "wiki/index-article" if kind == "kostka" else "wiki/article-per-element", f"chybí článek, {what} {name}")

    related = {}
    for a, b in rels:
        for dim, fact in ((a, b), (b, a)):
            if fact in facts and dim in visible and dim not in facts:
                related.setdefault(dim, set()).add(fact)

    for name, path in sorted(articles.items()):
        lines, fm, tags, fm_end = read_article(path)
        texts[path] = lines
        tagset = {t for _, t in tags}
        if name in expected:
            kind, obj = expected[name]
        elif "Údržba" in tagset:
            kind, obj = "udrzba", None
        elif name.startswith(kostka + " "):
            add(path, 1, "wiki/article-per-element", f"{name[len(kostka) + 1:]} v modelu ani v reportech kostky není, článek navrhni ke smazání nebo přejmenování")
            continue
        else:
            continue  # cizí článek, třeba poznámka ve wiki

        # frontmatter
        for key in ("title", "date", "tags"):
            if key not in fm:
                add(path, 1, "wiki/frontmatter", f"chybí {key}")
        want_title = kostka if kind == "kostka" else obj
        if want_title and "title" in fm and fm["title"][1] != want_title:
            add(path, fm["title"][0], "wiki/frontmatter", f"title je {fm['title'][1]}, má být {want_title}")
        date = fm.get("date", (0, ""))[1]
        if "date" in fm and not RE_DATE.fullmatch(date):
            add(path, fm["date"][0], "wiki/frontmatter", f"date {date} není ve tvaru RRRR-MM-DD")

        # tagy
        want = {"_" + kostka}
        if kind == "fakt":
            want.add("_" + obj)
        elif kind == "dim":
            want |= {obj} | {"_" + f for f in related.get(obj, ())}
        elif kind == "report":
            want |= {"_Report"} | {"_" + t for t in tmdl.report_tables(reports[obj]) if t in facts}
        elif kind == "udrzba":
            want = {"_" + kostka, "Údržba"}
        tline = fm.get("tags", (1, ""))[0]
        for t in sorted(want - tagset):
            add(path, tline, "wiki/tags", f"chybí tag {t}")
        if kind != "udrzba":
            for t in sorted(tagset - want):
                if t.startswith("_"):
                    note = ", technická vazba s klíčem vždy -1 tag nedostává" if kind == "dim" else ""
                    add(path, tline, "wiki/tags", f"tag {t} neodpovídá vazbám v modelu{note}")

        # sekce
        heads = {l[3:].strip().lower() for l in lines if l.startswith("## ")}
        for sec in SECTIONS[kind]:
            if sec.lower() not in heads:
                add(path, 1, "wiki/outline", f"chybí sekce ## {sec}")

        # model novější než revize
        if top and RE_DATE.fullmatch(date) and kind != "udrzba":
            src = {"kostka": os.path.dirname(definition), "report": reports.get(obj)}.get(kind) or (tables[obj]["file"] if obj in tables else None)
            changed = last_commit(top, src) if src else None
            if changed and changed > date:
                add(path, fm["date"][0], "wiki/revision-date", f"model se změnil {changed}, článek je revidovaný {date}")

        # odkazy bez aliasu
        for i, l in enumerate(lines):
            for m in RE_WIKILINK.finditer(l):
                if not m.group(1) and not m.group(4) and m.group(2).strip().startswith(kostka + " "):
                    add(path, i + 1, "wiki/wikilink-alias", f"odkaz [[{m.group(2).strip()}]] nemá alias, piš [[{m.group(2).strip()}|{m.group(2).strip()[len(kostka) + 1:]}]]")

        # tabulka ukazatelů
        if kind == "fakt":
            measures = measures_table.nacti_miry(tables[obj]["file"])
            if measures:
                block = measures_table.najdi_blok([l for l in lines])
                if block is None:
                    add(path, 1, "wiki/measures-table", f"článek nemá značky tabulky ukazatelů, viditelné míry faktovky: {len(measures)}")
                else:
                    log = []
                    if measures_table.aktualizuj(tables[obj]["file"], path, True, obj, out=log.append) == 1:
                        detail = "; ".join(m.strip() for m in log[1:-1]) or "jen text značky"
                        add(path, block[0] + 1, "wiki/measures-table", f"tabulka ukazatelů neodpovídá modelu: {detail}")

    return [f for f in findings if not allowed(texts.get(f[0], []), f[1], f[2])]


def allowed(lines, line, rule):
    """Výjimka komentářem <!-- pankostka: allow <identifikátor>, <důvod> --> na řádku nálezu nebo nad ním. Bez důvodu neplatí."""
    for i in (line - 1, line - 2):
        if 0 <= i < len(lines):
            m = RE_ALLOW.search(lines[i])
            if m and rule in [r.strip().lower() for r in m.group(1).split(",")]:
                return True
    return False


def display(path):
    try:
        path = os.path.relpath(path)
    except ValueError:
        pass  # jiný disk na Windows
    return path.replace("\\", "/")


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in argv if a != "--make"]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    findings = check(args[0])
    for path, line, rule, msg in sorted(findings):
        print(f"{display(path)}:{line}: [{rule}] {msg}")
    print(f"Nálezů: {len(findings)}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
