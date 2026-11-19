# Uživatelsky definované formuláře

Doplněk skillu `pankostka-nephrite`. Uživatelsky definovaný formulář (UDF, formulářová šablona z FormBuilderu) mění vzhled editačního formuláře třídy: pořadí a rozložení polí, záložky, popisky, ochranu polí, barvy a dopočtené sloupce navíc. Podrobný popis je v nápovědě Heliosu na stránkách `FormBuilder_-_příručka` a `Šablony_pro_formuláře_-_popis`, viz Dokumentace Heliosu ve `SKILL.md`. Tady je to, co je potřeba k úpravě šablony přímo v databázi.

## Kde je definice

| Tabulka | Třída | Obsah |
| --- | --- | --- |
| `lcs.noris_form_templates` | 983 Šablony formulářů | šablona: `cislo_sablony`, `trida`, `nazev_sablony`, tři XML (`sablona_xml`, `sablona_data_xml`, `sablona_msg_xml`), `parameters` (`FormBuilder=1 TableName=MasterTable` pro hlavičku, `EntriesTable` pro položky), platnost `rozsah_platnosti` a `seznam_poradacu` |
| `lcs.noris_form_views` | 1346 Formulářový pohled | pohled: `master_template` a `entries_template` ukazují na `cislo_sablony`, `grid_ms_net` je uložené rozložení okna (záložky vztahů, splittery), platnost stejně jako u šablony |
| `lcs.noris_defa_form_view` | | implicitní pohled: `pohled` pro třídu nebo pořadač (`trida_nebo_poradac` `T`/`P`, `poradac`) a pro kategorii nebo uživatele (`kategorie_nebo_uzivatel` `K`/`U`) |

Aplikace šablonu zapisuje přes view `lcs.template_form` s triggery `INSTEAD OF`. Tabulka má vlastní triggery, které při změně obnoví cache aplikace (`lcs.set_cache_timestamp`), přepíšou název v `lcs.repository_translate` a při vložení založí práva v `lcs.permissions`.

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
  - UDA atribut celým jménem `lcs.<uda_tabulka>.<sloupec>`, u UDA vazby s `_refer` nebo `_nazev` na konci,
  - dopočtený sloupec z `sqludfsyntax` s předponou `$udf_`, viz níže,
  - výpočtové pole libovolným jménem s atributem `Expr`.
- Časté atributy pole: `Width` (číslo, `100%`, `Auto`), `ColSpan`, `Height` (jen textarea a obrázek), `Label`, `LabelPos` (`Left`, `Up`, `None`), `ReadOnly`, `Required`, `InputType` (`text`, `checkbox`, `textarea`, `select`, `label`, `string`, `picture`, `button`, `group`, `Placeholder`...), `Values` u checkboxu s jinými hodnotami než `A,N`, `EditMask`, `EditStyle`, `RegisterItemChange`.
- **`Expr`, `Invisible`, `Protect`, `Required` a `FontAndColor` jsou výrazy** v syntaxi .NET `DataColumn.Expression`: `isnull(stav,'') = '1'`, `iif(cena>0,'GoodValue','BadValue')`. Na položkách se na hlavičku odkazuje `Parent.<sloupec>`. Kalíšek ve `FontAndColor` je výraz, takže jeho název musí být v apostrofech: `FontAndColor="'BadValue'"`.
- **Obrázek (`InputType="picture"`) potřebuje `RegisterItemChange="True"`.** Bez něj vložení většího obrázku shodí klienta.
- `InputType="string"` posílá na klienta prostý text, takže na něm nefunguje `Protect` ani `Invisible`.

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
- **Nad `UPDATE` je `SELECT` současného stavu** (`nephrite/select-before-update`), aby se dal výsledek uložit stranou a změna vrátit.
- **S XML se mění i `last_update = GETDATE()`.** Trigger podle něj aktualizuje evidenci přenosu konfigurace (`lcs.config_transfer_proxy`). Obnovení cache aplikace proběhne při každém `UPDATE` i bez toho.
- **Nový text XML se do skriptu píše celý jako literál `N'...'`**, apostrofy uvnitř zdvojené. Úprava přes `REPLACE` nad uloženým XML tiše nic neudělá, když se hledaný text liší jedinou mezerou.
- `rozsah_platnosti = 'P'` s prázdným `seznam_poradacu` trigger odmítne a celý `UPDATE` vrátí.
- Skript se nejdřív pustí na testovací databázi, ověří se otevřením formuláře v Heliosu a teprve potom jde do ostré.

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
```

**Pohled (`lcs.noris_form_views.grid_ms_net`) se ručně neupravuje.** Rozložení okna se změní tak, že se pohled v Heliosu aplikuje, upraví a uloží pod stejným názvem. Implicitní pohled pro pořadač nebo kategorii se nastavuje v Heliosu v pořadači Implicitní formulářové pohledy.

## Jak číst šablonu

XML jsou `nvarchar(max)` a SSMS je v mřížce ořízne. Čti je skriptem do souboru, v Pythonu přes `pyodbc` po jednom sloupci, a teprve soubor otevři. Než šablonu upravíš, porovnej ji se systémovým formulářem třídy (`lcs.nis_tridy.dw_formular`) a s šablonami jiných databází, kde už podobný formulář existuje. Dobře se tak najdou jména sloupců i osvědčené výrazy.
