# Publikace na web a do PDF

Doplněk skillu `pankostka-md`. Čte se, když se článek označuje markerem, když se upravuje veřejný článek a když se sestavuje web nebo PDF. Pravidla pro formát článku (frontmatter, tagy, obrázky s popisem) jsou v `SKILL.md` a platí pro každý článek, i neveřejný, aby byl připravený k publikaci.

Web staví [obsidian2html](https://github.com/pankostka/obsidian2html), veřejný nástroj ve vlastním repu. Do projektů se nekopíruje: kopie by se rozešla se zdrojem a kdo by ji spustil, dostal by jiný výstup, aniž by to poznal.

## Marker

**Co jde na web, určuje marker na konci názvu článku, ne frontmatter.** Třeba `Obsidian Nastavení 🌐.md`. `obsidian2html` publikuje jen články se znakem, který mu dávka předá přepínačem `--publish`, a z titulku i z adresy ho strhne.

Chybějící marker znamená neveřejné. Zveřejňuje se tak vědomým úkonem, nikdy opomenutím, a je to vidět rovnou ve stromu souborů, ne až v otevřeném článku. Web, který čte jen jeho autor, smí publikovat všechno (`--publish "*.md"`), ale i tam dávka říká nahlas, co jde ven. Klíč `publish` ve frontmatteru nástroj nečte a build na něj jen upozorní.

## Co do veřejného článku nepatří

- **Screenshoty s reálnými čísly** firmy nebo zákazníka.
- **Cokoli, co jmenuje konkrétního zákazníka.**

Do interní dokumentace to patří. Strojově to nepozná nikdo, proto se **před nasazením vypíše seznam publikovaných článků a přečte se**. Je to jediná pojistka.

## Odkazy z veřejných článků

**Veřejný článek nesmí odkazovat na neveřejný.** Marker vybírá články, ne odkazy, takže wikilink ven z té množiny projde a `obsidian2html` z něj na webu nechá jen holý text. Mrtvý odkaz sice nevznikne, ale čtenář narazí na zmínku, na kterou nejde kliknout. Opačný směr je v pořádku: interní rozcestník na veřejné články odkazovat může a má.

Série veřejných článků se proto musí odkazovat sama na sebe a všechno interní nechat na rozcestník. `obsidian2html` při buildu hlásí, kolik odkazů takhle zploštil, ale to je kontrola až po převodu. Hlídat se to má při psaní, pravidlo `publish` v `check_md.py` to umí.

## Slug

Ruční klíč `slug` ve frontmatteru je tam kvůli **stabilitě**. Jakmile je článek jednou venku, změna názvu by mu změnila adresu a rozbila odkazy zvenčí, které nikdo neopraví. U publikovaného článku proto slug jednou zapiš a už na něj nesahej, i kdyby se článek přejmenoval.

## Výstupy

Zdroj je vždy Markdown, výstupy jsou z něj odvozené a dají se kdykoli vyrobit znovu. Do gitu proto patří jinak:

| Výstup | Kam | Do gitu |
| --- | --- | --- |
| **PDF** | vedle článku, stejný název a sufix `-TMP` | ne, sufix ho vyřadí. Výjimečně se sufix odstraní a PDF se zaverzuje |
| **HTML** | kam řekne `--dest`, vždy mimo repo | ne, je to odvozený výstup |

**PDF vedle článku je záměr.** Kdo článek otevře, má u něj i to, co z něj naposledy šlo ven. Sufix `-TMP` drží tu kopii mimo historii. Když má konkrétní PDF být zaverzované (podepsaný dokument, příloha smlouvy), sufix se odstraní vědomě. Je to výjimka: git PDF nediffuje, takže každá verze uloží celý soubor znovu.

**HTML se neverzuje ani po kusech.** Zásah do šablony nebo stylu přegeneruje každou stránku a commit by vypadal jako změna všech článků. Adresář pro výstup má být **mimo repo**, aby ten commit nebyl možný, ne jen zakázaný.

**Uživatelům jde web**, tedy adresář stránek se sdíleným stylem a obrázky, ne samostatný soubor. **PDF se tiskne z prohlížeče**, když ho někdo chce jako přílohu do mailu, a vznikne i s hlavičkou a lištou webu.
