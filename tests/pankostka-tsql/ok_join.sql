-- Joiny bez nadbytečných slov a výjimky, které se nehlásí.
SELECT d.DenikKc
FROM s20.FactDenik AS d
JOIN s20.DimUcet AS u ON u.DimUcetID = d.DimUcetID
LEFT JOIN s20.DimUtvar AS t ON t.DimUtvarID = d.DimUtvarID
FULL JOIN s20.DimMena AS m ON m.DimMenaID = d.DimMenaID
CROSS JOIN s20.DimSpol AS s
INNER HASH JOIN s20.DimOrg AS o ON o.DimOrgID = d.DimOrgID
RIGHT JOIN s20.DimZdroj AS z ON z.DimZdrojID = d.DimZdrojID -- pankostka: allow tsql/no-right-join, všechny zdroje i bez zápisu
OUTER APPLY (SELECT TOP 1 k.Kurz FROM s20.FactKurz AS k) AS k
-- INNER JOIN v komentáři se nehlásí, RIGHT JOIN taky ne
-- pankostka: allow tsql/no-inner-outer, výjimka na řádku nad nálezem
LEFT OUTER JOIN s20.DimZak AS k2 ON k2.DimZakID = d.DimZakID
WHERE d.Popis <> 'LEFT OUTER JOIN v řetězci'
