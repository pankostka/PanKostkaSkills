---
name: pankostka-powerbi
description: Zásady pro sémantický model a report Power BI ve formátu PBIP - TMDL a PBIR místo .pbix, názvy tabulek, atributů, klíčů a hierarchií, skryté sloupce a isAvailableInMdx, money pro peněžní sloupce, názvy měr a časové tokeny (LY, YTD, R12M), DAX pro time intelligence, field parameters, role a RLS, Excel nad modelem, mrtvé odkazy v PBIR. Použij vždy, když zasahuješ do souborů .tmdl, do reportu PBIR (page.json, visual.json, report.json) nebo píšeš míru v DAX. S argumentem (adresář modelu nebo reportu, soubor .tmdl nebo --changed) zkontroluje model a reporty a vypíše neshody.
argument-hint: "[adresář | soubor.tmdl | --changed]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_powerbi.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_powerbi.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/validate_pbir.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/validate_pbir.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/validate_pbir_corpus.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/validate_pbir_corpus.py *)
---

# Power BI - model a report

Zásady pro sémantický model a report Power BI uložené jako soubory v gitu. Podrobnosti k jednotlivým tématům jsou v souborech vedle tohoto, čti je, až když na téma narazíš:

| Soubor | Kdy ho číst |
| --- | --- |
| `${CLAUDE_SKILL_DIR}/measures.md` | píšeš nebo pojmenováváš míru, hlavně časové varianty (LY, YTD, R12M), nebo zvažuješ calculation group |
| `${CLAUDE_SKILL_DIR}/field-parameters.md` | zakládáš nebo upravuješ field parameter, tedy tabulku `Select...`, nebo vizuál, který ho používá |
| `${CLAUDE_SKILL_DIR}/roles.md` | zakládáš nebo měníš roli, RLS nebo OLS |
| `${CLAUDE_SKILL_DIR}/excel.md` | uživatel čte model kontingenční tabulkou v Excelu, nebo ji sestavuješ skriptem |
| `${CLAUDE_SKILL_DIR}/glossary.md` | narazíš na zkratku (PBIP, PBIR, TMDL, RLS, TI), nebo zavádíš novou |

Argument: `$ARGUMENTS`

## Formát

`powerbi/pbip-only` Model se ukládá výhradně jako **PBIP**, nikdy jako binární `.pbix`. Je to formát vhodný pro git: sémantický model jako **TMDL** (`definition/*.tmdl`), report jako **PBIR** (`definition/pages/<page>/page.json` a `visuals/<visual>/visual.json`, jeden soubor na stránku a vizuál). Nejde tedy ani o starý `.bim`, ani o jeden velký `report.json`. Kam se PBIP v konkrétním repu ukládá, je věc struktury toho repa.

Když narazíš na `.pbix`, nahlas ho uživateli dřív, než cokoli uděláš.

## Názvy v TMDL

Při zásahu do modelu vždy zkontroluj:

- `powerbi/table-no-diacritics` **Názvy tabulek jsou vždy bez diakritiky**, tedy `table DimDoklPrvotni`, ne `DimDoklPrvotní`. Platí to i pro název souboru (`DimDoklPrvotni.tmdl`), název partition, `ref table` v `model.tmdl`, `PBI_QueryOrder` a odkazy v `relationships.tmdl`. Diakritika je jen v **atributech** (sloupcích, hierarchiích, mírách).
- `powerbi/attribute-prefix` **Viditelné atributy vždy pojmenuj `<Zkratka dimenze> <Atribut>`**: zkratka **i** atribut s diakritikou, atribut velkým písmenem. Zkratka je s diakritikou, i když tabulka nebo fyzický sloupec v databázi diakritiku nemá (tabulka `DimUcet` má atributy `Účet Název`, `Účet ČísNáz`, `Účet Charakter`). Fyzický sloupec v databázi je bez diakritiky (`UcetNazev`), přejmenování na zobrazované jméno se dělá v M partition (`Table.RenameColumns`).
- `powerbi/key-keep-name` **Primární a surrogátní klíče nepřejmenovávej.** Konvence `<Zkratka dimenze> <Atribut>` platí pro **popisné** atributy, ne pro klíče. Klíč si drží fyzický název ze zdroje (`Dim<Entita>ID`), i když ho záměrně odkryješ uživateli. `DimSaldo.'Sld ID'` je proti `DimSaldo.DimSaldoID` v DAXu i v definici relace nečitelné a u vazby `fromColumn: FactDenik.DimSaldoID`, `toColumn: DimSaldo.'Sld ID'` už z názvů není vidět, že jde o tentýž klíč. Přejmenování navíc vynutí apostrofy kvůli mezeře. Klíč do `Table.RenameColumns` vůbec nedávej.
- `powerbi/hierarchy-at` **Hierarchie pojmenuj s prefixem `@`** a dej je do display folderu `Atributy`, pokud je nepřesuneš jinam. Zavináč není konvence Power BI: seznam polí řadí abecedně a speciální znak vytáhne hierarchie nad sloupce. **Apostrofy kolem názvu piš jen tehdy, když je v názvu mezera**, tedy `hierarchy @Účet`, ale `hierarchy '@DPrv Třída'`. Desktop zbytečné apostrofy při uložení zahodí, takže jen vyrobí diff.
- `powerbi/sort-by-column` Každý textový sloupec, který se má řadit jinak než abecedně, má **`sortByColumn`**. Typicky měsíce a dny v týdnu, a hlavně v **role-playing dimenzích**.
- `powerbi/hide-technical` **Technické sloupce skrývej** (`isHidden`). Surrogátní klíče se v reportu standardně nezobrazují. Výjimka je dimenze, která nemá žádný jiný atribut vyplněný vždy: tam je odkrytý klíč jediný spolehlivý popisek řádku a odkryje se vědomě, s fyzickým názvem.
- `powerbi/measure-format-folder` Míry mají `formatString` a jsou zařazené do display folderu.

`powerbi/no-rename-legacy` **Starší objekty, které konvenci porušují, nepřejmenovávej bez potvrzení.** Visí na nich reporty a vizuály, které se tím tiše rozbijí. Seznam takových výjimek patří do `CLAUDE.md` repa.

## Velikost modelu

`powerbi/fact-hidden-no-mdx` **Skrytý sloupec faktové tabulky má `isAvailableInMdx: false`.** Power BI ke každému sloupci staví i hierarchii atributu: setříděný seznam všech různých hodnot a převodní tabulky. Potřebují ji jen klienti, kteří se ptají jazykem MDX, tedy hlavně kontingenční tabulka v Excelu. Vizuály Power BI posílají DAX a hierarchii nepoužívají. Skrytý sloupec v Excelu vidět není, takže jeho hierarchie je čistá ztráta místa.

Nejvíc to ušetří u sloupců s mnoha různými hodnotami. V modelu o 700 MB s faktovkou o 6,7 milionu řádků ušetřil samotný klíč transakce 39 MB a všechny skryté sloupce faktovek dohromady zhruba čtvrtinu modelu.

Vlastnost patří za `formatString`, kam ji ukládá Desktop, jinde vyrobí diff při dalším uložení. Desktop ji u nového sloupce sám nenastaví, takže se doplňuje u každé nové faktovky. **Na dimenzích ji nenastavuj**, jejich atributy uživatelé v kontingenčních tabulkách používají.

`powerbi/money-type` **Peněžní sloupce velkých faktovek ukládej v MSSQL jako `money`.** Power Query načte `decimal(p,s)` vždy jako `Decimal Number`, tedy double. `dataType: decimal` napsaný v TMDL ručně nepomůže, Desktop ho při refreshi přepíše podle M dotazu. Typ `money` Power Query rozpozná jako `Currency.Type` (Fixed Decimal) a v modelu vydrží. Převod v M (`Table.TransformColumnTypes(..., Currency.Type)`) je jen nouzové řešení: u milionů řádků refresh výrazně zpomalí a na notebooku nemusí doběhnout (`Memory Allocation failure`).

Fixed Decimal je ve VertiPaq celé číslo se škálou 4, komprimuje se líp než double a `SUM` vychází přesně. U double zůstává chyba v posledních bitech a vyrovnané saldo ukáže `-5,03E-8`. Míry, které porovnávají s nulou, ale `ROUND` dál potřebují.

`money` má jen 4 desetinná místa a zaokrouhluje mezivýsledky jinak než `decimal`. Proto se v něm jen ukládá, nepočítá: výpočty v plnicí proceduře proveď v `decimal` a na `money` převeď až ve sloupci tabulky, kterou čte model. Nepoužívej ho pro hodnoty s víc než 4 desetinnými místy, typicky kurzy. U atributů dimenze, které se nesčítají, stačí `decimal`.

## Názvy měr

Pozice zkratky v názvu míry nese význam:

| Pozice | Co mění | Příklad |
| --- | --- | --- |
| **Prefix** | povahu čísla: `#` počet, `Ø` průměr | `#Dokladů`, `ØCena` |
| **Suffix** | časový kontext | `HV LY`, `HV YTD` |
| **Suffix na časovém tokenu** | operátor srovnání | `HV LY△`, `HV LY%` |

`powerbi/measure-token-order` Operátor `△` nebo `%` patří **za** časový token. Seznam polí řadí abecedně, takže `HV LY`, `HV LY%`, `HV LY△` drží pohromadě varianty jednoho období. U kombinace tokenů je **nejdřív kumulace, pak posun**: `YTD LY`, ne `LY YTD`. Tokeny, pravidla pro DAX a vzory jsou v `measures.md`.

## Report PBIR

- `powerbi/report-logical-id` **Každý report má vlastní `logicalId`** v `.platform`. Report založený kopií jiného ho musí mít přegenerovaný, jinak je pro Fabric git integraci pořád tentýž objekt a druhý přepíše první.
- `powerbi/report-images` **Obrázky se při kopírování netáhnou samy.** Vizuál typu `image` odkazuje na `StaticResources/RegisteredResources/` přes `ResourcePackageItem`. Při kopírování stránky mezi reporty se musí zkopírovat i soubor **a** zapsat do `resourcePackages` v `report.json`, jinak stránka spadne na chybějícím obrázku.
- `powerbi/report-dead-refs` **Mrtvé odkazy na model PBIR nehlásí.** Zbytky po jiném modelu se schovávají v `sortDefinition`, v `dataPoint` selektorech barev a v `columnWidth`. Dotaz vizuálu je přitom v pořádku, takže Desktop nic neoznačí. Hledej je strukturálně, ne grepem: `"queryRef": "DimDatum.Datum"` obsahuje řetězec `Datum`, takže hledání podle názvu tabulky hlásí falešné poplachy. Na to je `validate_pbir.py`, viz Kontrola. **Po každém zásahu do reportu nebo modelu ho spusť.**
- `powerbi/report-no-invented-json` **Nevymýšlej tvar JSON.** Vlastnost formátování nebo hodnota, která není doložená v žádném jiném reportu, je skoro jistě vymyšlená. Desktop ji buď odmítne, nebo tiše ignoruje. Na to je `validate_pbir_corpus.py`.
- **Report s live connect** (`datasetReference.byConnection`) obsahuje název workspace. Není to heslo, ale je to produkční identifikátor. Když to v repu vadí, drží se report `byPath` a přepne se až při nasazení.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je adresář (prochází se rekurzivně), soubor `.tmdl`, nebo `--changed` pro soubory `.tmdl`, které git hlásí jako změněné nebo nové.

1. **Spusť kontrolu modelu** s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_powerbi.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Výstup je jedna řádka na neshodu ve tvaru `soubor:řádek: [identifikátor] zpráva`. TMDL nemá komentáře, takže výjimka `pankostka: allow` tu není: vědomou odchylku vyřaď z výpisu s vysvětlením. Pravidla:
   - `powerbi/table-no-diacritics`: název tabulky s diakritikou,
   - `powerbi/key-keep-name`: přejmenovaný klíč `Dim<Entita>ID`,
   - `powerbi/hierarchy-at`: hierarchie bez `@`, zbytečné apostrofy kolem názvu bez mezery,
   - `powerbi/measure-format-folder`: míra bez `formatString` nebo display folderu,
   - `powerbi/measure-token-order`: operátor před časovým tokenem, posun před kumulací,
   - `powerbi/fact-hidden-no-mdx`: skrytý sloupec tabulky `Fact*` bez `isAvailableInMdx: false`,
   - `powerbi/role-name`: role mimo tvar `Role<Model><Skupina>`,
   - `powerbi/select-name`: field parameter mimo tvar `Select[Dim]<Rozsah>[_TI][A|B]`.

2. **Spusť kontrolu reportů**, pokud argument obsahuje reporty (`*.Report`) nebo je to `--changed` a změnil se report:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/validate_pbir.py --quiet <adresář>
   python ${CLAUDE_SKILL_DIR}/scripts/validate_pbir_corpus.py --report <cesta.Report>
   ```

   `validate_pbir.py` hlídá `powerbi/report-dead-refs`, najde reporty sám a spáruje je s modelem. `CHYBA` je mrtvý odkaz, který se musí opravit, `VAROVANI` je zbytek, který nic nerozbije, ale patří uklidit. `validate_pbir_corpus.py` hlídá `powerbi/report-no-invented-json`: porovná tvar reportu s ostatními reporty v git repu (korpus jde rozšířit přepínačem `--corpus`). Jeho nález není chyba sama o sobě, jen konstrukce, která nikde jinde není: ověř ji proti dokumentaci. U reportu, který nikdo neupravoval, nálezy z korpusu jen shrň počtem.

3. **Projdi model sám** na to, co skripty nepoznají:
   - `powerbi/sort-by-column`: textové sloupce, které potřebují `sortByColumn`,
   - míra bez `formatString`: když vrací text (jméno uživatele, odkaz), je to v pořádku a hlášení vyřaď,
   - `powerbi/hide-technical`: odkrytý klíč, vědomá výjimka, nebo chyba,
   - `powerbi/attribute-prefix`: atributy mimo tvar `<Zkratka> <Atribut>`,
   - TI míra, která opakuje tělo základní míry místo `CALCULATE([X], ...)`, `%` bez `ABS` ve jmenovateli, `PREVIOUSMONTH` místo `DATEADD` (viz `measures.md`),
   - obsah field parameterů: strop asi 30 položek, žádné klíče ani skryté sloupce, časové varianty zvlášť (viz `field-parameters.md`),
   - starší objekty z výjimek v `CLAUDE.md` repa: nehlas je jako chybu, jen připomeň, že se nepřejmenovávají bez potvrzení.

4. **Vypiš výsledek** po souborech, u každé neshody identifikátor pravidla a konkrétní návrh opravy, na konci souhrn.

5. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí. Přejmenování tabulky, sloupce, míry nebo role rozbije reporty a přiřazení skupin, takže ho vždy jen navrhni.
