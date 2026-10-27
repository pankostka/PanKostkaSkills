-- Joiny bez nadbytečných slov a výjimky, které se nehlásí.
SELECT d.DenikKc
FROM s20.FactDenik AS d
JOIN s20.DimUcet AS u ON u.DimUcetID = d.DimUcetID
LEFT JOIN s20.DimUtvar AS t ON t.DimUtvarID = d.DimUtvarID
FULL JOIN s20.DimMena AS m ON m.DimMenaID = d.DimMenaID
CROSS JOIN s20.DimSpol AS s
INNER HASH JOIN s20.DimOrg AS o ON o.DimOrgID = d.DimOrgID
RIGHT JOIN s20.DimZdroj AS z ON z.DimZdrojID = d.DimZdrojID -- RIGHT JOIN záměrně: všechny zdroje i bez zápisu
OUTER APPLY (SELECT TOP 1 k.Kurz FROM s20.FactKurz AS k) AS k
-- INNER JOIN v komentáři se nehlásí, RIGHT JOIN taky ne
WHERE d.Popis <> 'LEFT OUTER JOIN v řetězci'
