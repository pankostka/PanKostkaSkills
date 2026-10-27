#!/usr/bin/env python3
"""Testy check_dwh.py ze skillu pankostka-dwh.

Každý test je adresář s malým repem rozděleným do vrstev (10_stage, 20_dim, 20_fact, 30_mart). Adresáře ok_* nesmí mít žádnou neshodu.
Adresáře ko_<pravidlo>_* musí mít jen neshody toho pravidla a právě tolik, kolik říká text `celkem N` v některém jejich souboru (bez něj 1).
Spuštění: python tests/pankostka-dwh/run.py
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "..", "plugins", "pankostka-dwh", "skills", "dwh", "scripts", "check_dwh.py")

spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def expected_count(case):
    for root, _, names in os.walk(case):
        for name in sorted(names):
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
        findings = [(os.path.relpath(p, case), *f) for p in sorted(check.collect([case])) for f in check.check_file(p)]
        if name.startswith("ok_"):
            ok = not findings
            expect = "0 neshod"
        else:
            rule = name[3:].split("_")[0]
            count = expected_count(case)
            ok = len(findings) == count and all(f[2] == rule for f in findings)
            expect = f"{count}x [{rule}]"
        print(f"{'OK  ' if ok else 'FAIL'} {name}: čekáno {expect}, nalezeno {len(findings)}")
        if not ok:
            failed += 1
            for path, line, rule, msg in findings:
                print(f"       {path}:{line}: [{rule}] {msg}")
    print(f"Testů: {len(names)}, selhalo: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
