# -*- coding: utf-8 -*-
"""
================================================================================
 POPIS
   Kontrola reportu v PBIR formatu proti semantickemu modelu v TMDL.
   Hleda to, co Power BI Desktop nenahlasi: odkazy na tabulky, sloupce, miry,
   hierarchie a jejich urovne, ktere v modelu neexistuji. Typicky vznikaji tim,
   ze se report zkopiruje od jineho modelu - dotaz vizualu je pritom v poradku,
   takze se vizual tvari funkcne a chyba se schova v sortDefinition, v barevnych
   selektorech dataPoint nebo v columnWidth.

   Hleda strukturalne, ne grepem. Retezec "Datum" je i v "queryRef": "DimDatum.Datum",
   takze hledani podle nazvu tabulky hlasi falesne poplachy.

 SPUSTENI
   python validate_pbir.py                     # cely repo
   python validate_pbir.py <adresar s modely>
   python validate_pbir.py --report <cesta.Report> --model <cesta.SemanticModel>
   python validate_pbir.py --quiet              # jen problemy

   Navratovy kod 0 = zadna CHYBA (varovani nevadi), 1 = nalezena chyba,
   2 = spatne parametry. Vhodne do pre-commit hooku.

 VYSTUP
   Vypis na stdout, jeden blok na report. CHYBA = rozbije se to v Power BI,
   VAROVANI = mrtvy balast, ktery nic nerozbije, ale patri pryc.

 CO KONTROLUJE
   CHYBA     odkaz na tabulku/sloupec/miru/hierarchii/uroven, ktera v modelu neni
   CHYBA     navigacni tlacitko mirici na neexistujici stranku
   CHYBA     pages.json nesouhlasi s adresari na disku
   CHYBA     page.name / visual.name nesouhlasi s nazvem sve slozky
   CHYBA     duplicitni jmeno vizualu
   CHYBA     obrazek pouzity ve vizualu chybi v RegisteredResources
   CHYBA     obrazek pouzity ve vizualu neni zapsany v report.json
   CHYBA     byPath odkazuje na neexistujici .SemanticModel
   VAROVANI  selector.metadata ukazuje na tabulku mimo model (zbytek columnWidth)
   VAROVANI  soubor v RegisteredResources, ktery neni v report.json
   VAROVANI  model pro report se nepodarilo najit (kontrola poli se preskoci)

 CO NEKONTROLUJE
   Vlastnosti formatovani (nazvy klicu v objects/visualContainerObjects) - na to
   by byla potreba znalost objektoveho modelu Power BI, ne jen TMDL.
   Vazby mezi tabulkami a smer filtrovani.
   Zda vizual dava smysl. Jen ze na neco nesahá, co neexistuje.
================================================================================
"""
import argparse
import json
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ==============================================================================
# TMDL - nacteni modelu
# ==============================================================================

def _unquote(name):
    """TMDL obaluje jmena s mezerou apostrofy, vnitrni apostrof zdvojuje."""
    name = name.strip()
    if name.startswith("'") and name.endswith("'") and len(name) >= 2:
        name = name[1:-1].replace("''", "'")
    return name


def _member_name(rest):
    """Z 'X = DAX' nebo 'X' vytahne jmeno. Rovnitko uvnitr apostrofu ignoruje."""
    in_quote = False
    i = 0
    while i < len(rest):
        ch = rest[i]
        if ch == "'":
            in_quote = not in_quote
        elif ch == '=' and not in_quote:
            return _unquote(rest[:i])
        i += 1
    return _unquote(rest)


class Model(object):
    """Tabulky, jejich sloupce a miry, a hierarchie s urovnemi."""

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path).replace('.SemanticModel', '')
        self.members = {}     # tabulka -> mnozina sloupcu, mer a hierarchii
        self.hierarchies = {}  # (tabulka, hierarchie) -> mnozina urovni
        self._load()

    def _load(self):
        tdir = os.path.join(self.path, 'definition', 'tables')
        if not os.path.isdir(tdir):
            return
        for fn in sorted(os.listdir(tdir)):
            if not fn.endswith('.tmdl'):
                continue
            self._load_table(os.path.join(tdir, fn))

    def _load_table(self, fp):
        with open(fp, encoding='utf-8') as f:
            lines = f.read().splitlines()
        table = None
        hier = None
        for line in lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip('\t'))
            body = line.strip()

            if indent == 0:
                m = re.match(r'^table\s+(.+)$', body)
                if m:
                    table = _unquote(m.group(1))
                    self.members.setdefault(table, set())
                    hier = None
                continue

            if table is None:
                continue

            if indent == 1:
                hier = None
                m = re.match(r'^(column|measure|hierarchy)\s+(.+)$', body)
                if m:
                    kind, name = m.group(1), _member_name(m.group(2))
                    self.members[table].add(name)
                    if kind == 'hierarchy':
                        hier = name
                        self.hierarchies.setdefault((table, hier), set())
                continue

            if indent >= 2 and hier is not None:
                m = re.match(r'^level\s+(.+)$', body)
                if m:
                    self.hierarchies[(table, hier)].add(_member_name(m.group(1)))

    def has_table(self, t):
        return t in self.members

    def has_member(self, t, p):
        return t in self.members and p in self.members[t]

    def tables_with_member(self, p):
        """Miru lze v DAX adresovat bez tabulky, takze spatna domovska tabulka
        v odkazu nemusi nic rozbit. Proto se hlasi jinak nez uplne chybejici pole."""
        return sorted(t for t, members in self.members.items() if p in members)

    def has_hierarchy(self, t, h):
        return (t, h) in self.hierarchies

    def has_level(self, t, h, lv):
        return lv in self.hierarchies.get((t, h), set())

    def with_report_measures(self, report_dir, res):
        """Miry ulozene primo v reportu (definition/reportExtensions.json) patri jen
        tomu reportu. Vraci kopii modelu s nimi, sdileny model v cache se nemeni."""
        fp = os.path.join(report_dir, 'definition', 'reportExtensions.json')
        if not os.path.isfile(fp):
            return self
        with open(fp, encoding='utf-8') as f:
            ext = json.load(f)
        clone = Model.__new__(Model)
        clone.path, clone.name, clone.hierarchies = self.path, self.name, self.hierarchies
        clone.members = {t: set(m) for t, m in self.members.items()}
        schema = ext.get('name', 'extension')
        n = 0
        for ent in ext.get('entities', []):
            t = ent.get('name')
            if t not in self.members:
                res.err('reportExtensions.json: tabulka %s v modelu neni' % t)
                continue
            # vizual se na miru z reportu odkazuje se SourceRef.Schema, proto vlastni klic schema:tabulka
            key = '%s:%s' % (schema, t)
            clone.members.setdefault(key, set())
            for ms in ent.get('measures', []):
                if ms.get('name') in self.members[t]:
                    res.err('reportExtensions.json: mira %s.%s uz je v modelu, jmeno musi byt jedinecne' % (t, ms.get('name')))
                clone.members[key].add(ms.get('name'))
                n += 1
        res.info.append('%d mer ulozenych v reportu (reportExtensions.json)' % n)
        return clone

    def __repr__(self):
        return '<Model %s: %d tabulek, %d hierarchii>' % (
            self.name, len(self.members), len(self.hierarchies))


# ==============================================================================
# PBIR - prochazeni odkazu na model
# ==============================================================================

class RefCollector(object):
    """Posbira odkazy na model z JSON stromu vizualu nebo stranky.

    Odkaz na pole ma v PBIR dve podoby:
      SourceRef.Entity  - primo nazev tabulky (projekce, sortDefinition, selektory)
      SourceRef.Source  - alias z bloku filter.From (vnitrek Advanced/Categorical filtru)
    Druhou podobu je nutne rozlozit podle From, jinak se vnitrek filtru nezkontroluje.
    """

    def __init__(self):
        self.tables = set()       # (tabulka, kde)
        self.members = set()      # (tabulka, pole, kde)
        self.hier = set()         # (tabulka, hierarchie, uroven|None, kde)
        self.metadata = set()     # selector.metadata -> (tabulka, kde)
        self.resources = set()    # ItemName obrazku

    def walk(self, node, where, aliases=None):
        if isinstance(node, list):
            for item in node:
                self.walk(item, where, aliases)
            return
        if not isinstance(node, dict):
            return

        # blok filtru zavadi aliasy tabulek pro svuj vnitrek
        if 'From' in node and isinstance(node.get('From'), list):
            sub = dict(aliases or {})
            for src in node['From']:
                if isinstance(src, dict) and 'Name' in src and 'Entity' in src:
                    sub[src['Name']] = src['Entity']
                    self.tables.add((src['Entity'], where))
            aliases = sub

        self._entity(node, where, aliases)
        self._hierarchy(node, where, aliases)
        self._selector(node, where)
        self._resource(node)

        for value in node.values():
            self.walk(value, where, aliases)

    def _resolve(self, expr, aliases):
        """Z Expression vytahne nazev tabulky, pres Entity nebo pres alias Source."""
        if not isinstance(expr, dict):
            return None
        src = expr.get('SourceRef')
        if not isinstance(src, dict):
            return None
        if 'Entity' in src:
            # mira ulozena v reportu ma SourceRef.Schema = jmeno rozsireni, model schema nema
            return '%s:%s' % (src['Schema'], src['Entity']) if src.get('Schema') else src['Entity']
        if 'Source' in src and aliases:
            return aliases.get(src['Source'])
        return None

    def _entity(self, node, where, aliases):
        if 'Property' not in node or 'Expression' not in node:
            return
        # HierarchyLevel resi _hierarchy, tady jen Column/Measure
        table = self._resolve(node.get('Expression'), aliases)
        if table:
            self.members.add((table, node['Property'], where))

    def _hierarchy(self, node, where, aliases):
        hl = node.get('HierarchyLevel')
        if isinstance(hl, dict):
            h = hl.get('Expression', {})
            h = h.get('Hierarchy') if isinstance(h, dict) else None
            if isinstance(h, dict):
                table = self._resolve(h.get('Expression'), aliases)
                if table:
                    self.hier.add((table, h.get('Hierarchy'), hl.get('Level'), where))
            return
        h = node.get('Hierarchy')
        if isinstance(h, dict) and 'Hierarchy' in h:
            table = self._resolve(h.get('Expression'), aliases)
            if table:
                self.hier.add((table, h.get('Hierarchy'), None, where))

    def _selector(self, node, where):
        sel = node.get('selector')
        if isinstance(sel, dict):
            md = sel.get('metadata')
            if isinstance(md, str) and '.' in md:
                self.metadata.add((md.split('.', 1)[0], where))

    def _resource(self, node):
        rpi = node.get('ResourcePackageItem')
        if isinstance(rpi, dict) and 'ItemName' in rpi:
            self.resources.add(rpi['ItemName'])


NAV_RE = re.compile(r'"navigationSection".{0,200}?"Value":\s*"\'([^\']+)\'"', re.S)


# ==============================================================================
# kontrola jednoho reportu
# ==============================================================================

class Result(object):
    """Problemy se sdruzuji podle textu, aby 33x tentyz mrtvy columnWidth
    nebyl 33 radku vypisu. Misto vyskytu se drzi zvlast."""

    def __init__(self, label):
        self.label = label
        self.errors = {}    # text -> [misto, ...] (poradi zachovano)
        self.warnings = {}
        self.info = []

    def _add(self, bucket, msg, where):
        bucket.setdefault(msg, [])
        if where:
            bucket[msg].append(where)

    def err(self, msg, where=None):
        self._add(self.errors, msg, where)

    def warn(self, msg, where=None):
        self._add(self.warnings, msg, where)

    @property
    def n_errors(self):
        return sum(max(1, len(v)) for v in self.errors.values())

    @property
    def n_warnings(self):
        return sum(max(1, len(v)) for v in self.warnings.values())

    def lines(self, tag, bucket, verbose):
        for msg, places in bucket.items():
            if not places:
                yield '   %-9s %s' % (tag, msg)
                continue
            if len(places) == 1:
                yield '   %-9s %s  [%s]' % (tag, msg, places[0])
                continue
            yield '   %-9s %s  - %dx' % (tag, msg, len(places))
            shown = places if verbose else places[:3]
            for p in shown:
                yield '   %-9s     %s' % ('', p)
            if len(places) > len(shown):
                yield '   %-9s     ... a dalsich %d (--verbose)' % ('', len(places) - len(shown))


def find_model_for_report(report_dir, repo_root):
    """Model pro report: byPath rovnou, byConnection podle 'initial catalog'."""
    pbir = os.path.join(report_dir, 'definition.pbir')
    if not os.path.isfile(pbir):
        return None, 'chybi definition.pbir'
    with open(pbir, encoding='utf-8') as f:
        ref = json.load(f).get('datasetReference', {})

    if 'byPath' in ref:
        p = os.path.normpath(os.path.join(report_dir, ref['byPath'].get('path', '')))
        if os.path.isdir(p):
            return p, None
        return None, 'byPath ukazuje na neexistujici %s' % ref['byPath'].get('path')

    if 'byConnection' in ref:
        cs = ref['byConnection'].get('connectionString', '') or ''
        m = re.search(r'initial catalog=([^;]+)', cs, re.I)
        if not m:
            return None, 'byConnection bez "initial catalog", model nelze dohledat'
        catalog = m.group(1).strip()
        for p in discover_models(repo_root):
            if os.path.basename(p) == catalog + '.SemanticModel':
                return p, None
        return None, 'model %s v repu nenalezen (live connect na jiny workspace?)' % catalog

    return None, 'definition.pbir nema byPath ani byConnection'


def check_report(report_dir, repo_root, models_cache, forced_model=None):
    label = os.path.relpath(report_dir, repo_root).replace('\\', '/')
    res = Result(label)

    pages_dir = os.path.join(report_dir, 'definition', 'pages')
    pages_json = os.path.join(pages_dir, 'pages.json')
    if not os.path.isfile(pages_json):
        res.err('chybi definition/pages/pages.json')
        return res

    # ---- model ----
    model = forced_model
    if model is None:
        model_path, problem = find_model_for_report(report_dir, repo_root)
        if problem:
            (res.err if 'neexistujici' in problem else res.warn)(problem)
        if model_path:
            if model_path not in models_cache:
                models_cache[model_path] = Model(model_path)
            model = models_cache[model_path]
    if model is not None:
        res.info.append('model %s (%d tabulek)' % (model.name, len(model.members)))
        model = model.with_report_measures(report_dir, res)
    else:
        res.info.append('model nenalezen - kontrola poli preskocena')

    # ---- stranky vs. disk ----
    with open(pages_json, encoding='utf-8') as f:
        pj = json.load(f)
    order = pj.get('pageOrder', [])
    on_disk = {d for d in os.listdir(pages_dir)
               if os.path.isdir(os.path.join(pages_dir, d))}
    for extra in sorted(on_disk - set(order)):
        res.err('stranka %s je na disku, ale neni v pageOrder' % extra)
    for missing in sorted(set(order) - on_disk):
        res.err('stranka %s je v pageOrder, ale neni na disku' % missing)
    if pj.get('activePageName') and pj['activePageName'] not in order:
        res.err('activePageName %s neni v pageOrder' % pj['activePageName'])

    # ---- prochazeni stranek a vizualu ----
    coll = RefCollector()
    navs = []
    seen_visual_names = {}
    page_count = 0

    for pid in order:
        if pid not in on_disk:
            continue
        page_count += 1
        pfile = os.path.join(pages_dir, pid, 'page.json')
        with open(pfile, encoding='utf-8') as f:
            page = json.load(f)
        if page.get('name') != pid:
            res.err('page.name = %r nesouhlasi s nazvem slozky' % page.get('name'), pid)
        coll.walk(page, '%s/page.json' % pid)

        vdir = os.path.join(pages_dir, pid, 'visuals')
        if not os.path.isdir(vdir):
            continue
        for vid in sorted(os.listdir(vdir)):
            where = '%s/%s' % (pid, vid)
            vfile = os.path.join(vdir, vid, 'visual.json')
            if not os.path.isfile(vfile):
                res.err('chybi visual.json', where)
                continue
            with open(vfile, encoding='utf-8') as f:
                text = f.read()
            visual = json.loads(text)
            if visual.get('name') != vid:
                res.err('visual.name = %r nesouhlasi s nazvem slozky'
                        % visual.get('name'), where)
            if visual.get('name') in seen_visual_names:
                # Power BI generuje jmena unikatni v celem reportu; duplicita vznika
                # kopirovanim stranky. Nerozbije to vizual, ale zalozky adresuji
                # vizual jmenem, takze se muze chytit ta spatna.
                res.warn('duplicitni jmeno vizualu %s, uz je na strance %s'
                         % (visual.get('name'), seen_visual_names[visual['name']]), where)
            else:
                seen_visual_names[visual.get('name')] = pid
            coll.walk(visual, where)
            for m in NAV_RE.finditer(text):
                navs.append((where, m.group(1)))

    # ---- navigace ----
    for where, target in navs:
        if target not in order:
            res.err('navigace na stranku %s, ktera v reportu neni' % target, where)

    # ---- odkazy na model ----
    if model:
        def sort_key(item):
            return tuple('' if x is None else str(x) for x in item)

        for table, where in sorted(coll.tables, key=sort_key):
            if not model.has_table(table):
                res.err('tabulka %s v modelu neni' % table, where)
        for table, prop, where in sorted(coll.members, key=sort_key):
            if not model.has_table(table):
                res.err('tabulka %s v modelu neni (odkaz na pole %s)' % (table, prop), where)
            elif not model.has_member(table, prop):
                jinde = model.tables_with_member(prop)
                v_reportu = [t for t in jinde if ':' in t]
                if v_reportu and ':' not in table:
                    # bez Schema hleda Power BI miru v modelu a vizual skonci chybou
                    res.err('%s[%s] je mira ulozena v reportu, odkaz musi mit SourceRef.Schema "%s"'
                            % (table, prop, v_reportu[0].split(':', 1)[0]), where)
                elif jinde:
                    res.warn('%s[%s] v te tabulce neni, ale existuje v %s '
                             '- odkaz ma spatnou domovskou tabulku'
                             % (table, prop, ', '.join(jinde)), where)
                else:
                    res.err('%s[%s] v modelu neni' % (table, prop), where)
        for table, hier, level, where in sorted(coll.hier, key=sort_key):
            if not model.has_table(table):
                res.err('tabulka %s v modelu neni (hierarchie %s)' % (table, hier), where)
            elif not model.has_hierarchy(table, hier):
                res.err('hierarchie %s[%s] v modelu neni' % (table, hier), where)
            elif level is not None and not model.has_level(table, hier, level):
                res.err('hierarchie %s[%s] nema uroven %s' % (table, hier, level), where)
        for table, where in sorted(coll.metadata, key=sort_key):
            if not model.has_table(table):
                res.warn('selector.metadata ukazuje na tabulku %s mimo model '
                         '(mrtvy zbytek, typicky columnWidth)' % table, where)

    # ---- obrazky ----
    rdir = os.path.join(report_dir, 'StaticResources', 'RegisteredResources')
    on_disk_res = set(os.listdir(rdir)) if os.path.isdir(rdir) else set()
    declared = set()
    rjson = os.path.join(report_dir, 'definition', 'report.json')
    if os.path.isfile(rjson):
        with open(rjson, encoding='utf-8') as f:
            for pack in json.load(f).get('resourcePackages', []):
                if pack.get('name') == 'RegisteredResources':
                    declared |= {i.get('path') for i in pack.get('items', [])}
    for name in sorted(coll.resources - on_disk_res):
        res.err('obrazek %s je pouzity ve vizualu, ale chybi v RegisteredResources' % name)
    for name in sorted(coll.resources - declared):
        res.err('obrazek %s je pouzity ve vizualu, ale neni v report.json' % name)
    for name in sorted(on_disk_res - declared):
        res.warn('soubor %s je v RegisteredResources, ale neni v report.json' % name)

    res.info.append('%d stranek, %d vizualu, %d navigacnich tlacitek'
                    % (page_count, len(seen_visual_names), len(navs)))
    return res


# ==============================================================================
# hledani modelu a reportu
# ==============================================================================

def discover_models(root):
    out = []
    for dirpath, dirnames, _ in os.walk(root):
        if '.git' in dirnames:
            dirnames.remove('.git')
        for d in list(dirnames):
            if d.endswith('.SemanticModel'):
                out.append(os.path.join(dirpath, d))
                dirnames.remove(d)
    return sorted(out)


def discover_reports(root):
    out = []
    for dirpath, dirnames, _ in os.walk(root):
        if '.git' in dirnames:
            dirnames.remove('.git')
        for d in list(dirnames):
            if d.endswith('.Report'):
                out.append(os.path.join(dirpath, d))
                dirnames.remove(d)
    return sorted(out)


def find_repo_root(start):
    p = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(p, '.git')):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            return os.path.abspath(start)
        p = parent


# ==============================================================================
def main(argv):
    ap = argparse.ArgumentParser(
        description='Kontrola PBIR reportu proti semantickemu modelu v TMDL.')
    ap.add_argument('cesta', nargs='?', default='.',
                    help='adresar k prohledani (vychozi: aktualni)')
    ap.add_argument('--report', help='konkretni *.Report adresar')
    ap.add_argument('--model', help='konkretni *.SemanticModel adresar (jen s --report)')
    ap.add_argument('--quiet', action='store_true', help='vypsat jen reporty s problemy')
    ap.add_argument('--verbose', action='store_true',
                    help='vypsat vsechna mista vyskytu, ne jen prvni tri')
    args = ap.parse_args(argv)

    if args.model and not args.report:
        print('--model jde pouzit jen spolu s --report', file=sys.stderr)
        return 2

    repo_root = find_repo_root(args.cesta if not args.report else args.report)
    models_cache = {}
    forced_model = None

    if args.report:
        if not os.path.isdir(args.report):
            print('%s neexistuje' % args.report, file=sys.stderr)
            return 2
        reports = [args.report]
        if args.model:
            if not os.path.isdir(args.model):
                print('%s neexistuje' % args.model, file=sys.stderr)
                return 2
            forced_model = Model(args.model)
    else:
        if not os.path.isdir(args.cesta):
            print('%s neexistuje' % args.cesta, file=sys.stderr)
            return 2
        reports = discover_reports(args.cesta)

    if not reports:
        print('Zadny *.Report adresar nenalezen v %s' % os.path.abspath(args.cesta))
        return 0

    results = [check_report(rd, repo_root, models_cache, forced_model) for rd in reports]

    total_err = total_warn = 0
    for res in results:
        total_err += res.n_errors
        total_warn += res.n_warnings
        if args.quiet and not res.errors and not res.warnings:
            continue
        print('=' * 78)
        print(res.label)
        for i in res.info:
            print('   %s' % i)
        for line in res.lines('CHYBA', res.errors, args.verbose):
            print(line)
        for line in res.lines('VAROVANI', res.warnings, args.verbose):
            print(line)
        if not res.errors and not res.warnings:
            print('   OK')

    print('=' * 78)
    print('Reportu: %d | chyb: %d | varovani: %d' % (len(results), total_err, total_warn))
    return 1 if total_err else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
