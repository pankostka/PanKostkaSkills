#!/usr/bin/env python3
"""Vyrobí testovací soubory .tmdl pro check_powerbi.py.

TMDL odsazuje taby a editory i nástroje AI je rády převedou na mezery, proto soubory vznikají tímhle skriptem. Řádek `/// celkem N` říká, kolik neshod test čeká.
Spuštění: python tests/pankostka-powerbi/make_cases.py, pak python tests/pankostka-powerbi/run.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T = "\t"


def w(name, lines):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(line.replace("    ", T) for line in lines) + "\n")


w("ok_fact.tmdl", [
    "/// Faktovka bez neshod.",
    "table FactProdej",
    "    lineageTag: 1",
    "",
    "    /// Základní míra.",
    "    measure HV = SUM ( FactProdej[ProdejKc] )",
    "        formatString: #,0",
    "        displayFolder: Výsledek",
    "",
    "    measure 'HV LY' =",
    "            VAR x = CALCULATE ( [HV], DATEADD ( DimDatum[Date], -1, YEAR ) )",
    "            RETURN x",
    "        formatString: #,0",
    "        displayFolder: Výsledek",
    "",
    "    measure 'HV LY△' = [HV] - [HV LY]",
    "        formatString: #,0",
    "        displayFolder: Výsledek",
    "",
    "    measure 'HV YTD LY' = CALCULATE ( [HV YTD], DATEADD ( DimDatum[Date], -1, YEAR ) )",
    "        formatString: #,0",
    "        displayFolder: Výsledek",
    "",
    "    measure '#Dokladů' = COUNTROWS ( FactProdej )",
    "        formatString: #,0",
    "        displayFolder: Počty",
    "",
    "    measure 'Dynamický formát' = [HV]",
    "        displayFolder: Výsledek",
    "        formatStringDefinition = \"#,0\"",
    "",
    "    column DimUcetID",
    "        dataType: int64",
    "        isHidden",
    "        formatString: 0",
    "        isAvailableInMdx: false",
    "        sourceColumn: DimUcetID",
    "",
    "    column ProdejKc",
    "        dataType: decimal",
    "        isHidden: true",
    "        isAvailableInMdx: false",
    "        sourceColumn: ProdejKc",
    "",
    "    column 'Prodej Poznámka'",
    "        dataType: string",
    "        sourceColumn: ProdejPozn",
    "",
    "    partition FactProdej = m",
    "        mode: import",
    "        source =",
    "                let",
    "                    Zdroj = Sql.Database(\"server\", \"db\")",
    "                in",
    "                    Zdroj",
])

w("ok_dim.tmdl", [
    "table DimUcet",
    "    column DimUcetID",
    "        isHidden",
    "        sourceColumn: DimUcetID",
    "",
    "    column 'Účet Název'",
    "        sourceColumn: UcetNazev",
    "",
    "    hierarchy @Účet",
    "        level Třída",
    "            column: 'Účet Třída'",
    "",
    "    hierarchy '@DPrv Třída'",
    "        level Třída",
    "            column: 'DPrv Třída'",
])

w("ok_role.tmdl", [
    "/// Role bez omezení.",
    "role RoleProdejManagement",
    "    modelPermission: read",
])

w("ok_select.tmdl", [
    "table SelectDimProdejA",
    "    column SelectDimProdejA",
    "        sourceColumn: [Value1]",
    "",
    "    column 'SelectDimProdejA Fields'",
    "        isHidden",
    "        sourceColumn: [Value2]",
    "",
    "        extendedProperty ParameterMetadata =",
    "                {",
    "                  \"version\": 3",
    "                }",
    "",
    "table SelectTrzba_TI",
    "    column 'SelectTrzba_TI Fields'",
    "        extendedProperty ParameterMetadata =",
    "                {}",
    "",
    "table VyberBezParametru",
    "    column Hodnota",
    "        sourceColumn: Hodnota",
])

w("ko_table-no-diacritics.tmdl", [
    "/// celkem 1",
    "table DimÚčet",
    "    column 'Účet Název'",
    "        sourceColumn: UcetNazev",
])

w("ko_key-keep-name.tmdl", [
    "/// celkem 1",
    "table DimSaldo",
    "    column 'Sld ID'",
    "        sourceColumn: DimSaldoID",
    "",
    "    column 'Sld Název'",
    "        sourceColumn: SaldoNazev",
])

w("ko_hierarchy-at.tmdl", [
    "/// celkem 2",
    "table DimDatum",
    "    hierarchy §RTD",
    "        level Rok",
    "            column: Rok",
    "",
    "    hierarchy '@Účet'",
    "        level Třída",
    "            column: Třída",
])

w("ko_measure-format-folder.tmdl", [
    "/// celkem 2",
    "table FactProdej",
    "    measure HV = SUM ( FactProdej[ProdejKc] )",
    "        displayFolder: Výsledek",
    "",
    "    measure Obrat = SUM ( FactProdej[ProdejKc] )",
    "        formatString: #,0",
])

w("ko_measure-token-order.tmdl", [
    "/// celkem 2",
    "table FactProdej",
    "    measure 'HV △LY' = [HV] - [HV LY]",
    "        formatString: #,0",
    "        displayFolder: Výsledek",
    "",
    "    measure 'HV LY YTD' = CALCULATE ( [HV LY], DATESYTD ( DimDatum[Date] ) )",
    "        formatString: #,0",
    "        displayFolder: Výsledek",
])

w("ko_fact-hidden-no-mdx.tmdl", [
    "/// celkem 2",
    "table FactProdej",
    "    column DimUcetID",
    "        isHidden",
    "        formatString: 0",
    "        sourceColumn: DimUcetID",
    "",
    "    column ProdejKc",
    "        isHidden",
    "        isAvailableInMdx: true",
    "        sourceColumn: ProdejKc",
    "",
    "    column 'Prodej Poznámka'",
    "        sourceColumn: ProdejPozn",
])

w("ko_role-name.tmdl", [
    "/// celkem 2",
    "role 'Prodej Uživatel'",
    "    modelPermission: read",
    "",
    "role RoleProdej_User",
    "    modelPermission: read",
])

w("ko_select-name.tmdl", [
    "/// celkem 2",
    "table SelectProdejAll",
    "    column 'SelectProdejAll Fields'",
    "        extendedProperty ParameterMetadata =",
    "                {}",
    "",
    "table ParametrProdej",
    "    column 'ParametrProdej Fields'",
    "        extendedProperty ParameterMetadata =",
    "                {}",
])
