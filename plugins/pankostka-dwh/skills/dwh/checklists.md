# Checklisty

Doplněk skillu `pankostka-dwh`. Na závěr každého postupu shrň, co se změnilo a co je potřeba ručně nasadit.

## Přidat dimenzi

Sáhne to do několika souborů napříč vrstvami. Projdi všechny:

1. `10_stage/<zdroj>/`: stage tabulka a její plnění, pokud zdroj chybí.
2. `20_dim/dim<Entita>.sql`: DDL včetně řádku `Key = -1`.
3. `20_dim/`: plnicí procedura, doplnit její zavolání do `nsp20Dim_RUN.sql`.
4. `20_fact/`: přidat cizí klíč do dotčených faktovek a doplnit lookup v jejich plnění.
5. `30_mart/<Kostka>/pbip/`: tabulka do TMDL modelu, vazba na faktovku, kardinalita, směr filtrování, `sortByColumn`, skrytí klíčů. Konvence modelu jsou ve skillu `pankostka-powerbi`.
6. Dokumentace: článek dimenze ve `Wiki<Kostka>/`, viz skill `pankostka-powerbi-wiki`, případně `docs/`.

## Přidat míru do faktovky

1. Sloupec do DDL faktovky.
2. Doplnit do plnicí procedury.
3. Do TMDL modelu, s `formatString` a display folderem.

Fyzicky se do faktovky ukládá jen hrubá hodnota na úrovni zrnitosti (například `DenikKc`). Skutečné míry (`MD`, `DAL`, `Obrat`) se nikdy neukládají jako sloupec, počítají se výhradně jako DAX v sémantickém modelu.
