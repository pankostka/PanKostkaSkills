"""Testovací repa pro check_tasks.py jako data.

Pravidlo git závisí na tom, co git sleduje, proto se repa staví až při testu v dočasném adresáři, viz run.py.
Případ: files = {cesta: obsah}, git = založit repo a přidat do indexu soubory kromě untracked, count = očekávaný počet neshod.
"""

INDEX = """# Tasks

- [[Report Prodej]] - report nad prodejem. Čeká na Desktop.
- [[Intercompany v KostkaEKO|Intercompany]] - vzájemné vztahy firem.
- Úkol, na kterém se ještě nedělá, je jen odrážkou.

Rozhodnutí jsou v [[TODO]].
"""


def base():
    return {
        "TODO.md": "Rozhodnutí.\n",
        "tasks/tasks.md": INDEX,
        "tasks/Report Prodej.md": "## Zadání\n\nReport.\n",
        "tasks/Intercompany v KostkaEKO.md": "## Stav\n\nMěří se.\n",
        "tasks/Intercompany v KostkaEKO-mereni-TMP.sql": "select 1\n",
    }


CASES = {
    "ok_tasks": {"git": True},
    "ok_nogit": {},
    "ko_index": {"count": 1, "drop": ["tasks/tasks.md"]},
    "ko_orphan": {"count": 1, "add": {"tasks/Nový úkol.md": "Zadání.\n"}},
    "ko_dead": {"count": 1, "add": {"tasks/tasks.md": INDEX + "- [[Smazaný úkol]] - hotovo.\n"}},
    "ko_leftover": {"count": 1, "add": {"tasks/Helios uroven UPDATE-TMP.sql": "update x\n"}},
    "ko_git": {"count": 1, "git": True, "untracked": ["tasks/Report Prodej.md"]},
}
