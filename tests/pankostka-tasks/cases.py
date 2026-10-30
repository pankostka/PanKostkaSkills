"""Testovací repa pro check_tasks.py jako data.

Pravidlo git závisí na tom, co git sleduje, proto se repa staví až při testu v dočasném adresáři, viz run.py.
Případ: files = {cesta: obsah}, git = založit repo a přidat do indexu soubory kromě untracked, count = očekávaný počet neshod.
"""

INDEX = """# Tasks

- [Report Prodej](Report%20Prodej/Report%20Prodej.md) - report nad prodejem. Čeká na Desktop.
- [Intercompany](<Intercompany v KostkaEKO/Intercompany v KostkaEKO.md>) - vzájemné vztahy firem.
- Úkol, na kterém se ještě nedělá, je jen odrážkou.

Rozhodnutí jsou v [TODO](../TODO.md).
"""


def base():
    return {
        "TODO.md": "Rozhodnutí.\n",
        "tasks/tasks.md": INDEX,
        "tasks/Report Prodej/Report Prodej.md": "## Zadání\n\nReport.\n",
        "tasks/Intercompany v KostkaEKO/Intercompany v KostkaEKO.md": "## Stav\n\nMěří se.\n",
        "tasks/Intercompany v KostkaEKO/mereni-TMP.sql": "select 1\n",
    }


CASES = {
    "ok_tasks": {"git": True},
    "ok_nogit": {},
    "ok_allow": {"add": {"tasks/tasks.md": INDEX + "<!-- pankostka: allow tasks/index, úkol je v jiném repu -->\n- [Úkol jinde](../../ProjektHelios/tasks/Úkol%20jinde/Úkol%20jinde.md) - vede se v ProjektHelios.\n"}},
    "ko_index": {"count": 1, "drop": ["tasks/tasks.md"]},
    "ko_article-per-task": {"count": 1, "add": {"tasks/Nový úkol/Nový úkol.md": "Zadání.\n"}},
    "ko_index_dead": {"count": 1, "add": {"tasks/tasks.md": INDEX + "- [Smazaný úkol](Smazaný%20úkol/Smazaný%20úkol.md) - hotovo.\n"}},
    "ko_task-folder": {"count": 1, "add": {
        "tasks/tasks.md": INDEX + "- [Starý úkol](Starý%20úkol.md) - článek mimo adresář.\n",
        "tasks/Starý úkol.md": "Zadání.\n",
    }},
    "ko_task-folder_empty": {"count": 1, "add": {"tasks/Prázdný/poznamky-TMP.txt": "x\n"}},
    "ko_tmp-in-task-folder": {"count": 1, "add": {"tasks/Helios uroven UPDATE-TMP.sql": "update x\n"}},
    "ko_in-git": {"count": 1, "git": True, "untracked": ["tasks/Report Prodej/Report Prodej.md"]},
}
