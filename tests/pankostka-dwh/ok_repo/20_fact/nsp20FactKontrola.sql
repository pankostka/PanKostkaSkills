-- Kontrola faktovky proti martu: vědomá výjimka s důvodem.
CREATE OR ALTER PROCEDURE nsp20FactKontrola AS
BEGIN
	-- pankostka: allow dwh/no-read-up, kontrola součtů proti martu, nic neplní
	SELECT SUM(m.DenikKc) FROM s30EKO.FactDenik AS m
	SELECT 1 FROM s30EKO.FactDenik AS m2 -- pankostka: allow dwh/no-read-up, druhá kontrola na stejném řádku
END
