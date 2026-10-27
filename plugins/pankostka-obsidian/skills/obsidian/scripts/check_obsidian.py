#!/usr/bin/env python3
"""Kontrola vaultu v Obsidianu ze skillu pankostka-obsidian.

Použití: check_obsidian.py <adresář vaultu>...
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Kontroluje vault, jeho vnořené vaulty a jejich řádky v .gitignore. Vzory v .gitignore vyhodnocuje git sám (git check-ignore), bez gitu se pravidla gitignore a tracked přeskočí.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import json
import os
import re
import subprocess
import sys

SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", "__pycache__"}
# výchozí hodnota Obsidianu, když klíč v app.json chybí, a hodnota, kterou skill vyžaduje
REQUIRED = {
    "attachmentFolderPath": ("/", "./Attachments"),
    "newLinkFormat": ("shortest", "shortest"),
    "alwaysUpdateLinks": (False, True),
    "showUnsupportedFiles": (False, False),
}
FILE_KEYS = ("attachmentFolderPath", "newLinkFormat", "alwaysUpdateLinks")
# cesta v .obsidian -> má ji .gitignore ignorovat?
IGNORE_PROBES = [
    ("plugins/plugin/main.js", True, "kód pluginu plugins/*/main.js"),
    ("plugins/plugin/styles.css", True, "styl pluginu plugins/*/styles.css"),
    ("themes/tema/theme.css", True, "témata themes/"),
    ("workspace.json", True, "stav oken workspace.json"),
    ("workspaces.json", True, "stav oken workspaces.json"),
    ("plugins/plugin/manifest.json", False, "manifest pluginu, tedy celé plugins/"),
    ("app.json", False, "nastavení app.json, tedy celé .obsidian/"),
]


def is_tmp(name):
    return re.search(r"-TMP(\.[^.]*)?$", name) is not None


def is_vault(d):
    return os.path.isdir(os.path.join(d, ".obsidian"))


def find_vault(start):
    d = os.path.abspath(start)
    while True:
        if is_vault(d):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def nested_vaults(vault):
    out = []
    for top, dirs, _ in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_tmp(d)]
        if top != vault and is_vault(top):
            out.append(top)
    return out


def load_app(vault, findings):
    """Načte app.json. Vrátí (slovník, text) nebo ({}, '') a zapíše neshodu, když je soubor vadný."""
    path = os.path.join(vault, ".obsidian", "app.json")
    if not os.path.isfile(path):
        return {}, ""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:
        return json.loads(text), text
    except ValueError:
        findings.append((path, 1, "settings", "app.json není platný JSON"))
        return {}, text


def line_of_key(text, key):
    for i, line in enumerate(text.splitlines()):
        if f'"{key}"' in line:
            return i + 1
    return 1


def effective(app, key):
    return app.get(key, REQUIRED[key][0])


def fmt(value):
    return json.dumps(value, ensure_ascii=False)


def check_settings(vault, app, text, parent_app, findings):
    path = os.path.join(vault, ".obsidian", "app.json")
    for key, (default, wanted) in REQUIRED.items():
        value = effective(app, key)
        if parent_app is not None and key in FILE_KEYS and value != effective(parent_app, key):
            findings.append((path, line_of_key(text, key), "vault", f"vnořený vault má {key} {fmt(value)}, nadřazený {fmt(effective(parent_app, key))}, nastav stejně"))
            continue
        if value != wanted:
            how = f"chybí, výchozí je {fmt(default)}" if key not in app else f"je {fmt(value)}"
            findings.append((path, line_of_key(text, key), "settings", f"{key} {how}, nastav {fmt(wanted)}"))
    for flt in app.get("userIgnoreFilters", []):
        if "*" in flt and not (flt.startswith("/") and flt.endswith("/") and len(flt) > 1):
            findings.append((path, line_of_key(text, "userIgnoreFilters"), "settings", f"filtr {flt} je glob, userIgnoreFilters zná jen cestu nebo /regulární výraz/"))


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def git_top(vault):
    try:
        r = git(vault, "rev-parse", "--show-toplevel")
    except OSError:
        return None
    return os.path.normpath(r.stdout.strip()) if r.returncode == 0 else None


def ignored(top, rel):
    """Vrátí zdroj vzoru, který cestu ignoruje, nebo None. Vyhodnocuje jen vzory, ne stav indexu."""
    r = git(top, "check-ignore", "-v", "--no-index", rel)
    if r.returncode != 0:
        return None
    return r.stdout.split(":", 1)[0]


def check_git(vault, findings):
    top = git_top(vault)
    if not top:
        return
    prefix = os.path.relpath(vault, top).replace("\\", "/")
    prefix = "" if prefix == "." else prefix + "/"
    gitignore = os.path.join(top, ".gitignore")
    app_source = ignored(top, prefix + ".obsidian/app.json")
    private = app_source is not None and app_source.replace("\\", "/").endswith(".git/info/exclude")

    if not private:
        for probe, should, label in IGNORE_PROBES:
            source = ignored(top, prefix + ".obsidian/" + probe)
            if should and not source:
                findings.append((gitignore, 1, "gitignore", f"neignoruje se {label}, doplň řádky z gitignore.txt"))
            elif not should and source:
                findings.append((source if os.path.isabs(source) else os.path.join(top, source), 1, "gitignore", f"ignoruje se {label}, verzuj nastavení a ignoruj jen kód pluginů, témata a stav oken"))

    tracked = git(top, "ls-files", "--", prefix + ".obsidian").stdout.splitlines()
    for rel in tracked:
        if re.search(r"\.obsidian/(plugins/[^/]+/(main\.js|styles\.css)|themes/|workspaces?\.json$)", rel) and ignored(top, rel):
            findings.append((os.path.join(top, rel), 1, "tracked", "git soubor verzuje, i když ho .gitignore ignoruje, odstraň ho z indexu přes git rm --cached"))


def first_content_line(path):
    with open(path, encoding="utf-8-sig") as f:
        lines = [l.strip() for l in f.read().splitlines()]
    if lines and lines[0] == "---":
        end = next((i for i in range(1, len(lines)) if lines[i] in ("---", "...")), 0)
        lines = lines[end + 1:]
    return next((l for l in lines if l), "")


def check_root(vault, nested, findings):
    """Vnořený vault je samostatný výstup a rozcestník mu určuje jeho obor, README.md se u něj nevyžaduje."""
    names = {n.lower(): n for n in os.listdir(vault)}
    readme = os.path.join(vault, names.get("readme.md", "README.md"))
    if "readme.md" not in names and not nested:
        findings.append((readme, 1, "root", "chybí README.md jako rozcestník vaultu"))
    for other in ("index.md", "home.md"):
        if other in names:
            findings.append((os.path.join(vault, names[other]), 1, "root", f"{names[other]} jako rozcestník, použij README.md"))
    if "menu.md" in names and "readme.md" in names and first_content_line(readme) != "![[menu]]":
        findings.append((readme, 1, "root", "menu.md existuje, ale README.md ho nevkládá prvním řádkem ![[menu]]"))


def check_vault(vault, parent):
    findings = []
    app, text = load_app(vault, findings)
    parent_app = None
    if parent:
        parent_app, _ = load_app(parent, [])
    check_settings(vault, app, text, parent_app, findings)
    check_git(vault, findings)
    check_root(vault, parent is not None, findings)
    return findings


def check_dir(arg):
    """Zkontroluje vault, do kterého patří adresář, a vaulty v něm vnořené."""
    vault = find_vault(arg)
    if not vault:
        return [(os.path.abspath(arg), 1, "vault", "adresář ani žádný nadřazený není vault, chybí .obsidian")]
    findings = []
    parent = find_vault(os.path.dirname(vault))
    for v in [vault] + nested_vaults(vault):
        p = parent if v == vault else find_vault(os.path.dirname(v))
        findings.extend(check_vault(v, p))
    return findings


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
    seen = set()
    for path, line, rule, msg in sorted(findings):
        if (path, line, rule, msg) not in seen:
            seen.add((path, line, rule, msg))
            print(f"{display(path)}:{line}: [{rule}] {msg}")
    print(f"Adresářů: {len(argv)}, neshod: {len(seen)}", file=sys.stderr)
    return 1 if seen else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
