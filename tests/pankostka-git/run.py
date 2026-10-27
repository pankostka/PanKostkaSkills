#!/usr/bin/env python3
"""Testy check_git.py ze skillu pankostka-git.

Repa popsaná v cases.py se postaví v dočasném adresáři, zkontrolují a smažou.
Případy ok_* nesmí mít žádnou neshodu, ko_<popis>_* jen neshody pravidla s tím popisem v počtu podle count.
Spuštění: python tests/pankostka-git/run.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "..", "plugins", "pankostka-git", "skills", "git", "scripts", "check_git.py")

spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
sys.path.insert(0, HERE)
from cases import CASES, base  # noqa: E402


def git(cwd, *args):
    subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "user.name=test", "-c", "user.email=test@test", *args],
                   cwd=cwd, check=True, capture_output=True)


def build(root, case):
    files = base()
    files.update(case.get("files", {}))
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = content.encode("utf-8")
        if rel in case.get("bom", []):
            data = b"\xef\xbb\xbf" + data
        with open(path, "wb") as f:
            f.write(data)
    git(root, "init", "-q")
    if not case.get("noadd"):
        git(root, "add", "-A")
    for rel in case.get("force", []):
        git(root, "add", "-f", rel)
    for i, subject in enumerate(case.get("commits", [])):
        msg = os.path.join(root, ".git", "MSG")
        with open(msg, "wb") as f:
            f.write(subject.encode("utf-8"))
        git(root, "commit", "-q", "--allow-empty", "-F", msg)
    if case.get("hooks_path"):
        git(root, "config", "core.hooksPath", "hooks")


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
            findings = check.check_repo(root)
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
