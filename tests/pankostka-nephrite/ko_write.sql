-- celkem 4
USE [HGFirmaOstra]
GO
UPDATE lcs.organizace SET nazev_subjektu = 'X' WHERE 1=1
INSERT INTO lcs.qn_nastaveni (a) SELECT 1
DELETE FROM lcs.uhrady WHERE 1=1

UPDATE lcs.noris_gs_main
SET colwidth = -1
WHERE cislo_sablony = 123
