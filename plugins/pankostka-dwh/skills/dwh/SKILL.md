---
name: pankostka-dwh
description: Zásady datového skladu (DWH) v MS SQL Server - vrstvy 10 STAGE, 20 STAR a 30 MART, pořadí plnění, nižší vrstva nečte z vyšší, struktura repa (00_common, 10_stage, 20_dim, 20_fact, 30_mart), jmenné konvence procedur nsp10/nsp20/nsp30, schémat s10/s20/s30, dimenzí, faktovek a klíčů, řádek Key = -1, alokační tabulky, konfigurační tabulky, řešení pro více společností. Použij vždy, když zakládáš, upravuješ nebo kontroluješ plnicí proceduru, tabulku nebo mart datového skladu. S argumentem (soubor, adresář nebo --changed) zkontroluje procedury proti konvencím a vypíše neshody.
argument-hint: "[soubor | adresář | --changed]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_dwh.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_dwh.py *)
---

# Datový sklad - vrstvy a konvence

Zásady pro datový sklad v MS SQL Server, nad kterým stojí reporting v Power BI. Pravidla psaní T-SQL jsou ve skillu `pankostka-tsql`, sémantický model ve skillu `pankostka-powerbi`. Konkrétní zdroje, společnosti, marty, server a databáze patří do `CLAUDE.md` nebo `CLAUDE_Project.md` repa.

Pojmy a zkratky (datamart, kostka, `Key = -1`, junk a degenerate dimension, alokace, zkratky v názvech sloupců jako `Org`, `Zak`, `SK`) jsou v `${CLAUDE_SKILL_DIR}/glossary.md`. Než zkratku použiješ nebo zavedeš novou, podívej se tam. Postupy pro přidání dimenze a míry jsou v `${CLAUDE_SKILL_DIR}/checklists.md`.

Argument: `$ARGUMENTS`

## Vrstvy

`dwh/load-order` Postupuje se striktně po vrstvách:

- **10 - STAGE**: načtená data ze zdrojů.
- **20 - STAR**: star schémata. Plní se **dimenze, pak faktovky**. Dimenze jsou obecné a mohou obsahovat řádky, které ve faktovkách nejsou.
- **30 - MART**: datamarty. Plní se **faktovky, pak dimenze**. Opět star schémata, ale odvozená z předchozí vrstvy. Faktovky jsou grupované (je-li třeba), dimenze obsahují jen prvky, které jsou ve faktovkách.

Vrstvy plní uložené procedury MSSQL, spouští je (orchestruje) job manager.

`dwh/no-read-up` **Nižší vrstva nikdy nesmí číst z vyšší.** Ve vrstvě 10 se tedy nesmí použít tabulky vrstvy 20, natož 30.

## Struktura repa

Číselný prefix adresáře drží **pořadí plnění**. Nezohledňuje ale, že vrstva 20 se plní dimenze, pak faktovky, a vrstva 30 faktovky, pak dimenze. Vrstvy jsou adresáře přímo v kořeni repa.

```
00_common/          sdílená infrastruktura, není to vrstva plnění (volá se z vrstev 10/20/30)
10_stage/           surové kopie ze zdrojů, jeden podadresář = jeden systém
20_dim/             společné dimenze sdílené napříč datamarty
20_fact/            faktové tabulky. Plní se až po naplnění dimenzí
30_mart/            jeden podadresář = jedna kostka (Kostka<Mart>)
  Kostka<Mart>/
    pbip/               Power BI projekt (TMDL + JSON): model a jeho testovací report
    pbir/               reporty pro uživatele, live connect na publikovaný model
    Wiki<Kostka>/       dokumentace kostky pro uživatele, viz skill pankostka-powerbi-wiki
    baseline/           testovací lavice: soubory a reporty pro ověřování a porovnávání modelu
    reports_from_users/ podklady a zpětná vazba od uživatelů
    reports_to_users/   výstupy určené uživatelům
docs/               dokumentace repa
tasks/              rozpracované úkoly
```

### 00_common

**Není to vrstva plnění.** Procedury odsud se volají *z* vrstev 10, 20 a 30, samy nic neplní. Prefix `00` je jen kvůli řazení na začátek.

Kritérium, co patří sem: **plní to tabulku?** Ano, pak do příslušné vrstvy. Ne, pak sem. Například HTTP klient a získání OAuth tokenu patří do `00_common/restapi/`, ale harvester, který stahuje metadata do stage tabulek, patří do `10_stage/<zdroj>/`.

Procedury tady nemají prefix `nsp<vrstva>`, protože do žádné vrstvy nepatří. Ne všechno tady je procedura: diagnostické skripty se spouští ručně v SSMS po sekcích a nezakládají žádný objekt v databázi.

## Vrstva 10 - STAGE

Adresář `10_stage`, podadresáře **po zdrojích**. Každý zdroj má zkratku (SourceCode), která se používá v názvech procedur a tabulek.

- `dwh/stage-minimal` **Jen potřebné řádky a sloupce. Minimum joinů.** Hlavní priorita je neohrozit funkčnost zdrojů.
- `dwh/stage-select-into` Tabulky se plní přes `DROP TABLE IF EXISTS ... SELECT ... INTO ...`, ne přes `TRUNCATE`. Výjimka jsou větší tabulky.
- Žádná velká transformační logika.

`dwh/proc-prefix` Tady se nerozlišují dimenzní a faktové tabulky.

| Co | Vzor | Příklad | Poznámka |
| --- | --- | --- | --- |
| Plnicí procedury | `dbo.nsp10Dim<SourceCode>_<Entita>` | `nsp10HN_Mena`, `nsp10HN_Subjekty` | Obvykle jedna procedura jedna tabulka, ale není to pravidlo |
| Tabulky | `s10<SourceCode>_<SpolZkratka>.Fact<Entita>` | `s10HN_AX.Mena` | |
| Názvy sloupců | Snaha je pojmenovat logicky, nikoli podle zdroje | Někdy je lepší použít zavedené názvosloví zdrojového systému | |
| Primární klíče | Nepoužívají se, pokud není zvláštní důvod | Zvláštní důvod může být zrychlení nápočtu vrstvy 20 | |

⚠️ Vzor a příklad v tabulce se liší (`Dim` a `Fact` ve vzoru, v příkladu ne). Do vyjasnění se řiď sousedními soubory ve stejném adresáři.

## Vrstva 20 - STAR

Adresáře `20_dim` a `20_fact`. Plní se **nejdřív dimenze, pak faktovky**. Faktovky při plnění dimenze používají.

`dwh/unknown-member` Dimenze mají většinou řádek pro neznámou hodnotu (`Key = -1`), aby faktovky nepotřebovaly outer join. Neplatí to pro fixní dimenze (třeba dimenze společností) nebo pokud je hodnota ve faktovce vždy vyplněná (třeba datum).

`dwh/proc-prefix` a `dwh/key-names` Názvy ve vrstvě 20:

| Co | Vzor | Příklad |
| --- | --- | --- |
| Plnicí procedury dimenzí | `dbo.nsp20Dim<Entita>` | `nsp20DimUcet`, `nsp20DimUtvar` |
| Plnicí procedury faktovky | `dbo.nsp20Fact<Entita>` | `nsp20FactKurz` |
| Dimenze | `s20.Dim<Entita>` | `s20.DimUcet` |
| Faktovka | `s20.Fact<Entita>` | `s20.FactDenik` |
| Primární klíč dimenze | `Dim<Entita>ID INT IDENTITY`, constraint `PK_Dim<Entita>ID` | `DimUcetID`, `PK_DimUcetID` |
| Primární klíč faktovky | Většinou žádný. Pokud výjimečně existuje, je to surrogátní `ID INT IDENTITY` bez jednotné konvence pro název constraintu | `FactKurz.ID` |
| Plnicí procedury alokace | `dbo.nsp20Alloc<Entita>` | `nsp20AllocPartnerPodil_AX` |
| Alokační tabulka | `s20.Alloc<Entita>`. Podíly pro rozpad faktovky na prvky dimenze, faktovky z ní jen čtou. Plní se **mezi faktovkami**: po těch, ze kterých čte, a před těmi, které ji používají | `s20.AllocPartnerPodil_AX` |

Tabulky `s20.Dim<Entita>_<SpolZkratka>` (pro jednu společnost) jsou platné, trvalé tabulky s vlastním PK `Dim<Entita>ID`. Nejsou to dočasné mezistupně, i když u nich `ID` typicky **není generované** (je to business klíč ze zdroje). Slouží samostatně a zároveň jako zdroj pro sdílenou `s20.Dim<Entita>`, kde už `Dim<Entita>ID` obvykle je skutečná `IDENTITY`.

## Vrstva 30 - MART

`dwh/mart-standalone` Adresář `30_mart`, pod ním jednotlivé marty. **Každý mart je samostatný**, star schéma. Plní se **faktovky, pak dimenze**. Faktovky jsou typicky grupované a v dimenzích jsou jen prvky, které jsou ve faktovkách.

Mart slouží jako zdroj dat pro sémantický model v Power BI. `dwh/mart-one-proc` **Celý mart vytváří jedna procedura.** Cizí klíče kontrolují vazby: na začátku procedury se všechny dropnou a po naplnění se vytvoří znovu. Součástí martu je model PBIP, nikdy `.pbix`, viz skill `pankostka-powerbi`.

`dwh/proc-prefix` a `dwh/key-names` Názvy ve vrstvě 30:

| Co | Vzor | Příklad |
| --- | --- | --- |
| Plnicí procedura | `dbo.nsp30<MART>` | `nsp30EKO.sql`, `nsp30AXMain.sql` |
| Dimenze | `s30<MART>.Dim<Entita>` | `s30EKO.DimUcet` |
| Faktovka | `s30<MART>.Fact<Entita>` | `s30EKO.FactDenik` |
| Primární klíč dimenze | Constraint `PK_Dim<Entita>` (bez `ID` na konci, na rozdíl od vrstvy 20) na sloupci `Dim<Entita>ID`. Jestli je hodnota generovaná, nebo převzatá ze zdroje, je věc okolností. Starší výjimkou je PK na business klíči `<Entita>CS` | `PK_DimUcet` |
| Primární klíč faktovky | Žádný | - |
| Cizí klíč dimenze | `FK_Fact<Entita>Dim<Entita2>` na sloupci `Dim<Entita2>ID`, dropne se na začátku procedury a vytvoří znovu po naplnění | `FK_FactDenikDimUcet` |

Sémantický model se jmenuje `Kostka<Mart>`. Pokud je celý mart určen jen pro jednu společnost, dostane název kostky, schématu i procedury sufix `_<SpolZkratka>` (`KostkaVysledovka_AX`). Mart pro všechny nebo více společností sufix nemá (`KostkaEKO`).

`baseline/` je testovací lavice martu: soubory a reporty, kterými se ověřuje a porovnává chování modelu, typicky proti prázdné šablonové variantě nebo proti dřívějšímu referenčnímu stavu. Prázdný šablonový sešit se jmenuje `Kostka<Mart>_EMPTY.xlsx`. `reports_to_users/` je na hotové výstupy (xlsx), PBIP tam nepatří.

## Jmenné konvence

- Pro systémové věci anglická zažitá zkratka (suffix, prefix). **Názvy objektů česky, ale bez diakritiky.** Diakritika jen v datech a komentářích.
- Jednotné číslo. **PascalCase**, podtržítka a pomlčky jen v konkrétních významech (podtržítko před zkratkou společnosti, pomlčka před sufixem `-VZOR`, `-DRAFT`, `-TMP`).
- `dwh/unique-names` **Unikátní názvy tabulek i sloupců**, aby šly fulltextově najít. Dimenzní a faktové tabulky používají pro názvy sloupců zkratku entity.
- `dwh/always-schema` **Vždy uváděj schéma.** `s20.FactDenik`, nikdy jen `FactDenik`.
- `dwh/name-before-dash` **Název objektu v databázi je vše před první pomlčkou** v názvu souboru: `nsp10HN_Denik-VZOR.sql` obsahuje proceduru `nsp10HN_Denik`.
- `dwh/unique-names` **Pozor na obecné názvy sloupců.** Jakmile se použije obecný název (`Cena`, `Ks`), nejde už udělat ukazatel se stejným názvem. Vhodné jsou dvouslovné názvy, tedy `CenaMj`, v Power BI pak `Cena mj`.

`dwh/config-ddl-only` **Konfigurační tabulky** mají prefix `config` malými písmeny a název entity: `dbo.configHeliosDB`, `dbo.configSPOL`. Jsou vždy ve schématu `dbo` a nepatří do žádné vrstvy, plní se ručně. Do gitu patří jen jejich DDL, nikdy `INSERT` s hodnotami, v konfiguraci bývají hesla a connection stringy.

`dwh/company-suffix` **Více společností.** Tabulka nebo procedura jen pro jednu společnost má na konci `_<SpolZkratka>`. Platí to i ve vyšších vrstvách, pokud je objekt specifický pro jednu společnost a další společnost v budoucnu přibýt nemůže. Hojně se používá dynamické SQL (řetězec a `EXEC`), aby kód nemusel být pro každou společnost zvlášť.

## Zásady

- `dwh/start-from-vzor` **Při zakládání procedury vyjdi z procedury `-VZOR` ve stejném adresáři.** Vzorů může být víc, třeba ve stage jeden s `OPENQUERY` a druhý bez. Když nevíš, který použít, zeptej se.
- **Podívej se na sousední soubory ve stejné vrstvě** a napodob jejich styl. Konzistence s existujícím kódem je důležitější než vlastní preference.
- `dwh/no-unit-price` **Nikdy nepoužívej jednotkové ceny.** Vždy množství a cenu celkem. Jednotková cena se počítá až v DAX podílem.
- `dwh/no-stored-measures` **Míry se neukládají jako sloupec.** Faktovka drží jen hrubou hodnotu na úrovni zrnitosti (`DenikKc`), míry (`MD`, `DAL`, `Obrat`) se počítají výhradně v DAX.
- **Nepřejmenovávej existující objekty bez potvrzení.** Visí na nich sémantické modely, které se tím tiše rozbijí.
- **Necommituj hesla, tokeny, klíče ani connection stringy s přihlašovacími údaji.** Název serveru a databáze ano, v M partition PBIP modelů být musí.

`dwh/minimal-logging` **Minimální logování.** Pokud je databáze v recovery modelu SIMPLE (nebo BULK_LOGGED), jsou `SELECT ... INTO` a `INSERT ... WITH (TABLOCK)` do prázdné tabulky minimálně logované a transakční log zůstává malý i u stomilionových faktovek. Když se tahle vlastnost poruší, například `INSERT` do tabulky, která už řádky má, log naroste řádově a obvykle jde o chybu v návrhu, ne v nastavení. Jaký recovery model databáze má, patří do `CLAUDE.md` repa.

## Výjimka z pravidla

Vědomé porušení pravidla zapiš komentářem na řádek nálezu nebo na řádek nad ním. Komentář jmenuje identifikátor pravidla a za čárkou důvod:

```sql
-- pankostka: allow dwh/no-read-up, kontrola součtů proti martu, nic neplní
SELECT SUM(m.DenikKc) FROM s30EKO.FactDenik AS m
```

Identifikátorů může být víc, oddělených čárkou. **Důvod je povinný**, bez něj skript nález hlásí dál.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je soubor `.sql`, adresář (prochází se rekurzivně), nebo `--changed` pro soubory `.sql`, které git hlásí jako změněné nebo nové. Vrstva se pozná podle adresáře s prefixem `00_`, `10_`, `20_` nebo `30_` v cestě.

1. **Spusť skript** s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_dwh.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Výstup je jedna řádka na neshodu ve tvaru `soubor:řádek: [identifikátor] zpráva`, řádek s výjimkou `pankostka: allow` a důvodem se nehlásí. Pravidla:
   - `dwh/name-before-dash`: název procedury v `CREATE` se liší od názvu souboru před první pomlčkou,
   - `dwh/proc-prefix`: prefix procedury nesedí na vrstvu,
   - `dwh/no-read-up`: nižší vrstva odkazuje na schéma vyšší vrstvy (kontroluje se i dynamické SQL v řetězcích),
   - `dwh/mart-standalone`: mart odkazuje na schéma jiného martu,
   - `dwh/key-names`: název primárního nebo cizího klíče mimo konvenci vrstvy.

   Soubory a adresáře se sufixem `-TMP` skript přeskočí.

2. **Projdi soubory sám** na to, co skript nepozná: `dwh/always-schema` (odkazy na tabulky bez schématu, procedury samotné se zakládají tak, jak to dělají sousední soubory), `dwh/unknown-member`, `dwh/load-order` v procedurách `_RUN`, `dwh/stage-minimal`, `dwh/no-unit-price`, `dwh/no-stored-measures` a `dwh/unique-names`. Pravidla T-SQL kontroluje skill `pankostka-tsql`.

3. **Vypiš výsledek** po souborech, u každé neshody identifikátor pravidla a konkrétní návrh opravy, na konci souhrn.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí. Přejmenování procedury nebo tabulky jen navrhni, visí na ní job a modely.
