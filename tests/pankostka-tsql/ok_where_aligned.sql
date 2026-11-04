-- AND zarovnané pod WHERE 1=1 je v pořádku, žádná neshoda.

SELECT *
FROM dbo.Tabulka
WHERE 1=1
AND Id = 1
--AND Nazev = 'x'

AND Datum >= '20260101'
GROUP BY Id

-- WHERE uvnitř CTE, AND na úrovni WHERE
;WITH a AS (
    SELECT Id
    FROM dbo.Tabulka
    WHERE 1=1
    AND Id > 0
)
SELECT * FROM a

-- řádky uvnitř závorek se nekontrolují
SELECT * FROM dbo.Tabulka
WHERE 1=1
AND (Id = 1
    OR Id = 2)
AND Nazev IN (
        SELECT Nazev FROM dbo.Jina
    )

-- tabulátor se počítá jako čtyři mezery
IF 1=1 BEGIN
	SELECT * FROM dbo.Tabulka
	WHERE 1=1
    AND Id = 1
END --END Konec TABULÁTOR

-- 1=1 na samostatném řádku, AND pod ním
SELECT * FROM dbo.Tabulka
WHERE
    1=1
    AND Id = 1

-- jednořádkový zápis nemá co zarovnávat
SELECT * FROM dbo.Tabulka WHERE 1=1 AND Id = 1
