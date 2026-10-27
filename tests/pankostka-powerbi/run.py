#!/usr/bin/env python3
"""Testy check_powerbi.py ze skillu pankostka-powerbi.

Soubory ok_*.tmdl nesmí mít žádnou neshodu.
Soubory ko_<pravidlo>_*.tmdl musí mít jen neshody toho pravidla a právě tolik, kolik říká text `celkem N` v souboru (bez něj 1).
Spuštění: python tests/pankostka-powerbi/run.py
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "..", "plugins", "pankostka-powerbi", "skills", "powerbi", "scripts", "check_powerbi.py")

spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def expected_count(path):
    with open(path, "rb") as f:
        m = re.search(rb"celkem (\d+)", f.read())
    return int(m.group(1)) if m else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    failed = 0
    names = sorted(n for n in os.listdir(HERE) if n.endswith(".tmdl"))
    for name in names:
        path = os.path.join(HERE, name)
        findings = check.check_file(path)
        if name.startswith("ok_"):
            ok = not findings
            expect = "0 neshod"
        else:
            rule = name[3:-5].split("_")[0]
            count = expected_count(path)
            ok = len(findings) == count and all(f[1] == rule for f in findings)
            expect = f"{count}x [{rule}]"
        print(f"{'OK  ' if ok else 'FAIL'} {name}: čekáno {expect}, nalezeno {len(findings)}")
        if not ok:
            failed += 1
            for line, rule, msg in findings:
                print(f"       {line}: [{rule}] {msg}")
    print(f"Testů: {len(names)}, selhalo: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
