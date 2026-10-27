USE [HGFirmaOstra] -- SQLSRVX
GO

SPADNI

CREATE TABLE lcs.FirmaTab
(
    cislo_nonsubjektu INT IDENTITY(1,1) NOT NULL,
    OrgCS INT NULL, --bez cizího klíče, nesmí blokovat zápis Heliosu
    CONSTRAINT pk_FirmaTab PRIMARY KEY (cislo_nonsubjektu)
)

-- select *
UPDATE g SET colwidth = -1 FROM lcs.FirmaTab AS g WHERE 1=1

UPDATE lcs.noris_gs_main
SET colwidth = -1
WHERE cislo_sablony = 123
	and expression like '%where 1=1%'

INSERT INTO lcs.FirmaTab (OrgCS) SELECT 1
