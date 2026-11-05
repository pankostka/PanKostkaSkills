# Obecný import

Doplněk skillu `pankostka-nephrite`. Obecný import (třída 515) je nástroj Heliosu, který zapíše data do jedné třídy přes aplikační logiku: dosadí implicitní hodnoty, spustí editační pravidla a integritní omezení, vygeneruje referenci. Proto je to správná cesta, jak dostat data do systémových tabulek, kam se z SQL zapisovat nesmí (`nephrite/no-write-system`). Podrobný popis je v nápovědě Heliosu na stránce `Obecný_import`, viz Dokumentace Heliosu ve `SKILL.md`. Tady je jen to, na co se při práci narazilo.

## Kde je definice

| Tabulka | Obsah |
| --- | --- |
| `lcs.genimp` | hlavička importu: cílová třída (`cislo_tridy`), pořadač (`cislo_poradac`), dotaz (`pre_qry`), mapování sloupců (`columns_mapping`: `0` dle pořadí, `1` dle názvů), transakční rozsah (`transaction_scope`), chování při konfliktu primárního klíče (`konflikt_pk`: `S` vynechat, `W` přepsat, `N` vložit nový) |
| `lcs.genimp_def` | definice sloupců: `dbname`, číslo vztahu, pořadí, příznak primárního klíče importu (`is_pkey`) |

Do obou tabulek se z SQL nezapisuje, definice se upravuje ve formuláři importu a funkcí Editace definice sloupců. Čtení je v pořádku a hodí se, když je potřeba zjistit, co import opravdu dělá.

## Dotaz jako zdroj dat

Import umí číst ze souboru, nebo z databáze dotazem v `pre_qry`. U dotazu:

- **Dotaz musí začínat slovem `select` a nesmí obsahovat komentáře.** Komentáře patří do skriptu, který zdroj připravuje, ne do pole dotazu.
- **Místo dotazu může být volání uložené procedury** s explicitně pojmenovanými parametry.
- **Účet aplikačního serveru potřebuje `SELECT` na zdrojovou tabulku**, resp. `EXECUTE` na proceduru. Vývojář je obvykle v roli, která práva má, takže chybějící právo se projeví až při spuštění pod jiným účtem.

Osvědčený postup je **procedura naplní vlastní tabulku a import nad ní jen vybírá**. Kontroly a převody se dají ladit v SQL, tabulka je vidět a import zůstává jednoduchý.

## Mapování sloupců dle pořadí

Sloupce dotazu se párují s definicí sloupců podle pořadí. **Definice musí obsahovat všechny importované sloupce ve stejném pořadí jako dotaz.** Definice s jediným sloupcem (třeba jen klíčem) nad dotazem s víc sloupci je chyba v nastavení: první sloupec dotazu se spáruje s klíčem a pro ostatní definice chybí.

## Mapování sloupců dle názvů

Sloupce se párují podle aliasu v dotazu. Definice sloupců pak není povinná, slouží jen k upřesnění, třeba k určení primárního klíče importu.

- **Atribut** se jmenuje jako sloupec v databázi. U nedokladových tříd stačí název bez tabulky (`reference_subjektu`), u dokladových je plný název (`lcs.<tabulka>.<sloupec>`) prakticky povinný.
- **Statický vztah** se jmenuje `<dbname>_refer` (reference navazovaného záznamu), `<dbname>_nazev` (název) nebo `<dbname>_cispor` (pořadač). Holý název vztahu bez přípony skončí chybou `Řetězec '...' byl rozpoznán jako vztah č. ..., ale neobsahuje příponu, která označuje vztah`.
- **Dynamický vztah** se jmenuje `<číslo vztahu>_refer`, `_nazev` nebo `_cispor`. Tak se zapíše vztah **zleva**, tedy definovaný na importované třídě.
- **Dynamický vztah zprava**, tedy definovaný na druhé třídě, potřebuje stranu: `<číslo vztahu>_R_refer`. Bez ní import hlásí `Číslo ..._refer ze seznamu sloupců nelze rozpoznat jako vztah třídy č. ...` a vztah se nenaváže. Ze které strany vztah je, ukáže `lcs.vztahy.cislo_tridy`. Ověřeno: účtovací skupina zboží na kmenové kartě je vztah ze strany skupiny a se zápisem `_R_refer` se navázala.
- **Atribut, jehož název končí na `_nazev`, `_refer` nebo `_cispor`** (třeba `alternativni_nazev` na kmenové kartě), import podle názvů nepozná: `Řetězec '...' ze seznamu sloupců nelze rozpoznat jako atribut nebo vztah`. Nepomůže ani plný databázový název `lcs.<tabulka>.<sloupec>`. Pravděpodobně jde o příponu vyhrazenou pro vztah. Ověřené řešení zatím není; zbývá mapování dle pořadí, nebo atribut doplnit jinak.
- **Alias začínající číslicí nebo obsahující tečku** se v T-SQL píše v hranatých závorkách.

## Cílový pořadač

**Při mapování dle názvů jde jeden import jen do jednoho pořadače.** Volba Zadání cílového pořadače `Jako první atribut v souboru` je v nápovědě popsaná pro definici sloupců dle pořadí. S mapováním dle názvů import první hodnotu řádku spotřebuje jako číslo pořadače, ale seznam názvů neposune, takže každá hodnota skončí v sousedním sloupci (chyba `Couldn't store <...> in ... Column`). Pořadač nejde poslat ani jako atribut: `lcs.subjekty.cislo_poradace` nápověda řadí mezi atributy, které import nenabízí. Pro víc pořadačů proto vzniká kopie importu na každý pořadač, s pořadačem v definici a podmínkou v dotazu. **Primární klíč kontrolovat v nastav na Celá třída**, jinak import kartu přesunutou do jiného pořadače nenajde a založí duplicitu.

## Hodnota vztahu

Vztah se dohledává podle reference, názvu a pořadače a musí se dohledat **právě jeden** záznam. Když reference není jednoznačná, dá se místo ní poslat **hvězdička a číslo primárního klíče** (`'*' + CAST(cislo_subjektu AS varchar(12))`), import pak hledá podle `cislo_subjektu`. Funguje i pro nonsubjektové třídy. Klíč se dohledá ve zdrojovém dotazu, takže chybějící vazba je vidět už tam, ne až v auditlogu.

**Ověř, na jakou třídu vztah vede**, název vztahu to neříká. Cíl se pozná podle pořadače záznamů, které už ve vztahu jsou, v jiné databázi s daty (`lcs.subjekty.cislo_poradace` -> `lcs.poradace.cislo_tridy`). Když import hlásí `Nedohledán záznam pro vztah ... Nalezeno: 0 odpovídajících záznamů` i pro číslo subjektu, které existuje, vede vztah na jinou třídu.

## Hodnoty atributů s editačním stylem

Atribut s editačním stylem (výběr ze seznamu) ukládá kód, ne popisek. Platný kód s jiným významem, než se čekalo, projde importem bez chyby a pozná se až na formuláři. Povolené hodnoty bývají zabudované v aplikaci, ne v tabulkách `lcs.case_editstyl_*`. Význam kódů se proto ověřuje v nápovědě k formuláři a podle rozložení hodnot v databázi s daty, ne odhadem z písmene. Příklad: typ kmenové karty `V` není výrobek, ale vratný obal; zboží, materiál i vlastní výrobky mají běžně `Z`.

## Povinné údaje

Import spouští editační pravidla formuláře. Povinný vztah, který v dotazu chybí nebo se nenaváže, skončí chybou `Editační pravidlo (č. ...): Zadejte vztah na ...` a záznam se neuloží. Varování o nenavázaném vztahu je pak v auditlogu o řádek výš a je to skutečná příčina.

## Transakční rozsah

| Rozsah | Chování |
| --- | --- |
| Soubor/Db dotaz | všechno, nebo nic; jedna chyba vrátí celý import |
| Záznam | uloží se, co prošlo |
| Test | jako Soubor/Db dotaz, ale vždy se vrátí; všechny chyby skončí v jednom auditlogu |

**Novou definici lad v režimu Test** a s omezeným počtem řádků (`TOP 100` v dotazu nebo Import od řádky / po řádek). Nic se neuloží a auditlog ukáže všechny problémy najednou. Rozsah Soubor/Db dotaz je pak vhodný pro ostrý běh nad daty, která procedura předem zkontrolovala. Nápověda doporučuje obecný import zhruba do 10 tisíc záznamů.

## Chyby importu

Výsledek importu se zapisuje do auditlogu, viz Auditlog ve `SKILL.md`. Import vypíše na začátku varování k definici (nerozpoznané sloupce), pak hlášení po řádcích a na konci souhrn: počet zpracovaných, úspěšných a neúspěšných záznamů a čísla chybných řádků.
