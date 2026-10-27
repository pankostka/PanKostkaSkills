#!/usr/bin/env python3
"""Vyrobí testovací vaulty pro check_md.py.

Testy porušují pravidla záměrně: zakázané znaky, mezery na konci řádku, BOM a cp1250. Editor i nástroje AI by je při zápisu tiše opravily, proto vznikají tímhle skriptem.
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


# --- ok_article: vzorový článek, porušení jen v kódu, komentáři a -TMP
w("ok_article/Článek Vzor.md", f"""---
title: Vzorový článek
date: 2026-10-27
tags:
  - Obsidian
  - Markdown
---
Úvodní odstavec na jednom řádku, ať je jakkoli dlouhý, a znak `—` v inline kódu se nepočítá.

## Sekce

Odkaz na [[Druhý Článek]] a na [[#Sekce]] uvnitř článku.

![Schéma prvního kroku](Attachments/schema_krok1.png)

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
w("ok_article/Druhý Článek.md", """---
tags: [Obsidian, PowerBI]
---
Druhý článek.
""")
w("ok_article/Attachments/schema_krok1.png", "")
w("ok_article/Poznámky-TMP.md", "Dočasný článek — se nekontroluje.\nA je zalomený.\n")
w(f"ok_article/Veřejný {G}.md", f"Odkaz na [[Druhý Veřejný {G}]] a [[Neexistující]].\n")
w(f"ok_article/Druhý Veřejný {G}.md", "Veřejný článek.\n")

# --- ok_blocks: bloky za sebou bez prázdného řádku nejsou zalomení
w("ok_blocks/Bloky.md", """# Nadpis
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
![Popis](Attachments/obr.png)

Text a pod ním čára.
---
""")

# --- ko_chars
w("ko_chars/Článek.md", """<!-- celkem 4 -->
Věta — s dlouhou pomlčkou.
Odstavec s „uvozovkami“.

Tři… tečky.

Rozměr 2×3 a `—` v kódu.
""".replace("pomlčkou.\nOdstavec", "pomlčkou.\n\nOdstavec"))

# --- ko_wrap
w("ko_wrap/Článek.md", """<!-- celkem 4 -->
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

# --- ko_image
w("ko_image/Článek.md", """<!-- celkem 5 -->
![[obrazek.png]]

![](Attachments/bez_popisu.png)

![Popis](img/jinde.png)

![](jinde_bez_popisu.png)

![[Jiný článek]] se nehlásí, je to vložený článek.
""")

# --- ko_frontmatter
w("ko_frontmatter/Článek.md", """---
titul: Starý titulek
datum: 2026-10-27
publish: true
date: 27.10.2026
tags: [obsidian, Power BI, _KostkaEKO, Údržba]
---
<!-- celkem 6 -->
Text.
""")

# --- ko_attachment
w("ko_attachment/Článek.md", """<!-- celkem 2 -->
![Vložený obrázek](Attachments/Pasted%20image%2020260727145759.png)

![Schéma](Attachments/Schema-Krok1.png)
""")
w("ko_attachment/Attachments/Pasted image 20260727145759.png", "")
w("ko_attachment/Attachments/Schema-Krok1.png", "")

# --- ko_tag
w("ko_tag/A.md", "---\ntags: [Obsidian]\n---\n<!-- celkem 1 -->\nA.\n")
w("ko_tag/B.md", "---\ntags:\n  - Obsidian\n---\nB.\n")
w("ko_tag/C.md", "---\ntags: [OBSIDIAN]\n---\nC.\n")

# --- ko_publish
w(f"ko_publish/Veřejný {G}.md", f"""<!-- celkem 3 -->
Odkaz na [[Interní]] a na [[Druhý {G}]].

![[Interní]]

Markdown odkaz na [interní článek](Interní.md).
""")
w("ko_publish/Interní.md", f"Interní článek smí odkazovat na [[Veřejný {G}]].\n")
w(f"ko_publish/Druhý {G}.md", "Veřejný.\n")

# --- ko_encoding
w("ko_encoding/S BOM.md", "<!-- celkem 2 -->\nČlánek s BOM.\n", bom=True)
w("ko_encoding/Cp1250.md", "Článek v kódování Windows-1250.\n", enc="cp1250")
