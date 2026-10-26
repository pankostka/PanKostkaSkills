#!/usr/bin/env python3
"""Kontrola mechanických pravidel T-SQL ze skillu tsql.

Použití: check.py <soubor|adresář>... | --changed
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Pravidla kontroluje jen v kódu mimo komentáře a řetězce. Dynamické SQL uvnitř řetězců proto neprojde a musí ho posoudit model.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys

RE_CREATE = re.compile(r"\bCREATE\s+(?!OR\s+ALTER\b)(PROC|PROCEDURE|FUNCTION|VIEW|TRIGGER)\b", re.IGNORECASE)
RE_WHERE = re.compile(r"\bWHERE\b", re.IGNORECASE)
RE_ONE_EQ_ONE = re.compile(r"\s*1\s*=\s*1\b")


def keep_newlines(s):
    return re.sub(r"[^\n]", " ", s)


def blank_comments_and_strings(text):
    """Nahradí komentáře a řetězce mezerami. Konce řádků nechá, aby seděla čísla řádků."""
    out = []
    i, n = 0, len(text)
    while i < n:
        two = text[i:i + 2]
        if two == "--":
            j = text.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        elif two == "/*":
            # blokové komentáře se v T-SQL dají vnořovat
            depth, j = 1, i + 2
            while j < n and depth:
                if text[j:j + 2] == "/*":
                    depth, j = depth + 1, j + 2
                elif text[j:j + 2] == "*/":
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            out.append(keep_newlines(text[i:j]))
            i = j
        elif text[i] == "'":
            # zdvojený apostrof je escapovaný apostrof uvnitř řetězce
            j = i + 1
            while j < n:
                if text[j] == "'":
                    if text[j + 1:j + 2] == "'":
                        j += 2
                        continue
                    j += 1
                    break
                j += 1
            out.append(keep_newlines(text[i:j]))
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def read_text(path, findings):
    """Načte soubor jako UTF-8. Při jiném kódování zapíše neshodu a vrátí None."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff") or b"\x00" in data[:4096]:
        findings.append((1, "encoding", "soubor je v UTF-16, nic v něm neupravuj, nejdřív ho převeď do UTF-8 bez BOM"))
        return None
    if data[:3] == b"\xef\xbb\xbf":
        findings.append((1, "encoding", "UTF-8 s BOM, ulož bez BOM"))
        data = data[3:]
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        findings.append((data.count(b"\n", 0, e.start) + 1, "encoding", "soubor není v UTF-8, nic v něm neupravuj, nejdřív ho převeď"))
        return None


def check_file(path):
    """Vrátí seznam neshod (řádek, pravidlo, zpráva)."""
    findings = []
    text = read_text(path, findings)
    if text is None:
        return findings
    code = blank_comments_and_strings(text)

    for m in RE_CREATE.finditer(code):
        findings.append((line_of(code, m.start()), "create", f"CREATE {m.group(1).upper()} bez OR ALTER, použij CREATE OR ALTER"))

    for m in RE_WHERE.finditer(code):
        if not RE_ONE_EQ_ONE.match(code, m.end()):
            findings.append((line_of(code, m.start()), "where", "WHERE nezačíná 1=1, podmínky připoj níž jako AND"))

    findings.sort()
    return findings


def changed_files():
    """Soubory .sql, které git hlásí jako změněné nebo nové, relativně k aktuálnímu adresáři."""
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
        if "D" in status or not path.lower().endswith(".sql"):
            continue
        files.append(os.path.join(top, path))
    return files


def collect(args):
    files = []
    for arg in args:
        if os.path.isdir(arg):
            for root, dirs, names in os.walk(arg):
                dirs[:] = [d for d in dirs if d != ".git"]
                files.extend(os.path.join(root, n) for n in names if n.lower().endswith(".sql"))
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
