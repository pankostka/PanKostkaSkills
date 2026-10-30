#!/usr/bin/env python3
"""Testy check_wiki.py ze skillu pankostka-powerbi-wiki.

Kostky popsané v cases.py se postaví v dočasném adresáři, zkontrolují a smažou.
Případy ok_* nesmí mít žádný nález, ko_<popis>_* jen nálezy pravidla s tím popisem v počtu podle count.
Spuštění: python tests/pankostka-powerbi-wiki/run.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "..", "plugins", "pankostka-powerbi", "skills", "wiki", "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("check_wiki", os.path.join(SCRIPTS, "check_wiki.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
import measures_table  # noqa: E402
from cases import CASES, M, W, base  # noqa: E402


def git(cwd, *args, date=None):
    env = dict(os.environ)
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date + "T12:00:00"
    subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "user.name=test", "-c", "user.email=test@test", *args],
                   cwd=cwd, check=True, capture_output=True, env=env)


def build(root, case):
    files = base()
    if case.get("change"):
        case["change"](files)
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    if case.get("measures"):
        for table in ("FactProdej",):
            article = os.path.join(root, W, f"KostkaTest {table}", f"KostkaTest {table}.md")
            if os.path.isfile(article):
                measures_table.aktualizuj(os.path.join(root, M, "tables", table + ".tmdl"), article, False, table, out=lambda *_: None)
    if case.get("git"):
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "model", date="2026-10-20")


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
            findings = check.check(os.path.join(root, "KostkaTest"))
            if name.startswith("ok_"):
                ok = not findings
                expect = "0 nálezů"
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
