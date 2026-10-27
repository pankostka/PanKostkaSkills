USE [HGFirmaOstra] -- SQLSRV1
--USE [HGFirmaTest]
GO
/*
POPIS
  Vzorová NSP procedura. Zmínka o /****** v komentáři bez slova Object se nehlásí.
*/
CREATE OR ALTER PROCEDURE [lcs].[FirmaNSP_Test]
	(@System_InputRecordNumber INT, @System_ResultRecordNumber INT OUTPUT)
AS
BEGIN
SET NOCOUNT ON;

IF ISNULL(@System_InputRecordNumber,0) <> 0
BEGIN
    RAISERROR('Nepouštějte na konkrétním záznamu! Klikněte do rychlého filtru.', 18, 1)
    RETURN
END

DROP TABLE IF EXISTS #x
CREATE TABLE #x (ID INT)
SELECT o.cislo_subjektu INTO #o FROM lcs.organizace AS o
-- UPDATE lcs.organizace v komentáři se nehlásí
DECLARE @sql nvarchar(max) = 'DELETE FROM lcs.uhrady'

END --KONEC PROCEDURY
GO
GRANT EXECUTE ON lcs.FirmaNSP_Test TO Uzivatele;
GO
GRANT EXECUTE ON lcs.FirmaNSP_Test TO Admin;
GO
