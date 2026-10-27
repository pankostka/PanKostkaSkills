#!/usr/bin/env python3
"""Kontrola mechanických pravidel Markdownu ze skillu pankostka-md.

Použití: check_md.py <soubor|adresář>... | --changed
Výstup: jedna řádka na neshodu ve tvaru soubor:řádek: [pravidlo] zpráva.
Návratový kód: 0 bez neshod, 1 s neshodami, 2 chybné použití.

Bloky kódu, inline kód a HTML komentáře se nekontrolují. Oslovení čtenáře, umístění a názvy článků posuzuje model.
Pravidla tag a publish porovnávají články mezi sebou, cíle odkazů hledá publish v celém vaultu.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import subprocess
import sys
from urllib.parse import unquote

FORBIDDEN = {
    "—": "dlouhá pomlčka, použij spojovník, dvojtečku nebo závorku",
    "–": "polodlouhá pomlčka, použij spojovník",
    "„": "typografická uvozovka, použij obyčejnou",
    "“": "typografická uvozovka, použij obyčejnou",
    "”": "typografická uvozovka, použij obyčejnou",
    "‚": "typografický apostrof, použij obyčejný",
    "‘": "typografický apostrof, použij obyčejný",
    "’": "typografický apostrof, použij obyčejný",
    "…": "výpustka, použij tři tečky",
    "×": "znak násobení, použij x",
}
MARKER = "\U0001F310"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", "__pycache__"}
OLD_KEYS = {
    "titul": "klíč titul nástroj nečte, použij title",
    "datum": "klíč datum nástroj nečte, použij date",
    "publish": "klíč publish nástroj nečte, co jde na web, určuje marker 🌐 v názvu článku",
}

RE_FENCE = re.compile(r"^\s*(`{3,}|~{3,}|\$\$)")
RE_INLINE_CODE = re.compile(r"(`+)(.+?)\1")
RE_COMMENT = re.compile(r"<!--.*?-->")
RE_HEADING = re.compile(r"#{1,6}(\s|$)")
RE_RULE = re.compile(r"(([-*_])(\s*\2){2,}|=+)$")
RE_ITEM = re.compile(r"([-*+]|\d+[.)])(\s|$)")
RE_LINKDEF = re.compile(r"\[\^?[^\]]+\]:")
RE_WIKI = re.compile(r"(!?)\[\[([^\]|#^]*)[^\]]*\]\]")
RE_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(\s*(<[^>]+>|[^)\s]+)[^)]*\)")
RE_MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)[^)]*\)")
RE_KEY = re.compile(r"([A-Za-z_][\w-]*)\s*:(.*)$")
RE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RE_ATTACHMENT = re.compile(r"[a-z0-9_]+(\.[a-z0-9]+)+")


def is_tmp(name):
    return re.search(r"-TMP(\.[^.]*)?$", name) is not None


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


def split_lines(text):
    """Rozdělí text na řádky a označí frontmatter a řádky, které se nekontrolují (kód, komentáře)."""
    lines = [line.rstrip("\r") for line in text.split("\n")]
    fm_end = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                fm_end = j + 1
                break
    skip = [False] * len(lines)
    fence = None
    in_comment = False
    for i in range(fm_end, len(lines)):
        line = lines[i]
        if in_comment:
            skip[i] = True
            in_comment = "-->" not in line
            continue
        m = RE_FENCE.match(line)
        if fence:
            skip[i] = True
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            continue
        if m:
            skip[i] = True
            fence = m.group(1)
            continue
        rest = RE_COMMENT.sub("", line)
        if "<!--" in rest:
            in_comment = True
    return lines, fm_end, skip


def clean(line):
    """Odstraní inline kód a komentáře, délka řádku zůstane."""
    line = RE_INLINE_CODE.sub(lambda m: " " * len(m.group()), line)
    line = RE_COMMENT.sub(lambda m: " " * len(m.group()), line)
    return line.split("<!--")[0]


def block_kind(line):
    s = line.strip()
    if not s:
        return "blank"
    if s.startswith(">"):
        inner = s.lstrip(">").strip()
        if not inner:
            return "blank"
        if inner.startswith("[!") or RE_HEADING.match(inner) or inner.startswith("|") or RE_ITEM.match(inner):
            return "block"
        return "text"
    if RE_HEADING.match(s) or s.startswith("|") or RE_RULE.match(s) or s.startswith("<") or s.startswith("!["):
        return "block"
    if RE_LINKDEF.match(s):
        return "block"
    if RE_ITEM.match(s):
        return "item"
    return "text"


def hard_break(line):
    low = line.lower()
    return line.endswith("  ") or line.endswith("\\") or low.rstrip().endswith(("<br>", "<br/>", "<br />"))


def ends_sentence(line):
    """Řádek končí větou. Zalomení za celou větou není zalomení na pevnou šířku, posoudí ho model."""
    return line.rstrip().rstrip("*_`").endswith((".", "!", "?", ":"))


def check_wrap(lines, fm_end, skip, findings):
    prev = "blank"
    prev_quote = False
    reported = False
    start = 0
    for i in range(fm_end, len(lines)):
        if skip[i]:
            prev, reported = "blank", False
            continue
        line = lines[i]
        kind = block_kind(line)
        quote = line.strip().startswith(">")
        # řádek s > za obyčejným textem začíná citaci, obyčejný text za citací je její líné pokračování
        continues = kind == "text" and prev in ("text", "item") and not (quote and not prev_quote) and not hard_break(lines[i - 1]) and not ends_sentence(lines[i - 1])
        if continues:
            if not reported:
                findings.append((start + 1, "wrap", "odstavec je zalomený uprostřed věty, spoj ho do jednoho řádku"))
                reported = True
        else:
            start, reported = i, False
        prev, prev_quote = kind, quote


def check_chars(lines, skip, findings):
    for i, line in enumerate(lines):
        if skip[i]:
            continue
        found = []
        for ch in clean(line):
            if ch in FORBIDDEN and FORBIDDEN[ch] not in found:
                found.append(FORBIDDEN[ch])
        for msg in found:
            findings.append((i + 1, "chars", f"zakázaný znak: {msg}"))


def check_images(lines, fm_end, skip, findings):
    for i in range(fm_end, len(lines)):
        if skip[i]:
            continue
        line = clean(lines[i])
        for m in RE_WIKI.finditer(line):
            if m.group(1) and os.path.splitext(m.group(2).strip())[1].lower() in IMAGE_EXT:
                findings.append((i + 1, "image", f"obrázek jako ![[{m.group(2).strip()}]], použij ![Popis](Attachments/soubor.png)"))
        for m in RE_MD_IMAGE.finditer(line):
            alt, target = m.group(1).strip(), unquote(m.group(2).strip("<>"))
            if not alt:
                findings.append((i + 1, "image", f"obrázek {target} nemá popis"))
            if re.match(r"[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
                continue
            if not target.replace("\\", "/").lstrip("./").startswith("Attachments/"):
                findings.append((i + 1, "image", f"obrázek {target} neleží v Attachments/ vedle článku"))


def parse_tags(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [t.strip().strip("'\"").lstrip("#") for t in raw.split(",") if t.strip().strip("'\"")]


def is_pascal(tag):
    for part in tag.lstrip("_").split("/"):
        if not part or not part[0].isupper() or not all(c.isalnum() for c in part):
            return False
    return True


def check_frontmatter(lines, fm_end, findings):
    """Zkontroluje frontmatter a vrátí tagy jako [(řádek, tag)]."""
    tags = []
    key = None
    for i in range(1, max(fm_end - 1, 1)):
        line = lines[i]
        m = RE_KEY.match(line)
        if m:
            key, value = m.group(1), m.group(2)
            if key.lower() in OLD_KEYS:
                findings.append((i + 1, "frontmatter", OLD_KEYS[key.lower()]))
            if key == "date":
                v = value.strip().strip("'\"")
                if v and not RE_DATE.fullmatch(v):
                    findings.append((i + 1, "frontmatter", f"date {v} není ve tvaru RRRR-MM-DD"))
            if key == "tags":
                tags.extend((i + 1, t) for t in parse_tags(value))
        elif key == "tags" and line.strip().startswith("- "):
            tags.extend((i + 1, t) for t in parse_tags(line.strip()[2:]))
    for line, tag in tags:
        if not is_pascal(tag):
            findings.append((line, "frontmatter", f"tag {tag} není v PascalCase"))
    return tags


def links_of(lines, fm_end, skip):
    """Odkazy na články jako [(řádek, cíl)], bez obrázků a příloh."""
    out = []
    for i in range(fm_end, len(lines)):
        if skip[i]:
            continue
        line = clean(lines[i])
        targets = [m.group(2) for m in RE_WIKI.finditer(line)]
        targets += [unquote(m.group(1).strip("<>")) for m in RE_MD_LINK.finditer(line) if m.group(1).lower().split("#")[0].endswith(".md")]
        for t in targets:
            t = t.strip().replace("\\", "/")
            ext = os.path.splitext(t)[1].lower()
            if not t or re.match(r"[a-z][a-z0-9+.-]*:", t, re.IGNORECASE) or (ext and ext != ".md"):
                continue
            out.append((i + 1, t[:-3] if ext == ".md" else t))
    return out


def check_attachment(path):
    name = os.path.basename(path)
    if name.startswith("Pasted image"):
        return [(1, "attachment", "nepřejmenovaný obrázek z Obsidianu, přejmenuj ho malými písmeny s podtržítky")]
    if os.path.basename(os.path.dirname(path)) == "Attachments" and not RE_ATTACHMENT.fullmatch(name):
        return [(1, "attachment", "název přílohy smí mít jen malá písmena bez diakritiky, číslice a podtržítka")]
    return []


def vault_index(root):
    """Články ve vaultu: malými písmeny název i cesta bez přípony -> skutečný název."""
    index = {}
    for top, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_tmp(d)]
        for n in names:
            if n.lower().endswith(".md") and not is_tmp(n):
                rel = os.path.relpath(os.path.join(top, n), root).replace("\\", "/")[:-3]
                index.setdefault(os.path.basename(rel).lower(), []).append(os.path.basename(rel))
                index.setdefault(rel.lower(), []).append(os.path.basename(rel))
    return index


def check_paths(paths, root):
    """Vrátí {cesta: [(řádek, pravidlo, zpráva)]} pro všechny soubory včetně pravidel mezi články."""
    results = {}
    tags = {}
    public = []
    for path in paths:
        findings = []
        results[path] = findings
        if not path.lower().endswith(".md"):
            findings.extend(check_attachment(path))
            continue
        text = read_text(path, findings)
        if text is None:
            continue
        lines, fm_end, skip = split_lines(text)
        check_chars(lines, skip, findings)
        check_wrap(lines, fm_end, skip, findings)
        check_images(lines, fm_end, skip, findings)
        for line, tag in check_frontmatter(lines, fm_end, findings):
            tags.setdefault(tag.lower(), {}).setdefault(tag, []).append((path, line))
        if MARKER in os.path.basename(path):
            public.append((path, links_of(lines, fm_end, skip)))

    for variants in tags.values():
        if len(variants) < 2:
            continue
        main = max(sorted(variants), key=lambda v: len(variants[v]))
        for variant, places in variants.items():
            if variant != main:
                for path, line in places:
                    results[path].append((line, "tag", f"tag {variant} má i variantu {main} ({len(variants[main])}x), sjednoť je"))

    if public:
        index = vault_index(root)
        for path, links in public:
            for line, target in links:
                key = target.lower()
                names = index.get(key) or [n for k, v in index.items() if k.endswith("/" + key) for n in v]
                if names and not any(MARKER in n for n in names):
                    results[path].append((line, "publish", f"veřejný článek odkazuje na neveřejný [[{target}]]"))

    for findings in results.values():
        findings.sort()
    return results


def wanted(path, rel):
    """Soubor, který kontrola zajímá: článek, nebo příloha. Sufix -TMP se hledá jen v relativní části cesty."""
    name = os.path.basename(path)
    if is_tmp(name) or any(is_tmp(p) or p in SKIP_DIRS for p in re.split(r"[\\/]", os.path.dirname(rel))):
        return False
    return name.lower().endswith(".md") or name.startswith("Pasted image") or os.path.basename(os.path.dirname(os.path.abspath(path))) == "Attachments"


def git_top():
    try:
        return subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("--changed: aktuální adresář není v git repu")


def changed_files():
    """Články a přílohy, které git hlásí jako změněné nebo nové."""
    top = git_top()
    raw = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], capture_output=True, check=True, cwd=top).stdout
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
        if "D" in status or not wanted(os.path.join(top, path), path):
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


def find_root(start):
    """Nejbližší nadřazený adresář s .obsidian, jinak výchozí adresář."""
    start = os.path.abspath(start)
    if os.path.isfile(start):
        start = os.path.dirname(start)
    d = start
    while True:
        if os.path.isdir(os.path.join(d, ".obsidian")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return start
        d = parent


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
    if argv == ["--changed"]:
        files, root = changed_files(), find_root(git_top())
    else:
        files, root = collect(argv), find_root(argv[0])
    results = check_paths(sorted(files), root)
    total = 0
    for path in sorted(results):
        for line, rule, msg in results[path]:
            print(f"{display(path)}:{line}: [{rule}] {msg}")
            total += 1
    print(f"Souborů: {len(files)}, neshod: {total}", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
