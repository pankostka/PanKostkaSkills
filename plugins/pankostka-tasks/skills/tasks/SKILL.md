---
name: pankostka-tasks
description: Zásady pro adresář tasks/ s rozpracovanými úkoly - rozcestník tasks.md, jeden článek na úkol, průběžný zápis postupu, pomocné soubory -TMP, mazání po dokončení, rozdíl proti souboru s rozhodnutími. Použij vždy, když zakládáš úkol, pracuješ na úkolu z tasks/ nebo ho dokončuješ. S argumentem (adresář repa nebo tasks/) zkontroluje rozcestník a články a vypíše neshody.
argument-hint: "[adresář]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_tasks.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_tasks.py *)
---

# Tasks - rozpracované úkoly

Adresář `tasks/` v kořeni repa je pracovní deník k rozpracované práci. **Není to dokumentace** a nepodléhá pravidlům pro `docs/`: rozhoduje životnost. Článek v `docs/` popisuje repo trvale, soubor v `tasks/` žije jen do chvíle, než je úkol nasazený a otestovaný, a pak se maže. Pravidla pro psaní samotných článků jsou ve skillu `pankostka-md`.

Argument: `$ARGUMENTS`

## Rozcestník

Rozcestník je `tasks/tasks.md`, seznam všech úkolů. Úkol, na kterém se ještě nedělá, je tam jen odrážkou. Jakmile se na něm začne pracovat, vznikne vedle článek `tasks/<Název úkolu>.md` a odrážka na něj odkáže wikilinkem. Když úkol vzniká za běhu a v `tasks.md` ještě není, doplň tam odrážku.

Odrážka má za odkazem jednu až dvě věty: o co jde a v jakém je úkol stavu. Rozcestník se tak dá přečíst bez otevírání článků.

## Průběh práce

**Když pracuješ na úkolu z `tasks/`, průběh piš do jeho článku, ne jen do chatu.** Patří tam zadání, zvolený postup a proč, dotčené objekty a soubory, stav testování a co zbývá ručně nasadit. Cílem je, aby se dalo navázat v jiné session bez čtení historie chatu, takže článek aktualizuj průběžně, ne až na konci.

**Doporučená osnova článku** podle toho, jak se úkoly v praxi píšou. Sekce, ke které není co napsat, se vynechá:

- **Zadání:** co se má udělat a proč, případně pilot, na kterém se postup ověří.
- **Rozhodnutí:** co je rozhodnuté a kdy, s datem. Předběžné rozhodnutí se tak označí.
- **Stav:** jedna až dvě věty nahoře v článku, co je hotové a co je na řadě. Aktualizuje se při každé změně.
- **Podúkoly:** tabulka s číslem, podúkolem, kde se dělá, na čem závisí, výstupem a stavem. Hodí se u úkolu s víc kroky.
- **Průběh:** co se udělalo, s datem, co se ověřilo a jak, co zbývá nasadit ručně.

## Pomocné soubory

Testovací dotazy, výstupy měření a ukázky k úkolu leží vedle jeho článku a jmenují se **`<Název úkolu>-<co>-TMP.<přípona>`**, třeba `Intercompany v KostkaEKO-mereni-TMP.sql`. Sufix `-TMP` je drží mimo git, název úkolu na začátku říká, ke kterému úkolu patří, a po smazání úkolu je jasné, co smazat s ním.

## Git

Články v `tasks/` jsou v gitu, ne `-TMP`. Bez toho je z jiného stroje ani z jiné session neuvidíš.

## Dokončení

Po dokončení úkolu smaž jeho článek, jeho pomocné soubory `-TMP` a odrážku v `tasks.md`. Co má přežít, přenes do `docs/` nebo k dotčenému objektu.

## Rozhodnutí a otevřené otázky

**Repo může mít vedle `tasks/` soubor s rozhodnutími a otevřenými otázkami** (v některých repech `TODO 🌐.md`). Rozdíl je životnost: tam leží vědomá rozhodnutí, která mají platit dlouhodobě a slouží k tomu, aby se stejná diskuse nevedla znovu. Do `tasks/` patří práce, která právě běží a po dokončení zmizí. Rozhodnutí z úkolu, které má přežít jeho smazání, se proto při dokončení přenese tam. Pravidla pro AI ani do jednoho nepatří, ta jsou v `CLAUDE.md`.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je adresář repa (kontroluje se jeho `tasks/`), nebo přímo adresář `tasks/`.

1. **Spusť skript** s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_tasks.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Výstup je jedna řádka na neshodu ve tvaru `soubor:řádek: [pravidlo] zpráva`. Pravidla:
   - `index`: chybí `tasks/tasks.md`,
   - `orphan`: článek v `tasks/`, na který v `tasks.md` nevede odkaz,
   - `dead`: odkaz v `tasks.md` na článek, který v `tasks/` není,
   - `leftover`: soubor `-TMP`, jehož název nezačíná názvem žádného úkolu, tedy nejspíš zbytek po smazaném úkolu,
   - `git`: článek úkolu, který git nesleduje.

2. **Projdi články sám**: dá se podle článku navázat bez historie chatu, odpovídá stav v článku stavu v `tasks.md`, nezůstal viset dokončený úkol a nepatří část textu do `docs/` nebo do souboru s rozhodnutími.

3. **Vypiš výsledek** s konkrétním návrhem u každé neshody a souhrnem na konci.

4. **Nic neopravuj ani nemaž**, dokud uživatel neodsouhlasí. Soubor `-TMP` není v gitu, smazaný se nedá vrátit.
