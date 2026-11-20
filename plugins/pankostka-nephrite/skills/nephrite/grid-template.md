# Šablona přehledu

Doplněk skillu `pankostka-nephrite`. Šablona přehledu (třída 20 Šablony, `nazev_pbl = 'gsb'`) určuje sloupce, řazení a uložené filtry přehledu jedné třídy. Tady je, jak je uložená a jak se přenáší mezi databázemi, třeba při zakládání nové firmy podle existující. Jak se volá XML rozhraní a co umí utilita `HeliosGreenXmlTask.exe`, je v `xml-task.md`.

## Kde je uložená

Šablona leží v pěti systémových tabulkách. Stejný výčet má procedura Heliosu `lcs.nsp_change_template_num`, která šablonu přečísluje.

| Tabulka | Obsah |
| --- | --- |
| `lcs.noris_templates` | hlavička: `cislo_template`, třída (`cislo_tridy`), vlastník (`owned_by`), `nazev_pbl` (`gsb` je šablona přehledu, `gsb_defa` výchozí šablona třídy) |
| `lcs.noris_gs_template` | nastavení přehledu, mimo jiné `s_mark`: seznam uložených filtrů oddělený **tabulátorem** |
| `lcs.noris_gs_main` | sloupce: `colcode`, `colwidth`, `expression` u sloupce typu výraz, `data_vztahy` (XML s čísly tříd a vztahů) |
| `lcs.noris_gs_select` | řádky uložených filtrů (`mark_name`, `sloupec`, `podminka`, `hodnota`) |
| `lcs.repository_translate` | název a popis šablony v jazycích, `cislo = cislo_template` a `cislo_tridy = 20` |

Práva na šablonu jsou v `lcs.permissions` (`cislo_objektu = cislo_template`, operace s `typ_oper = 'S'` v `lcs.noris_permission_list_of_fnc`). **Šablonu bez práv nevidí nikdo**, ani její autor. Výchozí jsou práva pro kategorii Všichni (`groupid = 2`, `sync_id = '$allusers'`) na pět operací: `sapl`, `sedit`, `sdel`, `s_print_template` a `s_print_template_on_server`. Kdo se dostane do pořadače, může pak aplikovat kteroukoli šablonu, a to je obvyklý stav.

**Trigger `trg_INSERT_template`** na `lcs.noris_templates` při vložení řádku z SQL založí řádky překladů (s prázdným názvem, pokud není `vlozeny_nazev`) a výchozí práva. Offline import šablonu zapisuje jinou cestou a výchozí práva při něm nevzniknou, viz níže.

**Nové číslo šablony je nejvyšší uživatelské číslo plus jedna.** Ověřeno na offline importu s volbou Vždy vkládat. Systémové šablony mají vysoká čísla (miliony), uživatelské začínají od 10000.

## Přenos do jiné databáze

| Cesta | Co přenese | Kdy |
| --- | --- | --- |
| Offline export a ruční offline import | všechno včetně nestandardních práv | jednotlivé šablony, šablony nad vlastními třídami |
| `RETRIEVE` přes `HeliosGreenXmlTask.exe`, převod skriptem a offline import | všechno, práva standardní pro Všichni | hromadný přenos, bez ručního exportu |
| SQL skript do pěti tabulek | čísla tak, jak jsou ve zdroji | jen výjimečně, viz níže |

`nephrite/template-offline-import` **Šablony se mezi databázemi přenášejí offline importem, SQL je výjimka.** Offline soubor zapisuje třídy a vztahy symbolicky (`cislo_tridy="{515,([cislo_tridy:515])}"`, ve výrazech `fm({515,...})`), vlastníka podle reference nebo `sync_id` a kategorii podle `sync_id`. Import je v cílové databázi dohledá sám, takže šablona sedí i tam, kde mají vlastní třídy, UDA a vztahy jiná čísla. SQL skript kopíruje čísla doslova, zapisuje do systémových tabulek (`nephrite/no-write-system`) a spadne, když se mezi verzemi Heliosu změní sloupce. Má smysl jen u šablon nad systémovými třídami, když je zdroj na stejném serveru a cesta přes XML rozhraní není k dispozici. Před ostrým během ho vyzkoušej na testovací databázi.

**Jednu šablonu nepřenášej dvěma cestami.** Každá založí nový záznam s jiným GUNID a vzniknou dvě šablony, které o sobě nevědí.

### Offline import

Export i import se spouští nad přehledem pořadače Šablony (Správa programu): ve zdrojové databázi se v něm označí šablony a spustí Offline export s volbou Exportovat včetně práv, v cílové databázi se v témže pořadači spustí Offline import. V pokynech pro uživatele vždy uveď i to, který pořadač má otevřít.

`nephrite/template-always-insert` **Při kopii do jiné databáze zvol Importované záznamy vždy vkládat.** Šablona dostane nové číslo a nic existujícího se nepřepíše. Práva ze souboru se navážou na novou šablonu, i když v souboru odkazují na původní číslo, a stávající práva se stejným číslem zůstanou beze změny. Ověřeno: práva se v cílové databázi hledají podle klíčových atributů (třída, pořadač, operace, kategorie, uživatel, objekt), ne podle čísla. Volba Vkládat nebo aktualizovat hledá záznam podle identifikace XML rozhraní (u šablon vztah na třídu a `sync_id`, jinak GUNID) a záznam, který najde, přepíše.

`nephrite/template-permissions` **Po importu zkontroluj, že šablona má práva.** Soubor bez bloku `<permissions>` založí šablonu bez práv a nikdo ji neuvidí. Auditlog to nehlásí, import skončí úspěšně. Práva do souboru dá offline export s volbou Exportovat včetně práv, nebo skript převodu z `RETRIEVE`.

```sql
SELECT t.cislo_template, t.cislo_tridy, t.owned_by, COUNT(p.cislo_nonsubjektu) AS prava
FROM lcs.noris_templates t
LEFT JOIN lcs.permissions p ON p.cislo_objektu = t.cislo_template AND p.cislo_tridy = t.cislo_tridy
WHERE 1=1
AND t.datum_vzniku >= @od
GROUP BY t.cislo_template, t.cislo_tridy, t.owned_by
```

**Každý záznam v souboru musí mít `SUBJECTID`**, i ten, který se hledá podle klíčových atributů (právo, operace, kategorie). Bez něj import spadne na `DataRecordId object cannot be created because record number is not set` a nezapíše nic. U záznamů, které se vkládají jako nové, stačí zástupné číslo mimo rozsah skutečných záznamů.

Úprava souboru ručně, třeba přepis vlastníka nebo vyhození práv, se nevyplácí. Bez práv šablona není vidět a vlastníka import dohledá sám podle reference.

### Hromadný přenos přes RETRIEVE

Offline export je zpráva `RETRIEVE` převedená na `INSERTUPDATE`. Spuštěný z `HeliosGreenXmlTask.exe` (funkce 2471) sice proběhne, ale soubor neuloží, protože ho posílá ke klientovi. Proto se šablony čtou přímo zprávou `RETRIEVE` a výsledek se převede skriptem:

```
python ${CLAUDE_SKILL_DIR}/scripts/retrieve_templates.py prikaz <odkaz.xml> <příkaz.xml> <číslo šablony> [<číslo šablony> ...]
HeliosGreenXmlTask.exe <příkaz.xml> <retrieve.xml>
python ${CLAUDE_SKILL_DIR}/scripts/retrieve_templates.py prevod <retrieve.xml> <import.xml>
```

- `prikaz` vezme přihlašovací část z odkazu na funkci (viz `xml-task.md`) a nahradí příkazy zprávou `RETRIEVE` na zadané šablony. Výsledný soubor obsahuje šifrované heslo, smaž ho po běhu.
- `prevod` přejmenuje kořen na `INSERTUPDATE`, ke každé šabloně doplní pět výchozích práv pro Všichni a escapuje tabulátory a konce řádků v hodnotách atributů, viz `xml-task.md`.

Výsledek se naimportuje funkcí Offline import v pořadači Šablony cílové databáze s volbou Vždy vkládat. Šablona s jinými než výchozími právy je dostane výchozí a dorovnají se ručně.

### SQL skript

Když už SQL, tak takhle:

- zdroj se čte třídílným názvem do dočasných tabulek, zápis jde v jedné transakci s přepínačem zkouška (`ROLLBACK`) a ostrý běh (`COMMIT`),
- nové číslo je nejvyšší uživatelské číslo plus jedna, vlastník se dohledá podle jména zaměstnance, překlady a práva založí trigger a skript jen doplní texty překladů,
- `SET QUOTED_IDENTIFIER ON` na začátku: `lcs.repository_translate` má index, který ho vyžaduje. `sqlcmd` ho má ve výchozím stavu vypnutý, SSMS zapnutý, takže skript ze SSMS projde a ze `sqlcmd` spadne na chybě 1934.
