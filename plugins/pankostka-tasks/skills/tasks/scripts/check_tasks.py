#!/usr/bin/env python3
"""Kontrola adresáře tasks/ ze skillu pankostka-tasks.

Použití: check_tasks.py <adresář repa | adresář tasks>...
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [identifikátor] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Úkol je adresář tasks/<Úkol>/ s článkem <Úkol>.md a pomocnými soubory -TMP. Odkaz z tasks.md, který míří mimo tasks/ (třeba na soubor s rozhodnutími), se hledá v celém repu. Bez gitu se pravidlo git přeskočí.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys
from urllib.parse import unquote

RE_WIKI = re.compile(r"(?<!!)\[\[([^\]|#]+)[^\]]*\]\]")
RE_MDLINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)>]+?\.md)>?\s*\)")
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__"}
RE_ALLOW = re.compile(r"pankostka:\s*allow\s+([a-z]+/[a-z0-9-]+(?:\s*,\s*[a-z]+/[a-z0-9-]+)*)\s*,\s*[^\s-]", re.IGNORECASE)


def is_tmp(name):
    return re.search(r"-TMP(\.[^.]*)?$", name) is not None


def tasks_dir(arg):
    arg = os.path.abspath(arg)
    return arg if os.path.basename(arg) == "tasks" else os.path.join(arg, "tasks")


def repo_articles(root):
    """Názvy všech článků v repu malými písmeny, pro odkazy z tasks.md mimo tasks/."""
    names = set()
    for top, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        names |= {f[:-3].lower() for f in files if f.lower().endswith(".md")}
    return names


def tracked(tdir):
    try:
        r = subprocess.run(["git", "ls-files", "-z", "--", "."], cwd=tdir, capture_output=True)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    return {os.path.normcase(os.path.join(tdir, p)) for p in r.stdout.decode("utf-8").split("\0") if p}


def check_dir(arg):
    """Vrátí seznam neshod (cesta, řádek, pravidlo, zpráva)."""
    tdir = tasks_dir(arg)
    index = os.path.join(tdir, "tasks.md")
    findings = []
    if not os.path.isdir(tdir):
        return [(tdir, 1, "tasks/index", "adresář tasks/ neexistuje")]

    articles = {}
    loose = []
    for n in sorted(os.listdir(tdir)):
        path = os.path.join(tdir, n)
        if is_tmp(n):
            loose.append(path)
        elif os.path.isdir(path):
            if n in SKIP_DIRS or n.startswith("."):
                continue
            article = os.path.join(path, n + ".md")
            if os.path.isfile(article):
                articles[n] = article
            else:
                findings.append((path, 1, "tasks/task-folder", f"adresář {n} nemá článek {n}/{n}.md"))
        elif n.lower().endswith(".md") and n.lower() != "tasks.md":
            # článek mimo adresář se hlásí, ale odkazy na něj platí, ať se nehlásí dvakrát
            articles[n[:-3]] = path
            findings.append((path, 1, "tasks/task-folder", f"článek úkolu leží mimo svůj adresář, přesuň ho do {n[:-3]}/{n}"))

    linked = set()
    if not os.path.isfile(index):
        findings.append((index, 1, "tasks/index", "chybí rozcestník tasks/tasks.md"))
    else:
        repo = repo_articles(os.path.dirname(tdir))
        with open(index, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
        lower = {a.lower(): a for a in articles}
        for i, line in enumerate(lines):
            targets = [m.group(1) for m in RE_WIKI.finditer(line)]
            targets += [os.path.basename(unquote(m.group(1)))[:-3] for m in RE_MDLINK.finditer(line)]
            for t in targets:
                t = t.strip().split("/")[-1]
                if t.lower() in lower:
                    linked.add(lower[t.lower()])
                elif t.lower() not in repo:
                    findings.append((index, i + 1, "tasks/index", f"odkaz [[{t}]] míří na článek, který v repu není"))

    if os.path.isfile(index):
        for name, path in articles.items():
            if name not in linked:
                findings.append((path, 1, "tasks/article-per-task", f"na úkol {name} nevede odkaz z tasks.md, doplň odrážku"))

    for path in loose:
        n = os.path.basename(path)
        findings.append((path, 1, "tasks/tmp-in-task-folder", f"{n} leží mimo adresář úkolu, přesuň ho k úkolu, nebo je to zbytek po smazaném úkolu (v gitu není, smazaný se nevrátí)"))

    known = tracked(tdir)
    if known is not None:
        for name, path in articles.items():
            if os.path.normcase(path) not in known:
                findings.append((path, 1, "tasks/in-git", f"článek úkolu {name} git nesleduje, články v tasks/ patří do gitu"))
        if os.path.isfile(index) and os.path.normcase(index) not in known:
            findings.append((index, 1, "tasks/in-git", "rozcestník tasks.md git nesleduje"))

    index_lines = lines if os.path.isfile(index) else []
    return sorted(f for f in findings if not (f[0] == index and allowed(index_lines, f[1], f[2])))


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
    if not argv:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    findings = []
    for arg in argv:
        if not os.path.isdir(arg):
            sys.exit(f"adresář neexistuje: {arg}")
        findings.extend(check_dir(arg))
    for path, line, rule, msg in findings:
        print(f"{display(path)}:{line}: [{rule}] {msg}")
    print(f"Neshod: {len(findings)}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
