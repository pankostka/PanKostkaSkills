# Uživatelsky definované formuláře

Doplněk skillu `pankostka-nephrite`. Uživatelsky definovaný formulář (UDF, formulářová šablona z FormBuilderu) mění vzhled editačního formuláře třídy: pořadí a rozložení polí, záložky, popisky, ochranu polí, barvy a dopočtené sloupce navíc. Podrobný popis je v nápovědě Heliosu na stránkách `FormBuilder_-_příručka` a `Šablony_pro_formuláře_-_popis`, viz Dokumentace Heliosu ve `SKILL.md`. Tady je to, co je potřeba k úpravě šablony přímo v databázi.

## Kde je definice

| Tabulka | Třída | Obsah |
| --- | --- | --- |
| `lcs.noris_form_templates` | 983 Šablony formulářů | šablona: `cislo_sablony`, `trida`, `nazev_sablony`, tři XML (`sablona_xml`, `sablona_data_xml`, `sablona_msg_xml`), `parameters` (`FormBuilder=1 TableName=MasterTable` pro hlavičku, `EntriesTable` pro položky), platnost `rozsah_platnosti` a `seznam_poradacu` |
| `lcs.noris_form_views` | 1346 Formulářový pohled | pohled: `master_template` a `entries_template` ukazují na `cislo_sablony`, `grid_ms_net` je uložené rozložení okna (záložky vztahů, splittery), platnost stejně jako u šablony |
| `lcs.noris_defa_form_view` | | implicitní pohled: `pohled` pro třídu nebo pořadač (`trida_nebo_poradac` `T`/`P`, `poradac`) a pro kategorii nebo uživatele (`kategorie_nebo_uzivatel` `K`/`U`) |

Aplikace šablonu zapisuje přes view `lcs.template_form` s triggery `INSTEAD OF`. Tabulka má vlastní triggery, které při změně obnoví cache aplikace (`lcs.set_cache_timestamp`), přepíšou název v `lcs.repository_translate` a při vložení založí práva v `lcs.permissions`.

**Co se zobrazí po zrušení šablony, řídí třída.** Příznak `use_default_template_for_form` v `lcs.noris_classes` (atribut třídy Při zrušení formulářové šablony/pohledu použít výchozí šablonu) určuje, co formulář ukáže, když uživatel v okně výběru šablon nebo pohledů zruší platnost aplikované šablony: `A` vrátí základní (systémovou) šablonu, `N` implicitní pohled podle `lcs.noris_defa_form_view`. Obdobný `use_default_template_for_browse` platí pro přehled. Výchozí hodnota sloupce je `N`, ve starších databázích ale bývají starší třídy nastavené na `A`, takže se hodnota mezi databázemi liší i bez zásahu správce. Kdo zavádí implicitní pohledy, má u třídy počítat s `N`, jinak uživatel po zrušení šablony skončí na systémovém formuláři místo na firemním.

**Formulář platí pro třídu, nebo pro pořadač.** Na šabloně a pohledu omezuje `rozsah_platnosti = 'P'` se `seznam_poradacu` (čísla oddělená čárkou), pro jaké pořadače se vůbec nabízejí. Častější je šablona pro celou třídu a implicitní pohled v `lcs.noris_defa_form_view` nastavený pro konkrétní pořadač, takže každý pořadač otevře jiný formulář. Kdo hledá, jaký formulář uživatel uvidí, čte obě místa.

## Tři XML šablony

| Sloupec | Obsah |
| --- | --- |
| `sablona_xml` | vzhled: `<template>` s `<tab>` (záložky a oddíly) a `<column>` (pole) |
| `sablona_data_xml` | datový zdroj: vlastní SELECT, prázdné znamená datový zdroj systémové šablony |
| `sablona_msg_xml` | texty `fm(<kód>)` v jazycích; FormBuilder do ní kopíruje celý katalog systémové šablony, proto bývá velká |

**XML je case-senzitivní a v kódování UTF-8.** `Name` a `name` jsou dva různé atributy a formulář se s chybnou velikostí písmen vykreslí špatně, aniž by nahlásil chybu.

### Vzhled

- `<tab TabPageLabel="...">` začíná novou záložku formuláře, `<tab>` bez popisku je oddíl v ní, prázdné `<tab/>` je vodorovná čára. `TableColumns` určuje počet sloupců rozložení.
- **Záložka se nesmí jmenovat `UDA`.** Název je vyhrazený jádru, které na ni doplňuje UDA atributy.
- `<column Name="...">` je pole. Povinný je jen `Name`, a ten musí být na formuláři jedinečný.
- **`Name` podle druhu pole:**
  - atribut třídy jménem sloupce (`nazev_subjektu`), vazba jako `<sloupec>_refer` nebo `<sloupec>_nazev`,
  - UDA atribut celým jménem `lcs.<uda_tabulka>.<sloupec>`, u UDA vazby s `_refer` nebo `_nazev` na konci. V šablonách uložených FormBuilderem se objevuje i tvar s podtržítky místo teček (`lcs_uda_<tabulka>_<sloupec>`); fungují oba, při hledání pole v XML hledej obojí,
  - dopočtený sloupec z `sqludfsyntax` s předponou `$udf_`, viz níže,
  - výpočtové pole libovolným jménem s atributem `Expr`.
- Časté atributy pole: `Width` (číslo, `100%`, `Auto`), `ColSpan`, `Height` (jen textarea a obrázek), `Label`, `LabelPos` (`Left`, `Up`, `None`), `ReadOnly`, `Required`, `InputType` (`text`, `checkbox`, `textarea`, `select`, `label`, `string`, `picture`, `button`, `group`, `Placeholder`...), `Values` u checkboxu s jinými hodnotami než `A,N`, `EditMask`, `EditStyle`, `RegisterItemChange`.
- **`Expr`, `Invisible`, `Protect`, `Required` a `FontAndColor` jsou výrazy** v syntaxi .NET `DataColumn.Expression`: `isnull(stav,'') = '1'`, `iif(cena>0,'GoodValue','BadValue')`. Na položkách se na hlavičku odkazuje `Parent.<sloupec>`. Kalíšek ve `FontAndColor` je výraz, takže jeho název musí být v apostrofech: `FontAndColor="'BadValue'"`.
- **Obrázek (`InputType="picture"`) potřebuje `RegisterItemChange="True"`.** Bez něj vložení většího obrázku shodí klienta.
- `InputType="string"` posílá na klienta prostý text, takže na něm nefunguje `Protect` ani `Invisible`.
- **Popisek `fm(<kód>)` musí mít kód v `sablona_msg_xml`**, jinak se nepřeloží. Nové pole proto dostane buď `Label` prostým textem, nebo kód, který v hláškách šablony už je; ručně přidaný kód je potřeba doplnit do `sablona_msg_xml` ve všech jazycích.

### Rozložení a ColSpan

Pole nemají souřadnice. Oddíl (`<tab>`) je mřížka o `TableColumns` buňkách na řádek (výchozí hodnota z `<template>`, jinak 1) a pole se do ní skládají v pořadí, jak jsou v XML, zleva doprava a po řádcích. **`ColSpan` určuje, přes kolik buněk se pole vykreslí** (výchozí 1). Pole, které se do zbytku řádku nevejde, začne na novém řádku. Poloha pole je tedy dána součtem `ColSpan` všech polí před ním v oddílu.

Proto **každý zásah do oddílu s víc sloupci přeskládá všechna pole za ním**: odebrané pole posune další o buňku doleva, přidané doprava, a změna `ColSpan` jednoho pole posune zbytek oddílu. Jestli je to žádoucí, rozhoduje člověk. Když má rozložení zůstat:

- místo odebraného pole se vloží prázdné místo stejné šířky: `<column Name="placeholder_<něco>" InputType="Placeholder" ColSpan="<původní>"></column>` (`Name` musí být v šabloně jedinečné; starší šablony místo toho používají pole s `InputType="label"`). Ověřeno: placeholder bez `Width` na místě pole s `Width="Auto"` vrátí oddíl do původního rozložení,
- nebo se o uvolněné buňky zvětší `ColSpan` sousedního pole.

**Šířka pole (`Width`) je zhruba v pixelech** při 100% měřítku Windows. Kalibrováno jednou podle snímku formuláře a změřením textu písmem klienta (Segoe UI 9 pt přes GDI `GetTextExtentPoint32`), přepočítávat to znovu není potřeba, stačí odhad:

| Co | Odhad |
| --- | --- |
| text s diakritikou, malá písmena | 5,8 px na znak |
| kódy, číslice, velká písmena (`ORG0000250`, `OPT-806/2026`) | 6,6 px na znak |
| okraje pole | +16 |
| ikona vazby u pole `_refer` nebo `_nazev` | +20 |

Pole pro 25 znaků názvu s vazbou tedy potřebuje asi `25 × 5,8 + 16 + 20 ≈ 180`. Délku hodnot ber z dat (hodnota, kterou pokryje zhruba 95 % záznamů, ne nejdelší), u vazby z navázaného číselníku. Popisek s `LabelPos="Left"` zabere vlastní buňku navíc, šířka řádku je tedy součet popisků a polí. Pro Full HD monitor se hodí šířka formuláře (`MasterWidth` na `<template>`) kolem 1000.

**Barvy pole** (`FontAndColor`) ber z kalíšků, které databáze už používá v jiných šablonách, nebo ze systémových (`BadValue`, `ToProcess`, `GoodValue`, `Success`, `Warning`, `GroupLabel`, `InProcess`). Přehled použitých kalíšků dá regulární výraz `FontAndColor="'([^']+)'"` nad `sablona_xml` všech šablon. Kalíšek s firemním názvem (`Blue_front_protect`) v jiné databázi být nemusí.

`nephrite/udf-layout-check` **U každé úpravy porovnej rozložení oddílů před a po** skriptem `${CLAUDE_SKILL_DIR}/scripts/udf_layout.py`. Nad skriptem úpravy porovná XML z bloku vrácení s novým XML a vypíše jen oddíly, kde se mřížka změnila, řádek po řádku:

```
python ${CLAUDE_SKILL_DIR}/scripts/udf_layout.py <skript.sql>
python ${CLAUDE_SKILL_DIR}/scripts/udf_layout.py <před.xml> <po.xml>
python ${CLAUDE_SKILL_DIR}/scripts/udf_layout.py <šablona.xml>
```

Výpis patří k návrhu úpravy, aby člověk viděl přeskládání dřív, než skript spustí. Skript upozorní i na `ColSpan` větší než `TableColumns` oddílu; takové pole vykreslí na celou šířku oddílu, jak se to v Heliosu skutečně zobrazí, je potřeba ověřit ve formuláři.

### Dopočtené sloupce

`nephrite/udf-sqludfsyntax` **Sloupce navíc přidávej přes `sqludfsyntax`, ne přes `sqlsyntax`.** `sqlsyntax` nahrazuje celý SELECT formuláře, a když dodavatel při aktualizaci přidá sloupec do systémové šablony, formulář s vlastním `sqlsyntax` přestane fungovat a musí se ručně opravit. `sqludfsyntax` načítá jen sloupce navíc, takže aktualizace systémové šablony ho nerozbije. Obojí v jedné šabloně je chyba.

```xml
<?xml version="1.0" encoding="utf-8"?>
<data Description="MasterTable" xmlns="http://tempuri.org/DataForm.Data.xsd">
    <select>
        <sqludfsyntax>select h.cislo_subjektu, h.cena_celkem cena_celkem
from lcs.sk_hlavicka h
where h.cislo_subjektu = @cislo_subjektu</sqludfsyntax>
    </select>
    <arguments>
        <argument Name="cislo_subjektu" Type="number"></argument>
    </arguments>
</data>
```

- **První sloupec SELECTu je klíč**: `cislo_subjektu` (u nonsubjektové třídy její primární klíč) pro hlavičku, `cislo_objektu` pro položky. Podle něj se řádky spárují s formulářem, do formuláře se nedostane.
- **Argumenty musí sedět se systémovou šablonou** počtem a typem, název se smí lišit. U položek je argumentem pořád číslo hlavičky, takže `where pol.cislo_subjektu = @cislo_subjektu`.
- **Ve vzhledu má sloupec předponu `$udf_`**, v SELECTu ji nemá: alias `cena_celkem` je ve `sablona_xml` `<column Name="$udf_cena_celkem" .../>`.
- Sloupce `$udf_` jsou jen pro čtení, jejich hodnota se do databáze neukládá.
- **SELECT běží při každém otevření formuláře.** Vyhýbej se funkcím po řádcích a dotazům bez indexu, u položek se násobí počtem řádků.
- Ze `sablona_data_xml` se u šablony z FormBuilderu použije jen `sqlsyntax`, `sqludfsyntax` (a jejich varianty `...archive` pro archivní data) a `arguments`. Ostatní se vždy bere ze systémové šablony.

## Úprava šablony v databázi

`nephrite/udf-create-in-formbuilder` **Šablonu zakládá člověk ve FormBuilderu, v databázi se jen upravuje.** Založení přidělí `cislo_sablony` (není `IDENTITY`), založí práva a překlady a nastaví platnost. Úprava hotové šablony je změna XML, a tu jde připravit přesněji než klikáním: hromadné přesuny polí, výrazy, `sqludfsyntax`.

Zápis do `lcs.noris_form_templates` je výjimka z `nephrite/no-write-system` a skript ji uvádí komentářem. Pravidla skriptu:

- **Vždy jedna šablona podle `cislo_sablony`**, nikdy podle názvu ani podle třídy.
- **XML se načte z databáze těsně před úpravou**, ne z dřívějšího výpisu. Šablonu mezitím mohl někdo uložit ve FormBuilderu.
- **`UPDATE` má podmínku na původní `last_update`.** Když šablonu někdo mezi načtením a spuštěním uložil, skript ji nepřepíše a za `UPDATE` vypíše `@@ROWCOUNT` 0.
- **Nad `UPDATE` je `SELECT` současného stavu** (`nephrite/select-before-update`).
- `nephrite/udf-rollback` **Na konci skriptu je zakomentovaný blok vrácení**: `UPDATE` s celým původním XML a původním `last_update`, s podmínkou na `cislo_sablony` i `nazev_sablony`. Spouští se označením řádků uvnitř komentáře. Bez něj se úprava, která formulář rozhodí, vrací jen ručně ve FormBuilderu. Blok musí být v `/* ... */`, aby ho F5 nad celým souborem nespustil; před tím ověř, že XML neobsahuje `*/`.
- **S XML se mění i `last_update = GETDATE()`.** Trigger podle něj aktualizuje evidenci přenosu konfigurace (`lcs.config_transfer_proxy`). Obnovení cache aplikace proběhne při každém `UPDATE` i bez toho.
- **Nový text XML se do skriptu píše celý jako literál `N'...'`**, apostrofy uvnitř zdvojené. Úprava přes `REPLACE` nad uloženým XML tiše nic neudělá, když se hledaný text liší jedinou mezerou.
- **Literál se generuje skriptem a porovná se s databází.** XML se upraví v Pythonu, ověří parserem, a literál vytažený zpět ze souboru se porovná s původním XML: rozdíl smí být jen v zamýšlených řádcích. Zachovej konce řádků (`CRLF`) a nepřidávej ani neubírej mezery. **V Pythonu na Windows zapisuj soubor s `newline=""`**: v textovém režimu se z uloženého `\r\n` stane `\r\r\n` a do šablony by se zapsaly prázdné řádky navíc.
- **Skript platí jen pro databázi, ze které bylo XML načtené.** Stejná šablona má v testovací a ostré databázi jiný `last_update`, často i jiný obsah. Pro ostrou se XML načte z ostré a skript se vygeneruje znovu; podmínka na `last_update` jinak `UPDATE` správně neprovede.
- **Soubor je v UTF-8 bez BOM a SSMS ho může otevřít ve špatném kódování.** Před spuštěním zkontroluj v SSMS text s diakritikou uvnitř XML, jinak se do šablony zapíšou rozsypané znaky.
- **Přesun nebo přidání pole posune sousedy**, viz Rozložení a ColSpan níže. Rozložení před a po se porovná skriptem a po úpravě se formulář v Heliosu otevře a zkontroluje.
- `rozsah_platnosti = 'P'` s prázdným `seznam_poradacu` trigger odmítne a celý `UPDATE` vrátí.
- Skript se nejdřív pustí na testovací databázi, ověří se otevřením formuláře v Heliosu a teprve potom jde do ostré. Po spuštění se v databázi zkontroluje, že uložené XML se shoduje s literálem ve skriptu a že se změnil `last_update`.

```sql
USE [HGFirmaTest24]
GO
-- select cislo_sablony, nazev_sablony, sablona_xml, sablona_data_xml, last_update from lcs.noris_form_templates where 1=1 and cislo_sablony = 10001
-- pankostka: allow nephrite/no-write-system, úprava XML existující UDF šablony založené ve FormBuilderu
UPDATE lcs.noris_form_templates
SET sablona_xml = N'<?xml version="1.0" encoding="utf-8"?>
<template ...>
...
</template>'
, last_update = GETDATE()
WHERE 1=1
AND cislo_sablony = 10001
AND last_update = '2026-01-01 10:00:00.000'

SELECT @@ROWCOUNT AS zmeneno_radku
GO

/* ===== VRÁCENÍ =====
USE [HGFirmaTest24]
-- pankostka: allow nephrite/no-write-system, vrácení úpravy XML UDF šablony
UPDATE lcs.noris_form_templates
SET sablona_xml = N'<?xml version="1.0" encoding="utf-8"?> ...původní XML celé...'
, last_update = '2026-01-01 10:00:00.000'
WHERE 1=1
AND cislo_sablony = 10001
AND nazev_sablony = N'<název šablony>'

SELECT @@ROWCOUNT AS vraceno_radku
GO
===== KONEC VRÁCENÍ ===== */
```

**Pohled (`lcs.noris_form_views.grid_ms_net`) se ručně neupravuje.** Rozložení okna se změní tak, že se pohled v Heliosu aplikuje, upraví a uloží pod stejným názvem. Implicitní pohled pro pořadač nebo kategorii se nastavuje v Heliosu v pořadači Implicitní formulářové pohledy.

## Jak číst šablonu

XML jsou `nvarchar(max)` a SSMS je v mřížce ořízne. Čti je skriptem do souboru, v Pythonu přes `pyodbc` po jednom sloupci, a teprve soubor otevři. Než šablonu upravíš, porovnej ji se systémovým formulářem třídy (`lcs.nis_tridy.dw_formular`) a s šablonami jiných databází, kde už podobný formulář existuje. Dobře se tak najdou jména sloupců i osvědčené výrazy.
