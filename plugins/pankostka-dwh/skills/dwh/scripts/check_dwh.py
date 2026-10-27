#!/usr/bin/env python3
"""Kontrola konvencí datového skladu ze skillu pankostka-dwh.

Použití: check_dwh.py <soubor|adresář>... | --changed
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Vrstvu souboru určuje první adresář v cestě s prefixem 00_, 10_, 20_ nebo 30_. Odkazy mezi vrstvami se hledají i v řetězcích, protože dynamické SQL je běžné, název procedury jen v kódu.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys

RE_LAYER_DIR = re.compile(r"(00|10|20|30)_\w+")
RE_CREATE = re.compile(r"\bCREATE\s+(?:OR\s+ALTER\s+)?(PROC|PROCEDURE|FUNCTION|VIEW|TRIGGER)\s+((?:\[?\w+\]?\s*\.\s*)?\[?(\w+)\]?)", re.IGNORECASE)
RE_SCHEMA_REF = re.compile(r"(?<![\w.])\[?s(10|20|30)(\w*)\]?\s*\.", re.IGNORECASE)
RE_CONSTRAINT = re.compile(r"\bCONSTRAINT\s+\[?(\w+)\]?", re.IGNORECASE)
PREFIX = {
    "10": (r"nsp10", "nsp10"),
    "20_dim": (r"nsp20Dim", "nsp20Dim"),
    "20_fact": (r"nsp20(Fact|Alloc)", "nsp20Fact nebo nsp20Alloc"),
    "30": (r"nsp30", "nsp30"),
}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def is_tmp(name):
    return re.search(r"-TMP(\.[^.]*)?$", name) is not None


def blank(text, strings):
    """Nahradí komentáře mezerami, se strings=True i řetězce. Konce řádků zůstanou, aby seděla čísla řádků."""
    out, i, n = [], 0, len(text)
    keep = lambda s: re.sub(r"[^\n]", " ", s)
    while i < n:
        two = text[i:i + 2]
        if two == "--":
            j = text.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        elif two == "/*":
            depth, j = 1, i + 2
            while j < n and depth:
                if text[j:j + 2] == "/*":
                    depth, j = depth + 1, j + 2
                elif text[j:j + 2] == "*/":
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            out.append(keep(text[i:j]))
            i = j
        elif text[i] == "'":
            j = i + 1
            while j < n:
                if text[j] == "'":
                    if text[j + 1:j + 2] == "'":
                        j += 2
                        continue
                    j += 1
                    break
                j += 1
            if strings:
                out.append(keep(text[i:j]))
            elif j - i >= 2 and text[j - 1] == "'":
                # řetězec je dynamické SQL: jeho komentáře a vnořené řetězce se vyprázdní, kód zůstane
                out.append("'" + blank(text[i + 1:j - 1], True) + "'")
            else:
                out.append(text[i:j])
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def layer_of(path):
    """Vrátí (vrstva, adresář vrstvy, adresář pod vrstvou) podle první části cesty s prefixem 00_ až 30_."""
    parts = re.split(r"[\\/]", os.path.abspath(path))
    for i, p in enumerate(parts[:-1]):
        m = RE_LAYER_DIR.fullmatch(p)
        if m:
            return m.group(1), p, parts[i + 1] if i + 1 < len(parts) - 1 else None
    return None, None, None


def read(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    if data[:3] == b"\xef\xbb\xbf":
        data = data[3:]
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1250", errors="replace")


def check_file(path):
    """Vrátí seznam neshod (řádek, pravidlo, zpráva)."""
    findings = []
    layer, layer_dir, sub = layer_of(path)
    text = read(path)
    code = blank(text, strings=True)
    with_strings = blank(text, strings=False)
    stem = os.path.basename(path).split("-")[0]
    if stem.lower().endswith(".sql"):
        stem = stem[:-4]
    stem = stem.split(".")[-1]  # název souboru může nést i schéma, lcs.Procedura.sql

    # název procedury
    proc = None
    for m in RE_CREATE.finditer(code):
        kind, name = m.group(1).upper(), m.group(3)
        line = line_of(code, m.start())
        if kind.startswith("PROC") and proc is None:
            proc = name
            if name != stem:
                findings.append((line, "name", f"procedura {name} se jmenuje jinak než soubor ({stem}), název objektu je vše před první pomlčkou"))
            key = "20_dim" if layer_dir == "20_dim" else "20_fact" if layer_dir == "20_fact" else layer
            if key in PREFIX and not re.match(PREFIX[key][0], name):
                findings.append((line, "name", f"procedura {name} ve vrstvě {layer_dir} nemá prefix {PREFIX[key][1]}"))
            if layer == "00" and re.match(r"nsp(10|20|30)", name):
                findings.append((line, "name", f"procedura {name} v 00_common nepatří do žádné vrstvy, prefix nsp<vrstva> nemá mít"))

    # odkazy mezi vrstvami
    # vlastní mart podle adresáře Kostka<Mart> i podle procedury nsp30<Mart>, ty se mohou lišit (KostkaCashFlow a nsp30CF)
    own = set()
    if layer == "30" and sub and sub.startswith("Kostka"):
        own.add("s30" + sub[6:].lower())
    if layer == "30" and proc and proc.lower().startswith("nsp30"):
        own |= {"s30" + proc[5:].lower(), "s30" + proc[5:].split("_")[0].lower()}
    seen = set()
    for m in RE_SCHEMA_REF.finditer(with_strings):
        ref_layer, schema = m.group(1), ("s" + m.group(1) + m.group(2))
        line = line_of(with_strings, m.start())
        if layer in ("10", "20") and int(ref_layer) > int(layer):
            msg = f"vrstva {layer} čte ze schématu {schema} vyšší vrstvy"
        elif own and ref_layer == "30" and schema.lower() not in own:
            msg = f"mart {sub or proc} čte ze schématu {schema} jiného martu"
        else:
            continue
        if (line, msg) not in seen:
            seen.add((line, msg))
            findings.append((line, "layer", msg))

    # názvy klíčů
    for m in RE_CONSTRAINT.finditer(with_strings):
        name = m.group(1)
        after = with_strings[m.end():m.end() + 3].lstrip()
        if after.startswith(("'", "+")) or len(name) <= 3:
            continue  # název skládaný v dynamickém SQL
        line = line_of(with_strings, m.start())
        if layer == "20" and name.startswith("PK_Dim") and not name.endswith("ID"):
            findings.append((line, "constraint", f"{name}: primární klíč dimenze ve vrstvě 20 je PK_Dim<Entita>ID"))
        if layer == "30" and name.startswith("PK_Dim") and name.endswith("ID"):
            findings.append((line, "constraint", f"{name}: primární klíč dimenze ve vrstvě 30 je PK_Dim<Entita> bez ID na konci"))
        if layer == "30" and name.startswith("FK_") and not re.fullmatch(r"FK_Fact\w+Dim\w+", name):
            findings.append((line, "constraint", f"{name}: cizí klíč ve vrstvě 30 je FK_Fact<Entita>Dim<Entita2>"))

    findings.sort()
    return findings


def wanted(path, rel):
    if not path.lower().endswith(".sql") or is_tmp(os.path.basename(path)):
        return False
    return not any(is_tmp(p) or p in SKIP_DIRS for p in re.split(r"[\\/]", os.path.dirname(rel)))


def changed_files():
    """Soubory .sql, které git hlásí jako změněné nebo nové."""
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
        if "D" in status or not wanted(path, path):
            continue
        files.append(os.path.join(top, path))
    return files


def collect(args):
    files = []
    for arg in args:
        if os.path.isdir(arg):
            for root, dirs, names in os.walk(arg):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_tmp(d)]
                files.extend(p for p in (os.path.join(root, n) for n in names) if wanted(p, os.path.relpath(p, arg)))
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
