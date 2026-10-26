-- Každý WHERE bez 1=1 se musí nahlásit jako [where], celkem 3 neshody.
SELECT * FROM dbo.Tabulka WHERE Id = 1

SELECT *
FROM dbo.Tabulka
WHERE
    Id = 1
    AND Nazev = 'x'

UPDATE dbo.Tabulka SET Nazev = 'y' WHERE 1=2

-- tohle je v pořádku a hlásit se nesmí
SELECT * FROM dbo.Tabulka WHERE 1=1 AND Id = 1
SELECT * FROM dbo.Tabulka
WHERE
    1=1
    AND Id = 1
