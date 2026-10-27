-- celkem 2
SELECT d.DenikKc
FROM s20.FactDenik AS d
RIGHT JOIN s20.DimUcet AS u ON u.DimUcetID = d.DimUcetID
RIGHT JOIN s20.DimUtvar AS t ON t.DimUtvarID = d.DimUtvarID -- komentář bez zdůvodnění
