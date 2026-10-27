#!/usr/bin/env python3
"""Kontrola skriptů nasazovaných do Heliosu Nephrite ze skillu pankostka-nephrite.

Použití: check_nephrite.py <soubor|adresář>... | --changed
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Pravidla se kontrolují jen v kódu mimo komentáře a řetězce, dynamické SQL proto posuzuje model.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys

RE_CREATE = re.compile(r"\bCREATE\s+(?:OR\s+ALTER\s+)?(PROC|PROCEDURE|FUNCTION|VIEW|TRIGGER|TABLE)\s+((?:\[?(\w+)\]?\s*\.\s*)?\[?([#\w]+)\]?)", re.IGNORECASE)
RE_WRITE = re.compile(r"\b(INSERT\s+(?:INTO\s+)?|UPDATE\s+|DELETE\s+(?:FROM\s+)?|MERGE\s+(?:INTO\s+)?)\[?lcs\]?\s*\.\s*\[?(\w+)\]?", re.IGNORECASE)
RE_NONSUBJ = re.compile(r"\[?cislo_nonsubjektu\]?\s+\[?int\]?\s+(?:NOT\s+NULL\s+)?IDENTITY", re.IGNORECASE)
RE_FK = re.compile(r"\b(FOREIGN\s+KEY|REFERENCES)\b", re.IGNORECASE)
SYSTEM = {"subjekty", "organizace", "uhrady", "poradace"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def is_tmp(name):
    return re.search(r"-TMP(\.[^.]*)?$", name) is not None


def blank(text):
    """Nahradí komentáře a řetězce mezerami. Konce řádků zůstanou, aby seděla čísla řádků."""
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
            out.append("'" + keep(text[i + 1:j - 1]) + "'" if j - i >= 2 else keep(text[i:j]))
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


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


def statement_end(code, start):
    """Konec příkazu: středník, GO na samostatném řádku, nebo prázdný řádek."""
    m = re.compile(r";|^\s*GO\s*$|\n\s*\n", re.MULTILINE | re.IGNORECASE).search(code, start)
    return m.start() if m else len(code)


def check_file(path):
    """Vrátí seznam neshod (řádek, pravidlo, zpráva)."""
    findings = []
    text = read(path)
    code = blank(text)

    m = re.search(r"/\*{6} Object:", text)
    if m:
        findings.append((line_of(text, m.start()), "dump", "zbytek dumpu ze SSMS s časovým razítkem, řádek smaž"))

    objects = [m for m in RE_CREATE.finditer(code) if not m.group(4).startswith("#")]
    if objects:
        first = re.search(r"\S+", code)
        if not first or first.group().upper() != "USE":
            findings.append((1, "use", "skript zakládá objekt v Heliosu, ale nezačíná USE [<databáze>] s poznámkou o serveru"))

    for m in objects:
        kind, schema, name = m.group(1).upper(), (m.group(3) or ""), m.group(4)
        line = line_of(code, m.start())
        if schema.lower() != "lcs":
            where = f"je ve schématu {schema}" if schema else "nemá schéma"
            findings.append((line, "schema", f"{kind} {name} {where}, objekty Heliosu patří do schématu lcs"))

        if kind.startswith("PROC") and "@system_inputrecordnumber" in code[m.end():m.end() + 400].lower():
            body = code[m.end():]
            if not re.search(r"\bIF\b[^\n]*@System_InputRecordNumber", body, re.IGNORECASE):
                findings.append((line, "nsp", f"NSP procedura {name} nekontroluje @System_InputRecordNumber, chybí odmítnutí spuštění nad jedním záznamem (nebo nad celým přehledem)"))
            if not re.search(r"\bRAISERROR\s*\([^)]*,\s*18\s*,", body, re.IGNORECASE):
                findings.append((line, "nsp", f"NSP procedura {name} nehlásí chybu přes RAISERROR(..., 18, 1)"))
            if not re.search(rf"\bGRANT\s+EXECUTE\s+ON\s+(?:OBJECT::)?\[?lcs\]?\s*\.\s*\[?{re.escape(name)}\]?", code, re.IGNORECASE):
                findings.append((line, "nsp", f"NSP procedura {name} nemá na konci GRANT EXECUTE, uživateli nepojede"))

        if kind == "TABLE" and schema.lower() == "lcs":
            if not RE_NONSUBJ.search(code[m.end():statement_end(code, m.end()) + 2000]):
                findings.append((line, "table", f"vlastní tabulka {name} nemá primární klíč cislo_nonsubjektu INT IDENTITY, Helios ji na přehled nenapojí"))
            fk = RE_FK.search(code)
            if fk:
                findings.append((line_of(code, fk.start()), "table", f"vlastní tabulka {name} má cizí klíč, zablokoval by zápis Heliosu"))

    for m in RE_WRITE.finditer(code):
        table = m.group(2).lower()
        line = line_of(code, m.start())
        verb = m.group(1).split()[0].upper()
        if table in SYSTEM or table.startswith("qn_"):
            findings.append((line, "write", f"{verb} do systémové tabulky lcs.{table}, do systémových tabulek Heliosu se nezapisuje"))
        elif table == "noris_gs_main" and verb == "UPDATE":
            stmt = code[m.start():statement_end(code, m.end())]
            if not re.search(r"\bexpression\s+like\b", stmt, re.IGNORECASE):
                findings.append((line, "write", "UPDATE lcs.noris_gs_main bez omezení na vlastní sloupce (and expression like ...), přepsal by sloupce Heliosu"))

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
