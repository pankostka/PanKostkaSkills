-- celkem 3
USE [HGFirmaOstra]
GO
CREATE OR ALTER PROCEDURE [lcs].[FirmaNSP_Bez]
	(@System_InputRecordNumber INT, @System_ResultRecordNumber INT OUTPUT)
AS
BEGIN
	RAISERROR('Chyba.', 16, 1)
END
