-- celkem 1
USE [HGFirmaOstra]
GO
CREATE OR ALTER PROCEDURE [lcs].[FirmaNSP_X]
	(@System_InputRecordNumber INT, @System_ResultRecordNumber INT OUTPUT)
AS
BEGIN
	RAISERROR('Chyba, zavolejte správce.', 18, 1)
END
GO
GRANT EXECUTE ON lcs.FirmaNSP_X TO Uzivatele;
GO
