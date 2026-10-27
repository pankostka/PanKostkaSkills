-- celkem 4
CREATE OR ALTER PROCEDURE nsp10X_A AS
BEGIN
	SELECT a.Kod FROM s20.DimA AS a
	DECLARE @sql nvarchar(max) = 'SELECT * FROM s30EKO.FactB'
	-- komentář s s30EKO.FactB se nepočítá
END
