-- celkem 3
SELECT d.DenikKc
FROM s20.FactDenik AS d
INNER JOIN s20.DimUcet AS u ON u.DimUcetID = d.DimUcetID
LEFT OUTER JOIN s20.DimUtvar AS t ON t.DimUtvarID = d.DimUtvarID
FULL OUTER JOIN s20.DimMena AS m ON m.DimMenaID = d.DimMenaID
