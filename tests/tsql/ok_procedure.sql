/*
Vzorová procedura, na které check.py nesmí nic hlásit.
Obsahuje záměrně věci, které vypadají jako porušení, ale jsou v komentáři nebo v řetězci:
CREATE PROCEDURE bez OR ALTER v tomhle komentáři, WHERE bez 1=1 taky.

--********** POPIS
Testovací procedura pro check.py.

--********** SPUSTENI
exec dbo.nspTestOk --0:01 (2026-10-26-1400)

--********** VYSTUPNI TABULKY
SELECT TOP 100 * FROM dbo.TestOk WHERE Id > 0
*/

CREATE OR ALTER PROCEDURE dbo.nspTestOk
AS
BEGIN
SET NOCOUNT ON
DECLARE @trvani DATETIME = GETDATE()
DECLARE @sql NVARCHAR(MAX)

--********** PLNĚNÍ **********
-- komentář na řádku: WHERE x = 1 se nehlásí
IF 1=1 BEGIN

    DROP TABLE IF EXISTS dbo.TestOk

    SELECT t.Id, t.Nazev, d.Popis
    INTO dbo.TestOk
    FROM dbo.Tabulka t
    JOIN dbo.Druh d ON d.DruhId = t.DruhId
    WHERE 1=1
        AND t.Datum >= '20260101'
        --AND t.Spol = 'AX'

    -- dynamické SQL: řetězec skript přeskakuje, i se zdvojeným apostrofem
    SET @sql = N'SELECT * FROM dbo.TestOk WHERE Nazev = ''CREATE PROCEDURE'''
    EXEC (@sql)

    DELETE FROM dbo.TestOk WHERE 1 = 1 AND Id < 0

END --END Konec PLNĚNÍ

/* vnořený /* blokový */ komentář: WHERE Id = 1 */

SELECT CONVERT(VARCHAR(8), GETDATE() - @trvani, 108) AS Trvani
END
