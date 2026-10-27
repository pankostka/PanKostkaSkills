-- celkem 4
SELECT d.DenikKc
FROM s20.FactDenik AS d
RIGHT JOIN s20.DimUcet AS u ON u.DimUcetID = d.DimUcetID
RIGHT JOIN s20.DimUtvar AS t ON t.DimUtvarID = d.DimUtvarID -- komentář bez zdůvodnění
RIGHT JOIN s20.DimMena AS m ON m.DimMenaID = d.DimMenaID -- pankostka: allow tsql/no-right-join
RIGHT JOIN s20.DimOrg AS o ON o.DimOrgID = d.DimOrgID -- pankostka: allow tsql/no-inner-outer, jiné pravidlo
