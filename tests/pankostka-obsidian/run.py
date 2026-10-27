#!/usr/bin/env python3
"""Testy check_obsidian.py ze skillu pankostka-obsidian.

Vaulty popsané v cases.py se postaví v dočasném adresáři, zkontrolují a smažou.
Případy ok_* nesmí mít žádnou neshodu, ko_<popis>_* jen neshody pravidla s tím popisem v počtu podle count.
Spuštění: python tests/pankostka-obsidian/run.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "..", "plugins", "pankostka-obsidian", "skills", "obsidian", "scripts", "check_obsidian.py")

spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
sys.path.insert(0, HERE)
from cases import CASES  # noqa: E402


def git(cwd, *args):
    subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=cwd, check=True, capture_output=True)


def build(base, case):
    if case.get("git"):
        os.makedirs(base)
        git(base, "init", "-q")
    for rel, content in case["files"].items():
        path = os.path.join(base, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    if case.get("git"):
        git(base, "add", "-A")
        for rel in case.get("force", []):
            git(base, "add", "-f", rel)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in sorted(CASES):
            case = CASES[name]
            base = os.path.join(tmp, name)
            build(base, case)
            findings = check.check_dir(base)
            if name.startswith("ok_"):
                ok = not findings
                expect = "0 neshod"
            else:
                rule = name[3:].split("_")[0]
                count = case.get("count", 1)
                ok = len(findings) == count and all(f[2].split("/")[-1] == rule for f in findings)
                expect = f"{count}x [{rule}]"
            print(f"{'OK  ' if ok else 'FAIL'} {name}: čekáno {expect}, nalezeno {len(findings)}")
            if not ok:
                failed += 1
                for path, line, rule, msg in findings:
                    print(f"       {os.path.relpath(path, base)}:{line}: [{rule}] {msg}")
    print(f"Testů: {len(CASES)}, selhalo: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
