#!/usr/bin/env python3
"""Převod wikilinků na standardní odkazy s relativní cestou podle pravidla md/no-wikilink ze skillu pankostka-md.

Použití: convert_wikilinks.py <adresář vaultu>... [--make]
Bez --make jen vypíše, co by změnil. S --make změny zapíše.
Výstup: soubor:řádek: před -> po, a soubor:řádek: ponecháno: důvod u wikilinku, který převést nejde.
Návratový kód: 0 bez ponechaných wikilinků, 1 s ponechanými, 2 chybné použití.

Cíl se hledá v celém adresáři z argumentu jako v Obsidianu: podle názvu, nebo podle cesty od kořene. Nejednoznačný a neexistující cíl se nepřevádí.
Bloky kódu, inline kód a komentáře se nemění. Vložení článku ![[...]] zůstává, standardní Markdown nic takového nezná. Vložený obrázek dostane prázdný popis, doplní ho člověk podle md/image-markdown-alt.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_md  # noqa: E402

RE_LINK = re.compile(r"(!?)\[\[([^\]|#^]*)((?:#[^\]|]*)?)(?:\\?\|([^\]]*))?\]\]")


def build_index(root):
    """Soubory v adresáři: malými písmeny název, název bez .md, cesta od kořene i bez .md -> [cesty]."""
    index = {}
    for top, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in check_md.SKIP_DIRS]
        for n in names:
            path = os.path.join(top, n)
            rel = os.path.relpath(path, root).replace("\\", "/")
            keys = {n.lower(), rel.lower()}
            if n.lower().endswith(".md"):
                keys |= {n[:-3].lower(), rel[:-3].lower()}
            for k in keys:
                index.setdefault(k, []).append(path)
    return index


def resolve(target, index, source):
    """Cesta cíle, nebo (None, důvod). Ze dvou stejných názvů vyhrává ten ve složce odkazujícího článku, jako v Obsidianu."""
    hits = sorted(set(index.get(target.lower(), [])))
    if not hits:
        return None, f"cíl {target} ve vaultu není"
    if len(hits) > 1:
        here = [h for h in hits if os.path.dirname(h) == os.path.dirname(source)]
        if len(here) != 1:
            return None, f"cíl {target} je ve vaultu {len(hits)}x, převeď ho ručně"
        hits = here
    return hits[0], None


def convert_line(line, cleaned, index, source):
    """Vrátí (nový řádek, [(před, po)], [důvod ponechání])."""
    changes, kept = [], []
    out = line
    for m in reversed(list(RE_LINK.finditer(cleaned))):
        embed, target, heading, alias = m.group(1), m.group(2).strip().rstrip("\\"), m.group(3), m.group(4)
        before = line[m.start():m.end()]
        if not target:
            kept.append(f"{before} je odkaz na nadpis v témž článku, kotva má v každém nástroji jiný tvar, převeď ho ručně")
            continue
        ext = os.path.splitext(target)[1].lower()
        image = ext in check_md.IMAGE_EXT
        if embed and not image:
            kept.append(f"{before} je vložení článku, standardní Markdown ho nezná, nahraď ho ručně odkazem nebo textem")
            continue
        path, why = resolve(target, index, source)
        if path is None:
            kept.append(f"{before}: {why}")
            continue
        rel = check_md.quote_path(os.path.relpath(path, os.path.dirname(source)).replace("\\", "/"))
        if image:
            after = f"![]({rel})"
            if alias:
                kept.append(f"{before}: velikost {alias.strip()} se nepřevádí")
        else:
            name = os.path.basename(target)
            if name.lower().endswith(".md"):
                name = name[:-3]
            text = (alias or "").strip() or name
            after = f"[{text}]({rel})"
            if heading:
                kept.append(f"{before}: odkaz vede na článek, nadpis {heading} se zahodil")
        out = out[:m.start()] + after + out[m.end():]
        changes.append((before, after))
    return out, changes[::-1], kept[::-1]


def convert_file(path, index):
    """Vrátí (nový obsah nebo None, [(řádek, před, po)], [(řádek, důvod)])."""
    with open(path, "rb") as f:
        data = f.read()
    bom = data[:3] == b"\xef\xbb\xbf"
    try:
        text = data[3 if bom else 0:].decode("utf-8")
    except UnicodeDecodeError:
        return None, [], [(1, "soubor není v UTF-8, nepřevádí se")]
    lines, fm_end, skip = check_md.split_lines(text)
    raw = text.split("\n")
    changes, kept = [], []
    for i in range(fm_end, len(lines)):
        if skip[i] or "[[" not in lines[i]:
            continue
        cleaned = check_md.clean(lines[i]).ljust(len(lines[i]))
        new, ch, kp = convert_line(lines[i], cleaned, index, path)
        changes += [(i + 1, b, a) for b, a in ch]
        kept += [(i + 1, k) for k in kp]
        if ch:
            raw[i] = new + ("\r" if raw[i].endswith("\r") else "")
    if not changes:
        return None, changes, kept
    return (b"\xef\xbb\xbf" if bom else b"") + "\n".join(raw).encode("utf-8"), changes, kept


def is_note(why):
    """Upozornění u převedeného odkazu, ne důvod, proč zůstal wikilink."""
    return why.endswith(("se zahodil", "se nepřevádí"))


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    make = "--make" in argv
    dirs = [a for a in argv if a != "--make"]
    if not dirs:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    files = total = left = 0
    for d in dirs:
        if not os.path.isdir(d):
            sys.exit(f"adresář neexistuje: {d}")
        index = build_index(d)
        for path in sorted(p for p in check_md.collect([d]) if p.lower().endswith(".md")):
            content, changes, kept = convert_file(path, index)
            for line, before, after in changes:
                print(f"{check_md.display(path)}:{line}: {before} -> {after}")
            for line, why in kept:
                label = "upozornění" if is_note(why) else "ponecháno"
                print(f"{check_md.display(path)}:{line}: {label}: {why}")
            total += len(changes)
            left += sum(1 for _, w in kept if not is_note(w))
            if content is not None:
                files += 1
                if make:
                    with open(path, "wb") as f:
                        f.write(content)
    verb = "Převedeno" if make else "K převodu (bez --make se nic nezapsalo)"
    print(f"{verb}: {total} odkazů v {files} souborech, ponecháno: {left}", file=sys.stderr)
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
