#!/usr/bin/env python3
"""Kontrola adresáře tasks/ ze skillu pankostka-tasks.

Použití: check_tasks.py <adresář repa | adresář tasks>...
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Odkaz z tasks.md, který míří mimo tasks/ (třeba na soubor s rozhodnutími), se hledá v celém repu. Bez gitu se pravidlo git přeskočí.
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
        return [(tdir, 1, "index", "adresář tasks/ neexistuje")]

    articles = {}
    others = []
    for n in sorted(os.listdir(tdir)):
        path = os.path.join(tdir, n)
        if is_tmp(n):
            others.append(path)
        elif n.lower().endswith(".md") and n.lower() != "tasks.md" and os.path.isfile(path):
            articles[n[:-3]] = path

    linked = set()
    if not os.path.isfile(index):
        findings.append((index, 1, "index", "chybí rozcestník tasks/tasks.md"))
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
                    findings.append((index, i + 1, "dead", f"odkaz [[{t}]] míří na článek, který v repu není"))

    if os.path.isfile(index):
        for name, path in articles.items():
            if name not in linked:
                findings.append((path, 1, "orphan", f"na úkol {name} nevede odkaz z tasks.md, doplň odrážku"))

    for path in others:
        n = os.path.basename(path)
        if not any(n.lower().startswith(a.lower()) for a in articles):
            findings.append((path, 1, "leftover", f"{n} nepatří k žádnému úkolu, nejspíš zbytek po smazaném úkolu (v gitu není, smazaný se nevrátí)"))

    known = tracked(tdir)
    if known is not None:
        for name, path in articles.items():
            if os.path.normcase(path) not in known:
                findings.append((path, 1, "git", f"článek úkolu {name} git nesleduje, články v tasks/ patří do gitu"))
        if os.path.isfile(index) and os.path.normcase(index) not in known:
            findings.append((index, 1, "git", "rozcestník tasks.md git nesleduje"))

    return sorted(findings)


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
