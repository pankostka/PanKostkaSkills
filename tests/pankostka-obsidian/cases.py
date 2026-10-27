"""Testovací vaulty pro check_obsidian.py jako data.

Vault v repu by byl vault ve vaultu PanKostkaSkills a jeho .gitignore by ovlivňoval git tohoto repa. Proto se vaulty staví až při testu v dočasném adresáři, viz run.py.

Každý případ: files = {cesta: obsah}, git = založit repo a přidat soubory do indexu, force = soubory přidané i přes .gitignore, count = očekávaný počet neshod.
Případy ok_* nesmí mít neshodu, ko_<pravidlo>_* jen neshody toho pravidla.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GITIGNORE = os.path.join(HERE, "..", "..", "plugins", "pankostka-obsidian", "skills", "obsidian", "gitignore.txt")
with open(GITIGNORE, encoding="utf-8") as f:
    GITIGNORE_TXT = f.read()

GOOD_APP = json.dumps({
    "alwaysUpdateLinks": True,
    "attachmentFolderPath": "./Attachments",
    "newLinkFormat": "shortest",
    "showUnsupportedFiles": False,
    "userIgnoreFilters": ["StaticResources/", "/-TMP/"],
}, indent=2)

CASES = {
    "ok_vault": {
        "git": True,
        "files": {
            ".obsidian/app.json": GOOD_APP,
            ".obsidian/community-plugins.json": '["plugin"]',
            ".obsidian/plugins/plugin/manifest.json": '{"id": "plugin"}',
            ".obsidian/plugins/plugin/data.json": "{}",
            ".gitignore": GITIGNORE_TXT,
            "README.md": "![[menu]]\n\nRozcestník.\n",
            "menu.md": "[[README]]\n",
            # vnořený vault se stejným nastavením souborů a vlastním rozcestníkem
            "WikiKostkaTest/.obsidian/app.json": json.dumps({"alwaysUpdateLinks": True, "attachmentFolderPath": "./Attachments", "strictLineBreaks": False}),
            "WikiKostkaTest/KostkaTest.md": "Rozcestník kostky.\n",
        },
    },
    "ok_private": {
        "git": True,
        "files": {
            ".obsidian/app.json": GOOD_APP,
            ".git/info/exclude": ".obsidian/\n",
            "README.md": "Rozcestník.\n",
        },
    },
    "ok_nogit": {
        "files": {
            ".obsidian/app.json": GOOD_APP,
            "README.md": "---\ntitle: Rozcestník\n---\n![[menu]]\n",
            "menu.md": "Lišta.\n",
        },
    },
    "ko_nested-same-settings": {
        "count": 2,
        "files": {
            ".obsidian/app.json": GOOD_APP,
            "README.md": "Rozcestník.\n",
            "Wiki/.obsidian/app.json": json.dumps({"alwaysUpdateLinks": False}),
            "Wiki/Wiki.md": "Wiki.\n",
        },
    },
    "ko_one-vault-per-repo": {
        "count": 1,
        "files": {"README.md": "Bez vaultu.\n"},
    },
    "ko_app-settings": {
        "count": 3,
        "files": {
            ".obsidian/app.json": json.dumps({
                "attachmentFolderPath": "/",
                "showUnsupportedFiles": True,
                "userIgnoreFilters": ["StaticResources/", "/-TMP/"],
            }, indent=2),
            "README.md": "Rozcestník.\n",
        },
    },
    "ko_ignore-filter-no-glob": {
        "count": 1,
        "files": {
            ".obsidian/app.json": json.dumps({
                "alwaysUpdateLinks": True,
                "attachmentFolderPath": "./Attachments",
                "userIgnoreFilters": ["*-TMP", "StaticResources/", "/-TMP/"],
            }, indent=2),
            "README.md": "Rozcestník.\n",
        },
    },
    "ko_gitignore-plugin-code": {
        # celé plugins/ ignorované, chybí themes/ a workspaces.json
        "count": 3,
        "git": True,
        "files": {
            ".obsidian/app.json": GOOD_APP,
            ".gitignore": ".obsidian/workspace.json\n.obsidian/plugins/\n",
            "README.md": "Rozcestník.\n",
        },
    },
    "ko_no-tracked-plugin-code": {
        "count": 2,
        "git": True,
        "force": [".obsidian/workspace.json", ".obsidian/plugins/plugin/main.js"],
        "files": {
            ".obsidian/app.json": GOOD_APP,
            ".obsidian/workspace.json": "{}",
            ".obsidian/plugins/plugin/main.js": "",
            ".obsidian/plugins/plugin/manifest.json": '{"id": "plugin"}',
            ".gitignore": GITIGNORE_TXT,
            "README.md": "Rozcestník.\n",
        },
    },
    "ko_root-readme": {
        "count": 3,
        "files": {
            ".obsidian/app.json": GOOD_APP,
            "index.md": "Rozcestník.\n",
            "home.md": "Rozcestník.\n",
        },
    },
    "ko_menu-embed": {
        "count": 1,
        "files": {
            ".obsidian/app.json": GOOD_APP,
            "README.md": "# Rozcestník\n\n![[menu]]\n",
            "menu.md": "Lišta.\n",
        },
    },
}
