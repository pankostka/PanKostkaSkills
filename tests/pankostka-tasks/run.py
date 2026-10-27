#!/usr/bin/env python3
"""Testy check_tasks.py ze skillu pankostka-tasks.

Repa popsaná v cases.py se postaví v dočasném adresáři, zkontrolují a smažou.
Případy ok_* nesmí mít žádnou neshodu, ko_<popis>_* jen neshody pravidla s tím popisem v počtu podle count.
Spuštění: python tests/pankostka-tasks/run.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "..", "plugins", "pankostka-tasks", "skills", "tasks", "scripts", "check_tasks.py")

spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
sys.path.insert(0, HERE)
from cases import CASES, base  # noqa: E402


def git(cwd, *args):
    subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=cwd, check=True, capture_output=True)


def build(root, case):
    files = base()
    files.update(case.get("add", {}))
    for rel in case.get("drop", []):
        del files[rel]
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    if case.get("git"):
        with open(os.path.join(root, ".gitignore"), "w") as f:
            f.write("*-TMP.*\n*-TMP\n")
        git(root, "init", "-q")
        git(root, "add", "-A")
        for rel in case.get("untracked", []):
            git(root, "rm", "-q", "--cached", rel)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in sorted(CASES):
            case = CASES[name]
            root = os.path.join(tmp, name)
            os.makedirs(root)
            build(root, case)
            findings = check.check_dir(root)
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
                    print(f"       {os.path.relpath(path, root)}:{line}: [{rule}] {msg}")
    print(f"Testů: {len(CASES)}, selhalo: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
