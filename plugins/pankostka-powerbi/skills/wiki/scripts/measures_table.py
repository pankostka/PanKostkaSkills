# -*- coding: utf-8 -*-
"""
================================================================================
 POPIS
   Udržuje tabulku ukazatelů v článku faktovky ve Wiki<Kostka>/ podle modelu.

   Tabulka leží v článku mezi značkami

     <!-- ukazatele:start ... -->
     ...
     <!-- ukazatele:end -->

   a nic mimo ně skript nemění. Sloupce:

     Adresář    displayFolder míry    z modelu, přepíše se při každém běhu
     Ukazatel   název míry            z modelu, přepíše se při každém běhu
     Popis      popis pro uživatele   píše člověk ve wiki, skript ho nemění

   Pod tabulkou je ve sbaleném callout [!dax]- výraz každé míry, z modelu.

   Řádek se s mírou páruje podle názvu. Nová míra, která v tabulce ještě
   není, dostane jako počáteční popis svůj `///` z TMDL. Tak se tabulka
   naplní i poprvé. Míra, která z modelu zmizela, z tabulky vypadne a její
   popis se vypíše, aby se neztratil. Když zároveň nějaká míra přibyla,
   vypíše se to jako možné přejmenování - popis se sám nepřenáší.

   Zdrojem popisu je wiki. Zápis popisu zpět do `///` zatím hotový není,
   tenhle skript model nemění.

 SPUSTENI
   python measures_table.py <adresář kostky> FactRegistrace
   python measures_table.py <adresář kostky> FactRegistrace --check
   python measures_table.py <adresář kostky> FactRegistrace --clanek <cesta.md>

   Adresář kostky obsahuje <Kostka>.SemanticModel (v libovolné hloubce)
   a Wiki<Kostka>/. Název kostky je název adresáře.

   --check      nic nezapíše, jen řekne, jestli by se blok změnil
   --clanek     jiný článek než Wiki<Kostka>/<Kostka> <Fakt>/<Kostka> <Fakt>.md (test na kopii)

   Návratový kód 0 = blok je aktuální nebo byl zapsán, 1 = při --check
   by se blok změnil, 2 = špatné parametry, chybí článek nebo značky.

 PRAVIDLA FORMATU
   Viz measures-table.md ve skillu pankostka-powerbi-wiki.
================================================================================
"""
import argparse
import locale
import os
import re
import sys
import unicodedata

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ZNACKA_START = '<!-- ukazatele:start - generuje skill pankostka-powerbi-wiki, ručně se píše jen sloupec Popis -->'
ZNACKA_KONEC = '<!-- ukazatele:end -->'
RE_START = re.compile(r'^<!-- ukazatele:start\b.*-->\s*$')
RE_KONEC = re.compile(r'^<!-- ukazatele:end\b.*-->\s*$')
SKRYTE_SLOZKY = ('hide', 'skryto')
HLAVICKA = ('Adresář', 'Ukazatel', 'Popis')


# ==============================================================================
# TMDL - míry jedné tabulky
# ==============================================================================

def _unquote(name):
    """TMDL obaluje jména s mezerou apostrofy, vnitřní apostrof zdvojuje."""
    name = name.strip()
    if name.startswith("'") and name.endswith("'") and len(name) >= 2:
        name = name[1:-1].replace("''", "'")
    return name


def _jmeno_a_vyraz(rest):
    """Z `X = DAX` vrátí (X, DAX). Rovnítko uvnitř apostrofů ignoruje."""
    in_quote = False
    for i, ch in enumerate(rest):
        if ch == "'":
            in_quote = not in_quote
        elif ch == '=' and not in_quote:
            return _unquote(rest[:i]), rest[i + 1:].strip()
    return _unquote(rest), ''


def nacti_miry(tmdl):
    """Viditelné míry tabulky jako seznam dict(slozka, nazev, popis, dax)."""
    with open(tmdl, encoding='utf-8') as f:
        radky = f.read().splitlines()
    miry = []
    popis = []
    i = 0
    while i < len(radky):
        radek = radky[i]
        if radek.startswith('\t///'):
            text = radek[4:].strip()
            # Oddělovací banner sekce nepatří k následující míře.
            popis = [] if text.startswith('###') else popis + [text]
            i += 1
            continue
        m = re.match(r'^\tmeasure\s+(.+)$', radek)
        if not m:
            if radek.strip():
                popis = []
            i += 1
            continue
        nazev, prvni = _jmeno_a_vyraz(m.group(1))
        dax = [prvni] if prvni else []
        slozka, skryta = '', False
        i += 1
        # Tělo míry: výraz má odsazení tři tabulátory (prázdný řádek výrazu
        # taky), vlastnosti dva. Úplně prázdné řádky jsou mezi vlastnostmi.
        while i < len(radky) and (radky[i].startswith('\t\t') or not radky[i].strip()):
            r = radky[i]
            if r.startswith('\t\t\t'):
                dax.append(r[3:])
            elif r.strip():
                telo = r.strip()
                if telo == 'isHidden':
                    skryta = True
                mf = re.match(r'^displayFolder:\s*(.+)$', telo)
                if mf:
                    slozka = mf.group(1).strip()
            i += 1
        while dax and not dax[-1].strip():
            dax.pop()
        while dax and not dax[0].strip():
            dax.pop(0)
        if not skryta and slozka.lower() not in SKRYTE_SLOZKY:
            miry.append(dict(slozka=slozka, nazev=nazev, popis=' '.join(popis), dax='\n'.join(dax)))
        popis = []
    return miry


# ==============================================================================
# Pořadí jako v seznamu polí
# ==============================================================================

def _kolace():
    for loc in ('cs_CZ.UTF-8', 'cs_CZ', 'Czech_Czech Republic.1250', 'Czech'):
        try:
            locale.setlocale(locale.LC_COLLATE, loc)
            return locale.strxfrm
        except locale.Error:
            pass
    print('POZOR: česká kolace není k dispozici, řadí se bez diakritiky.')
    return lambda t: ''.join(c for c in unicodedata.normalize('NFKD', t)
                             if not unicodedata.combining(c)).lower()


def serad(miry):
    """Na každé úrovni nejdřív míry, pak podsložky, obojí abecedně.
    Ověřeno proti snímku seznamu polí factregistrace_ukazatele.png."""
    k = _kolace()

    def klic(r):
        cesta = [c for c in r['slozka'].split('\\') if c]
        return [(1, k(c)) for c in cesta] + [(0, k(r['nazev']))]
    return sorted(miry, key=klic)


# ==============================================================================
# Článek - blok mezi značkami
# ==============================================================================

def _bunky(radek):
    """Rozdělí řádek Markdown tabulky na buňky. `\\|` je svislítko v textu."""
    radek = radek.strip()
    if not radek.startswith('|'):
        return None
    casti, akt, i = [], '', 1
    while i < len(radek):
        if radek[i] == '\\' and i + 1 < len(radek) and radek[i + 1] == '|':
            akt += '\\|'
            i += 2
            continue
        if radek[i] == '|':
            casti.append(akt.strip())
            akt = ''
        else:
            akt += radek[i]
        i += 1
    return casti


def _odescapuj(t):
    return t.replace('\\|', '|')


def _escapuj(t):
    return t.replace('|', '\\|')


def precti_popisy(blok):
    """Z existujícího bloku vrátí {název míry: popis tak, jak je v buňce}."""
    popisy = {}
    for radek in blok:
        b = _bunky(radek)
        if not b or len(b) < 3 or tuple(b[:3]) == HLAVICKA or set(b[0]) <= set('-: '):
            continue
        popisy[_odescapuj(b[1])] = b[2]
    return popisy


def vysledne_popisy(miry, popisy):
    """Popis z wiki, u míry bez řádku počáteční popis z `///`."""
    return {r['nazev']: popisy.get(r['nazev'], _escapuj(r['popis'])) for r in miry}


def sestav_blok(miry, vysledne):
    o = [ZNACKA_START,
         '| ' + ' | '.join(HLAVICKA) + ' |',
         '| --- | --- | --- |']
    for r in miry:
        o.append('| %s | %s | %s |' % (_escapuj(r['slozka']), _escapuj(r['nazev']), vysledne[r['nazev']]))
    o += ['', '> [!dax]- Výpočty (DAX)']
    for r in miry:
        o += ['>', '> **%s**' % r['nazev'], '> ```dax']
        o += [('> ' + l).rstrip() for l in r['dax'].split('\n')]
        o.append('> ```')
    o.append(ZNACKA_KONEC)
    return o


def najdi_blok(radky):
    starty = [i for i, r in enumerate(radky) if RE_START.match(r)]
    konce = [i for i, r in enumerate(radky) if RE_KONEC.match(r)]
    if len(starty) != 1 or len(konce) != 1 or konce[0] < starty[0]:
        return None
    return starty[0], konce[0]


# ==============================================================================
# Hlavní běh
# ==============================================================================

def najdi_model(kostka_dir, kostka):
    """Cesta k definition/ modelu <Kostka>.SemanticModel kdekoli pod adresářem kostky."""
    for root, dirs, _ in os.walk(kostka_dir):
        dirs[:] = [d for d in dirs if d != '.git']
        if os.path.basename(root) == kostka + '.SemanticModel':
            return os.path.join(root, 'definition')
    return None


def aktualizuj(tmdl, clanek, kontrola, fakt, out=print):
    """Srovná blok ukazatelů v článku s mírami tabulky. Vrátí 0 aktuální nebo zapsáno, 1 změnil by se, 2 chyba."""
    with open(clanek, encoding='utf-8', newline='') as f:
        text = f.read()
    crlf = '\r\n' in text
    radky = text.replace('\r\n', '\n').split('\n')
    poloha = najdi_blok(radky)
    if poloha is None:
        out('CHYBA: v článku %s chybí značky bloku, nebo jsou víc než jednou.' % clanek)
        out('       Vlož do sekce ## Ukazatele dva řádky a spusť znovu:')
        out('       ' + ZNACKA_START)
        out('       ' + ZNACKA_KONEC)
        return 2
    od, do = poloha

    miry = serad(nacti_miry(tmdl))
    popisy = precti_popisy(radky[od + 1:do])
    vysledne = vysledne_popisy(miry, popisy)
    novy = sestav_blok(miry, vysledne)

    # Hlášení
    v_modelu = {r['nazev'] for r in miry}
    nove = [r['nazev'] for r in miry if r['nazev'] not in popisy]
    zmizele = [n for n in popisy if n not in v_modelu]
    bez_popisu = [n for n, t in vysledne.items() if not t.strip()]
    rozdil = [r['nazev'] for r in miry if r['nazev'] in popisy
              and _odescapuj(popisy[r['nazev']]) != r['popis']]
    out('%s: %d měr' % (fakt, len(miry)))
    if nove and not popisy:
        out('  počáteční naplnění: %d řádků, popis převzat z ///' % len(nove))
    elif nove:
        out('  nové řádky (popis převzat z ///): %s' % ', '.join(nove))
    for n in zmizele:
        out('  vypadlo z modelu: %s | popis: %s' % (n, popisy[n] or '(prázdný)'))
    if zmizele and nove:
        out('  POZOR: možné přejmenování - popis se nepřenáší, zkontroluj ručně.')
    if bez_popisu:
        out('  bez popisu: %s' % ', '.join(bez_popisu))
    if rozdil:
        out('  popis ve wiki se liší od ///: %s' % ', '.join(rozdil))

    # Starou značku bloku (jiný text za ukazatele:start) skript rozpozná a nahradí novou.
    if radky[od:do + 1] == novy:
        out('  blok je aktuální')
        return 0
    if kontrola:
        out('  blok by se změnil')
        return 1
    radky[od:do + 1] = novy
    vystup = '\n'.join(radky)
    with open(clanek, 'w', encoding='utf-8', newline='') as f:
        f.write(vystup.replace('\n', '\r\n') if crlf else vystup)
    out('  zapsáno: %s' % clanek)
    return 0


def main():
    p = argparse.ArgumentParser(description='Udržuje tabulku ukazatelů v článku faktovky podle modelu.')
    p.add_argument('kostka', help='adresář kostky, obsahuje <Kostka>.SemanticModel a Wiki<Kostka>/')
    p.add_argument('fakt', help='tabulka v modelu, například FactRegistrace')
    p.add_argument('--clanek', help='cesta k článku, jinak Wiki<Kostka>/<Kostka> <Fakt>/<Kostka> <Fakt>.md')
    p.add_argument('--check', '--kontrola', dest='kontrola', action='store_true', help='nic nezapíše')
    a = p.parse_args()

    kostka = os.path.basename(os.path.normpath(a.kostka))
    definition = najdi_model(a.kostka, kostka)
    if not definition:
        print('CHYBA: pod %s není %s.SemanticModel' % (a.kostka, kostka))
        return 2
    tmdl = os.path.join(definition, 'tables', a.fakt + '.tmdl')
    nazev = '%s %s' % (kostka, a.fakt)
    clanek = a.clanek or os.path.join(a.kostka, 'Wiki' + kostka, nazev, nazev + '.md')
    for cesta in (tmdl, clanek):
        if not os.path.isfile(cesta):
            print('CHYBA: soubor neexistuje: %s' % cesta)
            return 2
    return aktualizuj(tmdl, clanek, a.kontrola, a.fakt)


if __name__ == '__main__':
    sys.exit(main())
