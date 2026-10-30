#!/usr/bin/env python3
"""Testy check_md.py ze skillu pankostka-md.

Každý test je adresář, tedy malý vault. Adresáře ok_* nesmí mít žádnou neshodu.
Adresáře ko_<popis>_* musí mít jen neshody pravidla s tím popisem a právě tolik, kolik říká text `celkem N` v některém jejich článku (bez něj 1).
Spuštění: python tests/pankostka-md/run.py
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "..", "plugins", "pankostka-md", "skills", "md", "scripts", "check_md.py")

spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
sys.path.insert(0, os.path.dirname(CHECK))
import convert_wikilinks as convert  # noqa: E402


def expected_count(case):
    for root, dirs, names in os.walk(case):
        for name in sorted(names):
            if name.endswith(".md"):
                with open(os.path.join(root, name), "rb") as f:
                    m = re.search(rb"celkem (\d+)", f.read())
                if m:
                    return int(m.group(1))
    return 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    failed = 0
    names = sorted(n for n in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, n)) and n[:3] in ("ok_", "ko_"))
    for name in names:
        case = os.path.join(HERE, name)
        results = check.check_paths(sorted(check.collect([case])), case)
        findings = [(os.path.relpath(p, case), *f) for p, fs in sorted(results.items()) for f in fs]
        if name.startswith("ok_"):
            ok = not findings
            expect = "0 neshod"
        else:
            rule = name[3:].split("_")[0]
            count = expected_count(case)
            ok = len(findings) == count and all(f[2].split("/")[-1] == rule for f in findings)
            expect = f"{count}x [{rule}]"
        print(f"{'OK  ' if ok else 'FAIL'} {name}: čekáno {expect}, nalezeno {len(findings)}")
        if not ok:
            failed += 1
            for path, line, rule, msg in findings:
                print(f"       {path}:{line}: [{rule}] {msg}")
    failed += test_convert()
    print(f"Testů: {len(names) + 1}, selhalo: {failed}")
    return 1 if failed else 0


def test_convert():
    """Převod wikilinků ve vaultu convert/: každý <článek>.md se po převodu musí shodovat s <článek>.expected vedle něj."""
    case = os.path.join(HERE, "convert")
    index = convert.build_index(case)
    bad = []
    for root, dirs, names in os.walk(case):
        for name in names:
            if name.endswith(".expected"):
                path = os.path.join(root, name[:-9] + ".md")
                content, changes, kept = convert.convert_file(path, index)
                with open(os.path.join(root, name), "rb") as f:
                    if content != f.read():
                        bad.append(os.path.relpath(path, case))
    print(f"{'FAIL' if bad else 'OK  '} convert: převod wikilinků{', liší se: ' + ', '.join(bad) if bad else ''}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
