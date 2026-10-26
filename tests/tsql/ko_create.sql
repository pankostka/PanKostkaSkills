-- Každý CREATE bez OR ALTER se musí nahlásit jako [create], celkem 4 neshody.
CREATE PROCEDURE dbo.nspTestKo
AS
SELECT 1
GO

create proc dbo.nspTestKo2 AS SELECT 1
GO

CREATE FUNCTION dbo.fnTestKo() RETURNS INT AS BEGIN RETURN 1 END
GO

CREATE   VIEW dbo.vwTestKo AS SELECT 1 AS Id
GO

-- tohle je v pořádku a hlásit se nesmí
CREATE OR ALTER PROCEDURE dbo.nspTestOk AS SELECT 1
GO

CREATE TABLE dbo.TestKo (Id INT)
