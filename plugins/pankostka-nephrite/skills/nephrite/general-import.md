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

**Pořadí sloupců v dotazu je pořadí, v jakém import nastavuje hodnoty**, a po každé hodnotě proběhne logika formuláře. Pozdější sloupec tak může přepsat hodnotu, kterou logika dopočítala z dřívějšího, a naopak. Sloupec, ze kterého logika dopočítává jiný, proto patří před něj. Ověřeno na položce skladového dokladu: prázdná `cena_jedn_mena` zařazená za `cena_jedn` u dokladu v Kč přepočítala cenu v Kč na 0, v opačném pořadí cena zůstala.

**Reference z dotazu má přednost před maskou pořadače.** Import ji převezme i u pořadače s dynamickou maskou a negeneruje novou. Ověřeno na tvaru `OPT-117/2026` v pořadači s maskou `############` a zapnutou kontrolou reference.

## Cílový pořadač

**Při mapování dle názvů jde jeden import jen do jednoho pořadače.** Volba Zadání cílového pořadače `Jako první atribut v souboru` je v nápovědě popsaná pro definici sloupců dle pořadí. S mapováním dle názvů import první hodnotu řádku spotřebuje jako číslo pořadače, ale seznam názvů neposune, takže každá hodnota skončí v sousedním sloupci (chyba `Couldn't store <...> in ... Column`). Pořadač nejde poslat ani jako atribut: `lcs.subjekty.cislo_poradace` nápověda řadí mezi atributy, které import nenabízí. Pro víc pořadačů proto vzniká kopie importu na každý pořadač, s pořadačem v definici a podmínkou v dotazu. **Primární klíč kontrolovat v nastav na Celá třída**, jinak import kartu přesunutou do jiného pořadače nenajde a založí duplicitu.

## Doklad s položkami

Dokladová třída (hlavička a položky, třeba skladový doklad nebo objednávka) se importuje jedním dotazem: **jeden řádek dotazu je jedna položka a sloupce hlavičky se na řádcích opakují.**

- **Primární klíč importu je na hlavičce** a smí jím být jen atribut nebo statický vztah hlavičky. V definici sloupců musí být na začátku, jinak import doklady podle klíče nerozdělí. Řádky se stejnou hodnotou klíče import složí do jednoho dokladu jako jeho položky. Klíčem může být i UDA, v definici sloupců se zapíše plným názvem `lcs.uda_<tabulka hlavičky>.<sloupec>`.
- **Řádky jednoho dokladu musí jít v dotazu za sebou**, dotaz proto řadí podle klíče.
- **Řaď i podle pořadí položky.** Helios čísluje položky (`cislo_radky`) sám od 1 v pořadí, v jakém je import vloží. `ORDER BY` jen podle klíče pořadí položek uvnitř dokladu neurčuje, takže položky skončí v náhodném pořadí a nedají se spárovat se zdrojem. Druhým klíčem řazení je pořadí ze zdroje, nejlépe přečíslované od 1 bez mezer (`ROW_NUMBER() OVER (PARTITION BY <klíč> ORDER BY <pořadí ve zdroji>)`), pak se párují podle `cislo_radky`.

**Konflikt primárního klíče se týká celého dokladu:**

| Volba | Chování u dokladu |
| --- | --- |
| Přepsat | smaže všechny položky dokladu a založí je znovu podle dotazu |
| Vynechat | přeskočí celý doklad včetně položek |
| Vložit nový | založí druhý doklad, tedy duplicitu |

Přidat položky k existujícímu dokladu import neumí. Opakovaný běh s Přepsat proto zpracuje znovu všechny doklady včetně těch, které se nezměnily, a u velkého objemu trvá jako první běh. Pro přenos po částech je vhodnější Vynechat a dotaz, který doklady už přenesené vůbec nevrátí. Doklad změněný ve zdroji se pak v Heliosu smaže a import ho přenese znovu.

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

## Rychlost

**Import dokladů je pomalý kvůli logice Heliosu, ne kvůli databázi.** Ověřeno trace na importu objednávek: asi 0,1 s na položku a 2 s na doklad o 20 položkách, na jednu položku kolem 10 dotazů do databáze (zápis položky, kontroly karty, katalogového čísla, subjektu). SQL Server z toho času strávil asi 4 %, zbytek je aplikační server a obrátky mezi ním a SQL. Při 150 tisících položek to vychází na hodiny.

- **Index ani kontrola primárního klíče jen v pořadači znatelně nepomůže.** Hledání klíče je jeden rychlý dotaz na doklad. Index nad UDA s klíčem má smysl až u velké tabulky.
- **Vypnutí formulářové logiky v definici importu zrychlí zhruba o 40 %**, ale import pak nedopočítá to, co dělá formulář. Použij ho jen tam, kde dotaz posílá všechny hodnoty hotové a výsledek se zkontroluje proti zdroji.
- **Pomůže dělení na části a souběžný běh** více importů, třeba jednoho na pořadač, a Vynechat při konfliktu klíče, viz Doklad s položkami.

**Kde import tráví čas, ukáže trace ze SQL Profileru.** Soubor `.trc` přečte `sys.fn_trace_gettable`, ale jen na serveru, kde soubor leží. Bez SQL Serveru ho přečte skript `${CLAUDE_SKILL_DIR}/scripts/read_trc.py <soubor.trc>`: sečte dobu, čtení a CPU podle dotazů s nahrazenými literály a ukáže, kolik času připadá na databázi a kolik na mezery mezi dotazy. Velký podíl mezer znamená, že brzdou je aplikace, ne SQL.

## Chyby importu

Výsledek importu se zapisuje do auditlogu, viz Auditlog ve `SKILL.md`. Import vypíše na začátku varování k definici (nerozpoznané sloupce), pak hlášení po řádcích a na konci souhrn: počet zpracovaných, úspěšných a neúspěšných záznamů a čísla chybných řádků.
