---
name: pankostka-md
description: Zásady psaní dokumentace ve standardním Markdownu nezávisle na editoru (Obsidian, Markra) - čeština bez typografických znaků a bez oslovení čtenáře, odstavec na jednom řádku, kde článek leží, adresář na článek a přílohy v něm, názvy souborů, standardní odkazy místo wikilinků, mrtvé odkazy a obrázky, frontmatter a tagy, callouty, publikace na web. Použij vždy, když píšeš, upravuješ nebo kontroluješ soubor .md, tedy článek, README.md, CLAUDE.md, úkol nebo jinou dokumentaci. S argumentem (soubor, adresář nebo --changed) zkontroluje soubory proti zásadám a vypíše neshody.
argument-hint: "[soubor | adresář | --changed]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_md.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_md.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/convert_wikilinks.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/convert_wikilinks.py *)
---

# Markdown - zásady

Jak psát dokumentaci v Markdownu. Dokumentací se rozumí popis repa, jeho částí a know-how kolem něj. Platí i pro instrukce pro AI (`CLAUDE.md`, popisy skillů), s jedinou výjimkou: ty mluví na agenta, takže tykají.

Argument: `$ARGUMENTS`

## Článek

`md/term-article` Soubor `*.md` se nazývá **článek**. Nepoužívej nota, note, poznámka ani artikl. Jeden pojem, ať se dá hledat.

Dokumentace je věcná, krátká a srozumitelná, psaná formálním a profesionálním stylem a s jednotnou terminologií v celém článku.

`md/no-hard-wrap` **Markdown nezalamuj na pevnou šířku.** Jeden odstavec je jeden řádek, jedna odrážka je jeden řádek, ať je jakkoli dlouhý. Zalamování dělá editor. Pevné zalomení jen rozhazuje text a v diffu se kvůli jednomu opravenému slovu přeskládá celý odstavec. Netýká se to bloků kódu, tabulek a nadpisů. Při úpravě stávajícího článku nepřidávej zalomení tam, kde žádné není.

## Jazyk

`md/czech-style` Jak se píše:

- Česky, včetně diakritiky.
- Kratší věty, ne dlouhá souvětí.
- Postponovaný přívlastek, kde se hodí: spíše *konfigurace zakázková* než *zakázková konfigurace*.

### Znaky

`md/keyboard-chars` **Piš jen znaky, které jsou na běžné klávesnici, české i anglické.** Česká diakritika je v pořádku. Nepoužívej dlouhou pomlčku (`—`), polodlouhou pomlčku (`–`), typografické uvozovky (`„ “`), výpustku (`…`) ani znak násobení (`×`). Místo dlouhé pomlčky použij spojovník (`-`), dvojtečku, závorku, nebo větu rozděl na dvě.

Důvod: text musí jít opravit a dopsat přímo v editoru bez vkládání speciálních znaků a musí vypadat stejně jako to, co do něj dopíše člověk.

**Šipka je povolená**, ale přednost má zápis `->`, protože jde napsat z klávesnice. Výjimkou jsou emoji ve funkci markeru, znaky, které jsou obsahem sdělení (ukázka kódu, vzorec, citace), a diagram kreslený znaky, tedy strom nebo schéma.

### Oslovení čtenáře

`md/no-addressing-reader` **Nemluv na čtenáře.** Nepoužívej sloveso ve druhé osobě (*otevřeš*, *uvidíš*, *můžeš*), rozkazovací způsob (*klikni*, *zvol*) ani zájmena *ty*, *tvůj*, *tvoje*. Popis veď zvratným trpným rodem, nebo tak, že podmětem je popisovaná věc. Tedy ne *Článek otevřeš přetažením záložky*, ale *Článek se otevře přetažením záložky*; ne *pro konfiguraci klikni na ikonu A*, ale *Ikona A zobrazí konfiguraci*.

Výjimkou jsou instrukce pro AI (`CLAUDE.md`, popisy skillů), které mluví na agenta.

## Editor

`md/standard-markdown` **Článek se píše ve standardním Markdownu** (CommonMark a GitHub Flavored Markdown), ne v syntaxi jednoho editoru. Tentýž článek se upravuje v Obsidianu i v Markře a čte se i na GitHubu, takže musí vypadat stejně všude. Jak založit a nastavit vault v Obsidianu, řeší skill `pankostka-obsidian`.

Callout (`> [!typ] Titulek`) je povolený. Obsidian, GitHub i Markra vykreslí jako rámeček typy `note`, `tip`, `important`, `warning` a `caution`. Vlastní typ, třeba `navrh-ai`, má barvu a ikonu jen v Obsidianu z CSS snippetu v `.obsidian/snippets/`, jinde se zobrazí jako obyčejná citace. Nerozbije se, jen ztratí barvu.

Vložení článku do jiného (`![[Článek]]`) standardní Markdown nezná a jiný editor ho vypíše doslova. **Článek se nevkládá, odkazuje se na něj** (`md/no-wikilink`). Proto ani navigační lišta `menu.md` vkládaná do rozcestníku: navigaci dělá strom souborů a rozcestník v `README.md`.

## Kde článek leží

Rozhodovací otázka: **dá se ten text použít i mimo tohle repo?**

| Odpověď | Kam patří |
| --- | --- |
| Ne, popisuje tohle repo nebo jeho objekt | do repa, viz níže |
| Ano, je to obecné know-how | do vaultu s know-how, mimo projekt |
| Je to pravidlo platné napříč repy | do skillu nebo repa se standardy, ne do projektu |

`md/article-location` Rozsah a umístění jsou dvě různé otázky. Uvnitř repa platí:

| Článek je o čem | Kde leží | Příklad |
| --- | --- | --- |
| o celém repu, o vazbách mezi částmi | `docs/` | `docs/Nasazení/Nasazení.md` |
| o jednom objektu, tedy proceduře, tabulce, modulu | v adresáři objektu, spolu s jeho kódem | `20_dim/nsp20DimUcet/nsp20DimUcet.md` |

**Článek pojmenovaný po objektu leží u toho objektu.** Stejná logika jako u kódu: procedura neleží v centrálním `procedures/`, ale ve své vrstvě. Kdo hledá popis procedury, hledá ho tam, kde je procedura. Objekt, který má článek, dostane vlastní adresář a jeho kód leží v něm, viz Adresář článku. Objekt bez článku zůstává souborem ve své vrstvě.

Cenou je, že se články nedají vyjmenovat jedním výpisem `docs/`. `md/readme-index` **Rozcestník v `README.md` proto není volitelný.** Je to jediné místo, kde je vidět, co všechno je zdokumentované.

## Adresář článku

`md/article-folder` **Každý článek leží ve vlastním adresáři, který se jmenuje přesně jako článek**, včetně markeru 🌐 a sufixu `-TMP`: `Obsidian Nastavení 🌐/Obsidian Nastavení 🌐.md`. V adresáři je všechno, co k článku patří: obrázky, přílohy, ukázky, pomocné soubory `-TMP` i export do PDF.

Důvod: článek je celek. Přesune se, přejmenuje nebo smaže jako jeden adresář a nezůstanou po něm osiřelé přílohy. Ve společné složce na přílohy nebylo poznat, co patří ke kterému článku.

Platí to všude stejně: v `docs/`, ve vaultu s know-how, ve wiki kostky i u úkolů v `tasks/`. Článek o objektu leží v adresáři pojmenovaném po objektu, třeba po plnicí proceduře, a s ním i kód objektu: `20_dim/nsp20DimUcet/` obsahuje `nsp20DimUcet.md`, `nsp20DimUcet.sql` a případně skript tabulky.

Přejmenování článku znamená přejmenovat i adresář. V Obsidianu to udělá plugin Folder Notes ze šablony vaultu (viz `pankostka-obsidian`), který také otevře článek kliknutím na adresář. V jiném editoru se adresář přejmenuje ručně a opraví se odkazy na článek, viz Odkazy.

Vlastní adresář nedostávají soubory, jejichž jméno a umístění určuje nástroj nebo konvence:

| Soubor | Proč |
| --- | --- |
| `README.md` | titulní strana repa na GitHubu a rozcestník vaultu |
| `CLAUDE.md`, `CLAUDE_Project.md`, `AGENTS.md` | AI je hledá podle jména |
| `LICENSE.md`, `CHANGELOG.md`, `CONTRIBUTING.md` | konvence GitHubu |
| `SKILL.md` a články vedle něj | adresář skillu je jejich adresářem |
| `tasks/tasks.md` | rozcestník úkolů, viz `pankostka-tasks` |
| rozcestník vnořeného vaultu | leží v jeho kořeni, třeba `Wiki<Kostka>/<Kostka>.md` |
| šablony Obsidianu | nejsou to články, ale kostry, složku šablon určuje `.obsidian/templates.json` |

## Přílohy

`md/attachment-own-folder` Příloha je soubor, který článek doplňuje, ale sám článkem není: obrázek, XML vzorek, tabulka, dokument od dodavatele. **Leží přímo v adresáři článku, vedle souboru `.md`**, bez další podsložky. Složka `Attachments/` se nepoužívá: adresář článku je sám tou složkou a další úroveň by jen prodloužila cestu.

**Příloha patří jen jednomu článku.** Když tentýž obrázek potřebuje druhý článek, dostane vlastní kopii, nebo odkáže na článek, ve kterém obrázek je. Na obrázek v adresáři jiného článku se neodkazuje: po přesunu nebo smazání toho článku by se rozbil odkaz, o kterém nikdo neví. Odkaz na jiný soubor v repu, třeba na proceduru, je v pořádku, to není příloha.

Pravidlo *dokumentace se píše v Markdownu* mluví o tom, co se píše, ne o tom, co někdo pošle. Přijatý soubor (Word od dodavatele, screenshot, export) je příloha a sám o sobě se do Markdownu nepřevádí. Jakmile se ale stane autoritativním popisem něčeho v repu, **převeď ho na článek**: binární dokument se nedá diffovat, hledat v něm ani publikovat. Po převodu je z něj historický podklad, ne druhý zdroj pravdy. Podklad, který už nemá funkci, dostane sufix `-TMP`, takže zůstane na disku, ale ne v gitu.

Aby přílohy vznikaly na správném místě samy, má Obsidian nastavené `attachmentFolderPath` na `./`, tedy *do stejné složky jako aktuální soubor*. V jiném editoru se vkládání obrázků nastaví stejně, pokud to editor umí, jinak se obrázek přesune vedle článku ručně. Platí to i pro soubory bez vlastního adresáře: obrázek vložený do `README.md` leží vedle něj.

`md/attachment-name` Vložený obrázek pojmenuje Obsidian sám jako `Pasted image 20260727145759.png`, tedy s mezerou, velkým písmenem a nic neříkajícím číslem. **Přejmenuj ho hned**. Obsidian si odkaz opraví sám, v jiném editoru se opraví ručně. Výjimkou je náhledový obrázek pro web, ten se jmenuje jako článek (`Obsidian Nastavení.png`), protože ho generátor webu hledá podle názvu.

### Soubory -TMP

Pomocné soubory k článku, tedy testovací dotazy, výstupy měření, podklady, které už neplatí, a export do PDF, leží v adresáři článku se sufixem `-TMP`. Smažou se s článkem a je jasné, k čemu patří. Na pojmenování se nekontrolují, takže PDF může nést název článku.

`md/no-link-to-tmp` **Veřejný článek na soubor `-TMP` neodkazuje.** Soubor není v gitu ani na webu, takže čtenář narazí na mrtvý odkaz. Interní článek odkazovat smí, třeba úkol na výstup měření, protože ho čte ten, kdo soubor má na disku.

Rozepsaný článek mimo git má sufix na adresáři i na souboru: `Nový Článek-TMP/Nový Článek-TMP.md`. Adresář se sufixem `-TMP` vyřadí z gitu i všechno uvnitř.

## Názvy souborů

`md/file-names` Názvy článků, příloh a složek:

| Co | Konvence | Příklad |
| --- | --- | --- |
| **Článek** | mezera jako oddělovač, každé slovo velkým, **s diakritikou** | `Obsidian Nastavení.md` |
| **Článek pojmenovaný po objektu** | přesně název objektu, včetně diakritiky, pokud ji objekt má | `DimZakaznik.md`, `DimÚčet.md` |
| **Adresář článku** | přesně jako článek, včetně markeru 🌐 a sufixu `-TMP` | `Obsidian Nastavení 🌐/` |
| **Obrázek a příloha** | **malými písmeny bez diakritiky**, podtržítko jako oddělovač | `nastaveni_mapovani_krok1.png` |
| **Složka strukturální** | **anglicky, ASCII**, bez emoji | `docs/`, `tasks/` |
| **Složka tematická** | jako článek, bez emoji | `Účetnictví/` |

Oddělovač v názvu přílohy je **podtržítko, ne pomlčka**. Pomlčka je vyhrazená pro sufixy `-VZOR`, `-DRAFT` a `-TMP`, které popisuje skill `pankostka-git`.

Adresář článku je součást článku, ne struktura repa, proto smí mít diakritiku i marker. Složka strukturální je součást uspořádání repa nebo nástroje, složka tematická sdružuje články podle obsahu a čte se jako titulek. Rozhoduje povaha názvu, ne jeho autor: co se objeví v cestě, v adrese nebo v konfiguraci, je struktura; co čte člověk jako titulek, je obsah. Struktura zůstává v ASCII, protože se propisuje do skriptů, příkazové řádky a odkazů na GitHubu, kde diakritika naráží na kódování.

Článek pojmenovaný po objektu smí mít diakritiku, aby šel dohledat podle přesného názvu objektu. Do adresy na webu se diakritika stejně nedostane, slug ji odstraní.

## Odkazy

`md/no-wikilink` **Odkaz na článek je standardní markdownový odkaz s relativní cestou**, ne wikilink `[[...]]`:

```markdown
[Obsidian Nastavení](../Obsidian%20Nastavení/Obsidian%20Nastavení.md)
```

Wikilink je syntaxe Obsidianu. GitHub ho vypíše jako holý text a jiný editor ho nemusí otevřít. Standardní odkaz funguje všude. Pravidlo hlásí i vložení článku `![[...]]`, viz Editor.

- **Mezera v cestě se píše `%20`**, tak odkaz zapíše Obsidian. Funguje i cesta v lomených závorkách `[Text](<../Obsidian Nastavení/Obsidian Nastavení.md>)`. Diakritika a emoji se nekódují.
- **Text odkazu je název článku**, nebo slova věty, ke kterým odkaz patří.
- **Odkaz vede na článek, ne na nadpis v něm.** Kotva nadpisu má v každém nástroji jiný tvar (Obsidian `#Název%20nadpisu`, GitHub `#nazev-nadpisu`). Výjimkou je odkaz na sekci uvnitř téhož článku.

`md/no-broken-link` **Odkaz míří na existující soubor.** Cenou za standardní odkaz je cesta: přesun nebo přejmenování článku ji rozbije. Obsidian odkazy při přejmenování a přesunu opraví sám, v Markře, gitem, skriptem nebo v AI se musí opravit ručně. Proto skript hlásí každý relativní odkaz a obrázek, jehož cíl neexistuje. Cíl se sufixem `-TMP` neověřuje, ten v gitu není. Číslo řádku za cestou (`../20_dim/nsp20DimUcet.sql:179`) skript ignoruje a ověřuje jen soubor.

**Převod starých wikilinků** dělá skript `convert_wikilinks.py`, jen na výslovný pokyn uživatele. Bez `--make` vypíše, co by změnil, s `--make` to zapíše:

```
python ${CLAUDE_SKILL_DIR}/scripts/convert_wikilinks.py <adresář vaultu> [--make]
```

Cíl hledá jako Obsidian, podle názvu v celém adresáři. Nejednoznačný a neexistující cíl a odkaz na nadpis v témž článku nechá a vypíše jako `ponecháno`, ty se převedou ručně. Odkaz na nadpis jiného článku převede na odkaz na článek. Vloženému obrázku dá prázdný popis, který se doplní podle `md/image-markdown-alt`. Před `--make` musí být změny v gitu commitnuté, aby šel převod porovnat a případně vrátit.

`md/image-markdown-alt` **Obrázek se vkládá jako `![Popis obrázku](soubor.png)`**, ne `![[soubor.png]]`. Popis potřebuje generátor webu i čtečka pro nevidomé.

## Frontmatter

Volitelný. Článek bez frontmatteru je plnohodnotný článek.

| Klíč | Kdy | Význam |
| --- | --- | --- |
| `title` | jen když název souboru nemůže být titulkem | přebije název souboru |
| `slug` | jen když se odvozený název nehodí | přebije název výstupního souboru |
| `tags` | volitelně | témata |
| `date` | volitelně | datum vydání ve tvaru `RRRR-MM-DD` |

`md/frontmatter-keys` **Klíče jsou anglicky, protože je čte nástroj.** Generátor webu [obsidian2html](https://github.com/pankostka/obsidian2html) rozumí `title` a `date`. Starší české klíče `titul` a `datum` ignoruje, takže článek s `datum` dostane na webu datum souboru, které se mění při kopírování i synchronizaci.

`md/title-from-filename` **Titulek je název souboru**, jako v Obsidianu. `title` je výjimka pro technický název, třeba článek pojmenovaný po objektu. **Titulek se nebere z nadpisu `# H1`.** Jediné H1 bývá titulek, ale v článku ze šablony to může být první sekce, třeba `# Popis`, a z textu se to poznat nedá.

**Slug je název výstupního souboru, tedy i adresa na webu.** Odvozuje se z názvu článku: malá písmena, bez diakritiky, mezera na pomlčku. `Obsidian Nastavení.md` dá `obsidian-nastaveni.html`.

`md/tag-pascal-case` **Tag se píše v PascalCase**, tedy `Obsidian`, `Markdown`, `PowerBI`, `AI`: každé slovo velkým, bez mezer a oddělovačů. Tak, jak je zapsaný, se zobrazí na webu, takže je to i popisek pro čtenáře.

`md/tag-one-variant` **Jedna varianta na tag.** Obsidian páruje tagy bez ohledu na velikost písmen, takže `#Obsidian` a `#obsidian` jsou pro něj jeden tag a nekonzistence se v editoru neprojeví. Generátor webu je ale porovnává jako řetězce: vzniknou dvě stránky téhož tagu, jedna přepíše druhou a část článků ze stránky tagu zmizí, aniž by to build ohlásil.

## Publikace

Co jde na web, určuje **marker 🌐 na konci názvu článku**, ne frontmatter. Chybějící marker znamená neveřejné. `md/no-link-to-private` Veřejný článek nesmí odkazovat na neveřejný ani na soubor `-TMP`. Než článek označíš markerem, upravíš veřejný článek nebo budeš sestavovat web či PDF, přečti si `publishing.md` v adresáři tohoto skillu (`${CLAUDE_SKILL_DIR}/publishing.md`).

## Co do dokumentace nepatří

`md/no-secrets-generated`

- **Hesla, tokeny, connection stringy s přihlašovacími údaji.** Názvy serverů a databází ano.
- **Vygenerované HTML.** Zdroj je Markdown, HTML se z něj dá kdykoli vyrobit znovu.
- **PDF bez sufixu `-TMP`**, pokud to není vědomá výjimka.

`md/utf8-no-bom` **Článek je v UTF-8 bez BOM**, jako každý textový soubor, viz `pankostka-git`.

## Výjimka z pravidla

Vědomé porušení pravidla zapiš HTML komentářem na řádek nálezu nebo na řádek nad ním. Komentář jmenuje identifikátor pravidla a za čárkou důvod:

```markdown
<!-- pankostka: allow md/no-hard-wrap, adresa po řádcích -->
Firma s.r.o.
Ulice 1
```

Identifikátorů může být víc, oddělených čárkou. **Důvod je povinný**, bez něj skript nález hlásí dál. V náhledu editoru ani na webu komentář vidět není.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je cesta k souboru, k adresáři (prochází se rekurzivně), nebo `--changed` pro soubory, které git hlásí jako změněné nebo nové.

1. **Spusť skript** na mechanická pravidla, s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_md.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Skript vypíše jednu řádku na neshodu ve tvaru `soubor:řádek: [identifikátor] zpráva`, řádek s výjimkou `pankostka: allow` a důvodem nehlásí. Pravidla:
   - `md/utf8-no-bom`: soubor není v UTF-8 bez BOM,
   - `md/keyboard-chars`: zakázané znaky mimo bloky kódu a inline kód,
   - `md/no-hard-wrap`: odstavec, odrážka nebo citace zalomená uprostřed věty, tedy na pevnou šířku,
   - `md/article-folder`: článek neleží v adresáři svého jména a není mezi výjimkami z tabulky v části Adresář článku,
   - `md/no-wikilink`: odkaz jako `[[...]]`, s návrhem standardního odkazu, když článek ve vaultu najde, a vložení článku `![[...]]`,
   - `md/no-broken-link`: relativní odkaz nebo obrázek, jehož cíl neexistuje,
   - `md/image-markdown-alt`: obrázek jako `![[...]]`, obrázek bez popisu,
   - `md/attachment-own-folder`: obrázek neleží přímo v adresáři článku (cesta s `/`, tedy i `Attachments/`),
   - `md/frontmatter-keys`: klíče `titul`, `datum` a `publish`, `date` mimo tvar `RRRR-MM-DD`,
   - `md/tag-pascal-case`: tag mimo PascalCase (podtržítko na začátku je povolené),
   - `md/attachment-name`: `Pasted image*`, obrázek v adresáři článku s jinými znaky než malá písmena, číslice a podtržítko, kromě náhledu pojmenovaného jako článek,
   - `md/tag-one-variant`: tentýž tag ve více variantách velikosti písmen,
   - `md/no-link-to-private`: článek s markerem 🌐 odkazuje na článek bez markeru,
   - `md/no-link-to-tmp`: článek s markerem 🌐 odkazuje na soubor nebo článek se sufixem `-TMP`.

   Pravidla `md/tag-one-variant` a `md/no-link-to-private` porovnávají články mezi sebou. `md/tag-one-variant` vidí jen kontrolované soubory, takže je úplný jen při kontrole celého vaultu. `md/no-link-to-private` hledá cíl odkazu v celém vaultu, tedy od nejbližšího adresáře s `.obsidian`. Soubory a adresáře se sufixem `-TMP` skript přeskakuje.

2. **Projdi soubory sám** na pravidla, která skript nepokrývá:
   - `md/no-addressing-reader` a `md/czech-style`: oslovení čtenáře a dlouhá souvětí,
   - **věty na samostatných řádcích bez prázdného řádku mezi nimi**: skript je nehlásí, protože nejde o zalomení na pevnou šířku. Obsidian je zobrazí pod sebou, jiné nástroje je ale mohou spojit do jednoho odstavce. Když jde o samostatné myšlenky, navrhni prázdný řádek mezi nimi nebo odrážky,
   - `md/standard-markdown`: syntaxe jen jednoho editoru, třeba zvýraznění `==text==` nebo komentář `%%...%%`,
   - `md/term-article`: jednotná terminologie a pojem článek,
   - `md/article-location` a `md/readme-index`: umístění článku (`docs/` nebo v adresáři objektu spolu s jeho kódem) a rozcestník v `README.md`,
   - `md/file-names`: název článku a složky podle tabulky Názvy souborů,
   - `md/attachment-own-folder`: odkaz na přílohu, která není obrázek, v adresáři jiného článku. Odkaz na kód nebo jiný soubor repa, který přílohou není, je v pořádku,
   - `md/tag-pascal-case` a `md/tag-one-variant`: tagy zapsané v textu jako `#Tag`, skript čte jen frontmatter,
   - **výjimky ze zakázaných znaků**: skript hlásí i znak v citaci nebo v diagramu mimo blok kódu, takové hlášení posuď a případně vyřaď.

   Soubor, který skript nahlásil jako mimo UTF-8, nečti a nekontroluj.

3. **Vypiš výsledek** po souborech. U každé neshody `soubor:řádek`, identifikátor porušeného pravidla a konkrétní návrh opravy. Neshody ze skriptu a z vlastní kontroly slouč do jednoho seznamu a u sporných případů napiš, proč jsou sporné. Na konec dej souhrn: kolik souborů, kolik neshod podle pravidel.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí. Přejmenování přílohy nebo článku a přesun článku do vlastního adresáře dělej v Obsidianu nebo s opravou všech odkazů, jinak se rozbijí. Po přesunu spusť kontrolu znovu, `md/no-broken-link` ukáže, co zbylo. Při přesunu do adresáře přesuň i přílohy, které článek používá, a oprav cesty k obrázkům.

U velkého adresáře nejdřív řekni, kolik souborů kontrola obsahuje, a u více než dvaceti se zeptej, jestli pokračovat, nebo zúžit výběr.
