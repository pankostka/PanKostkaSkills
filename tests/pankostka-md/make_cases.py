#!/usr/bin/env python3
"""Vyrobí testovací vaulty pro check_md.py.

Testy porušují pravidla záměrně: zakázané znaky, mezery na konci řádku, BOM a cp1250. Editor i nástroje AI by je při zápisu tiše opravily, proto vznikají tímhle skriptem.
Každý článek leží v adresáři svého jména, jinak by každý test hlásil i md/article-folder.
Spuštění: python tests/pankostka-md/make_cases.py, pak python tests/pankostka-md/run.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
G = "\U0001F310"


def w(rel, text, enc="utf-8", bom=False):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.encode(enc)
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def a(case, name, text, **kw):
    """Článek v adresáři svého jména: <case>/<name>/<name>.md."""
    w(f"{case}/{name}/{name}.md", text, **kw)


# --- ok_article: vzorový článek, porušení jen v kódu, komentáři a -TMP
a("ok_article", "Článek Vzor", f"""---
title: Vzorový článek
date: 2026-10-27
tags:
  - Obsidian
  - Markdown
---
Úvodní odstavec na jednom řádku, ať je jakkoli dlouhý, a znak `—` v inline kódu se nepočítá.

## Sekce

Odkaz na [Druhý Článek](../Druhý%20Článek/Druhý%20Článek.md), na [tentýž článek](<../Druhý Článek/Druhý Článek.md>) v lomených závorkách a na [sekci](#sekce) uvnitř článku.

![Schéma prvního kroku](schema_krok1.png)

![Schéma druhého kroku](./schema_krok2.png)

Interní článek smí odkazovat na [měření](mereni-TMP.sql).

> [!note] Callout
> Text calloutu na jednom řádku.

- odrážka
- další odrážka
  - vnořená odrážka

| A | B |
| --- | --- |
| 1 | 2 |

```
Blok kódu: dlouhá pomlčka — „uvozovky“ … 2×3
a druhý řádek
```

Řádek s tvrdým zalomením lomítkem\\
pokračuje záměrně.

Řádek s tvrdým zalomením mezerami{"  "}
pokračuje záměrně.

<!-- komentář — se nekontroluje -->
""")
w("ok_article/Článek Vzor/schema_krok1.png", "")
w("ok_article/Článek Vzor/schema_krok2.png", "")
w("ok_article/Článek Vzor/Článek Vzor.png", "")  # náhled pro web se jmenuje jako článek
w("ok_article/Článek Vzor/Pomocný Výstup-TMP.png", "")
a("ok_article", "Druhý Článek", """---
tags: [Obsidian, PowerBI]
---
Druhý článek.
""")
w("ok_article/Poznámky-TMP.md", "Dočasný článek — se nekontroluje.\nA je zalomený.\n")
a("ok_article", f"Veřejný {G}", f"Odkaz na [Druhý Veřejný {G}](../Druhý%20Veřejný%20{G}/Druhý%20Veřejný%20{G}.md) a na [web](https://example.com).\n")
a("ok_article", f"Druhý Veřejný {G}", "Veřejný článek.\n")
# článek o objektu leží v adresáři objektu spolu s jeho kódem
a("ok_article", "nsp20DimUcet", "Plnění dimenze účtů, kód je v [nsp20DimUcet.sql](nsp20DimUcet.sql).\n")
w("ok_article/nsp20DimUcet/nsp20DimUcet.sql", "SELECT 1\n")

# --- ok_no-folder: soubory, které vlastní adresář nedostávají
w("ok_no-folder/README.md", "Rozcestník.\n\n![Logo](logo.png)\n")
w("ok_no-folder/logo.png", "")
w("ok_no-folder/CLAUDE.md", "Pravidla pro AI.\n")
w("ok_no-folder/menu.md", "Lišta.\n")
w("ok_no-folder/tasks/tasks.md", "Rozcestník úkolů.\n")
w("ok_no-folder/skills/md/SKILL.md", "Zásady.\n")
w("ok_no-folder/skills/md/glossary.md", "Slovník vedle SKILL.md.\n")

# --- ok_blocks: bloky za sebou bez prázdného řádku nejsou zalomení
a("ok_blocks", "Bloky", """# Nadpis
Odstavec hned pod nadpisem.
- odrážka hned pod odstavcem
- druhá odrážka
## Další nadpis
Odstavec.
> Citace hned pod odstavcem.

1. číslovaná
2. číslovaná

Text před tabulkou.
| A | B |
| --- | --- |

Text před obrázkem.
![Popis](obr.png)

Text a pod ním čára.
---
""")
w("ok_blocks/Bloky/obr.png", "")

# --- ok_allow: vědomá výjimka komentářem s důvodem
a("ok_allow", "Článek", """Citace dodavatele „doslova“ <!-- pankostka: allow md/keyboard-chars, citace dodavatele beze změny -->

<!-- pankostka: allow md/no-hard-wrap, adresa po řádcích -->
Firma s.r.o.
Ulice 1
""")

# --- ko_article-folder
w("ko_article-folder/Bez Adresáře.md", "<!-- celkem 2 -->\nČlánek přímo v kořeni.\n")
w("ko_article-folder/Jiný/Jiný Název.md", "Článek v adresáři jiného jména.\n")

# --- ko_keyboard-chars
a("ko_keyboard-chars", "Článek", """<!-- celkem 5 -->
Věta — s dlouhou pomlčkou.

Odstavec s „uvozovkami“.

Tři… tečky.

Rozměr 2×3 a `—` v kódu.

Výjimka bez důvodu — <!-- pankostka: allow md/keyboard-chars -->
""")

# --- ko_no-hard-wrap
a("ko_no-hard-wrap", "Článek", """<!-- celkem 4 -->
První odstavec
zalomený na dva řádky.

Druhý odstavec
zalomený
na tři řádky.

- odrážka
  pokračuje na dalším řádku

> [!note] Callout
> první řádek calloutu
> druhý řádek calloutu
""")

# --- ko_image-markdown-alt
a("ko_image-markdown-alt", "Článek", """<!-- celkem 3 -->
![[obrazek.png]]

![](bez_popisu.png)

![](taky_bez_popisu.png)

![[Jiný článek]] se nehlásí, je to vložený článek.
""")
w("ko_image-markdown-alt/Článek/bez_popisu.png", "")
w("ko_image-markdown-alt/Článek/taky_bez_popisu.png", "")

# --- ko_attachment-own-folder
a("ko_attachment-own-folder", "Článek", """<!-- celkem 3 -->
![Popis](img/jinde.png)

![Popis](../Jiný/cizi.png)

![Popis](Attachments/stary.png)
""")
w("ko_attachment-own-folder/Článek/img/jinde.png", "")
w("ko_attachment-own-folder/Jiný/cizi.png", "")
w("ko_attachment-own-folder/Článek/Attachments/stary.png", "")

# --- ko_frontmatter-keys
a("ko_frontmatter-keys", "Článek", """---
titul: Starý titulek
datum: 2026-10-27
publish: true
date: 27.10.2026
tags: [Obsidian, _KostkaEKO, Údržba]
---
<!-- celkem 4 -->
Text.
""")

# --- ko_tag-pascal-case
a("ko_tag-pascal-case", "Článek", """---
tags: [obsidian, Power BI, _KostkaEKO]
---
<!-- celkem 2 -->
Text.
""")

# --- ko_attachment-name
a("ko_attachment-name", "Článek", """<!-- celkem 2 -->
![Vložený obrázek](Pasted%20image%2020260727145759.png)

![Schéma](Schema-Krok1.png)
""")
w("ko_attachment-name/Článek/Pasted image 20260727145759.png", "")
w("ko_attachment-name/Článek/Schema-Krok1.png", "")

# --- ko_tag-one-variant
a("ko_tag-one-variant", "A", "---\ntags: [Obsidian]\n---\n<!-- celkem 1 -->\nA.\n")
a("ko_tag-one-variant", "B", "---\ntags:\n  - Obsidian\n---\nB.\n")
a("ko_tag-one-variant", "C", "---\ntags: [OBSIDIAN]\n---\nC.\n")

# --- ko_no-link-to-private
a("ko_no-link-to-private", f"Veřejný {G}", f"""<!-- celkem 3 -->
Odkaz na [Interní](../Interní/Interní.md) a na [Druhý {G}](../Druhý%20{G}/Druhý%20{G}.md).

![[Interní]]

Odkaz v lomených závorkách na [interní článek](<../Interní/Interní.md>).
""")
a("ko_no-link-to-private", "Interní", f"Interní článek smí odkazovat na [Veřejný {G}](../Veřejný%20{G}/Veřejný%20{G}.md).\n")
a("ko_no-link-to-private", f"Druhý {G}", "Veřejný.\n")

# --- ko_no-link-to-tmp
a("ko_no-link-to-tmp", f"Veřejný {G}", f"""<!-- celkem 3 -->
![Graf](graf-TMP.png)

Export do [PDF](<Veřejný {G}-TMP.pdf>).

Rozepsaný [článek](../Rozepsaný-TMP/Rozepsaný-TMP.md).
""")
a("ko_no-link-to-tmp", "Interní", "Interní článek smí odkazovat na [měření](mereni-TMP.sql).\n")

# --- ko_no-wikilink: vložení článku ![[...]] se toleruje
a("ko_no-wikilink", "Článek", """<!-- celkem 3 -->
Odkaz na [[Druhý]], s aliasem na [[Druhý|druhý článek]] a na [[Neexistující]].

![[Druhý]]
""")
a("ko_no-wikilink", "Druhý", "Druhý článek.\n")

# --- ko_no-broken-link: adresa, kotva a soubor -TMP se neověřují
a("ko_no-broken-link", "Článek", """<!-- celkem 3 -->
Odkaz na [chybějící článek](../Chybí/Chybí.md) a na [skript](<data/skript.sql>).

![Obrázek](chybi.png)

Na [web](https://example.com), na [sekci](#sekce) a na [měření](mereni-TMP.sql) se nehlásí.
""")

# --- ko_utf8-no-bom
a("ko_utf8-no-bom", "S BOM", "<!-- celkem 2 -->\nČlánek s BOM.\n", bom=True)
a("ko_utf8-no-bom", "Cp1250", "Článek v kódování Windows-1250.\n", enc="cp1250")
