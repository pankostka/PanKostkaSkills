#!/usr/bin/env python3
"""Skript úpravy UDF šablony Heliosu (lcs.noris_form_templates) z XML souborů, ze skillu pankostka-nephrite.

Použití:
  udf_sql.py úprava   <db> <cislo_sablony> <nazev_sablony> <trida> <last_update> <původní.xml> <nové.xml> <výstup.sql> <popis>
  udf_sql.py obnovení <db> <cislo_sablony> <nazev_sablony> <trida> <last_update> <nové.xml> <výstup.sql> <popis>

úprava:   UPDATE s podmínkou na původní last_update a zakomentovaný blok vrácení s původním XML a last_update.
obnovení: UPDATE výsledného XML bez podmínky na last_update (k obnovení šablony nebo nasazení jinam), bez bloku vrácení.

XML se čte i zapisuje beze změny konců řádků (newline=''), skript je v UTF-8 bez BOM s konci řádků CRLF.
Literály se po zápisu vytáhnou ze souboru zpět a porovnají se vstupy. Databázi skript nečte: původní XML,
název, třídu a last_update je potřeba načíst z databáze těsně předtím. Jen standardní knihovna.
"""
import sys

NL = "\r\n"


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def check(xml, label):
    if "/*" in xml or "*/" in xml:
        sys.exit(f"{label}: XML obsahuje /* nebo */, blok vrácení by nešel zakomentovat.")
    if xml.count("\n") != xml.count("\r\n"):
        print(f"POZOR {label}: XML nemá jednotné konce řádků CRLF.")


def q(s):
    return s.replace("'", "''")


def crlf(s):
    return s.replace("\n", NL)


def main():
    a = sys.argv[1:]
    if len(a) == 10 and a[0] == "úprava":
        mode, db, n, nazev, trida, lu, old_f, new_f, out, popis = a
        old = read(old_f)
        check(old, "původní")
    elif len(a) == 9 and a[0] == "obnovení":
        mode, db, n, nazev, trida, lu, new_f, out, popis = a
        old = None
    else:
        sys.exit(__doc__)
    new = read(new_f)
    check(new, "nové")
    n = int(n)
    head = f"""USE [{db}]
GO
-- Šablona formuláře {n} {nazev} (třída {trida}): {popis}
-- {'XML načteno z ' + db + ', last_update šablony ' + lu + '. Při 0 řádcích je potřeba XML načíst znovu.' if old is not None else 'Výsledná podoba v ' + db + ' k last_update ' + lu + '. Slouží k obnovení šablony nebo k nasazení jinam; v jiné databázi ověř číslo šablony.'}

-- select cislo_sablony, nazev_sablony, trida, last_update, sablona_xml from lcs.noris_form_templates where 1=1 and cislo_sablony = {n}

-- pankostka: allow nephrite/no-write-system, úprava XML existující UDF šablony založené ve FormBuilderu
UPDATE lcs.noris_form_templates
SET sablona_xml = N'"""
    cond = f"AND last_update = '{lu}'" if old is not None else f"AND nazev_sablony = N'{q(nazev)}'\nAND trida = {int(trida)}"
    mid = f"""'
, last_update = GETDATE()
WHERE 1=1
AND cislo_sablony = {n}
{cond}

SELECT @@ROWCOUNT AS zmeneno_radku
GO
"""
    text = crlf(head) + q(new) + crlf(mid)
    if old is not None:
        rb_head = f"""
/* ===== VRÁCENÍ =====
Vrátí šablonu {n} do stavu před touto úpravou, včetně původního last_update.
Spustí se označením řádků od USE po GO uvnitř tohoto komentáře a F5.

USE [{db}]
-- pankostka: allow nephrite/no-write-system, vrácení úpravy XML UDF šablony
UPDATE lcs.noris_form_templates
SET sablona_xml = N'"""
        rb_tail = f"""'
, last_update = '{lu}'
WHERE 1=1
AND cislo_sablony = {n}
AND nazev_sablony = N'{q(nazev)}'

SELECT @@ROWCOUNT AS vraceno_radku
GO
===== KONEC VRÁCENÍ ===== */
"""
        text += crlf(rb_head) + q(old) + crlf(rb_tail)
    open(out, "w", encoding="utf-8", newline="").write(text)

    t = read(out)
    got_new = t[t.index("N'") + 2:t.index("'\r\n, last_update = GETDATE")].replace("''", "'")
    ok = got_new == new
    msg = f"nové XML OK: {ok}"
    if old is not None:
        r = t[t.index("/* ===== VRÁCENÍ"):]
        got_old = r[r.index("N'") + 2:r.index("'\r\n, last_update")].replace("''", "'")
        ok = ok and got_old == old
        msg += f" | vrácení OK: {got_old == old}"
    print(msg, "|", out)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
