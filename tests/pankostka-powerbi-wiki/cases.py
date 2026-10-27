"""Testovací kostky pro check_wiki.py jako data.

Základ je malá kostka KostkaTest: faktovka, dimenze, skrytá tabulka, field parameter, uživatelský report a testovací report, wiki se všemi články. Každý případ základ upraví.
Vault wiki v repu by byl vault ve vaultu a TMDL potřebuje taby, proto se kostky staví až při testu v dočasném adresáři, viz run.py.

Případ: change = funkce, která upraví slovník {cesta: obsah}, count = očekávaný počet nálezů, git = commit modelu s datem, measures = vygenerovat tabulky ukazatelů před kontrolou.
"""
M = "KostkaTest/pbip/KostkaTest.SemanticModel/definition/"
W = "KostkaTest/WikiKostkaTest/"
T = "\t"


def tmdl(*lines):
    return "\n".join(l.replace("    ", T) for l in lines) + "\n"


def article(title, tags, sections, body="", date="2026-12-31"):
    out = ["---", f"title: {title}", f"date: {date}", f"tags: [{', '.join(tags)}]", "---", "Úvod.", ""]
    for s in sections:
        out += [f"## {s}", "", body if s != "Ukazatele" else "Míry.\n\n<!-- ukazatele:start -->\n<!-- ukazatele:end -->", ""]
    return "\n".join(out)


def base():
    return {
        M + "tables/FactProdej.tmdl": tmdl(
            "table FactProdej",
            "    /// Tržba bez DPH.",
            "    measure Tržba = SUM ( FactProdej[ProdejKc] )",
            "        formatString: #,0",
            "        displayFolder: Prodej",
            "",
            "    column DimZakaznikID",
            "        isHidden",
            "        isAvailableInMdx: false",
            "        sourceColumn: DimZakaznikID",
        ),
        M + "tables/FactSklad.tmdl": tmdl(
            "table FactSklad",
            "    column Mnozstvi",
            "        isHidden",
            "        sourceColumn: Mnozstvi",
        ),
        M + "tables/DimZakaznik.tmdl": tmdl(
            "table DimZakaznik",
            "    column 'Zák Název'",
            "        sourceColumn: ZakaznikNazev",
        ),
        M + "tables/DimPomocna.tmdl": tmdl(
            "table DimPomocna",
            "    isHidden",
            "",
            "    column Hodnota",
            "        sourceColumn: Hodnota",
        ),
        M + "tables/SelectProdej.tmdl": tmdl(
            "table SelectProdej",
            "    column 'SelectProdej Fields'",
            "        extendedProperty ParameterMetadata =",
            "                {}",
        ),
        M + "relationships.tmdl": tmdl(
            "relationship r1",
            "    fromColumn: FactProdej.DimZakaznikID",
            "    toColumn: DimZakaznik.DimZakaznikID",
        ),
        "KostkaTest/pbir/Prodej/Prodej.Report/definition/pages/p1/visuals/v1/visual.json":
            '{"visual": {"query": {"From": [{"Name": "f", "Entity": "FactProdej"}]}}}',
        "KostkaTest/pbip/KostkaTest.Report/definition/report.json": "{}",
        W + "KostkaTest.md": article("KostkaTest", ["_KostkaTest"], ["Vazby", "Reporty", "Aktuálnost dat"],
                                     "[[KostkaTest FactProdej|FactProdej]] a [[KostkaTest Prodej|Prodej]]."),
        W + "KostkaTest FactProdej.md": article("FactProdej", ["_KostkaTest", "_FactProdej"], ["Dimenze", "Ukazatele", "Zdroj dat"]),
        W + "KostkaTest FactSklad.md": article("FactSklad", ["_KostkaTest", "_FactSklad"], ["Dimenze", "Ukazatele", "Zdroj dat"]),
        W + "KostkaTest DimZakaznik.md": article("DimZakaznik", ["_KostkaTest", "_FactProdej", "DimZakaznik"], ["Kde se vyskytuje", "Zdroj dat"]),
        W + "KostkaTest Prodej.md": article("Prodej", ["_KostkaTest", "_FactProdej", "_Report"], ["Stránky", "Z čeho čerpá"]),
        W + "KostkaTest Mapování.md": article("Mapování", ["_KostkaTest", "Údržba"], ["Postup", "Na co si dát pozor"]),
        W + "Poznámky-TMP.md": "Dočasný článek se nekontroluje.\n",
    }


def drop(*names):
    def f(files):
        for n in names:
            del files[W + n]
    return f


def put(name, text):
    def f(files):
        files[W + name] = text
    return f


CASES = {
    "ok_kostka": {"measures": True, "git": True},
    # odkaz bez aliasu s vědomou výjimkou a důvodem se nehlásí
    "ok_allow": {"measures": True, "change": put("KostkaTest.md", article("KostkaTest", ["_KostkaTest"], ["Vazby", "Reporty", "Aktuálnost dat"], "<!-- pankostka: allow wiki/wikilink-alias, celý název je tu záměrně -->\n[[KostkaTest FactProdej]]"))},
    "ko_article-per-element": {"count": 2, "measures": True, "change": drop("KostkaTest DimZakaznik.md", "KostkaTest Prodej.md")},
    "ko_article-per-element_orphan": {"count": 1, "measures": True, "change": put("KostkaTest DimStara.md", article("DimStara", ["_KostkaTest", "DimStara"], ["Kde se vyskytuje", "Zdroj dat"]))},
    "ko_frontmatter": {"count": 2, "measures": True, "change": put("KostkaTest DimZakaznik.md", article("Zákazník", ["_KostkaTest", "_FactProdej", "DimZakaznik"], ["Kde se vyskytuje", "Zdroj dat"], date="31.12.2026"))},
    "ko_tags": {"count": 2, "measures": True, "change": put("KostkaTest DimZakaznik.md", article("DimZakaznik", ["_KostkaTest", "_FactSklad", "DimZakaznik"], ["Kde se vyskytuje", "Zdroj dat"]))},
    "ko_outline": {"count": 1, "measures": True, "change": put("KostkaTest Prodej.md", article("Prodej", ["_KostkaTest", "_FactProdej", "_Report"], ["Stránky"]))},
    "ko_revision-date": {"count": 1, "measures": True, "git": True, "change": put("KostkaTest DimZakaznik.md", article("DimZakaznik", ["_KostkaTest", "_FactProdej", "DimZakaznik"], ["Kde se vyskytuje", "Zdroj dat"], date="2026-01-01"))},
    # text je v každé ze tří sekcí, vložení ![[...]] alias nepotřebuje
    "ko_wikilink-alias": {"count": 3, "measures": True, "change": put("KostkaTest.md", article("KostkaTest", ["_KostkaTest"], ["Vazby", "Reporty", "Aktuálnost dat"], "[[KostkaTest FactProdej]] a ![[KostkaTest Prodej]]."))},
    # FactProdej bez vygenerované tabulky, FactSklad nemá viditelné míry, takže se nehlásí
    "ko_measures-table": {"count": 1},
}
