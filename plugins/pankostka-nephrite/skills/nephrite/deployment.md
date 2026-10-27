# Skripty nasazované do Heliosu

Doplněk skillu `pankostka-nephrite`. Platí pro skripty, které zakládají nebo mění objekty v databázi Heliosu, ne pro dotazy, které z Heliosu jen čtou.

## Kam se nasazuje

**Rozhoduje cíl nasazení, ne téma.** Skript, který běží v databázi Heliosu, se řídí tímhle souborem, i kdyby s datovým skladem nesouvisel vůbec (třeba procedura pro report). Skript, který běží jinde, například v databázi datového skladu, se jím neřídí, i kdyby z Heliosu četl.

**Nasazuje a spouští správce Heliosu**, ne vývojář a ne job datového skladu. Repo je zdroj pravdy pro obsah skriptů, ne pro to, co je kde skutečně nasazené. Nikdy proto netvrď, že je změna nasazená, jen protože je v repu.

## Hlavička USE

`nephrite/use-header` **Skript začíná `USE [<databáze>]`.** V Heliosu bývají vedle sebe databáze víc společností, často na různých serverech, a spuštění nad špatnou z nich znamená založení objektu v cizí produkci. Za `USE` patří poznámka, na kterém serveru databáze je:

```sql
USE [HGFirmaOstra] -- SQLSRVX
GO
```

Když objekt patří do víc databází, další se dopíšou zakomentované hned pod první. Ten řádek je jediná stopa, podle které se pozná, že nasazení má proběhnout víckrát:

```sql
USE [FirmaA]
--USE [FirmaB] -- do obou databází!
GO
```

Zakomentovaný `USE` na testovací databázi je běžný a nech ho tam. Když objekt naopak patří jen do jedné databáze a je to překvapivé, napiš to komentářem na řádek `USE`. Hlavičku nikdy nevyhazuj.

## Víc databází

- `nephrite/one-file-all-dbs` **Jeden soubor na objekt, obsah pro všechny databáze shodný.** Rozdíl mezi verzemi v různých databázích je **chyba k opravě**, ne stav k zachycení, proto se nezavádí ani sufix podle databáze. Verze se ladí zvlášť přímo v produkci a rozejdou se tiše. Než u objektu ve víc databázích cokoli změníš, ověř, že soubor v repu odpovídá všem.
- **Odlišnosti mezi firmami řeš podmínkou v kódu, ne kopií souboru**, třeba `if db_name() like '%Firma%' BEGIN ... END` pro části, které jinde neexistují.
- **Čísla objektů v Heliosu (pořadače, funkce, šablony) se mezi databázemi liší.** V kódu a v hlášeních je uváděj s popisem, ne nahým číslem: `pořadač CF Pohyby (č.p. 10981)`. Seznam čísel patří do `CLAUDE.md` nebo `CLAUDE_Project.md` repa.
- **Dotazy přes víc databází jdou přes linked servery** (`server.databaze.lcs.<tabulka>`). Jsou na porovnávací a diagnostické selecty, ne do produkčních procedur.

## Název souboru

**`<schéma>.<objekt>.sql`**, tedy přesně jak se objekt jmenuje v databázi, včetně malých písmen a podtržítek: `lcs.FirmaNSP_Ucet.sql`. DDL tabulky má `<schéma>.<objekt>.Table.sql`, jak ho pojmenuje SSMS. Sufixy `-VZOR`, `-DRAFT` a `-TMP` fungují jako všude jinde: název objektu je vše mezi první tečkou a pomlčkou se sufixem. Skripty, které objekt nezakládají, se jmenují popisně a schéma v názvu nemají.

## Dump ze SSMS

`nephrite/clean-dump` Skript vygenerovaný přes *Script Stored Procedure as* není hotový soubor. Než ho položíš do repa:

1. **Smaž řádek `/****** Object: ... Script Date: ... ******/`.** Je v něm časové razítko, takže by každý nový dump vyrobil diff i bez jediné změny kódu.
2. **Přepiš `CREATE PROCEDURE` na `CREATE OR ALTER PROCEDURE`.** Bez toho skript není idempotentní a druhé spuštění spadne.
3. **Zkontroluj hlavičku `USE`.**
4. **Dopiš na konec `GRANT EXECUTE`**, pokud proceduru spouští uživatelé Heliosu nebo účet reportingu. Dump práva neobsahuje a bez nich funkce uživateli nepojede.
5. **Převeď soubor do UTF-8.** SSMS ukládá UTF-16 LE. Takový soubor needituj a nahlas ho, jinak se rozsype diakritika a v diffu bude celý soubor.

Syrové dumpy pro srovnání drž v adresáři se sufixem `-TMP`, mimo git, a necituj z nich jako ze zdroje pravdy.

## DDL tabulky

`nephrite/ddl-spadni` **Skript s DDL existující tabulky se nesmí dát spustit celý.** Tabulka už existuje a má data. `CREATE TABLE` a pozdější `ALTER TABLE ADD` v souboru jsou **historie vzniku**, ne spustitelný skript. Proto je hned za `USE` řádek `SPADNI`: úmyslná syntaktická chyba, aby F5 nad celým souborem spadl a člověk musel označit jen sekci, kterou chce pustit. **Tuhle zábranu nikdy neodstraňuj** a v nových souborech s DDL ji zachovej.

## Úpravy dat

`nephrite/select-before-update` Nad výkonným `UPDATE`, `DELETE` nebo `INSERT` nech **zakomentovaný `-- select *`** se stejným `FROM`, aby se dal jedním odkomentováním zkontrolovat dopad.

Mezikroky dělej přes `DROP TABLE IF EXISTS #x` a `SELECT ... INTO #x`, ne přes tabulkové proměnné. Dají se po běhu prohlédnout.
