-- Kontrolní procedura martu EKO čte jeho vlastní schéma.
CREATE OR ALTER PROCEDURE nsp30EKO_KONTROLA AS SELECT * FROM s30EKO.FactDenik
