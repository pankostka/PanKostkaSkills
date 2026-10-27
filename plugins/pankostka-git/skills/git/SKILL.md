---
name: pankostka-git
description: Zásady práce s gitem - commit zpráva bez dvojitých uvozovek a její předání shellu (PowerShell souborem bez BOM, Bash heredocem), kdy commitovat a pushovat, git příkazy po jednom, UTF-8 bez BOM, sufixy -VZOR, -DRAFT a -TMP v názvech souborů a adresářů, .gitignore pro -TMP, verzované hooky. Použij vždy, když commituješ, pushuješ, píšeš commit zprávu, pojmenováváš soubor se sufixem nebo upravuješ .gitignore. S argumentem (adresář repa) zkontroluje repo a vypíše neshody.
argument-hint: "[adresář repa]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_git.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_git.py *)
---

# Git - zásady

Jak se změna dostane do gitu bez úhony. Velká část pravidel je vázaná na **PowerShell 5.1 na Windows**, protože právě tam se láme kódování a uvozování. V Bashi většina těch pastí není. Co se v dokumentaci a commit zprávách *píše* (jazyk, styl, znaky), řeší skill `pankostka-md`.

Argument: `$ARGUMENTS`

## Commit zpráva

V commit zprávě **nepoužívej dvojité uvozovky** (`"`). PowerShell 5.1 při předávání víceřádkového textu nativnímu programu vložené uvozovky rozbije, git pak text za nimi bere jako cesty a commit spadne na `error: pathspec ... did not match`. Diakritika projde v pořádku, problém dělají jen uvozovky. Když je potřeba něco odlišit, použij `zpětné apostrofy` nebo jednoduchý apostrof (`'`). Typografické uvozovky nejsou řešení, ty zakazuje `pankostka-md`.

**Syntaxe víceřádkového textu se musí trefit se shellem, ve kterém příkaz spouštíš.** PowerShell má here-string `@'...'@`, Bash má heredoc (`git commit -F - <<'EOF' ... EOF`). Když se to zamění, druhý shell to nebere jako uvozovací značku a strčí ji doslova do textu: commit projde, ale zpráva začíná `@` nebo `EOF`. Nejspolehlivější je předat zprávu přes `-F`, protože ji pak neparsuje shell ani git jako argument. V PowerShellu ale **souborem**, ne rourou na stdin, viz další odstavec.

**V PowerShellu předávej commit zprávu souborem, ne rourou.** Konstrukce `@'...'@ | git commit -F -` přidá na začátek zprávy **BOM** (`EF BB BF`): PowerShell 5.1 kóduje rouru do nativního programu podle `[Console]::OutputEncoding`, a to bývá UTF-8 **s** tříbajtovým preamblem. Na `$OutputEncoding` se nespoléhej, ten preamble mít nemusí a stejně nerozhoduje. Subject commitu pak začíná neviditelným znakem, `git log --oneline` ukáže znak před textem a hledání commitu podle prvního slova nic nenajde. Roura navíc překlopí konce řádků na CRLF. Zprávu proto zapiš do souboru jako UTF-8 bez BOM a předej cestu:

```powershell
[System.IO.File]::WriteAllText($f, $msg, (New-Object System.Text.UTF8Encoding($false)))
git commit -F $f
```

V Bashi problém není, tam heredoc do `git commit -F -` projde čistě.

## Kdy commitovat

**Hotovou změnu rovnou commitni a pushni**, neptej se předem. Platí jedna změna = jeden commit: přidávej do commitu jen soubory, kterých se zadání týkalo, ostatní rozeditované nech být. Výsledek pak shrň: co je v commitu a co jsi nechal stranou. Neplatí to pro věci, které se běžně nevrací zpátky: `git push --force`, `git reset --hard`, přepis už odeslané historie, mazání větví. Tam se zeptej.

**Změna, přidání nebo smazání doby běhu u procedury nepotřebuje samostatný commit.** Kvůli jednomu řádku se zanáší historie. Je to výjimka z pravidla jedna změna = jeden commit. Soubor, ve kterém se změnila jen doba běhu, do commitu nepřidávej. Sveze se s dalším commitem, který sáhne na tentýž soubor.

## Jak volat git

**Git příkazy spouštěj po jednom volání**: zvlášť `git add`, zvlášť `git commit`, zvlášť `git push`. Slepené středníkem nebo `&&` do jednoho volání jsou pokaždé unikátní řetězec, netrefí se do permission pravidel a na každý commit vyskočí potvrzovací dialog.

## Kódování souborů

**Textové soubory piš v UTF-8 bez BOM.** BOM je neviditelný, takže se neohlásí chybou, ale důsledkem. U commit zprávy posune subject o tři bajty. Jinde se projeví tak, že se soubor tváří jako změněný, i když se v něm nic nezměnilo, nebo že nástroj načte první řádek i s tou hlavičkou. Když formát vyžaduje něco jiného, drž se formátu: to je výjimka, ne volba.

## Sufixy v názvech

Za pomlčkou na konci názvu souboru nebo adresáře může následovat jeden z těchto sufixů. **Jiné nepoužívej.**

- **`-VZOR`**: referenční implementace, kopíruj ji při zakládání podobného objektu.
- **`-DRAFT`**: neověřeno, není v produkci. Nicméně je v gitu.
- **`-TMP`**: dočasný soubor nebo adresář mimo git, tedy poznámky, testovací dotazy, cizí kód pro inspiraci. Používat ho můžeš, ale jen pokud není moc velký.

**Sufix na konci názvu adresáře platí pro všechny soubory uvnitř.**

**Název objektu (procedury, tabulky, reportu) je vše před první pomlčkou**: `nsp10HN_Denik-VZOR.sql` obsahuje proceduru `nsp10HN_Denik`. Pomlčka je proto vyhrazená pro sufixy a jako oddělovač slov v názvu objektu se nepoužívá. Kde repo pojmenování s pomlčkou zavedlo (třeba reporty `<Mart>-<Téma>`), drž se repa.

## Co do gitu nepatří

**Sufix `-TMP` v názvu vyřadí soubor z verzování.** V `.gitignore` jsou potřeba dva vzory:

```gitignore
*-TMP.*
*-TMP
```

Druhý vzor sedí na název, který sufixem opravdu končí, a to včetně adresářů: `Grafika-TMP/` pokryje i s obsahem, protože vzor bez lomítka platí na soubory i adresáře. První vzor je tam kvůli souborům s příponou: `logo_zapeceno-TMP.svg` končí na `.svg`, ne na `-TMP`, takže by ho druhý vzor minul. Řádek `*-TMP/` navíc nic nepokrývá. Když už v `.gitignore` je, škodit nebude, ale nutný není.

**Hesla, tokeny, klíče a connection stringy s přihlašovacími údaji** do gitu nepatří nikdy, patří do konfigurace mimo repo. Název serveru a databáze ano.

## Hooky

**Verzovaný hook se sám nespustí.** Git spouští jen to, co leží v `.git/hooks`, a ten adresář se neverzuje. Hook proto patří do `hooks/` v repu a na každém stroji se jednou zapne `git config core.hooksPath hooks`. Dokud to nikdo neudělá, hook mlčí a nikdo si nevšimne, že kontrola neběží. Proto ta instalační řádka patří do hlavičky samotného hooku nebo do `README.md`. Přeskočit hook jednorázově jde přes `git commit --no-verify`, ale jen když o to uživatel výslovně požádá.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je adresář repa.

1. **Spusť skript** s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_git.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Výstup je jedna řádka na neshodu ve tvaru `soubor:řádek: [pravidlo] zpráva`. Pravidla:
   - `gitignore`: `.gitignore` neignoruje soubor nebo adresář se sufixem `-TMP`,
   - `tracked`: git verzuje soubor se sufixem `-TMP`,
   - `suffix`: sufix z velkých písmen, který není `-VZOR`, `-DRAFT` ani `-TMP`,
   - `bom`: textový soubor v gitu s BOM,
   - `message`: commit z posledních 50 se subjectem, který začíná BOM, `@` nebo `EOF`,
   - `hooks`: repo má adresář `hooks/`, ale `core.hooksPath` na něj nemíří.

2. **Projdi repo sám** na to, co skript nepozná: hesla a connection stringy v souborech, velké soubory `-TMP`, které by stálo za to uklidit, commity s víc změnami najednou.

3. **Vypiš výsledek** s konkrétním návrhem u každé neshody a souhrnem na konci.

4. **Nic neopravuj**, dokud uživatel neodsouhlasí. Přepis historie kvůli rozbité commit zprávě nenavrhuj u commitů, které už jsou pushnuté.
