---
name: pankostka-obsidian
description: Zásady pro vault v Obsidianu nad git repem - jeden vault na repo, vnořený vault, kořen vaultu s README.md a navigace bez menu.md, nastavení app.json (přílohy vedle článku, standardní odkazy s relativní cestou, skryté soubory), plugin Folder Notes, co z .obsidian verzovat a co patří do .gitignore, šablona konfigurace pro nový vault. Použij, když zakládáš, nastavuješ nebo kontroluješ vault, adresář .obsidian nebo jeho řádky v .gitignore. S argumentem (adresář vaultu) zkontroluje vault proti zásadám a vypíše neshody.
argument-hint: "[adresář vaultu]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_obsidian.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_obsidian.py *)
---

# Obsidian - vault nad git repem

Jak založit a udržovat vault v Obsidianu, když leží v git repu. Jak psát samotné články, řeší skill `pankostka-md`. Obsidian není jediný editor: články jsou ve standardním Markdownu a stejně se upravují třeba v Markře, nastavení vaultu proto nesmí vést k syntaxi, které rozumí jen Obsidian.

Argument: `$ARGUMENTS`

## Kdy vault

`obsidian/one-vault-per-repo` **Jeden vault na repo, a jen tam, kde je dokumentace.** Repo s několika markdowny vault nepotřebuje, článek se otevře v čemkoli. Vault se zakládá, až dokumentace přibude.

**Jeden vault nad všemi repy nefunguje**, i když láká kvůli odkazům napříč repy:

- **Cizí obsah se z indexu nedá vyřadit.** Export z cizího nástroje umí přinést tisíce prázdných souborů téhož jména a ty lezou do hledání i do Quick switcheru. `userIgnoreFilters` je jen ztlumí, neodstraní.
- **Nastavení je na vault, ne na složku.** Repa kolegů a moje repa nejde ve společném vaultu nastavit zvlášť.

Cenou za rozdělení je, že **odkaz neumí přejít z vaultu do vaultu**: Obsidian soubor mimo otevřený vault neotevře. Náhradou je odkaz `obsidian://open?vault=<Vault>&file=<Článek>`, který funguje, ale Obsidian ho při přejmenování článku neopraví. Rozdělení obvykle kopíruje obsah: v repu je dokumentace k tomu repu, obecné know-how je ve vlastním vaultu a odkazovat je potřeba hlavně uvnitř té hranice.

### Vnořený vault

Vault uvnitř jiného vaultu je povolený, **když je to samostatný výstup**, typicky wiki pro uživatele, která se otevírá zvlášť. Nadřazený vault indexuje i jeho články, takže tytéž soubory žijí ve dvou vaultech.

`obsidian/nested-same-settings` Proto musí mít vnořený vault **stejná nastavení, která rozhodují o souborech**, jako vault nadřazený: `attachmentFolderPath`, `useMarkdownLinks`, `newLinkFormat` a `alwaysUpdateLinks`. Jinak má článek podle otevřeného okna jinou složku na přílohy a jiný tvar odkazů. Vzhled, téma a pluginy se lišit smějí.

Rozcestník vnořeného vaultu určuje jeho obor, ne tenhle skill. Wiki kostky má rozcestník `<Kostka>.md` a `README.md` v ní být nemá, protože by ve vaultu repa nebyl jednoznačný.

## Kořen vaultu

`obsidian/root-readme` Ve všech vaultech stejně:

| Soubor | Role |
| --- | --- |
| `CLAUDE.md` | pravidla pro AI, nepublikuje se |
| `README.md` | rozcestník vaultu |

**Jednotný název není kosmetika.** Na rozcestník vedou odkazy ze záložky, ze startovního článku i z jiných článků. Se shodným názvem jde nastavení startovního článku do sdílené šablony.

**Navigační lišta `menu.md` se nepoužívá.** Vkládala se do rozcestníku řádkem `![[menu]]`, který GitHub ani Markra neumí a vypíšou ho doslova, a byla to jediná syntaxe Obsidianu, kterou `pankostka-md` povoloval. Navigaci dělá strom souborů s očíslovanými oblastmi (`10.PowerBI/`, `61.Obsidian/`) a adresář na článek, viz `pankostka-md`. Rozcestník v `README.md` dává přehled odkazy na články. Ve velkém vaultu ho může psát skript, který projde adresáře článků a zapíše strom mezi dvě značky v `README.md`, zbytek rozcestníku zůstane ručně psaný. Rozcestníky oblastí (`61.Obsidian/61.Obsidian.md`) se také nezakládají: obsahují jen seznam článků, který strom souborů ukazuje sám, a každý další článek je potřeba do nich dopsat.

**Proč `README.md`, a ne `home.md` nebo `index.md`:**

- Repo na GitHubu už README jako titulní stranu má. Druhý rozcestník vedle něj by byla kopie, která se rozejde.
- `index.md` koliduje s generátorem webu [obsidian2html](https://github.com/pankostka/obsidian2html), který generuje titulku `index.html`.

Na co si dát pozor:

- **`README.md` v podadresářích dělá název nejednoznačným.** Odkaz s cestou se trefí, ale Quick switcher a hledání nabídnou všechny.
- **Startovní článek povinný není.** Obsidian ho sám neumí, je na to komunitní plugin Homepage. Bez něj se obnoví poslední rozložení oken a na rozcestník se jde záložkou nebo Quick switcherem.

## Nastavení

`obsidian/app-settings` Povinná nastavení v `.obsidian/app.json`:

| Klíč | Hodnota | Proč |
| --- | --- | --- |
| `attachmentFolderPath` | `./` | přílohy vznikají ve složce aktuálního článku, tedy v jeho adresáři (viz `pankostka-md`) |
| `useMarkdownLinks` | `true` | nový odkaz je standardní `[Text](cesta.md)`, ne wikilink (viz `pankostka-md`) |
| `newLinkFormat` | `relative` | cesta relativní k článku, funguje i na GitHubu a v jiném editoru |
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
| Obsah vaultu | `README.md` | je to článek, ne konfigurace |

`obsidian/gitignore-plugin-code` a `obsidian/no-tracked-plugin-code` Do gitu jde `.obsidian` celý **kromě kódu pluginů, témat a stavu oken**. Řádky do `.gitignore` jsou v `gitignore.txt` v adresáři tohoto skillu (`${CLAUDE_SKILL_DIR}/gitignore.txt`):

- `plugins/*/main.js` a `plugins/*/styles.css` jsou cizí kód, který se ze storu stáhne znovu. Verzuje se `manifest.json` (který plugin a v jaké verzi) a `data.json` (jeho nastavení). **Celé `plugins/` se neignoruje**, jinak by se ztratilo rozhodnutí, které pluginy vault používá.
- `themes/` je cizí CSS, téma určuje `appearance.json`.
- `workspace.json` a `workspaces.json` se mění při každém zavření aplikace.
- **Plugin, který ve storu není** (BRAT, beta, vlastní), se verzuje celý, protože po klonu už není odkud ho vzít.
- `obsidian/colleague-repo-exclude` **V repu kolegů se `.obsidian` necommituje vůbec.** Nepatří do sdíleného `.gitignore`, ale do `.git/info/exclude`, který zůstane jen na jednom stroji.

## Šablona

Adresář `template/` v adresáři tohoto skillu je hromádka *jak se Obsidian chová*: nastavení, seznam pluginů s manifesty a CSS snippety. Kód pluginů a téma v ní nejsou, Obsidian po otevření vaultu nabídne jejich stažení ze storu.

**Plugin Folder Notes** je v šabloně kvůli adresáři na článek: článek leží v adresáři svého jména a plugin ho otevře kliknutím na adresář, skryje ho ve stromu souborů a při přejmenování adresáře přejmenuje i článek. Jeho výchozí nastavení (článek uvnitř adresáře, název podle adresáře) odpovídá pravidlům, takže `data.json` v šabloně není potřeba.

`obsidian/template-file-list` **Kopíruje se jmenovitý seznam souborů, adresář se nezrcadlí.** Zrcadlení by při další synchronizaci smazalo `data.json` pluginů a další soubory, které jmenují články cílového vaultu.

## Založení vaultu

Na požádání uživatele, ne z argumentu:

1. Zkopíruj obsah `${CLAUDE_SKILL_DIR}/template/` do `<repo>/.obsidian/`. Existující soubory nepřepisuj, rozdíly ukaž a zeptej se.
2. Doplň do `.gitignore` řádky z `${CLAUDE_SKILL_DIR}/gitignore.txt`, pokud tam ještě nejsou. V repu kolegů místo toho přidej `.obsidian/` do `.git/info/exclude`.
3. Když chybí `README.md`, založ ho jako rozcestník. `menu.md` ani rozcestníky oblastí nezakládej.
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
   - `obsidian/root-readme`: chybí `README.md` (u vnořeného vaultu se nevyžaduje), nebo existuje `index.md` či `home.md`.

   Zbylou `menu.md` a řádek `![[menu]]` hlásí `pankostka-md` jako `md/article-folder` a `md/no-wikilink`.

   Vnořené vaulty uvnitř argumentu kontroluje skript taky.

2. **Projdi vault sám** na to, co skript nepozná:
   - jestli vault v tomhle repu dává smysl, nebo je dokumentace tak málo, že ho není potřeba,
   - jestli je vnořený vault opravdu samostatný výstup,
   - `data.json` a další soubory, které jmenují články, v šabloně nebo ve sdílené konfiguraci,
   - plugin mimo store, který je potřeba verzovat celý.

3. **Vypiš výsledek** s konkrétním návrhem opravy u každé neshody a souhrnem na konci.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí.
