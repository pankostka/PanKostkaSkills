---
name: pankostka-obsidian
description: Zásady pro vault v Obsidianu nad git repem - jeden vault na repo, vnořený vault, kořen vaultu s README.md a menu.md, nastavení app.json (Attachments, odkazy, skryté soubory), co z .obsidian verzovat a co patří do .gitignore, šablona konfigurace pro nový vault. Použij, když zakládáš, nastavuješ nebo kontroluješ vault, adresář .obsidian nebo jeho řádky v .gitignore. S argumentem (adresář vaultu) zkontroluje vault proti zásadám a vypíše neshody.
argument-hint: "[adresář vaultu]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_obsidian.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_obsidian.py *)
---

# Obsidian - vault nad git repem

Jak založit a udržovat vault v Obsidianu, když leží v git repu. Jak psát samotné články, řeší skill `pankostka-md`.

Argument: `$ARGUMENTS`

## Kdy vault

`obsidian/one-vault-per-repo` **Jeden vault na repo, a jen tam, kde je dokumentace.** Repo s několika markdowny vault nepotřebuje, článek se otevře v čemkoli. Vault se zakládá, až dokumentace přibude.

**Jeden vault nad všemi repy nefunguje**, i když láká kvůli odkazům napříč repy:

- **Cizí obsah se z indexu nedá vyřadit.** Export z cizího nástroje umí přinést tisíce prázdných souborů téhož jména a ty lezou do hledání i do Quick switcheru. `userIgnoreFilters` je jen ztlumí, neodstraní.
- **Nastavení je na vault, ne na složku.** Repa kolegů a moje repa nejde ve společném vaultu nastavit zvlášť.

Cenou za rozdělení je, že **wikilink neumí přejít z vaultu do vaultu**. Náhradou je odkaz `obsidian://open?vault=<Vault>&file=<Článek>`, který funguje, ale Obsidian ho při přejmenování článku neopraví. Rozdělení obvykle kopíruje obsah: v repu je dokumentace k tomu repu, obecné know-how je ve vlastním vaultu a odkazovat je potřeba hlavně uvnitř té hranice.

### Vnořený vault

Vault uvnitř jiného vaultu je povolený, **když je to samostatný výstup**, typicky wiki pro uživatele, která se otevírá zvlášť. Nadřazený vault indexuje i jeho články, takže tytéž soubory žijí ve dvou vaultech.

`obsidian/nested-same-settings` Proto musí mít vnořený vault **stejná nastavení, která rozhodují o souborech**, jako vault nadřazený: `attachmentFolderPath`, `newLinkFormat` a `alwaysUpdateLinks`. Jinak má článek podle otevřeného okna jinou složku na přílohy a jiný tvar odkazů. Vzhled, téma a pluginy se lišit smějí.

Rozcestník vnořeného vaultu určuje jeho obor, ne tenhle skill. Wiki kostky má rozcestník `<Kostka>.md` a `README.md` v ní být nemá, protože by ve vaultu repa nebyl jednoznačný.

## Kořen vaultu

`obsidian/root-readme` a `obsidian/menu-embed` Ve všech vaultech stejně:

| Soubor | Role |
| --- | --- |
| `CLAUDE.md` | pravidla pro AI, nepublikuje se |
| `README.md` | rozcestník vaultu |
| `menu.md` | navigační lišta, vkládá se do rozcestníku prvním řádkem `![[menu]]`. **Jen tam, kde je co navigovat** |

**Jednotný název není kosmetika.** Na rozcestník vedou odkazy z lišty, ze záložky i ze startovního článku. Se shodným názvem je řádek `![[menu]]` i celá lišta přenositelná mezi vaulty a nastavení startovního článku jde do sdílené šablony.

**Proč `README.md`, a ne `home.md` nebo `index.md`:**

- Repo na GitHubu už README jako titulní stranu má. Druhý rozcestník vedle něj by byla kopie, která se rozejde.
- `index.md` koliduje s generátorem webu [obsidian2html](https://github.com/pankostka/obsidian2html), který generuje titulku `index.html`.

Na co si dát pozor:

- **GitHub `![[menu]]` neumí** a vypíše ho v README doslova. To je cena za jeden soubor místo dvou.
- **`README.md` v podadresářích dělá název nejednoznačným.** Odkaz `[[README]]` z kořene se trefí, protože Obsidian hledá nejdřív ve složce odkazujícího souboru, ale Quick switcher nabídne všechny.
- **Startovní článek povinný není.** Obsidian ho sám neumí, je na to komunitní plugin Homepage. Bez něj se obnoví poslední rozložení oken a na rozcestník se jde záložkou nebo Quick switcherem.

## Nastavení

`obsidian/app-settings` Povinná nastavení v `.obsidian/app.json`:

| Klíč | Hodnota | Proč |
| --- | --- | --- |
| `attachmentFolderPath` | `./Attachments` | přílohy vznikají v podsložce aktuální složky, vedle článku |
| `newLinkFormat` | `shortest` | wikilink jen názvem článku |
| `alwaysUpdateLinks` | `true` | přejmenování článku nebo přílohy opraví odkazy bez ptaní |
| `showUnsupportedFiles` | `false` | `.sql`, `.json`, `.xlsx` a další se nezobrazí, adresář bez článků taky ne |

`showUnsupportedFiles: false` je hlavní způsob, jak udržet vault nad repem lehký. Vedlejší efekt: skryje i skripty, takže v repu se zásadami je vidět jen text.

`obsidian/ignore-filter-no-glob` **`userIgnoreFilters`** je na to, co projde přes první filtr a stejně ve vaultu nemá co dělat, třeba obrázky uvnitř Power BI reportů (`StaticResources/`). Filtr soubory **jen ztlumí**: vypadnou z hledání, Quick switcheru, grafu a nabídky odkazů, ale ve stromu souborů zůstanou zešedlé. Pole čeká cestu nebo regulární výraz v lomítkách, **glob nezná**: `*-TMP` nefiltruje nic, správně je `/-TMP/`.

Doporučené filtry:

```
StaticResources/
/-TMP/
```

**Linter plugin musí mít vyloučené adresáře s kopiemi cizích souborů.** Dorovnává šířku sloupců v tabulkách a kopie by se rozešla se zdrojem.

## Co se verzuje

Konfigurace `.obsidian` se dělí na tři hromádky. Test: **jmenuje ten soubor konkrétní článek?** Pak to není nastavení, ale obsah.

| Hromádka | Soubory | Do šablony |
| --- | --- | --- |
| Jak se Obsidian chová | `app.json`, `appearance.json`, `core-plugins.json`, `community-plugins.json`, `plugins/*/manifest.json`, `snippets/` | ano |
| Co jmenuje konkrétní články | `bookmarks.json`, `templates.json`, `types.json`, `plugins/*/data.json`, `workspace*.json` | nikdy |
| Obsah vaultu | `README.md`, `menu.md` | je to článek, ne konfigurace |

`obsidian/gitignore-plugin-code` a `obsidian/no-tracked-plugin-code` Do gitu jde `.obsidian` celý **kromě kódu pluginů, témat a stavu oken**. Řádky do `.gitignore` jsou v `gitignore.txt` v adresáři tohoto skillu (`${CLAUDE_SKILL_DIR}/gitignore.txt`):

- `plugins/*/main.js` a `plugins/*/styles.css` jsou cizí kód, který se ze storu stáhne znovu. Verzuje se `manifest.json` (který plugin a v jaké verzi) a `data.json` (jeho nastavení). **Celé `plugins/` se neignoruje**, jinak by se ztratilo rozhodnutí, které pluginy vault používá.
- `themes/` je cizí CSS, téma určuje `appearance.json`.
- `workspace.json` a `workspaces.json` se mění při každém zavření aplikace.
- **Plugin, který ve storu není** (BRAT, beta, vlastní), se verzuje celý, protože po klonu už není odkud ho vzít.
- `obsidian/colleague-repo-exclude` **V repu kolegů se `.obsidian` necommituje vůbec.** Nepatří do sdíleného `.gitignore`, ale do `.git/info/exclude`, který zůstane jen na jednom stroji.

## Šablona

Adresář `template/` v adresáři tohoto skillu je hromádka *jak se Obsidian chová*: nastavení, seznam pluginů s manifesty a CSS snippety. Kód pluginů a téma v ní nejsou, Obsidian po otevření vaultu nabídne jejich stažení ze storu.

`obsidian/template-file-list` **Kopíruje se jmenovitý seznam souborů, adresář se nezrcadlí.** Zrcadlení by při další synchronizaci smazalo `data.json` pluginů a další soubory, které jmenují články cílového vaultu.

## Založení vaultu

Na požádání uživatele, ne z argumentu:

1. Zkopíruj obsah `${CLAUDE_SKILL_DIR}/template/` do `<repo>/.obsidian/`. Existující soubory nepřepisuj, rozdíly ukaž a zeptej se.
2. Doplň do `.gitignore` řádky z `${CLAUDE_SKILL_DIR}/gitignore.txt`, pokud tam ještě nejsou. V repu kolegů místo toho přidej `.obsidian/` do `.git/info/exclude`.
3. Když chybí `README.md`, založ ho jako rozcestník. `menu.md` zakládej, jen když uživatel chce lištu.
4. Když jde o vnořený vault, srovnej nastavení podle části Vnořený vault.
5. Spusť kontrolu níže.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je adresář vaultu. Když v něm `.obsidian` není, kontroluje se nejbližší nadřazený vault.

1. **Spusť skript** s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_obsidian.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Skript vypíše jednu řádku na neshodu ve tvaru `soubor:řádek: [identifikátor] zpráva`. JSON komentáře nemá, výjimka `pankostka: allow` tu proto není. Pravidla:
   - `obsidian/one-vault-per-repo`: adresář ani žádný nadřazený není vault,
   - `obsidian/nested-same-settings`: vnořený vault nemá nastavení souborů shodné s nadřazeným,
   - `obsidian/app-settings`: chybné nebo chybějící povinné nastavení v `app.json`,
   - `obsidian/ignore-filter-no-glob`: glob v `userIgnoreFilters`,
   - `obsidian/gitignore-plugin-code`: chybí řádky z `gitignore.txt`, nebo se ignoruje celé `plugins/`. Neplatí, když je `.obsidian` v `.git/info/exclude`,
   - `obsidian/no-tracked-plugin-code`: git verzuje kód pluginu, téma nebo stav oken,
   - `obsidian/root-readme`: chybí `README.md` (u vnořeného vaultu se nevyžaduje), nebo existuje `index.md` či `home.md`,
   - `obsidian/menu-embed`: `menu.md` není vložené prvním řádkem `README.md`.

   Vnořené vaulty uvnitř argumentu kontroluje skript taky.

2. **Projdi vault sám** na to, co skript nepozná:
   - jestli vault v tomhle repu dává smysl, nebo je dokumentace tak málo, že ho není potřeba,
   - jestli je vnořený vault opravdu samostatný výstup,
   - `data.json` a další soubory, které jmenují články, v šabloně nebo ve sdílené konfiguraci,
   - plugin mimo store, který je potřeba verzovat celý.

3. **Vypiš výsledek** s konkrétním návrhem opravy u každé neshody a souhrnem na konci.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí.
