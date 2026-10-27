-- celkem 1
USE [HGFirmaOstra]
GO
CREATE OR ALTER PROCEDURE [lcs].[FirmaNSP_X]
	(@System_InputRecordNumber INT, @System_ResultRecordNumber INT OUTPUT)
AS
BEGIN
IF ISNULL(@System_InputRecordNumber,0) <> 0
BEGIN
    RAISERROR('Nepouštějte na konkrétním záznamu!', 16, 1)
    RETURN
END
END
GO
GRANT EXECUTE ON lcs.FirmaNSP_X TO Uzivatele;
GO
