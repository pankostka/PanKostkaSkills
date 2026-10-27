# PanKostkaSkills

Marketplace pluginů pro Claude Code. Každý plugin obsahuje skilly s pravidly a kontrolou souborů proti nim. Repo je zatím soukromé, zveřejní se po kontrole obsahu.

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
- Kontrolní skript: `scripts/check_<téma>.py`, tedy `check_tsql.py`. Přípona tématu ho odliší od skriptů ostatních skillů.
- Testy: `tests/pankostka-<téma>/`.

## Zásady

- Názvy souborů a adresářů anglicky, obsah česky včetně diakritiky.
- `SKILL.md` je zdroj pravidel, ne výtah z jiného dokumentu. Odůvodnění pravidel v něm zůstávají.
- Skilly musí fungovat i samostatně jako zip pro claude.ai: žádné odkazy mimo adresář skillu a žádné `${CLAUDE_PLUGIN_ROOT}`, jen `${CLAUDE_SKILL_DIR}`.
- Skripty jen se standardní knihovnou Pythonu.
- Mechanická pravidla kontroluje skript, úsudek model. Nové pravidlo ve skriptu potřebuje test `ko_<pravidlo>_*`.
- Testy: `ok_*` nesmí mít neshodu, `ko_<pravidlo>_*` jen neshody toho pravidla, počet podle textu `celkem N` v testu. Test je soubor, nebo adresář, když pravidlo porovnává soubory mezi sebou (`pankostka-md`: přílohy, tagy, odkazy). Testy `ko_` porušují pravidla záměrně, kontrola skillu na ně nemíří.
- Po každé změně spusť testy (`python tests/<plugin>/run.py`) a `claude plugin validate .`.
- Textové soubory v UTF-8 bez BOM. Výjimkou jsou testy kódování, ty mají BOM nebo jiné kódování záměrně.
- Testy, které potřebují zakázané znaky, mezery na konci řádku nebo jiné kódování, se generují skriptem v Pythonu, třeba `tests/pankostka-md/make_cases.py`. Editor i nástroje AI je při zápisu tiše opraví, mezery na konci řádku umaže už nástroj Write.
- Pole `version` v `plugin.json` zatím nevyplňujeme, aktualizace se berou podle commitu.
