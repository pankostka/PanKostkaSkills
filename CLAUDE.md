# PanKostkaSkills

Marketplace pluginů pro Claude Code. Každý plugin obsahuje skilly s pravidly a kontrolou souborů proti nim. Repo je veřejné pod licencí MIT. Do skillů proto nepatří nic citlivého: hesla, tokeny, GUID workspace a datasetů, skutečné názvy serverů a databází ani údaje zákazníků. V příkladech používej neutrální názvy (`HGFirmaOstra`, `SQLSRVX`).

## Struktura

- `.claude-plugin/marketplace.json` - katalog, `name` je `pankostka`.
- `plugins/<plugin>/` - jeden plugin, `name` v `plugin.json` musí být stejný jako v `marketplace.json`.
- `plugins/<plugin>/skills/<skill>/SKILL.md` - zásady a režim kontroly, skripty vedle v `scripts/`.
- `tests/<plugin>/` - testy skriptů, do pluginu se nebalí.

## Pojmenování

Všechno, co uživatel píše, začíná `pankostka-`, a volání je v Claude Code i na claude.ai stejné: `/pankostka-<téma>`.

- Plugin: `pankostka-<téma>`, adresář `plugins/pankostka-<téma>/`.
- `name` v `SKILL.md`: `pankostka-<téma>`. Na claude.ai je to jediný název skillu.
- Adresář skillu: jen `<téma>`, tedy `plugins/pankostka-tsql/skills/tsql/`. **Nesmí se jmenovat stejně jako `name`.** Claude Code povoluje volání bez prefixu pluginu jen u skillu, jehož `name` se liší od adresáře. Se stejným názvem by zbylo jen `/pankostka-tsql:pankostka-tsql`.
- Další skill v pluginu: `name` je `pankostka-<téma>-<podtéma>`, adresář jen `<podtéma>`, tedy `plugins/pankostka-powerbi/skills/wiki/` pro `pankostka-powerbi-wiki`.
- Kontrolní skript: `scripts/check_<téma>.py`, tedy `check_tsql.py`, u dalšího skillu `check_<podtéma>.py`. Přípona odliší skript od skriptů ostatních skillů.
- Testy: `tests/<name skillu>/`, tedy `tests/pankostka-tsql/`.

## Argumenty skillu

- Bez argumentu skill jen načte zásady.
- S argumentem (soubor, adresář, `--changed`, název objektu) skill kontroluje a vypisuje neshody s návrhy. **Nic nezapisuje.**
- Zápis povoluje jen přepínač `--make`, a jen u skillu, který ho v `argument-hint` uvádí. Dnes je to `pankostka-powerbi-wiki`. Pokyn slovy, který o zápis výslovně žádá (třeba `Aktualizuj wiki`), znamená totéž co `--make`.

## Identifikátory pravidel

Každé normativní pravidlo (co se má nebo nesmí) má identifikátor **`<téma>/<krátký-popis>`**, třeba `tsql/no-right-join`, `md/no-hard-wrap`. Téma je `name` skillu bez `pankostka-`, u dalšího skillu v pluginu jen podtéma (`wiki/`). Popis je anglicky, malými písmeny s pomlčkami, `no-` na začátku znamená zákaz. Identifikátor se nečísluje a nemění: nové pravidlo se nikam neřadí a smazané nenechá díru.

- V `SKILL.md` stojí identifikátor v zpětných apostrofech na začátku pravidla: `` `tsql/no-right-join` **Nepoužívej `RIGHT JOIN`.** ``
- Skript ho vypisuje jako pravidlo nálezu: `soubor:řádek: [tsql/no-right-join] zpráva`.
- Test se jmenuje `ko_<popis>` nebo `ko_<popis>_<varianta>`, tedy `ko_no-right-join.sql`. Jeden test `ko_` hlásí jen jeden identifikátor.

**Výjimka komentářem.** Vědomé porušení pravidla se zapíše komentářem na řádku nálezu nebo na řádku nad ním: `-- pankostka: allow tsql/no-right-join, důvod` v SQL, `<!-- pankostka: allow md/keyboard-chars, důvod -->` v Markdownu. Identifikátorů může být víc, oddělených čárkou, **důvod je povinný**, bez něj skript nález hlásí dál. Výjimku umí skripty, jejichž nálezy se vážou k řádku textu: `tsql`, `md`, `dwh`, `nephrite`, `wiki` a `tasks`. V `obsidian` (JSON), `git` (repo) a `powerbi` (TMDL nemá komentáře) není.

## Zásady

- Názvy souborů a adresářů anglicky, obsah česky včetně diakritiky.
- `SKILL.md` je zdroj pravidel, ne výtah z jiného dokumentu. Odůvodnění pravidel v něm zůstávají.
- Skilly musí fungovat i samostatně jako zip pro claude.ai: žádné odkazy mimo adresář skillu a žádné `${CLAUDE_PLUGIN_ROOT}`, jen `${CLAUDE_SKILL_DIR}`.
- Skripty jen se standardní knihovnou Pythonu.
- Mechanická pravidla kontroluje skript, úsudek model. Nové pravidlo ve skriptu potřebuje test `ko_<popis>`.
- Testy: `ok_*` nesmí mít neshodu, `ko_<popis>_*` jen neshody pravidla s tím popisem, počet podle textu `celkem N` v testu. Test je soubor, nebo adresář, když pravidlo porovnává soubory mezi sebou (`pankostka-md`: přílohy, tagy, odkazy). Testy `ko_` porušují pravidla záměrně, kontrola skillu na ně nemíří.
- Po každé změně spusť testy (`python tests/<plugin>/run.py`) a `claude plugin validate .`.
- Textové soubory v UTF-8 bez BOM. Výjimkou jsou testy kódování, ty mají BOM nebo jiné kódování záměrně.
- Testy, které potřebují zakázané znaky, mezery na konci řádku nebo jiné kódování, se generují skriptem v Pythonu, třeba `tests/pankostka-md/make_cases.py`. Editor i nástroje AI je při zápisu tiše opraví, mezery na konci řádku umaže už nástroj Write.
- Pole `version` v `plugin.json` zatím nevyplňujeme, aktualizace se berou podle commitu.
