-- Jediná podmínka celá na řádku s WHERE se nehlásí, i bez 1=1.

SELECT * FROM dbo.Tabulka WHERE Id = 1

-- víceřádkový dotaz, ale podmínka je jediná a na jednom řádku
SELECT Spol
FROM dbo.configHeliosDB
WHERE SourceSRV IS NOT NULL
ORDER BY Spol

-- řada UNION ALL
SELECT * FROM (
    SELECT Id FROM s20.DimZdroj_AD WHERE DimZdrojID <> -1
    UNION ALL
    SELECT Id FROM s20.DimZdroj_AV WHERE DimZdrojID <> -1
) subs

-- BETWEEN ... AND není složená podmínka
SELECT * FROM dbo.Tabulka WHERE Datum BETWEEN '20260101' AND '20261231'

-- další klauzule na stejném řádku
SELECT * FROM dbo.Tabulka WHERE Id > 0 ORDER BY Id

-- AND uvnitř řetězce ani komentáře se nepočítá
SELECT * FROM dbo.Tabulka WHERE Nazev = 'A AND B' -- AND Id = 1

UPDATE dbo.Tabulka SET Nazev = 'y' WHERE Id = 2

-- s 1=1 je v pořádku vždy
SELECT * FROM dbo.Tabulka WHERE 1=1 AND Id = 1
SELECT * FROM dbo.Tabulka
WHERE
    1=1
    AND Id = 1
