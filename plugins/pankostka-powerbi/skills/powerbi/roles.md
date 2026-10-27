# Role a zabezpečení

Doplněk skillu `pankostka-powerbi`.

Role sémantického modelu jsou v `definition/roles/<Role>.tmdl`, jeden soubor na roli, plus `ref role` v `model.tmdl`.

## Pojmenování

`powerbi/role-name` **`Role<Model><Skupina>`**: PascalCase, bez diakritiky, jednotné číslo. U modelu `Prodej` tedy `RoleProdejManagement`, `RoleProdejPowerUser`, `RoleProdejUser`. Prefix `Role` je systémová věc, tedy anglicky. Jméno modelu je uvnitř modelu redundantní, ale v Power BI Service jsou modely vedle sebe a ve fulltextu přes repo je název jednoznačný. Microsoft žádnou konvenci nemá. Název role se v TMDL musí obalit apostrofy, pokud obsahuje mezeru, tečku, dvojtečku nebo rovnítko, proto jedním slovem.

Členství se nepřiřazuje jednotlivcům, vždy **bezpečnostní skupinou** v AD nebo Entra, pojmenovanou zrcadlově `PBI-<Model>-<Skupina>`. Nastavuje se v Power BI Service u **sémantického modelu** (ne u reportu), v nabídce Security.

## Na co si dát pozor

- **Přejmenování role ruší přiřazení skupin.** Service drží členství u role podle jména, po nasazení přejmenované role se musí naklikat znovu. Jméno se má vybrat napoprvé.
- **Členství v rolích se sčítá.** Skupiny musí být disjunktní, jinak vyhrává ta nejštědřejší.
- **Model s rolemi potřebuje i roli bez omezení.** Uživatel s právem Viewer, který není v žádné roli, dostane při otevření chybu. Kdo je ve workspace Admin, Member nebo Contributor, RLS i OLS obchází a roli nepotřebuje. Proto se testuje přes *Test as role*, ne otevřením reportu na sobě.
- `powerbi/rls-not-ols` **Pokud uživatelé chodí do modelu Excelem, omezuj přes RLS, ne OLS.** OLS objekt odstraní z metadat a kontingenční tabulka, která na něj odkazuje, spadne s chybou. RLS jen odfiltruje řádky: tabulka i míry zůstanou v seznamu polí a vrátí prázdno, sešit dál funguje. Zneviditelnění celé faktovky se pak píše jako `tablePermission Fact<Entita> = FALSE()`.
- **RLS na sdílenou dimenzi omezí všechny faktovky, které na ní visí.** Když má omezení dopadnout jen na jednu faktovku, patří filtr přímo na ni.
- **Dynamická RLS** přes `USERPRINCIPALNAME()` a mapovací tabulku má smysl teprve tehdy, když se právo liší osoba od osoby. Pro pravidlo platné celé skupině stačí filtr přímo v roli. Kdyby na ni došlo, patří ručně udržovaná data do konfigurační tabulky v databázi a mapovací tabulka do modelu **odpojená** (bez vazby, filtr se čte v DAX). Obousměrné vazby kvůli RLS nezaváděj. Mapovací tabulka potřebuje vlastní filtr na `USERPRINCIPALNAME()`, jinak z ní každý přečte seznam všech uživatelů.
- **Dotaz pod přihlášeným uživatelem závisí na jeho rolích.** Když míra z faktovky schované přes RLS vrátí prázdno, nemusí to být chyba modelu.

**Exportované sešity RLS nechrání.** Hodnoty napočtené v cache kontingenční tabulky zůstávají v souboru bez ohledu na role, takže hotové `.xlsx` předané uživateli je plnohodnotná kopie dat.
