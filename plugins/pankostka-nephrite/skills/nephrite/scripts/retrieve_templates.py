"""Hromadný přenos šablon přehledu (třída 20) mezi databázemi Heliosu přes zprávu RETRIEVE.

Použití:
    python retrieve_templates.py prikaz <odkaz.xml> <příkaz.xml> <číslo šablony> [<číslo šablony> ...]
    python retrieve_templates.py prevod <retrieve.xml> <import.xml>

prikaz: z odkazu na funkci (soubor shortcut vytvořený v Heliosu) převezme přihlašovací část a příkazy nahradí
zprávou RETRIEVE na zadané šablony. Výstup obsahuje šifrované heslo z odkazu, po běhu ho smaž.

prevod: odpověď RETRIEVERESULT z HeliosGreenXmlTask.exe převede na soubor pro offline import (INSERTUPDATE):
- escapuje tabulátor a konec řádku v hodnotách atributů, utilita je zapisuje nevyescapované a parser XML
  by z nich udělal mezery (rozpadl by se seznam filtrů s_mark),
- ke každé šabloně doplní pět výchozích práv pro kategorii Všichni (sync_id $allusers), stejných, jaká
  zakládá trigger trg_INSERT_template; offline import je sám nezaloží a šablona bez práv není vidět.

Soubor se importuje funkcí Offline import s volbou Importované záznamy vždy vkládat.
"""
import re
import sys
import xml.dom.minidom
from xml.sax.saxutils import quoteattr

# systémová čísla operací (lcs.noris_permission_list_of_fnc), ve všech databázích stejná
OPERACE = {'sapl': 11, 'sedit': 12, 'sdel': 13, 's_print_template': 81, 's_print_template_on_server': 82}
KLICE_PRAVA = '102730,102731,102725,102726,102727,102735'
# XML rozhraní chce u každého záznamu SUBJECTID; u nového práva je to jen zástupné číslo mimo skutečný rozsah
PRVNI_ZASTUPNE_CISLO = 900000001


def prikaz(odkaz, vystup, cisla):
    if not cisla or not all(c.isdigit() for c in cisla):
        raise SystemExit('Zadej aspoň jedno číslo šablony, jen číslice.')
    t = open(odkaz, encoding='utf-8-sig').read()
    if '<shortcut' not in t or '<commands>' not in t:
        raise SystemExit(f'{odkaz} není odkaz na funkci (chybí shortcut nebo commands).')
    zaznamy = ''.join(f'\n        <RECORD SUBJECTID="{c}" CLASSID="20" />' for c in cisla)
    prikazy = f'<commands>\n    <command>\n      <RETRIEVE>{zaznamy}\n      </RETRIEVE>\n    </command>\n  </commands>'
    t = re.sub(r'<commands>.*</commands>', lambda _: prikazy, t, count=1, flags=re.S)
    open(vystup, 'w', encoding='utf-8').write(t)
    print(f'Příkaz RETRIEVE na {len(cisla)} šablon: {vystup}')
    print('Soubor obsahuje šifrované heslo z odkazu, po běhu ho smaž.')


def escapuj_atributy(t):
    return re.sub(r'="([^"]*)"', lambda m: '="' + m.group(1).replace('\t', '&#x9;').replace('\r', '&#xD;').replace('\n', '&#xA;') + '"', t)


def pravo(cislo, operace, sablona, trida, gunid, porada, nazev):
    return ''.join([
        f'<RECORD SUBJECTID="{cislo}" CLASSID="1752" REFERENCE="*{cislo}" NAME="*{cislo}" CLASSNAME="Právo" FOLDERNAME="Práva" keyAttributes="{KLICE_PRAVA}" permission_flag="0">',
        f'<RELATION RELID="102730" RELNAME="cislo_tridy" ORIENTATION="L" TRANSFORMATION="trida" requirementLevel="error"><RECORD SUBJECTID="{trida}" CLASSID="11" REFERENCE="{trida}" keyAttributes="cislo_tridy" /></RELATION>',
        '<RELATION RELID="102731" RELNAME="cislo_poradace" ORIENTATION="L" TRANSFORMATION="poradac" />',
        f'<RELATION RELID="102725" RELNAME="operace" ORIENTATION="L" TRANSFORMATION="operace" requirementLevel="error"><RECORD SUBJECTID="{OPERACE[operace]}" CLASSID="969" REFERENCE="*{OPERACE[operace]}" NAME="*{OPERACE[operace]}" keyAttributes="syst_nazev_oper" syst_nazev_oper={quoteattr(operace)} /></RELATION>',
        '<RELATION RELID="102726" RELNAME="groupid" ORIENTATION="L" TRANSFORMATION="kategorie" requirementLevel="error"><RECORD SUBJECTID="2" CLASSID="792" REFERENCE="*2" NAME="Všichni" keyAttributes="sync_id" sync_id="$allusers" /></RELATION>',
        '<RELATION RELID="102727" RELNAME="zamid" ORIENTATION="L" TRANSFORMATION="uzivatel" />',
        f'<RELATION RELID="102735" RELNAME="cislo_objektu" ORIENTATION="L" TRANSFORMATION="objekt" requirementLevel="error"><RECORD SUBJECTID="{sablona}" CLASSID="20" GUNID="{gunid}" FOLDERID="{porada}" REFERENCE="{sablona}" NAME={quoteattr(nazev)} CLASSNAME="Šablony" FOLDERNAME="Šablony" /></RELATION>',
        '<RELATION RELID="102804" RELNAME="cislo_subjektu_pachatel" ORIENTATION="L" TRANSFORMATION="pachatel" />',
        '</RECORD>',
    ])


def prevod(vstup, vystup):
    t = open(vstup, encoding='utf-8-sig').read()
    if '<RETRIEVERESULT' not in t:
        raise SystemExit(f'{vstup} není odpověď RETRIEVERESULT.')
    if 'STATE="SUCCESS"' not in t[:500]:
        raise SystemExit(f'{vstup}: RETRIEVE neskončil úspěchem, zkontroluj DETAIL v souboru.')
    t = escapuj_atributy(t)

    # hlavní záznamy šablon; vnořené záznamy mají jinou třídu než 20
    sablony = re.findall(r'<RECORD SUBJECTID="(\d+)" CLASSID="20" GUNID="([^"]+)" FOLDERID="(\d+)" REFERENCE="[^"]*" NAME="([^"]*)"', t)
    tridy = dict(re.findall(r'<lcs\.noris_templates cislo_template="(\d+)" cislo_tridy="\{(\d+),', t))
    casti = t.split('<validityScope')
    if len(casti) - 1 != len(sablony):
        raise SystemExit(f'Nesedí počet šablon ({len(sablony)}) a bloků validityScope ({len(casti) - 1}), soubor má neočekávaný tvar.')
    if '<permissions>' in t:
        raise SystemExit('Soubor už práva obsahuje, převod by je zdvojil.')

    cislo = PRVNI_ZASTUPNE_CISLO
    out = casti[0]
    for i, (sablona, gunid, porada, nazev) in enumerate(sablony):
        if sablona not in tridy:
            raise SystemExit(f'U šablony {sablona} chybí třída v USERDATA.')
        prava = []
        for operace in OPERACE:
            prava.append(pravo(cislo, operace, sablona, tridy[sablona], gunid, porada, nazev))
            cislo += 1
        out += '<permissions><records>' + ''.join(prava) + '</records></permissions><validityScope' + casti[i + 1]
        print(f'šablona {sablona} (třída {tridy[sablona]}): {nazev}')

    out = re.sub(r'<RETRIEVERESULT [^>]*>', '<INSERTUPDATE action="insertUpdate">', out, count=1).replace('</RETRIEVERESULT>', '</INSERTUPDATE>')
    # BOM jako u souboru z offline exportu Heliosu
    open(vystup, 'w', encoding='utf-8-sig').write(out)
    xml.dom.minidom.parse(vystup)
    print(f'{len(sablony)} šablon, soubor pro offline import: {vystup}')
    print('Importuj s volbou Importované záznamy vždy vkládat a zkontroluj práva.')


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'prikaz':
        prikaz(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif len(sys.argv) == 4 and sys.argv[1] == 'prevod':
        prevod(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(__doc__)
