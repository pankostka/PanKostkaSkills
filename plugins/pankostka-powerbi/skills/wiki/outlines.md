# Osnovy článků wiki

Doplněk skillu `pankostka-powerbi-wiki`.

Sekce se píšou v uvedeném pořadí. Sekce označená jako volitelná se vynechá, když k ní není co napsat, prázdný nadpis v článku nezůstává. Každá sekce má pár vět nebo krátký seznam, ne odstavce. Článek se píše z pohledu uživatele, věcně a bez oslovení, jak vyžaduje `pankostka-md`.

## Kostka

Rozcestník. Uživatel se z něj dozví, co kostka pokrývá, a dostane se odsud ke všem ostatním článkům.

- **Úvod** (bez nadpisu): dvě až tři věty, co kostka pokrývá a pro koho je.
- **Vazby:** matice vazeb, viz níže.
- **Reporty:** seznam reportů nad kostkou, každý wikilinkem a jednou větou.
- **Aktuálnost dat:** jak často se data obnovují a kde se pozná, kdy naposledy. Konkrétní čas posledního nápočtu sem nepatří, zastaral by.
- **Parametry a pomocné tabulky** (volitelná): field parametry a tabulky, které nejsou dimenze ani faktovka, každá jednou větou.
- **Na co si dát pozor** (volitelná): vlastnosti kostky jako celku, například technické vazby, které při kombinaci témat vyprázdní výsledek.

**Matice vazeb.** Ve sloupcích faktovky, v řádcích dimenze řazené abecedně, obojí jako wikilink. V buňce co nejkratší popis vazby, třeba `datum případu`. Prázdná buňka znamená, že vazba neexistuje. Diagram je volitelný doplněk, matice je závazná: text, který jde uživateli, na diagram spoléhat nesmí.

## Faktovka

- **Úvod** (bez nadpisu): co je jeden řádek, tedy zrnitost, a jakou oblast faktovka pokrývá.
- **Dimenze:** na které dimenze faktovka vede a v jakém významu, pokud není zřejmý, například dvě data v jedné faktovce.
- **Ukazatele:** úvodní text píše člověk, pod ním je tabulka ukazatelů generovaná z modelu, viz `measures-table.md`. Text nad tabulkou vysvětluje jen míry s výjimkou nebo zvláštností.
- **Zdroj dat:** kde se udržují podkladová data (ERP, soubor xlsx) a jaký je rozsah, například jen dva roky zpět.
- **Na co si dát pozor** (volitelná).

## Dimenze

- **Úvod** (bez nadpisu): co je jeden řádek dimenze.
- **Kde se vyskytuje:** ve kterých faktovkách a reportech, jako wikilinky.
- **Zdroj dat:** kde se udržují podkladová data a jak se kombinují zvláštní informace, například hierarchie udržovaná v Excelu.
- **Atributy** (volitelná): jen atributy, jejichž význam není zřejmý z názvu, a hierarchie. Úplný seznam atributů sem nepatří, je vidět v Power BI.
- **Na co si dát pozor** (volitelná).

## Report

- **Úvod** (bez nadpisu): k čemu report je a pro koho.
- **Stránky:** seznam stránek v pořadí v reportu, u každé jedna věta, co ukazuje.
- **Z čeho čerpá:** faktovky a dimenze, jako wikilinky.
- **Na co si dát pozor** (volitelná).

## Údržba

Volitelný článek, píše ho člověk, viz zásada B v `SKILL.md`.

- **Úvod** (bez nadpisu): co uživatel udržuje, kde, a proč na tom závisí čísla v reportu. Odkaz zpět na faktovku nebo dimenzi, které se týká.
- **Postup:** kde se data udržují, které sloupce se vyplňují a co znamenají. Prázdná hodnota se vysvětlí, pokud nemá zřejmý význam.
- **Na co si dát pozor:** chyby, které vedou k nesprávným číslům nebo k selhání přepočtu, s doporučeným postupem.
- **Jak poznat, že něco chybí** (volitelná): kde se v reportu chybějící data projeví.

Selhání přepočtu se popisuje tím, co uživatel uvidí, ne tím, jak přepočet funguje.
