---
name: pankostka-nephrite
description: Zásady pro databázi ERP Helios Nephrite (dříve Noris, LCS) - schéma lcs, datový model (třída, pořadač, cislo_subjektu a cislo_nonsubjektu, dynamické vztahy, valuace), vlastní tabulky bez cizích klíčů, NSP procedury jako funkce nad přehledem, formulářové šablony a přehledy, zákaz zápisu do systémových tabulek, nasazení skriptů do Heliosu (USE, víc databází, dump ze SSMS), dokumentační portál. Použij vždy, když čteš data z Heliosu, zakládáš nebo upravuješ objekt ve schématu lcs nebo píšeš skript, který se nasazuje do Heliosu. S argumentem (soubor, adresář nebo --changed) zkontroluje skripty proti zásadám a vypíše neshody.
argument-hint: "[soubor | adresář | --changed]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/check_nephrite.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_nephrite.py *)
---

# Helios Nephrite - objekty v databázi

Pravidla pro databázi Heliosu Nephrite (dříve Noris, LCS): jak jejímu datovému modelu rozumět při čtení a jak do ní zakládat objekty. Vycházejí z toho, jak je Helios čte a používá. Nejsou to preference, ale požadavky aplikace: když se poruší, obvykle nespadne build, ale uživateli přestane fungovat formulář nebo funkce nad přehledem.

Obecné zásady psaní T-SQL jsou ve skillu `pankostka-tsql` a platí i tady. Pojmy (`CS`, `CN`, `NSP`, pořadač, třída) jsou v `${CLAUDE_SKILL_DIR}/glossary.md`. Jak psát skripty, které se do Heliosu nasazují, je v `${CLAUDE_SKILL_DIR}/deployment.md`, čti ho před založením nebo úpravou takového skriptu.

Konkrétní databáze, servery, prefixy vlastních objektů a čísla objektů v Heliosu se liší zákazník od zákazníka. Sem nepatří, jejich místo je v `CLAUDE.md` repa nebo v repu organizace.

Argument: `$ARGUMENTS`

## Schéma lcs

`nephrite/schema-lcs` **Všechny objekty Heliosu žijí ve schématu `lcs`** a vlastní objekty se zakládají vedle systémových, do téhož schématu. Oddělené schéma pro vlastní věci není na výběr: Helios objekt v jiném schématu nenajde. Vlastní objekty se proto odlišují **prefixem** v názvu, který určuje repo.

**Schéma vždy uváděj**, tedy `lcs.adresa`, nikdy jen `adresa`. Bez schématu závisí výsledek na výchozím schématu přihlášeného uživatele, a to je jiné na serveru a jiné v SSMS.

**Systémové tabulky Nephrite se jmenují malými písmeny česky**: `lcs.adresa`, `lcs.subjekty`, `lcs.uhrady`. Není to `TabAdresa` jako v Helios Orange. Kdo přichází od Orange, hledá tabulky pod špatnými názvy a obvykle usoudí, že v databázi nejsou.

`nephrite/no-write-system` **Do systémových tabulek Heliosu se nezapisuje**: `lcs.subjekty`, `lcs.organizace`, `lcs.uhrady`, `lcs.poradace`, `lcs.qn_*` a další. Čti z nich, ale `INSERT`, `UPDATE` ani `DELETE` do nich neposílej. Helios si je udržuje sám a spoléhá na vlastní logiku, kterou z SQL nevidíš. Jedinou výjimkou jsou tabulky konfigurace přehledů, a i tam se sahá pouze na vlastní sloupce.

## Datový model

**Třída** je typ objektu v Heliosu, třeba "Faktury vydané": sada tabulek hlavička, položka a UDA, které k sobě patří. Definice třídy je v repository tabulce `lcs.nis_tridy`. **Pořadač** je číselná řada uvnitř třídy, rozlišená sloupcem `cislo_poradace`. Jedna třída může mít víc pořadačů, ale musí mít aspoň jeden, definice je v `lcs.poradace`. Neznámou třídu, třeba název tabulky v cizím SELECTu, jde přes obě repository tabulky dohledat bez přístupu do klienta Heliosu.

**Třídy jsou subjektové, nebo nonsubjektové, a od toho se odvíjí, jak se čtou.** Subjektová třída má primární klíč `cislo_subjektu` a duplicitní řádek navíc v `lcs.subjekty`. Proto k ní automaticky existuje sledování změn (kdo a kdy záznam pořídil) a `cislo_subjektu` je jednoznačné v celé databázi. Nonsubjektová třída má primární klíč `cislo_nonsubjektu` a v `lcs.subjekty` žádný odpovídající řádek nemá. Vlastní tabulky mají `cislo_nonsubjektu` právě proto, že jsou nonsubjektové.

**`lcs.subjekty.nazev_subjektu` je oříznuté na `varchar(40)`.** Třídy s delším názvem (třeba `lcs.organizace`) ho v plné délce drží ve vlastní tabulce. Pro plný název proto čti z konkrétní třídy, ne z metatabulky.

**Dynamické vztahy jsou vazba M:N mezi třídami, kterou může uživatel v Heliosu měnit.** Navazuje vztah mezi jedním záznamem a druhým, aniž by šlo o obyčejný cizí klíč v datech. Žijí v `lcs.vztahy_subjektu` (pro položky `lcs.objektsubjekt`): `cislo_subjektu` a `cislo_vztaz_subjektu` jsou dvě strany vztahu, `cislo_vztahu` určuje, mezi jakými třídami vztah je. Když v datech chybí vazba, kterou bys čekal jako cizí klíč, může být modelovaná takhle.

**Uložená hodnota sloupce a to, co vidí uživatel, se může lišit, hledej valuaci.** `lcs.attribute_valuation_entry` mapuje fyzickou hodnotu (třeba `'O'` ve sloupci `char(1)`) na popisek, který vidí uživatel (třeba `'OK'`). Bez kontroly téhle tabulky si stavový nebo příznakový sloupec můžeš vyložit špatně.

## Vlastní tabulky

`nephrite/own-table-pk` **Primární klíč je `cislo_nonsubjektu INT IDENTITY(1,1)`.** Je to **požadavek Heliosu**: bez něj se tabulka nedá napojit na přehled a uživatel se k datům nedostane. Ze stejného důvodu se sloupec nesmí jmenovat jinak.

`nephrite/no-fk` **Cizí klíče se na vlastní tabulky nedávají.** Vazba je jen sloupec a řeší se joinem. Helios do těch tabulek zapisuje sám a constraint by ho zablokoval, přičemž chyba se projeví až uživateli při ukládání formuláře. Kde to hrozí, patří do kódu poznámka, aby to někdo "nedodělal".

`nephrite/cs-cn-suffix` **Vazební sloupce nesou sufix `CS` nebo `CN`** podle toho, na jaký klíč ukazují: `CS` na `cislo_subjektu`, `CN` na `cislo_nonsubjektu`. Ze jména sloupce je pak vidět, do které tabulky se joinuje a přes co.

## NSP procedury

`nephrite/nsp-signature` Procedura, kterou uživatel spouští jako **funkci nad přehledem**, má povinnou signaturu a povinné chování. Signaturu dává Helios:

```sql
CREATE OR ALTER PROCEDURE [lcs].[<procedura>]
	(@System_InputRecordNumber INT, @System_ResultRecordNumber INT OUTPUT)
AS
BEGIN
SET NOCOUNT ON;
```

`nephrite/nsp-input-check` **`@System_InputRecordNumber` je `cislo_nonsubjektu` záznamu, nad kterým uživatel funkci pustil.** Procedura, která má běžet nad **celým** přehledem, musí spuštění nad jedním záznamem odmítnout. Jinak tiše zpracuje jediný řádek a uživatel si myslí, že přepočet proběhl celý:

```sql
IF ISNULL(@System_InputRecordNumber,0) <> 0
BEGIN
    RAISERROR('Nepouštějte na konkrétním záznamu! Klikněte prosím do rychlého filtru a pak na ikonku funkce.', 18, 1)
    RETURN
END
```

Procedura, která naopak **má** běžet nad jedním záznamem, má podmínku obrácenou. Parametry se nechávají i u procedur, které se z Heliosu zatím nespouští, aby se to dalo kdykoli zavést.

`nephrite/nsp-raiserror` **Chyby hlas přes `RAISERROR(..., 18, 1)` česky a s instrukcí, co má uživatel udělat.** Zprávu čte účetní, ne vývojář. U orchestračních procedur, které volají další procedury, do zprávy patří i to, co se **ne**provedlo a v jakém stavu data zůstala. Jinak uživatel neví, jestli může pokračovat, nebo musí volat.

`nephrite/nsp-try-catch` **Volání dalších procedur obal do `BEGIN TRY ... BEGIN CATCH`** s vlastním `RAISERROR`. Bez toho dostane uživatel systémovou chybu bez kontextu.

`nephrite/nsp-grant` **Na konci souboru udělení práv, každý `GRANT` s vlastním `GO`:**

```sql
GRANT EXECUTE ON lcs.<procedura> TO Uzivatele;
GO
GRANT EXECUTE ON lcs.<procedura> TO Admin;
GO
```

Bez toho funkce uživateli nepojede, i když je v Heliosu správně nadefinovaná. Chyba se projeví až u uživatele, protože vývojář bývá v roli, která práva má.

Konec procedury komentuj `END --KONEC PROCEDURY`.

## Formulářové šablony a přehledy

`nephrite/form-select` **Editační formulář a přehled se v Heliosu definují SELECTem, ne kódem.** Ten SELECT je součástí dodávky, takže patří do repa. V databázi ho jinak nikdo nenajde a při nasazení do další firmy se píše znovu.

**Vzor je `SELECT ... FROM lcs.<tabulka> pk ... WHERE pk.cislo_nonsubjektu = :cislo_nonsubjektu`.** Dvojtečkový parametr doplňuje Helios, není to T-SQL a v SSMS to samo nepojede.

**Pro každou vazbu se vedle klíče vrací dva doplňkové sloupce:** `<Sloupec>_refer` (reference nebo číslo, které uživatel vidí) a `<Sloupec>_nazev` (název). Pojmenování je konvence Heliosu, neměň ho, formulář se na ně odkazuje jménem.

**Šířky a formáty sloupců přehledu jsou data**, ne definice. Sedí v systémové tabulce konfigurace přehledů `lcs.noris_gs_main` (`cislo_sablony`, `colwidth`, `sl_format_net`), `colwidth = -1` znamená skrytý sloupec. `nephrite/grid-own-columns` **`UPDATE` nad nimi vždy omez na vlastní sloupce**: vzor s `and expression like '%where 1=1%'` je tam právě proto, aby nešlo přepsat systémové sloupce šablony. Bez toho omezení se přepíše i to, co patří Heliosu, a přehled se rozbije všem.

## Adresáti mailů

`nephrite/mail-categories` **Adresáty ber z kategorií Heliosu, ne z natvrdo napsaných adres.** `lcs.zamestnanci` -> `lcs.subjekt_hledspec` (`cislo_subjektu`) -> `lcs.kategorie` (`cislo_selected` = `cislo_kategorie`), s filtrem `datum_uk_prace is null` a `e_mail is not null`. Seznam lidí se pak udržuje v Heliosu bez zásahu do kódu. Háček, který je potřeba říct uživateli: **kategorie řídí i práva**, takže změna práv tiše změní adresáty. `lcs.categories` je jen pohled nad `lcs.kategorie`, používej tabulku.

## Změny existujících objektů

`nephrite/no-rename` **Objekty ani sloupce nepřejmenovávej a neodstraňuj bez potvrzení.** V Heliosu na nich visí přehledy, formulářové šablony a definice funkcí, které se na ně odkazují **jménem**. Rozbijí se tiše: nespadne build, ale uživateli spadne formulář. Mezi změnou a jejím projevem můžou uběhnout týdny, protože se to pozná až ve chvíli, kdy někdo tu funkci pustí.

## Dokumentace Heliosu

**Oficiální nápověda Heliosu Nephrite je dokumentační portál** `https://public.helios.eu/nephrite/doc/cs/index.php?title=Hlavní_strana` (MediaWiki, česky). Než hádáš, co tabulka, třída nebo funkce dělá, podívej se tam. Jsou v něm popisy aplikačních modulů, novinky po verzích a popisy tříd s čísly (`Popis třídy:Dopravní prostředek (108)`).

**Portál vyžaduje přihlášení, takže `WebFetch` nefunguje**, vrací jen `Vyžadováno přihlášení`. Čti ho v prohlížeči, kde je uživatel přihlášený, typicky přes Claude in Chrome. **Než sáhneš na nápovědu, ověř, že je prohlížeč připojený. Když není, řekni uživateli, ať ho pustí, a nehádej obsah z hlavy.** Heslo do přihlašovacího formuláře nezadávej, ani když je veřejné, přihlášení je na uživateli.

Vzory URL:

- článek: `.../index.php?title=<Název_stránky>` (mezery jako `_`, diakritika URL-encoded),
- fulltext: `.../index.php?title=Speciální:Hledání&search=<dotaz>&fulltext=1`.

`nephrite/portal-no-copy` **Obsah portálu je licenčně omezený** (jen pro zaměstnance, zákazníky a partnery dodavatele Heliosu). Necituj ho do commitů ani na veřejná místa a nekopíruj do repa. Stačí odkaz na stránku a vlastními slovy, co z ní plyne.

## Výjimka z pravidla

Vědomé porušení pravidla zapiš komentářem na řádek nálezu nebo na řádek nad ním. Komentář jmenuje identifikátor pravidla a za čárkou důvod:

```sql
-- pankostka: allow nephrite/no-write-system, oprava dat schválená dodavatelem Heliosu
UPDATE lcs.organizace SET nazev_subjektu = 'X' WHERE cislo_subjektu = 1
```

Identifikátorů může být víc, oddělených čárkou. **Důvod je povinný**, bez něj skript nález hlásí dál.

## Kontrola

Platí, jen když argument výše není prázdný. Argument je soubor `.sql`, adresář (prochází se rekurzivně), nebo `--changed` pro soubory `.sql`, které git hlásí jako změněné nebo nové. Kontroluj jen skripty, které se nasazují do Heliosu, ne dotazy datového skladu, které z Heliosu jen čtou.

1. **Spusť skript** s argumentem beze změny:

   ```
   python ${CLAUDE_SKILL_DIR}/scripts/check_nephrite.py $ARGUMENTS
   ```

   Když `python` neexistuje, použij `python3`. Skript spouštěj přes Bash, ne přes PowerShell: v PowerShellu volání padá na chybě `The command line is too long`. Výstup je jedna řádka na neshodu ve tvaru `soubor:řádek: [identifikátor] zpráva`, řádek s výjimkou `pankostka: allow` a důvodem se nehlásí. Pravidla:
   - `nephrite/schema-lcs`: objekt založený mimo schéma `lcs`,
   - `nephrite/use-header`: skript zakládá objekt, ale nezačíná `USE`,
   - `nephrite/nsp-input-check`: procedura s `@System_InputRecordNumber` bez kontroly toho parametru,
   - `nephrite/nsp-raiserror`: NSP procedura bez `RAISERROR(..., 18, 1)`,
   - `nephrite/nsp-grant`: NSP procedura bez `GRANT EXECUTE`,
   - `nephrite/own-table-pk`: vlastní tabulka bez `cislo_nonsubjektu INT IDENTITY`,
   - `nephrite/no-fk`: vlastní tabulka s cizím klíčem,
   - `nephrite/no-write-system`: zápis do systémové tabulky ze seznamu výše,
   - `nephrite/grid-own-columns`: `UPDATE lcs.noris_gs_main` bez omezení na vlastní sloupce,
   - `nephrite/clean-dump`: zbytek dumpu ze SSMS `/****** Object: ... ******/`.

   Soubory a adresáře se sufixem `-TMP` skript přeskočí.

2. **Projdi soubory sám** na to, co skript nepozná: `nephrite/no-write-system` u tabulek mimo seznam, `nephrite/nsp-raiserror` (zpráva bez instrukce pro uživatele), `nephrite/nsp-try-catch`, `nephrite/form-select` (doplňkové sloupce `_refer` a `_nazev`), `nephrite/cs-cn-suffix` a pravidla z `deployment.md` (`nephrite/one-file-all-dbs`, `nephrite/ddl-spadni`, `nephrite/select-before-update`). Kódování a `CREATE OR ALTER` kontroluje `pankostka-tsql`.

3. **Vypiš výsledek** po souborech, u každé neshody identifikátor pravidla a konkrétní návrh opravy, na konci souhrn.

4. **Nic neopravuj**, dokud uživatel opravy neodsouhlasí. Nikdy netvrď, že je skript nasazený, jen protože je v repu.
