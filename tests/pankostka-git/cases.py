"""Testovací repa pro check_git.py jako data.

Pravidla závisí na indexu, historii a konfiguraci gitu, proto se repa staví až při testu v dočasném adresáři, viz run.py.
Případ: files = {cesta: obsah}, bom = soubory s BOM, force = soubory přidané i přes .gitignore, commits = subjecty commitů,
hooks_path = nastavit core.hooksPath, noadd = nepřidávat soubory do indexu, count = očekávaný počet neshod.
"""

GITIGNORE = "*-TMP.*\n*-TMP\n"


def base():
    return {
        ".gitignore": GITIGNORE,
        "README.md": "Repo.\n",
        "nsp10HN_Denik-VZOR.sql": "select 1\n",
        "Report-DRAFT.md": "Rozpracované.\n",
        "pbir/AXMain-Výsledovka-V2.md": "Verze se nehlásí.\n",
        "Poznamky-TMP.md": "Dočasné, v gitu není.\n",
        "dump-2026-NLX-TABLE-TMP/x.sql": "Uvnitř adresáře -TMP se sufixy nekontrolují.\n",
    }


CASES = {
    "ok_repo": {"commits": ["Běžný commit"], "files": {"hooks/pre-commit": "#!/bin/sh\n"}, "hooks_path": True},
    # bez git add: s chybným .gitignore by se do indexu dostal i Poznamky-TMP.md a hlásil by se jako tracked
    "ko_gitignore": {"count": 1, "files": {".gitignore": "*-TMP\n"}, "noadd": True},
    "ko_tracked": {"count": 1, "files": {"dotaz-TMP.sql": "select 1\n"}, "force": ["dotaz-TMP.sql"]},
    "ko_suffix": {"count": 2, "files": {"nsp20FactDenik-LAVICE.sql": "select 1\n", "Data-OLD/a.txt": "x\n"}},
    "ko_bom": {"count": 1, "bom": ["README.md"]},
    "ko_message": {"count": 2, "commits": ["Dobrý commit", "@'Zpráva z PowerShellu", "﻿Oprava rourou"]},
    "ko_hooks": {"count": 1, "files": {"hooks/pre-commit": "#!/bin/sh\n"}},
}
