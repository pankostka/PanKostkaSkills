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
| `pankostka-git` | Práce s gitem: commit zpráva a její předání shellu, kdy commitovat, kódování, sufixy `-VZOR`, `-DRAFT` a `-TMP`, hooky. Kontrola `.gitignore`, sufixů, BOM a commit zpráv | `/pankostka-git [adresář repa]` |
| `pankostka-powerbi` | Wiki kostky pro uživatele: článek na kostku, faktovku, dimenzi a report, tabulka ukazatelů z modelu. Kontrola wiki proti modelu, s `--make` zakládá a upravuje články | `/pankostka-powerbi-wiki [<Kostka> [--make]]` |

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

```bash
python tests/pankostka-git/run.py
```

Kontrola marketplace a pluginů:

```bash
claude plugin validate .
```

## Licence

[MIT](LICENSE). Obsah skillů i skripty je možné volně používat, upravovat a šířit, jen se zachováním informace o autorovi a licenci.
