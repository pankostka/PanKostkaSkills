---
name: pankostka-powerbi-wiki
description: Dokumentace kostky (sémantického modelu Power BI a jeho reportů) pro uživatele ve wiki v Obsidianu - adresář Wiki<Kostka>, jeden článek na kostku, faktovku, dimenzi a report, osnovy článků, frontmatter a tagy, tabulka ukazatelů generovaná z modelu, callouty Návrh AI. Použij, když zakládáš, píšeš nebo kontroluješ článek ve Wiki<Kostka>/, a na pokyn Aktualizuj wiki <Kostka> (také Make wiki, Do wiki). S argumentem <Kostka> porovná wiki s modelem a vypíše, co by udělal; s --make články založí a upraví.
argument-hint: "[<Kostka> [--make]]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_wiki.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_wiki.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/measures_table.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/measures_table.py *)
---

# Wiki kostky

Jak se dokumentuje kostka pro uživatele. **Kostka** je sémantický model Power BI a jeho reporty, typicky nad jedním datamartem. Obecná pravidla pro články (jazyk, přílohy, odkazy, názvy souborů) jsou ve skillu `pankostka-md` a platí i tady. Konvence modelu jsou ve skillu `pankostka-powerbi`.

Osnovy jednotlivých článků jsou v `${CLAUDE_SKILL_DIR}/outlines.md`, tabulka ukazatelů v článku faktovky v `${CLAUDE_SKILL_DIR}/measures-table.md`. Čti je, když článek zakládáš, kontroluješ nebo upravuješ.

Argument: `$ARGUMENTS`

## Zásady

A. `wiki/user-view` **Z pohledu uživatele.** Dokumentace popisuje to, **co uživatel vidí**.

B. `wiki/article-per-element` **Z prvků.** Prvky jsou čtyři a každý má právě jeden článek: **kostka**, **faktovka**, **dimenze** a **report**. Prvek patří vždy ke konkrétní kostce. Když stejnou dimenzi používají dvě kostky, má článek v každé z nich.

K prvkům se volitelně řadí **údržba**: článek o tom, jak uživatel udržuje data ve zdrojovém systému, aby kostka počítala správně, například mapování účtů na řádky výkazu v ERP. Nepopisuje model, ale práci uživatele. Patří sem jen tehdy, když chybná nebo chybějící data mění čísla v reportu. Zdrojem může být ERP i sešit. Článek údržby se váže na faktovku nebo dimenzi, které se týká, a píše ho člověk. AI ho nezakládá, protože model o něm nic neví.

C. `wiki/simple` **Jednoduchá.** Píše se jen to podstatné a to, co se z modelu nedá vyčíst. **Co je samozřejmé, se nepíše**: atribut `Číslo karty` popis nepotřebuje. Výpočet se popisuje jen tehdy, když má výjimku nebo zvláštnost. Krátký text se čte a hlavně udržuje: co se nenapíše, to nezastará.

D. `wiki/ai-draft-human-edit` **Vytvářená AI, upravovaná člověkem.** První verzi článku napíše AI jako koncept, **člověk ho přeformuluje** pro člověka. Po přeformulování AI jeho text nepřepisuje: drobné věcné chyby opraví, delší místa jen **navrhne** způsobem popsaným v části Aktualizace.

`wiki/measures-table` **Výjimka ze zásad C a D je tabulka ukazatelů** v článku faktovky. Mezi jejími značkami udržuje skript `measures_table.py` sloupce Adresář a Ukazatel a výrazy DAX podle modelu, i u samozřejmých měr. Popis míry píše člověk a skript ho nemění. Jinam do článku žádný nástroj nezapisuje.

## Umístění a názvy

Wiki leží v adresáři **`Wiki<Kostka>/`** vedle PBIP projektu kostky. Adresář se jmenuje `Wiki<Kostka>`, ne jednotně: Obsidian používá název adresáře jako název vaultu a stejně pojmenované vaulty by v seznamu nešly rozlišit.

Rozcestník leží v kořeni wiki, **každý další článek ve vlastním adresáři** s přílohami vedle sebe, stejně jako každý článek podle `pankostka-md`: `Wiki<Kostka>/KostkaEKO FactDenik/KostkaEKO FactDenik.md`.

| Článek | Název | Příklad |
| --- | --- | --- |
| kostka, tedy rozcestník | `<Kostka>.md` v kořeni wiki | `KostkaEKO.md` |
| faktovka | `<Kostka> <Tabulka>.md` | `KostkaEKO FactDenik.md` |
| dimenze | `<Kostka> <Tabulka>.md` | `KostkaEKO DimÚčet.md` |
| report | `<Kostka> <Report>.md` | `KostkaEKO Výsledovka.md` |
| údržba | `<Kostka> <Téma>.md` | `KostkaAXMain Mapování ManČlen.md` |

`wiki/kostka-prefix` **Předpona kostky je povinná.** Obsidian páruje wikilinky podle názvu napříč celým vaultem a `DimDatum` je ve více kostkách. Bez předpony by `[[DimDatum]]` vedl náhodně do jedné z nich.

**Tabulka a report se jmenují přesně jako v modelu**, včetně diakritiky, pokud ji model má. Článek se tak dá dohledat z Power BI i naopak.

`wiki/wikilink-alias` **Wikilink se píše s aliasem**, tedy `[[KostkaEKO DimÚčet|DimÚčet]]`. Předpona je v názvu kvůli jednoznačnosti, čtenáři nic neříká.

`wiki/index-article` **Rozcestník kostky je `<Kostka>.md`, ne `README.md`.** `README.md` je rozcestník repa a ve vaultu repa by další soubor téhož jména nebyl jednoznačný. `README.md` repa odkazuje na rozcestník každé kostky, protože články leží u kostek a jedním výpisem adresáře se vyjmenovat nedají.

Wiki se otevírá i jako samostatný vault. Jeho nastavení souborů musí být stejné jako ve vaultu repa, viz skill `pankostka-obsidian`.

## Frontmatter a tagy

`wiki/frontmatter` **Frontmatter nese `title`, `date` a `tags`.**

- `title` je název, který vidí uživatel v Power BI, tedy název tabulky nebo reportu bez předpony kostky (`DimÚčet`), u rozcestníku název modelu (`KostkaEKO`).
- `wiki/revision-date` `date` je datum poslední revize článku **člověkem** ve tvaru `RRRR-MM-DD`. AI ho vyplní při založení, člověk ho přepíše, když článek zreviduje. Čtenář z něj pozná, ke kterému dni text platí, a kontrola podle něj pozná, že se model změnil později. Datum souboru TMDL se nepoužívá: git data souborů neukládá, po klonu je v něm datum klonu.
- `tags` řadí článek do skupin.

`wiki/tags` **Tagy.** Podtržítko na začátku znamená *patří do*, tag bez podtržítka znamená *je to*. Názvy tagů jsou přesně názvy z modelu, bez předpony kostky.

| Článek | Tagy | Příklad |
| --- | --- | --- |
| kostka | `_<Kostka>` | `_KostkaEKO` |
| faktovka | `_<Kostka>`, `_<Faktovka>` | `_KostkaEKO`, `_FactDenik` |
| dimenze | `_<Kostka>`, `_<Faktovka>` za každou faktovku, do které patří, `<Dimenze>` | `_KostkaEKO`, `_FactDenik`, `DimÚčet` |
| report | `_<Kostka>`, `_<Faktovka>` za každou faktovku, ze které čerpá, `_Report` | `_KostkaEKO`, `_FactDenik`, `_Report` |
| údržba | `_<Kostka>`, `_<Faktovka>` za každou faktovku, které se týká, `Údržba` | `_KostkaAXMain`, `_FactVysledovka`, `Údržba` |

Dimenze patří do faktovky jen tehdy, když na ni vede skutečná vazba. Technická vazba, kde je klíč ve faktovce vždy `-1`, tag nedostává, v matici vazeb zůstane s poznámkou.

Tagy platí pro celý vault, ne pro jednu kostku. Stejná dimenze ve dvou kostkách má stejný tag, a to je záměr: tag `DimDatum` najde kalendář ve všech kostkách.

## Aktualizace

Pokyn **Aktualizuj wiki `<Kostka>`** (synonyma `Make wiki`, `Do wiki`) srovná wiki kostky s modelem. Napsaný slovy znamená zápis, tedy totéž co `/pankostka-powerbi-wiki <Kostka> --make`. Bez `--make` se jen vypíše, co by se udělalo.

`wiki/ai-edit-two-ways` **AI smí do existujícího článku zasáhnout jen dvěma způsoby.** Jinak ho nemění.

- **Drobná věcná oprava přímo v textu.** Přejmenovaný sloupec nebo míra, mrtvý odkaz, zastaralý název, jedno slovo. Každou opravu vypiš ve tvaru `soubor, řádek, před -> po`.
- **Návrh pro delší místo.** Odstavec, který je nesprávný, zavádějící, neúplný, zastaralý nebo v rozporu s jiným článkem. Původní odstavec **nech** a hned pod něj vlož callout:

  ```markdown
  > [!navrh-ai] Návrh AI
  > Přeformulovaný odstavec. Důvod: míra `Obrat` v modelu už není, nahradila ji `Obrat bez DPH`.
  ```

  Callout obsahuje navrhovaný text a **důvod**. Člověk návrh přijme tak, že smaže původní odstavec a hlavičku calloutu, a odmítne ho smazáním calloutu. Callouty `Návrh AI` smíš při dalším běhu přepsat nebo aktualizovat.

`wiki/no-edit-dirty` **Rozeditovaný článek.** Když má článek neuložené změny (`M` v `git status`), do jeho textu nezapisuj ani drobnosti a nespouštěj v něm `measures_table.py`. I drobnosti dej jako callout, aby se úpravy nesmíchaly v diffu s člověkovými.

Nenavrhuj čistě stylistické přeformulování a neměň `date` ve frontmatteru, protože značí revizi člověkem.

Postup:

1. **Projdi model kostky (TMDL) a její reporty (PBIR).** Zjisti viditelné faktovky, dimenze a reporty. Model čti přímo z TMDL, žádný mezikrok ani pomocný soubor nevytvářej.
2. **Spusť kontrolu** (viz Kontrola níže). Ukáže chybějící články, články navíc, zastaralé revize a tabulky ukazatelů, které neodpovídají modelu.
3. **Chybějící článek založ** podle osnovy v `outlines.md`. Podkladem jsou model, reporty, plnicí procedury a existující texty u kostky. Procedury čti proto, abys zjistil, kde se udržují podkladová data, ne abys popisoval SQL. Co z podkladů nevyčteš a do článku patří, označ na místě značkou `⚠️` s konkrétní otázkou. **Nedomýšlej si.** Do článku faktovky dej do sekce Ukazatele značky bloku a spusť `measures_table.py`.
4. **Existující článek zkontroluj proti modelu.** Drobné chyby oprav, delší místa navrhni calloutem, ostatní vypiš:
   - **model novější než revize**: první filtr, co procházet, ne nález sám o sobě,
   - **rozpor s modelem**: atribut, míra, vazba nebo stránka reportu, která v článku chybí nebo v modelu už není, a tag, který vazbám neodpovídá,
   - **porušení osnovy**: chybějící povinná sekce, sekce navíc, text, který do článku nepatří,
   - **nesrozumitelné místo**: věta, které uživatel bez znalosti skladu nerozumí,
   - **návrh doplnění**: co bys doplnil a proč, včetně zbylých značek `⚠️`.
5. **Tabulky ukazatelů aktualizuj** skriptem `measures_table.py`, jen v článcích, které nejsou rozeditované.
6. **Prvek, který z modelu zmizel, navrhni ke smazání**, přejmenovaný k přejmenování článku. Každý návrh potvrzuje člověk zvlášť a do potvrzení se nic nemění.
7. **Na konci vypiš nahoře**, které články jsi založil, seznam drobných oprav, vložené callouty a návrhy, které čekají na potvrzení. Pod to hlášení podle článků, v rámci článku od nejzávažnějšího.

## Co do wiki nepatří

`wiki/not-in-wiki`

- **Popis, jak je to udělané v SQL.** Uživatelská dokumentace mluví o datech, ne o procedurách.
- **Předávací dokumentace pro vývojáře**, tedy proč je něco udělané takhle, provoz, pasti a rozpracovanost. Patří k plnicí proceduře.
- **Skryté sloupce, skryté míry a pomocné tabulky.** Uživatel je v modelu nenajde.
- **Samozřejmosti.** Úplný seznam atributů s popisem, který jen opakuje název. Tabulka ukazatelů je výjimka, viz zásady.
- **Proměnlivé provozní údaje**, tedy čas posledního nápočtu, doba běhu, počty řádků a kdo report používá. Zastarají dřív, než je někdo přečte.

Wiki se převádí do HTML nástrojem [obsidian2html](https://github.com/pankostka/obsidian2html) celá a bez markeru publikace. HTML se neverzuje a leží mimo repo.

## Výjimka z pravidla

Vědomé porušení pravidla v článku zapiš HTML komentářem na řádek nálezu nebo na řádek nad ním. Komentář jmenuje identifikátor pravidla a za čárkou důvod: `<!-- pankostka: allow wiki/wikilink-alias, celý název je tu záměrně -->`. **Důvod je povinný**, bez něj skript nález hlásí dál. Nálezy, které se netýkají řádku článku (chybějící článek, revize starší než model), se výjimkou vyřadit nedají.

## Kontrola

Platí, jen když argument výše není prázdný. Prvním slovem argumentu je název kostky (adresář `Wiki<Kostka>/` a model `<Kostka>.SemanticModel` se najdou v aktuálním repu), nebo cesta k adresáři kostky.

1. **Spusť skript** s argumentem bez `--make`:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_wiki.py <Kostka>
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Skript nic nezapisuje. Výstup je jedna řádka na nález ve tvaru `soubor:řádek: [identifikátor] zpráva`:
   - `wiki/article-per-element`: viditelná tabulka nebo report bez článku,
   - `wiki/index-article`: chybí rozcestník,
   - `wiki/article-per-element`: článek s předponou kostky, ke kterému v modelu ani v reportech nic není (údržba s tagem `Údržba` se nehlásí),
   - `wiki/frontmatter`: chybí `title`, `date` nebo `tags`, `title` neodpovídá názvu v modelu,
   - `wiki/tags`: tagy neodpovídají druhu článku nebo vazbám v `relationships.tmdl`,
   - `wiki/outline`: chybí povinná sekce osnovy,
   - `wiki/revision-date`: poslední commit TMDL tabulky nebo PBIR reportu je novější než `date` článku,
   - `wiki/wikilink-alias`: wikilink na článek kostky bez aliasu,
   - `wiki/measures-table`: tabulka ukazatelů neodpovídá modelu, nebo článek faktovky značky nemá.

2. **Projdi články sám** podle kroku 4 postupu výše: rozpor textu s modelem, nesrozumitelná místa, technické vazby s klíčem vždy `-1`, zbylé značky `⚠️` a porušení zásady C.

3. **Bez `--make` nic nezapisuj.** Vypiš výsledek ve tvaru z kroku 7 postupu: co bys založil, opravil a navrhl. Na konec napiš, že zápis spustí `/pankostka-powerbi-wiki <Kostka> --make`, přesně v tomhle tvaru.

4. **S `--make`** proveď postup výše. Před zápisem ověř `git status` a rozeditované články nech jen s callouty. Mazání a přejmenování článků jen navrhni.
