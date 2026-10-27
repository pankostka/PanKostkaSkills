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

## Plánované skilly

Skilly postupně nahradí repo `_JDStandards` a jeho kopie `_Standards/` v projektech. Pořadí v tabulce je pořadí převodu. Po převodu všech souborů se `_JDStandards` archivuje.

| Plugin | Skill | Obsah | Zdroj |
|---|---|---|---|
| `pankostka-tsql` | `pankostka-tsql` | hotovo | `sql_JD.md` |
| `pankostka-md` | `pankostka-md` | hotovo | `dokumentace_JD.md`, část `dokumentace.md` |
| `pankostka-obsidian` | `pankostka-obsidian` | hotovo | `dokumentace.md`, šablona z `_JDStandards/.obsidian` |
| `pankostka-powerbi` | `pankostka-powerbi` | hotovo | `powerbi_JD.md`, obecná část Vrstvy 30 z `ProjektDWH/CLAUDE.md`, validátory z `ProjektDWH/00_common/pbi` |
| `pankostka-powerbi` | `pankostka-powerbi-wiki` | dokumentace modelu pro uživatele, `Wiki<Kostka>/`, osnovy článků, postup aktualizace. Jako jediný skill do souborů zapisuje | `dwh_dokumentace_JD.md` |
| `pankostka-dwh` | `pankostka-dwh` | vrstvy 10/20/30, pořadí plnění, jmenné konvence, `Key = -1` | `ProjektDWH/CLAUDE.md`, `EMGDWH/CLAUDE.md` |
| `pankostka-nephrite` | `pankostka-nephrite` | objekty v Heliosu: schéma `lcs`, vlastní tabulky, NSP procedury, formuláře, pojmy Heliosu | `helios_objekty_JD.md` |
| `pankostka-tasks` | `pankostka-tasks` | adresář `tasks/`, rozcestník, článek na úkol, průběžný zápis, mazání po dokončení | `tasks_JD.md` |
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

Kontrola marketplace a pluginů:

```bash
claude plugin validate .
```
