# PanKostkaSkills

Pravidla, podle kterých píšu datové sklady a jejich dokumentaci, zabalená jako skilly pro Claude. Každý skill má dva režimy: bez argumentu jen načte zásady pro práci, s cestou k souboru nebo adresáři ji projde a vypíše neshody s návrhy úprav.

Obsah skillů je česky.

## Pluginy

| Plugin | Co dělá | Volání |
|---|---|---|
| `tsql` | Zásady psaní T-SQL pro MS SQL Server a kontrola souborů `.sql` | `/tsql:tsql [soubor \| adresář \| --changed]` |

## Instalace do Claude Code

Přidat marketplace a nainstalovat plugin:

```bash
claude plugin marketplace add pankostka/PanKostkaSkills
```

```bash
claude plugin install tsql@pankostka
```

Totéž jde uvnitř session přes `/plugin`, kde se pluginy dají vybírat po jednom. Aktualizace:

```bash
claude plugin marketplace update pankostka
```

## Použití

Bez argumentu se skill načte sám, když Claude píše nebo upravuje SQL. Ručně ho spustíš s cestou ke kontrole:

```
/tsql:tsql 20_dim/nsp20DimUcet.sql
/tsql:tsql 20_dim
/tsql:tsql --changed
```

`--changed` zkontroluje jen soubory `.sql`, které git hlásí jako změněné nebo nové. Výsledkem je seznam neshod se soubory, řádky a návrhy oprav; nic se neopravuje bez odsouhlasení.

## Vývoj

Testy kontrolního skriptu:

```bash
python tests/tsql/run.py
```

Kontrola marketplace a pluginů:

```bash
claude plugin validate .
```
