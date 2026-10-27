---
name: pankostka-tsql
description: Zásady psaní T-SQL pro MS SQL Server - WHERE 1=1, JOIN na jednom řádku, sargable predikáty, CREATE OR ALTER, sekce v těle procedury s dvojitým END, hlavička procedury, kódování UTF-8. Použij vždy, když píšeš, upravuješ nebo kontroluješ SQL dotaz, uloženou proceduru (stored procedure), funkci nebo skript .sql. S argumentem (soubor, adresář nebo --changed) zkontroluje soubory proti zásadám a vypíše neshody.
argument-hint: "[soubor | adresář | --changed]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_tsql.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_tsql.py *)
---

# T-SQL - zásady

Zásady psaní T-SQL. Míří hlavně na uložené procedury, protože tam se text čte a upravuje opakovaně, ale formátování a výkonová pravidla platí i pro jednorázový dotaz.

Komentáře česky včetně diakritiky, názvy objektů bez diakritiky.

Skill má dva režimy podle argumentu. Bez argumentu se jen řiď zásadami níže při psaní a úpravách SQL. S argumentem postupuj podle sekce [Kontrola](#kontrola) na konci.

Argument: `$ARGUMENTS`

## Komentáře

**Text komentáře nezalamuj kolem sta znaků.** Věta patří na jednu řádku a zalomit se má teprve tam, kde by řádka přesáhla **200 znaků**. Zalomení po stovce trhá souvětí na kusy, které se čtou jako samostatné body: komentář je dvakrát vyšší, než musí být, a v proceduře zabírá místo, které mělo patřit kódu. Dvě stě znaků se na široký monitor vejde; hranice je tu jen proto, že editor SQL řádku nezalamuje sám.

Delší komentář se dělí podle **obsahu**, ne podle šířky. Nová řádka začíná novou myšlenkou, nikoli pokračováním rozpůlené věty.

## Idempotence

**Opakované spuštění skriptu nesmí nic rozbít.** Skript se spouští znovu po chybě, po nasazení do dalšího prostředí a při vývoji desítky krát - když je výsledek závislý na tom, kolikrát už proběhl, nedá se rozdělaná práce dokončit a chyba se hledá jinde, než je.

Procedury proto zakládej přes `CREATE OR ALTER PROCEDURE`. Vzor `IF OBJECT_ID(...) IS NOT NULL DROP PROCEDURE` s následným `CREATE` má dvě vady: mezi `DROP` a `CREATE` procedura neexistuje, a `DROP` zahodí oprávnění přidělená na objekt. Totéž platí pro funkce, pohledy a triggery.

## Čitelnost dotazu

**Podmínku začínej `WHERE 1=1`** a každou skutečnou podmínku připoj níž jako `AND`. Důvod je praktický: každý filtr je pak samostatná řádka, kterou lze zakomentovat nebo přesunout bez toho, aby zbytek dotazu přestal být syntakticky správný. Bez toho je první podmínka výsadní - zakomentovat ji znamená sáhnout i na tu druhou.

```sql
WHERE 1=1
    AND datum >= @od
    --AND spolecnost = @spolecnost
```

**Výjimkou je jediná podmínka celá na řádku s `WHERE`**, třeba `... FROM s20.DimZdroj_AD WHERE DimZdrojID <> -1` v řadě `UNION ALL` nebo `WHERE SourceSRV IS NOT NULL` v kurzoru. Tam není co zakomentovat bez sáhnutí na `WHERE` a `1=1` by řádku jen prodloužilo. Jakmile podmínka pokračuje na další řádek nebo obsahuje `AND` či `OR`, `1=1` je povinné. `BETWEEN ... AND` se za složenou podmínku nepočítá.

**Každý JOIN piš na jednu řádku**, tedy tabulku i podmínku spojení pohromadě. Seznam joinů se tak dá přečíst svisle a je vidět, kolik tabulek dotaz spojuje. Když se podmínka na jednu řádku nevejde, je to obvykle signál, že spojení je složitější, než se zdá, a zaslouží komentář.

## Výkon

**Predikáty musí být sargable**, tedy takové, aby na ně server mohl použít index. Nebal sloupec do funkce na levé straně podmínky - tím se index zahodí a z hledání se stane průchod celou tabulkou. Rozdíl je jen v zápisu, výsledek je stejný:

| Špatně | Správně |
|---|---|
| `WHERE CAST(datum AS date) = @d` | `WHERE datum >= @d AND datum < DATEADD(day, 1, @d)` |
| `WHERE YEAR(datum) = @rok` | `WHERE datum >= @zacatek AND datum < @zacatekPristiho` |
| `WHERE ISNULL(kod, '') = @kod` | `WHERE kod = @kod` a `NULL` řeš zvlášť |

Platí to jen pro levou stranu. Funkce nad parametrem nebo konstantou je v pořádku, protože se vyhodnotí jednou a index zůstane použitelný.

## Sekce v těle procedury

Delší procedura se dělí na **sekce**. Zápis je závazný, protože se podle něj kód sbaluje:

```sql
--********** NÁZEV SEKCE **********
-- poznámka/komentář 1
-- poznámka/komentář 2
IF 1=1 BEGIN

    TADY JE VÝKONNÝ KÓD

END --END Konec NÁZEV SEKCE
```

`IF 1=1 BEGIN` není podmínka, ale **obal, který jde v editoru sbalit**. Sekce se pak dá zavřít na jednu řádku a v proceduře o stovkách řádek je vidět postup místo textu. Vedlejší efekt: sekci lze vyřadit z běhu změnou na `IF 1=0` bez komentování celého bloku.

**Dvojité `END` na konci je součást konvence**, ne omyl. První je jazykové ukončení bloku, druhé je součást komentáře s názvem sekce - u zavřeného bloku je totiž vidět jen ta řádka s `END`, a bez názvu nikdo nepozná, co se právě sbalilo.

Nadpis sekce se píše velkými písmeny mezi hvězdičkami, aby šel najít hledáním a byl odlišitelný od běžného komentáře.

## Hlavička a konec procedury

Procedura začíná **komentářovým blokem** s klíči `POPIS`, `SPUSTENI` a `VYSTUPNI TABULKY`. Za nimi mohou být zakomentované testovací dotazy pro rychlé ověření výstupu - kdo proceduru otevře po roce, potřebuje spustit něco, co ukáže, jestli je výsledek správný, a vymýšlet to znovu je zbytečná práce.

Na konci procedury bývá **měření doby běhu** (`SELECT ... AS Trvani`). Bez čísla se u pomalého nápočtu jen hádá, která část ho zdržela.

**Naměřenou dobu běhu připiš komentářem na řádek `exec` v bloku `SPUSTENI`**, nejnovější hned za `--`, starší za ní. Formát je `m:ss (RRRR-MM-DD-hhmm)`; datum stačí u měření, na kterém záleží, a za datum se dá připsat okolnost, která čas ovlivnila. Číslo je orientační, slouží k odhadu, kolik bude stát spuštění, a k tomu, aby bylo vidět zpomalení. Přesnou historii nenahrazuje.

Konkrétní podoba hlavičky se zatím sjednocuje. Než bude ustálená, drž se toho, co je v proceduře nejblíž té upravované.

## Kódování souborů

**Soubory `.sql` drž v UTF-8 bez BOM.** Pokud narazíš na soubor v jiném kódování (typicky UTF-16 LE, jak ho ukládá SSMS), **nic v něm neupravuj a nahlas to.** Soubor se musí nejdřív převést. Editace v původním kódování rozsype diakritiku a v diffu je pak celý soubor jako změněný, takže skutečná úprava zmizí v šumu a nedá se zkontrolovat.

BOM je neviditelný, takže se neohlásí chybou, ale důsledkem: soubor se tváří jako změněný, i když se v něm nic nezměnilo, nebo nástroj načte první řádek i s hlavičkou.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je cesta k souboru, k adresáři (prochází se rekurzivně), nebo `--changed` pro soubory `.sql`, které git hlásí jako změněné nebo nové.

1. **Spusť skript** na mechanická pravidla, s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_tsql.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Skript vypíše jednu řádku na neshodu ve tvaru `soubor:řádek: [pravidlo] zpráva`. Kontroluje kódování, `CREATE` bez `OR ALTER` a víceřádkový nebo složený `WHERE` bez `1=1`. Soubor v UTF-16 nebo mimo UTF-8 jen nahlásí a dál ho nečte.

2. **Projdi soubory sám** na pravidla, která skript nepokrývá:
   - sargable predikáty,
   - JOIN rozdělený na více řádků,
   - sekce: nadpis mezi hvězdičkami, `IF 1=1 BEGIN`, dvojité `END` s názvem sekce,
   - hlavička procedury s `POPIS`, `SPUSTENI`, `VYSTUPNI TABULKY` a měření doby běhu,
   - komentáře zalomené kolem sta znaků nebo rozdělené podle šířky místo obsahu,
   - **dynamické SQL v řetězcích**: skript řetězce přeskakuje, takže `WHERE` a `CREATE` uvnitř `'...'` posuď ty.

   Soubor, který skript nahlásil jako UTF-16 nebo mimo UTF-8, nečti a nekontroluj.

3. **Vypiš výsledek** po souborech. U každé neshody `soubor:řádek`, porušené pravidlo a konkrétní návrh opravy. Neshody ze skriptu a z vlastní kontroly slouč do jednoho seznamu a u sporných případů napiš, proč jsou sporné. Na konec dej souhrn: kolik souborů, kolik neshod podle pravidel.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí.

U velkého adresáře nejdřív řekni, kolik souborů kontrola obsahuje, a u více než dvaceti se zeptej, jestli pokračovat, nebo zúžit výběr.
