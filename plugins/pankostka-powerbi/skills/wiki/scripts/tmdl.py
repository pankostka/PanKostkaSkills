"""Čtení sémantického modelu v TMDL a reportů PBIR pro kontrolu wiki kostky.

Jen to, co wiki potřebuje: tabulky a jejich viditelnost, field parametry, vazby mezi tabulkami a tabulky použité v reportech.
Jen standardní knihovna, aby skript běžel i v prostředí claude.ai.
"""
import json
import os
import re


def unquote(name):
    """TMDL obaluje jména s mezerou apostrofy, vnitřní apostrof zdvojuje."""
    name = name.strip()
    if name.startswith("'") and name.endswith("'") and len(name) >= 2:
        name = name[1:-1].replace("''", "'")
    return name


def split_column_ref(ref):
    """Z `Tabulka.Sloupec` nebo `'Tab ulka'.Sloupec` vrátí název tabulky."""
    ref = ref.strip()
    if ref.startswith("'"):
        i = 1
        while i < len(ref):
            if ref[i] == "'":
                if ref[i + 1:i + 2] == "'":
                    i += 2
                    continue
                break
            i += 1
        return unquote(ref[:i + 1])
    return ref.split(".")[0]


def read_table(path):
    """Vrátí dict(name, hidden, param) z jednoho souboru tables/*.tmdl."""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    name, hidden, param = None, False, False
    for line in lines:
        if line.startswith("table "):
            rest = line[6:].strip()
            name = split_column_ref(rest) if rest.startswith("'") else rest.split("=")[0].strip()
        elif re.fullmatch(r"\tisHidden(:\s*true)?\s*", line):
            hidden = True  # vlastnost tabulky, ne sloupce, ta má dva tabulátory
        elif "ParameterMetadata" in line:
            param = True
    return {"name": name or os.path.splitext(os.path.basename(path))[0], "hidden": hidden, "param": param, "file": path}


def read_relationships(definition):
    """Vazby jako seznam dvojic (tabulka z, tabulka do)."""
    path = os.path.join(definition, "relationships.tmdl")
    if not os.path.isfile(path):
        return []
    rels, cur = [], {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f.read().splitlines():
            s = line.strip()
            if line.startswith("relationship "):
                cur = {}
            m = re.match(r"(fromColumn|toColumn):\s*(.+)$", s)
            if m:
                cur[m.group(1)] = split_column_ref(m.group(2))
                if len(cur) == 2:
                    rels.append((cur["fromColumn"], cur["toColumn"]))
    return rels


def load_model(definition):
    """Tabulky modelu {název: dict} a vazby."""
    tables = {}
    tdir = os.path.join(definition, "tables")
    if os.path.isdir(tdir):
        for n in sorted(os.listdir(tdir)):
            if n.endswith(".tmdl"):
                t = read_table(os.path.join(tdir, n))
                tables[t["name"]] = t
    return tables, read_relationships(definition)


def entities(obj, out):
    """Všechny hodnoty klíče Entity v JSON stromu. Jsou to skutečné názvy tabulek, aliasy jsou v klíči Source."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "Entity" and isinstance(v, str):
                out.add(v)
            else:
                entities(v, out)
    elif isinstance(obj, list):
        for v in obj:
            entities(v, out)
    return out


def report_tables(report_dir):
    """Tabulky, na které report odkazuje, ze všech JSON souborů jeho definice."""
    found = set()
    for root, _, names in os.walk(os.path.join(report_dir, "definition")):
        for n in names:
            if n.endswith(".json"):
                try:
                    with open(os.path.join(root, n), encoding="utf-8-sig") as f:
                        entities(json.load(f), found)
                except (ValueError, OSError):
                    pass
    return found
