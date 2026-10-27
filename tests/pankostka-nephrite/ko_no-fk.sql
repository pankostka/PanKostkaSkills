-- celkem 1
USE [HGFirmaOstra]
GO
CREATE TABLE lcs.FirmaTab
(
    cislo_nonsubjektu INT IDENTITY(1,1) NOT NULL,
    OrgCS INT NULL REFERENCES lcs.organizace (cislo_subjektu)
)
