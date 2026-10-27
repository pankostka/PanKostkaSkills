-- Víceřádkový nebo složený WHERE bez 1=1 se musí nahlásit jako [where], celkem 5 neshod.

-- podmínka začíná až na dalším řádku
SELECT *
FROM dbo.Tabulka
WHERE
    Id = 1
    AND Nazev = 'x'

-- složená podmínka na jednom řádku
SELECT * FROM dbo.Tabulka WHERE Id = 1 AND Nazev = 'x'

-- OR na jednom řádku
SELECT * FROM dbo.Tabulka WHERE Id = 1 OR Id = 2

-- pokračování na dalším řádku přes AND
SELECT * FROM dbo.Tabulka
WHERE Id = 1
    AND Nazev = 'x'

-- jediná podmínka, ale přes víc řádků v závorce
SELECT * FROM dbo.Tabulka
WHERE Id IN (
    SELECT Id FROM dbo.Jina
)
