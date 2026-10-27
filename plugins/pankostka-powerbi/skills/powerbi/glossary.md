# Pojmy Power BI

Doplněk skillu `pankostka-powerbi`. Zkratky konkrétních modelů a společností sem nepatří, jsou v repu projektu nebo organizace.

| Pojem | Popis |
| --- | --- |
| BI | Business Intelligence. |
| PBIP | Formát projektu Power BI vhodný pro git: model jako TMDL, report jako PBIR, každá stránka a vizuál ve vlastním souboru. Náhrada binárního `.pbix`. |
| PBIR | Formát reportu uvnitř PBIP. Mrtvé odkazy na model nehlásí, takže se musí kontrolovat skriptem. |
| RLS | Row Level Security. Omezuje řádky, které uživatel v reportu vidí, například jen svůj útvar. Nastavuje se v rolích sémantického modelu, členství se přiřazuje bezpečnostní skupinou. Pozor: na sdílené dimenzi omezí **všechny** faktovky, které na ní visí. |
| TI | Time intelligence. Časové varianty míry v Power BI: `LY`, `YTD`, `R12M`. Používá se jako sufix v názvech field parameterů (`Select<Základ>_TI`), ne v názvech samotných měr. |
| TMDL | Tabular Model Definition Language. Textový formát sémantického modelu Power BI, jeden soubor na tabulku. |

Zkratky ve zobrazovaných názvech atributů a měr (`Účet`, `DPrv`, `#`, `Ø`) jsou zkratky dimenzí a povahy čísla. Nejsou to pojmy slovníku a do něj se nezapisují.
