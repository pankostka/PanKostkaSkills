#!/usr/bin/env python3
"""Kontrola repa proti zásadám práce s gitem ze skillu pankostka-git.

Použití: check_git.py <adresář repa>...
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Vzory v .gitignore vyhodnocuje git sám (git check-ignore). Sufix se kontroluje jen na konci názvu souborů a adresářů na disku, kromě položek -TMP.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys

ALLOWED = {"VZOR", "DRAFT", "TMP"}
RE_SUFFIX = re.compile(r"-([A-Z]{3,})$")
TEXT_EXT = {".md", ".sql", ".py", ".json", ".tmdl", ".txt", ".ps1", ".psm1", ".cmd", ".bat", ".sh", ".yml", ".yaml",
            ".xml", ".csv", ".css", ".js", ".html", ".pbir", ".platform", ".gitignore", ".gitattributes"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
PROBES = ["probe-TMP.sql", "probe-TMP", "probe-TMP/soubor.txt"]


def is_tmp(name):
    return re.search(r"-TMP(\.[^.]*)?$", name) is not None


def git(cwd, *args):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True)
    except OSError:
        return None, b""
    return r.returncode, r.stdout


def check_repo(arg):
    """Vrátí seznam neshod (cesta, řádek, pravidlo, zpráva)."""
    code, out = git(arg, "rev-parse", "--show-toplevel")
    if code != 0:
        return [(os.path.abspath(arg), 1, "gitignore", "adresář není git repo")]
    top = os.path.normpath(out.decode("utf-8").strip())
    findings = []
    gitignore = os.path.join(top, ".gitignore")

    # .gitignore pro -TMP
    for probe in PROBES:
        if git(top, "check-ignore", "-q", "--no-index", probe)[0] != 0:
            findings.append((gitignore, 1, "gitignore", f"neignoruje se {probe}, doplň vzory *-TMP.* a *-TMP"))

    # verzované soubory
    _, raw = git(top, "ls-files", "-z")
    tracked = [p for p in raw.decode("utf-8").split("\0") if p]
    for rel in tracked:
        parts = rel.split("/")
        if any(is_tmp(p) for p in parts):
            findings.append((os.path.join(top, rel), 1, "tracked", "git verzuje soubor se sufixem -TMP, odstraň ho z indexu přes git rm --cached"))
        ext = os.path.splitext(rel)[1].lower() or ("." + parts[-1].lstrip(".") if parts[-1].startswith(".") else "")
        if ext in TEXT_EXT:
            try:
                with open(os.path.join(top, rel), "rb") as f:
                    if f.read(3) == b"\xef\xbb\xbf":
                        findings.append((os.path.join(top, rel), 1, "bom", "soubor je v UTF-8 s BOM, ulož ho bez BOM"))
            except OSError:
                pass

    # sufixy na disku: jen poslední část názvu, soubory a adresáře -TMP v gitu nejsou a přeskočí se
    for root, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_tmp(d)]
        for name in dirs + [f for f in files if not is_tmp(f)]:
            stem = name if name in dirs else os.path.splitext(name)[0]
            m = RE_SUFFIX.search(stem)
            if m and m.group(1) not in ALLOWED:
                findings.append((os.path.join(root, name), 1, "suffix", f"sufix -{m.group(1)} není povolený, používej jen -VZOR, -DRAFT a -TMP"))

    # commit zprávy
    _, log = git(top, "log", "-50", "--format=%h%x00%s%x01")
    for entry in log.decode("utf-8", errors="replace").split("\x01"):
        entry = entry.strip("\n")
        if "\0" not in entry:
            continue
        sha, subject = entry.split("\0", 1)
        if subject.startswith("﻿"):
            findings.append((top, 1, "message", f"commit {sha}: subject začíná BOM, zpráva šla rourou z PowerShellu, předávej ji souborem"))
        elif subject.startswith("@") or subject.startswith("EOF"):
            findings.append((top, 1, "message", f"commit {sha}: subject začíná {subject[:3]}, syntaxe víceřádkového textu nesedí se shellem"))

    # hooky
    hooks = os.path.join(top, "hooks")
    if os.path.isdir(hooks) and os.listdir(hooks):
        _, path = git(top, "config", "core.hooksPath")
        if path.decode("utf-8").strip().rstrip("/\\") != "hooks":
            findings.append((hooks, 1, "hooks", "repo má hooks/, ale core.hooksPath na něj nemíří, hook se nespustí. Zapni ho: git config core.hooksPath hooks"))

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
        findings.extend(check_repo(arg))
    for path, line, rule, msg in findings:
        print(f"{display(path)}:{line}: [{rule}] {msg}")
    print(f"Neshod: {len(findings)}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
