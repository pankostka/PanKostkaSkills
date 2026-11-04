-- AND pod WHERE 1=1 odsazené jinak než WHERE se musí nahlásit jako [where-one-equals-one], celkem 5 neshod.

-- odsazené o čtyři mezery, dvě neshody
SELECT *
FROM dbo.Tabulka
WHERE 1=1
    AND Id = 1
    AND Nazev = 'x'

-- WHERE uvnitř CTE, AND odsazené víc než WHERE
;WITH a AS (
    SELECT Id
    FROM dbo.Tabulka
    WHERE 1=1
        AND Id > 0
)
SELECT * FROM a

-- OR se počítá stejně jako AND
SELECT * FROM dbo.Tabulka
WHERE 1=1
  OR Id = 2

-- 1=1 na samostatném řádku, AND musí být pod ním
SELECT * FROM dbo.Tabulka
WHERE
    1=1
AND Id = 1
