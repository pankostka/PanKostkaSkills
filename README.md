# PanKostkaSkills

Pravidla, podle kterých píšu datové sklady a jejich dokumentaci, zabalená jako skilly pro Claude. Každý skill má dva režimy: bez argumentu jen načte zásady pro práci, s cestou k souboru nebo adresáři ji projde a vypíše neshody s návrhy úprav.

Obsah skillů je česky.

## Pluginy

| Plugin | Co dělá | Volání |
|---|---|---|
| `pankostka-tsql` | Zásady psaní T-SQL pro MS SQL Server a kontrola souborů `.sql` | `/pankostka-tsql [soubor \| adresář \| --changed]` |
| `pankostka-md` | Zásady psaní dokumentace v Markdownu a Obsidianu a kontrola souborů `.md` | `/pankostka-md [soubor \| adresář \| --changed]` |
| `pankostka-obsidian` | Vault v Obsidianu nad git repem: nastavení, co verzovat, šablona konfigurace, kontrola vaultu | `/pankostka-obsidian [adresář vaultu]` |
| `pankostka-powerbi` | Sémantický model a report Power BI v PBIP: TMDL, PBIR, názvy měr, DAX, field parameters, role. Kontrola modelu a mrtvých odkazů v reportech | `/pankostka-powerbi [adresář \| soubor.tmdl \| --changed]` |
| `pankostka-dwh` | Datový sklad v MS SQL Server: vrstvy stage, star a mart, pořadí plnění, struktura repa, jmenné konvence. Kontrola názvů procedur, odkazů mezi vrstvami a klíčů | `/pankostka-dwh [soubor \| adresář \| --changed]` |
| `pankostka-nephrite` | Databáze ERP Helios Nephrite: schéma `lcs`, datový model, vlastní tabulky, NSP procedury, formuláře, nasazení skriptů. Kontrola skriptů nasazovaných do Heliosu | `/pankostka-nephrite [soubor \| adresář \| --changed]` |
| `pankostka-tasks` | Adresář `tasks/` s rozpracovanými úkoly: rozcestník, článek na úkol, průběžný zápis, pomocné soubory, mazání po dokončení. Kontrola rozcestníku a článků | `/pankostka-tasks [adresář]` |
| `pankostka-powerbi` | Wiki kostky pro uživatele: článek na kostku, faktovku, dimenzi a report, tabulka ukazatelů z modelu. Kontrola wiki proti modelu, s `--make` zakládá a upravuje články | `/pankostka-powerbi-wiki [<Kostka> [--make]]` |

## Plánované skilly

Skilly postupně nahradí repo `_JDStandards` a jeho kopie `_Standards/` v projektech. Pořadí v tabulce je pořadí převodu. Po převodu všech souborů se `_JDStandards` archivuje.

| Plugin | Skill | Obsah | Zdroj |
|---|---|---|---|
| `pankostka-tsql` | `pankostka-tsql` | hotovo | `sql_JD.md` |
| `pankostka-md` | `pankostka-md` | hotovo | `dokumentace_JD.md`, část `dokumentace.md` |
| `pankostka-obsidian` | `pankostka-obsidian` | hotovo | `dokumentace.md`, šablona z `_JDStandards/.obsidian` |
| `pankostka-powerbi` | `pankostka-powerbi` | hotovo | `powerbi_JD.md`, obecná část Vrstvy 30 z `ProjektDWH/CLAUDE.md`, validátory z `ProjektDWH/00_common/pbi` |
| `pankostka-powerbi` | `pankostka-powerbi-wiki` | hotovo | `dwh_dokumentace_JD.md`, rozhodnutí o tabulce ukazatelů z `ProjektDWH/TODO 🌐.md`, `wiki_ukazatele.py` z `ProjektDWH/00_common/pbi` |
| `pankostka-dwh` | `pankostka-dwh` | hotovo, nesrovnalosti zdroje zatím převzaté beze změny | `ProjektDWH/CLAUDE.md`, `EMGDWH/CLAUDE.md`, pojmy DWH ze `slovnik_zkratek_JD.md` |
| `pankostka-nephrite` | `pankostka-nephrite` | hotovo | `helios_objekty_JD.md`, obecné části `EMGDWH/05_source_helios/CLAUDE.md` a `ProjektHelios/CLAUDE.md`, pojmy Heliosu ze `slovnik_zkratek_JD.md` |
| `pankostka-tasks` | `pankostka-tasks` | hotovo | `tasks_JD.md`, praxe v `tasks/` v ProjektDWH a EMGDWH |
| `pankostka-git` | `pankostka-git` | commit zpráva, kdy commitovat, jak volat git, kódování, hooky, sufixy `-VZOR`, `-DRAFT` a `-TMP` v názvech souborů a adresářů | `git_JD.md`, sufixy z `ProjektDWH/CLAUDE.md` |

Slovník zkratek se rozdělí podle domén do skillů `pankostka-nephrite`, `pankostka-dwh` a `pankostka-powerbi`, každý ho bude mít jako soubor, který čte jen při potřebě.

Mimo toto repo:

- `PanKostkaSkillsAD` a `PanKostkaSkillsEMG`: organizační pravidla, tedy zkratky společností, servery a databáze. Soukromá repa.
- `PanKostkaSkillsJD`: osobní prostředí (seznam vaultů, `PKVault`) a záznamy rozhodnutí z `_JDStandards/ProjektBIDoc/`. Soukromé repo.
- Git pravidla pro mě: `~/.claude/CLAUDE.md`, protože musí platit v každé session, ne jen na vyžádání.

Při převodu platí:

- Odkaz na `_Standards/*` v `CLAUDE.md` projektu se přepíše na skill, až když je skill hotový a ověřený. Do té doby platí obojí.
- Repo, které skilly používá, má v `.claude/settings.json` položky `extraKnownMarketplaces` a `enabledPlugins`. Kdo repo naklonuje, dostane nabídku instalace a pravidla mu nezmizí s koncem `_Standards/`.

## Instalace do Claude Code

Přidat marketplace a nainstalovat plugin:

```bash
claude plugin marketplace add pankostka/PanKostkaSkills
```

```bash
claude plugin install pankostka-tsql@pankostka
```

Totéž jde uvnitř session přes `/plugin`, kde se pluginy dají vybírat po jednom. Aktualizace:

```bash
claude plugin marketplace update pankostka
```

## Použití

Bez argumentu se skill načte sám, když Claude píše nebo upravuje soubor, kterého se týká. Ručně ho spustíš s cestou ke kontrole:

```
/pankostka-tsql 20_dim/nsp20DimUcet.sql
/pankostka-tsql 20_dim
/pankostka-tsql --changed
/pankostka-md docs
```

`--changed` zkontroluje jen soubory skillu (`.sql`, `.md` a přílohy), které git hlásí jako změněné nebo nové. Výsledkem je seznam neshod se soubory, řádky a návrhy oprav; nic se neopravuje bez odsouhlasení.

Zapisovat smí jen skill s přepínačem `--make`, dnes `pankostka-powerbi-wiki`: `/pankostka-powerbi-wiki KostkaEKO` jen vypíše, co by udělal, `/pankostka-powerbi-wiki KostkaEKO --make` články založí a upraví.

## Vývoj

Testy kontrolního skriptu:

```bash
python tests/pankostka-tsql/run.py
```

```bash
python tests/pankostka-md/run.py
```

```bash
python tests/pankostka-obsidian/run.py
```

```bash
python tests/pankostka-powerbi/run.py
```

```bash
python tests/pankostka-powerbi-wiki/run.py
```

```bash
python tests/pankostka-dwh/run.py
```

```bash
python tests/pankostka-nephrite/run.py
```

```bash
python tests/pankostka-tasks/run.py
```

Kontrola marketplace a pluginů:

```bash
claude plugin validate .
```
