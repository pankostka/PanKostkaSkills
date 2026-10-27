-- Vzor: název objektu je vše před první pomlčkou. Zmínka o s20.DimMena v komentáři se nepočítá.
CREATE OR ALTER PROCEDURE nsp10HN_Mena AS
BEGIN
	DECLARE @sql nvarchar(max) = '
		DROP TABLE IF EXISTS s10HN_AX.Mena
		SELECT m.Kod --cílová dimenze je s20.DimMena
		INTO s10HN_AX.Mena
		FROM openquery(HELIOS, ''select * from TabKodMen'') AS m
	'
	EXEC (@sql)
END
