---
name: pankostka-md
description: Zásady psaní dokumentace v Markdownu a Obsidianu - čeština bez typografických znaků a bez oslovení čtenáře, odstavec na jednom řádku, kde článek leží, přílohy v Attachments, názvy souborů, wikilinky a obrázky, frontmatter a tagy, callouty, publikace na web. Použij vždy, když píšeš, upravuješ nebo kontroluješ soubor .md, tedy článek, README.md, CLAUDE.md, úkol nebo jinou dokumentaci. S argumentem (soubor, adresář nebo --changed) zkontroluje soubory proti zásadám a vypíše neshody.
argument-hint: "[soubor | adresář | --changed]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_md.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_md.py *)
---

# Markdown - zásady

Jak psát dokumentaci v Markdownu. Dokumentací se rozumí popis repa, jeho částí a know-how kolem něj. Platí i pro instrukce pro AI (`CLAUDE.md`, popisy skillů), s jedinou výjimkou: ty mluví na agenta, takže tykají.

Argument: `$ARGUMENTS`

## Článek

Soubor `*.md` se nazývá **článek**. Nepoužívej nota, note, poznámka ani artikl. Jeden pojem, ať se dá hledat.

Dokumentace je věcná, krátká a srozumitelná, psaná formálním a profesionálním stylem a s jednotnou terminologií v celém článku.

**Markdown nezalamuj na pevnou šířku.** Jeden odstavec je jeden řádek, jedna odrážka je jeden řádek, ať je jakkoli dlouhý. Zalamování dělá editor. Pevné zalomení jen rozhazuje text a v diffu se kvůli jednomu opravenému slovu přeskládá celý odstavec. Netýká se to bloků kódu, tabulek a nadpisů. Při úpravě stávajícího článku nepřidávej zalomení tam, kde žádné není.

## Jazyk

- Česky, včetně diakritiky.
- Kratší věty, ne dlouhá souvětí.
- Postponovaný přívlastek, kde se hodí: spíše *konfigurace zakázková* než *zakázková konfigurace*.

### Znaky

**Piš jen znaky, které jsou na běžné klávesnici, české i anglické.** Česká diakritika je v pořádku. Nepoužívej dlouhou pomlčku (`—`), polodlouhou pomlčku (`–`), typografické uvozovky (`„ “`), výpustku (`…`) ani znak násobení (`×`). Místo dlouhé pomlčky použij spojovník (`-`), dvojtečku, závorku, nebo větu rozděl na dvě.

Důvod: text musí jít opravit a dopsat přímo v editoru bez vkládání speciálních znaků a musí vypadat stejně jako to, co do něj dopíše člověk.

**Šipka je povolená**, ale přednost má zápis `->`, protože jde napsat z klávesnice. Výjimkou jsou emoji ve funkci markeru, znaky, které jsou obsahem sdělení (ukázka kódu, vzorec, citace), a diagram kreslený znaky, tedy strom nebo schéma.

### Oslovení čtenáře

**Nemluv na čtenáře.** Nepoužívej sloveso ve druhé osobě (*otevřeš*, *uvidíš*, *můžeš*), rozkazovací způsob (*klikni*, *zvol*) ani zájmena *ty*, *tvůj*, *tvoje*. Popis veď zvratným trpným rodem, nebo tak, že podmětem je popisovaná věc. Tedy ne *Článek otevřeš přetažením záložky*, ale *Článek se otevře přetažením záložky*; ne *pro konfiguraci klikni na ikonu A*, ale *Ikona A zobrazí konfiguraci*.

Výjimkou jsou instrukce pro AI (`CLAUDE.md`, popisy skillů), které mluví na agenta.

## Obsidian

Předpokládaným editorem je **Obsidian**, ale jen v repu, které má v kořeni adresář `.obsidian`. Jinde se s ním nepočítá a článek se otevře v čemkoli. Jak vault založit a co z jeho nastavení verzovat, řeší skill `pankostka-obsidian`.

Callout (`> [!typ] Titulek`) je syntaxe Obsidianu. V Obsidianu se vykreslí jako barevný rámeček, jinde (GitHub, HTML, PDF) jako obyčejná citace, takže se nerozbije, jen ztratí barvu. Vlastní typ dostane barvu a ikonu z CSS snippetu v `.obsidian/snippets/`, bez snippetu se zobrazí jako výchozí modrá poznámka.

## Kde článek leží

Rozhodovací otázka: **dá se ten text použít i mimo tohle repo?**

| Odpověď | Kam patří |
| --- | --- |
| Ne, popisuje tohle repo nebo jeho objekt | do repa, viz níže |
| Ano, je to obecné know-how | do vaultu s know-how, mimo projekt |
| Je to pravidlo platné napříč repy | do skillu nebo repa se standardy, ne do projektu |

Rozsah a umístění jsou dvě různé otázky. Uvnitř repa platí:

| Článek je o čem | Kde leží | Příklad |
| --- | --- | --- |
| o celém repu, o vazbách mezi částmi | `docs/` | `docs/Nasazení.md` |
| o jednom objektu, tedy proceduře, tabulce, modulu | u toho objektu | `20_dim/nsp20DimUcet.md` |

**Článek pojmenovaný po objektu leží u toho objektu.** Stejná logika jako u kódu: procedura neleží v centrálním `procedures/`, ale ve své vrstvě. Kdo hledá popis procedury, hledá ho tam, kde je procedura.

Cenou je, že se články nedají vyjmenovat jedním výpisem `docs/`. **Rozcestník v `README.md` proto není volitelný.** Je to jediné místo, kde je vidět, co všechno je zdokumentované.

## Přílohy

Příloha je soubor, který článek doplňuje, ale sám článkem není: obrázek, XML vzorek, tabulka, dokument od dodavatele. Leží ve složce **`Attachments/`** vedle článku, který ji používá. Jiný název složky nepoužívej, ani `img/`, ani `obrazky/`. Jeden pojem, jeden název.

Pravidlo *dokumentace se píše v Markdownu* mluví o tom, co se píše, ne o tom, co někdo pošle. Přijatý soubor (Word od dodavatele, screenshot, export) je příloha a sám o sobě se do Markdownu nepřevádí. Jakmile se ale stane autoritativním popisem něčeho v repu, **převeď ho na článek**: binární dokument se nedá diffovat, hledat v něm ani publikovat. Po převodu je z něj historický podklad, ne druhý zdroj pravdy. Podklad, který už nemá funkci, dostane sufix `-TMP`, takže zůstane na disku, ale ne v gitu.

Aby přílohy vznikaly na správném místě samy, má Obsidian nastavené `attachmentFolderPath` na `./Attachments`, tedy *v podsložce aktuální složky*. Bez toho ukládá vložené obrázky jinam.

Vložený obrázek pojmenuje Obsidian sám jako `Pasted image 20260727145759.png`, tedy s mezerou, velkým písmenem a nic neříkajícím číslem. **Přejmenuj ho hned**, odkaz si Obsidian opraví sám.

## Názvy souborů

| Co | Konvence | Příklad |
| --- | --- | --- |
| **Článek** | mezera jako oddělovač, každé slovo velkým, **s diakritikou** | `Obsidian Nastavení.md` |
| **Článek pojmenovaný po objektu** | přesně název objektu, včetně diakritiky, pokud ji objekt má | `DimZakaznik.md`, `DimÚčet.md` |
| **Obrázek a příloha** | **malými písmeny bez diakritiky**, podtržítko jako oddělovač | `nastaveni_mapovani_krok1.png` |
| **Složka strukturální** | **anglicky, ASCII**, bez emoji | `docs/`, `Attachments/` |
| **Složka tematická** | jako článek, bez emoji | `Účetnictví/` |

Oddělovač v názvu přílohy je **podtržítko, ne pomlčka**. Pomlčka je vyhrazená pro sufixy `-VZOR`, `-DRAFT` a `-TMP`, které popisuje skill `pankostka-git`.

Složka strukturální je součást uspořádání repa nebo nástroje, složka tematická sdružuje články podle obsahu a čte se jako titulek. Rozhoduje povaha názvu, ne jeho autor: co se objeví v cestě, v adrese nebo v konfiguraci, je struktura; co čte člověk jako titulek, je obsah. Struktura zůstává v ASCII, protože se propisuje do skriptů, příkazové řádky a odkazů na GitHubu, kde diakritika naráží na kódování.

Článek pojmenovaný po objektu smí mít diakritiku, aby šel dohledat podle přesného názvu objektu. Do adresy na webu se diakritika stejně nedostane, slug ji odstraní.

## Odkazy

Schválně dvě konvence, protože každá řeší jiný problém:

| Co | Jak | Proč |
| --- | --- | --- |
| **Odkaz na článek** | wikilink `[[Název článku]]` | Obsidian ho opraví při přejmenování i přesunu |
| **Obrázek** | markdown `![Popis obrázku](Attachments/soubor.png)` | popis potřebuje generátor webu i čtečka pro nevidomé |

## Frontmatter

Volitelný. Článek bez frontmatteru je plnohodnotný článek.

| Klíč | Kdy | Význam |
| --- | --- | --- |
| `title` | jen když název souboru nemůže být titulkem | přebije název souboru |
| `slug` | jen když se odvozený název nehodí | přebije název výstupního souboru |
| `tags` | volitelně | témata |
| `date` | volitelně | datum vydání ve tvaru `RRRR-MM-DD` |

**Klíče jsou anglicky, protože je čte nástroj.** Generátor webu [obsidian2html](https://github.com/pankostka/obsidian2html) rozumí `title` a `date`. Starší české klíče `titul` a `datum` ignoruje, takže článek s `datum` dostane na webu datum souboru, které se mění při kopírování i synchronizaci.

**Titulek je název souboru**, jako v Obsidianu. `title` je výjimka pro technický název, třeba článek pojmenovaný po objektu. **Titulek se nebere z nadpisu `# H1`.** Jediné H1 bývá titulek, ale v článku ze šablony to může být první sekce, třeba `# Popis`, a z textu se to poznat nedá.

**Slug je název výstupního souboru, tedy i adresa na webu.** Odvozuje se z názvu článku: malá písmena, bez diakritiky, mezera na pomlčku. `Obsidian Nastavení.md` dá `obsidian-nastaveni.html`.

**Tag se píše v PascalCase**, tedy `Obsidian`, `Markdown`, `PowerBI`, `AI`: každé slovo velkým, bez mezer a oddělovačů. Tak, jak je zapsaný, se zobrazí na webu, takže je to i popisek pro čtenáře.

**Jedna varianta na tag.** Obsidian páruje tagy bez ohledu na velikost písmen, takže `#Obsidian` a `#obsidian` jsou pro něj jeden tag a nekonzistence se v editoru neprojeví. Generátor webu je ale porovnává jako řetězce: vzniknou dvě stránky téhož tagu, jedna přepíše druhou a část článků ze stránky tagu zmizí, aniž by to build ohlásil.

## Publikace

Co jde na web, určuje **marker 🌐 na konci názvu článku**, ne frontmatter. Chybějící marker znamená neveřejné. Než článek označíš markerem, upravíš veřejný článek nebo budeš sestavovat web či PDF, přečti si `publishing.md` v adresáři tohoto skillu (`${CLAUDE_SKILL_DIR}/publishing.md`).

## Co do dokumentace nepatří

- **Hesla, tokeny, connection stringy s přihlašovacími údaji.** Názvy serverů a databází ano.
- **Vygenerované HTML.** Zdroj je Markdown, HTML se z něj dá kdykoli vyrobit znovu.
- **PDF bez sufixu `-TMP`**, pokud to není vědomá výjimka.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je cesta k souboru, k adresáři (prochází se rekurzivně), nebo `--changed` pro soubory, které git hlásí jako změněné nebo nové.

1. **Spusť skript** na mechanická pravidla, s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_md.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript vypíše jednu řádku na neshodu ve tvaru `soubor:řádek: [pravidlo] zpráva`. Pravidla:
   - `encoding`: soubor není v UTF-8 bez BOM,
   - `chars`: zakázané znaky mimo bloky kódu a inline kód,
   - `wrap`: odstavec, odrážka nebo citace zalomená uprostřed věty, tedy na pevnou šířku,
   - `image`: obrázek jako `![[...]]`, obrázek bez popisu, obrázek mimo `Attachments/`,
   - `frontmatter`: klíče `titul`, `datum` a `publish`, `date` mimo tvar `RRRR-MM-DD`, tag mimo PascalCase (podtržítko na začátku je povolené),
   - `attachment`: `Pasted image*`, příloha v `Attachments/` s jinými znaky než malá písmena, číslice a podtržítko,
   - `tag`: tentýž tag ve více variantách velikosti písmen,
   - `publish`: článek s markerem 🌐 odkazuje na článek bez markeru.

   Pravidla `tag` a `publish` porovnávají články mezi sebou. `tag` vidí jen kontrolované soubory, takže je úplný jen při kontrole celého vaultu. `publish` hledá cíl odkazu v celém vaultu, tedy od nejbližšího adresáře s `.obsidian`. Soubory a adresáře se sufixem `-TMP` skript přeskakuje.

2. **Projdi soubory sám** na pravidla, která skript nepokrývá:
   - oslovení čtenáře a dlouhá souvětí,
   - **věty na samostatných řádcích bez prázdného řádku mezi nimi**: skript je nehlásí, protože nejde o zalomení na pevnou šířku. Obsidian je zobrazí pod sebou, jiné nástroje je ale mohou spojit do jednoho odstavce. Když jde o samostatné myšlenky, navrhni prázdný řádek mezi nimi nebo odrážky,
   - jednotná terminologie a pojem článek,
   - umístění článku (`docs/` nebo u objektu) a rozcestník v `README.md`,
   - název článku a složky podle tabulky Názvy souborů,
   - odkaz na přílohu, která není obrázek, mimo `Attachments/`,
   - tagy zapsané v textu jako `#Tag`, skript čte jen frontmatter,
   - **výjimky ze zakázaných znaků**: skript hlásí i znak v citaci nebo v diagramu mimo blok kódu, takové hlášení posuď a případně vyřaď.

   Soubor, který skript nahlásil jako mimo UTF-8, nečti a nekontroluj.

3. **Vypiš výsledek** po souborech. U každé neshody `soubor:řádek`, porušené pravidlo a konkrétní návrh opravy. Neshody ze skriptu a z vlastní kontroly slouč do jednoho seznamu a u sporných případů napiš, proč jsou sporné. Na konec dej souhrn: kolik souborů, kolik neshod podle pravidel.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí. Přejmenování přílohy nebo článku dělej v Obsidianu nebo s opravou všech odkazů, jinak se rozbijí.

U velkého adresáře nejdřív řekni, kolik souborů kontrola obsahuje, a u více než dvaceti se zeptej, jestli pokračovat, nebo zúžit výběr.
