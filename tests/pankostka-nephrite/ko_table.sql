-- celkem 2
USE [HGFirmaOstra]
GO
CREATE TABLE lcs.FirmaTab
(
    ID INT IDENTITY(1,1) NOT NULL,
    OrgCS INT NULL REFERENCES lcs.organizace (cislo_subjektu)
)
