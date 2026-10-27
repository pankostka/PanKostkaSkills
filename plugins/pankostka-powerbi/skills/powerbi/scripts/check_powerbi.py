#!/usr/bin/env python3
"""Kontrola mechanických pravidel sémantického modelu v TMDL ze skillu pankostka-powerbi.

Použití: check_powerbi.py <adresář|soubor.tmdl>... | --changed
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [identifikátor] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Čte jen soubory .tmdl, každý samostatně. Reporty PBIR kontrolují validate_pbir.py a validate_pbir_corpus.py.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys

RE_KEY = re.compile(r"Dim\w*ID")
RE_ROLE = re.compile(r"Role[A-Z][A-Za-z0-9]*")
RE_SELECT = re.compile(r"Select[A-Z][A-Za-z0-9]*(_TI)?")
SHIFT = r"(?:LY|LQ|LM|[DWMQY]-\d+)"
CUMUL = r"(?:YTD|QTD|MTD|R\d+[DWMQY])"
RE_OP_BEFORE = re.compile(rf"[△%](?:{SHIFT}|{CUMUL})(?!\w)")
RE_SHIFT_FIRST = re.compile(rf"(?<!\w){SHIFT}\s+{CUMUL}(?!\w)")
MEMBERS = {"column", "measure", "hierarchy", "partition", "calculationGroup", "calculationItem"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def parse_name(rest):
    """Vrátí (jméno, v apostrofech?) z textu za klíčovým slovem. Rovnítko mimo apostrofy končí jméno."""
    rest = rest.strip()
    if rest.startswith("'"):
        i, out = 1, []
        while i < len(rest):
            if rest[i] == "'":
                if rest[i + 1:i + 2] == "'":
                    out.append("'")
                    i += 2
                    continue
                break
            out.append(rest[i])
            i += 1
        return "".join(out), True
    return rest.split("=")[0].strip(), False


class Member:
    def __init__(self, kind, name, quoted, line):
        self.kind, self.name, self.quoted, self.line = kind, name, quoted, line
        self.props = {}


def indent_of(line):
    return len(line) - len(line.lstrip("\t"))


def check_member(table, m, findings):
    p = m.props
    if m.kind == "column":
        src = p.get("sourceColumn", "").strip("[]")
        if RE_KEY.fullmatch(src) and m.name != src:
            findings.append((m.line, "powerbi/key-keep-name", f"klíč {src} je přejmenovaný na {m.name}, klíč si drží fyzický název"))
        hidden = "isHidden" in p and p["isHidden"].lower() != "false"
        if table and table.name.startswith("Fact") and hidden and p.get("isAvailableInMdx", "").lower() != "false":
            findings.append((m.line, "powerbi/fact-hidden-no-mdx", f"skrytý sloupec {m.name} faktovky nemá isAvailableInMdx: false (zapiš ho za formatString)"))
        if "ParameterMetadata" in p.get("extendedProperty", "") and table:
            table.is_param = True
    elif m.kind == "measure":
        if "formatString" not in p and "formatStringDefinition" not in p:
            findings.append((m.line, "powerbi/measure-format-folder", f"míra {m.name} nemá formatString (textová míra ho nepotřebuje)"))
        if "displayFolder" not in p:
            findings.append((m.line, "powerbi/measure-format-folder", f"míra {m.name} není v display folderu"))
        if RE_OP_BEFORE.search(m.name):
            findings.append((m.line, "powerbi/measure-token-order", f"míra {m.name}: operátor △ nebo % patří za časový token, třeba HV LY△"))
        if RE_SHIFT_FIRST.search(m.name):
            findings.append((m.line, "powerbi/measure-token-order", f"míra {m.name}: nejdřív kumulace, pak posun, třeba HV YTD LY"))
    elif m.kind == "hierarchy":
        if not m.name.startswith("@"):
            findings.append((m.line, "powerbi/hierarchy-at", f"hierarchie {m.name} nemá prefix @"))
        elif m.quoted and re.fullmatch(r"@\w+", m.name):
            findings.append((m.line, "powerbi/hierarchy-at", f"hierarchie '{m.name}' má zbytečné apostrofy, piš je jen při mezeře v názvu"))


def check_table(t, findings):
    if not t.name.isascii():
        findings.append((t.line, "powerbi/table-no-diacritics", f"tabulka {t.name} má v názvu diakritiku"))
    if t.is_param:
        if not RE_SELECT.fullmatch(t.name.rstrip("AB")) and not RE_SELECT.fullmatch(t.name):
            findings.append((t.line, "powerbi/select-name", f"field parameter {t.name} není ve tvaru Select[Dim]<Rozsah>[_TI][A|B]"))
        elif re.search(r"All(_TI)?[AB]?$", t.name):
            findings.append((t.line, "powerbi/select-name", f"field parameter {t.name} má sufix All, pojmenuj rozsah podle reportu nebo tématu"))


def check_file(path):
    """Vrátí seznam neshod (řádek, pravidlo, zpráva)."""
    findings = []
    with open(path, "rb") as f:
        data = f.read()
    if data[:3] == b"\xef\xbb\xbf":
        data = data[3:]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [(1, "powerbi/utf8-no-bom", "soubor není v UTF-8")]
    table = member = None
    member_indent = 0
    in_fence = False
    for i, raw in enumerate(text.split("\n")):
        line = raw.rstrip("\r")
        s = line.strip()
        if in_fence:
            in_fence = s.count("```") % 2 == 0
            continue
        if s.count("```") % 2 == 1:
            in_fence = True
        if not s or s.startswith("///"):
            continue
        ind = indent_of(line)
        word, _, rest = s.partition(" ")
        if ind == 0:
            if member:
                check_member(table, member, findings)
                member = None
            if table:
                check_table(table, findings)
                table = None
            if word == "table":
                name, quoted = parse_name(rest)
                table = Member("table", name, quoted, i + 1)
                table.is_param = False
            elif word == "role":
                name, _ = parse_name(rest)
                if not RE_ROLE.fullmatch(name):
                    findings.append((i + 1, "powerbi/role-name", f"role {name} není ve tvaru Role<Model><Skupina>"))
            continue
        if word in MEMBERS and table and (member is None or ind <= member_indent):
            if member:
                check_member(table, member, findings)
            name, quoted = parse_name(rest)
            member, member_indent = Member(word, name, quoted, i + 1), ind
            continue
        if member and ind == member_indent + 1:
            key, sep, value = s.partition(":")
            key = key.split()[0] if key else key
            if key == "extendedProperty":
                member.props[key] = member.props.get(key, "") + " " + s
            else:
                member.props.setdefault(key, value.strip() if sep else "")
    if member:
        check_member(table, member, findings)
    if table:
        check_table(table, findings)
    findings.sort()
    return findings


def changed_files():
    """Soubory .tmdl, které git hlásí jako změněné nebo nové."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
        raw = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], capture_output=True, check=True, cwd=top).stdout
    except (OSError, subprocess.CalledProcessError):
        sys.exit("--changed: aktuální adresář není v git repu")
    entries = raw.decode("utf-8").split("\0")
    files, i = [], 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            i += 1  # za přejmenováním následuje původní cesta
        if "D" in status or not path.lower().endswith(".tmdl"):
            continue
        files.append(os.path.join(top, path))
    return files


def collect(args):
    files = []
    for arg in args:
        if os.path.isdir(arg):
            for root, dirs, names in os.walk(arg):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                files.extend(os.path.join(root, n) for n in names if n.lower().endswith(".tmdl"))
        elif os.path.isfile(arg):
            files.append(arg)
        else:
            sys.exit(f"cesta neexistuje: {arg}")
    return files


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
    files = changed_files() if argv == ["--changed"] else collect(argv)
    total = 0
    for path in sorted(files):
        for line, rule, msg in check_file(path):
            print(f"{display(path)}:{line}: [{rule}] {msg}")
            total += 1
    print(f"Souborů: {len(files)}, neshod: {total}", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
