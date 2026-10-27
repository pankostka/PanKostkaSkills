-- Adresář a procedura se jmenují jinak, schéma s30CF je přesto vlastní.
CREATE OR ALTER PROCEDURE nsp30CF AS SELECT * INTO s30CF.FactCF FROM s20.FactDenik
