# Tabulka ukazatelů

Doplněk skillu `pankostka-powerbi-wiki`. Tabulka ukazatelů v sekci `## Ukazatele` článku faktovky je jediné místo wiki, kam zapisuje nástroj: skript `measures_table.py`.

## Zdroj a směr

| Sloupec | Směr | Kdo píše |
| --- | --- | --- |
| Adresář, Ukazatel | model -> wiki | skript |
| DAX | model -> wiki | skript, pod tabulkou, ne v ní |
| Popis | wiki -> model (`///`) | člověk, AI navrhne |

**Zdrojem popisu míry je wiki.** Popis se píše v Obsidianu, kde vzniká zbytek dokumentace, a ne v Power BI Desktop. Zápis popisu z wiki do `///` v TMDL zatím hotový není. Do té doby skript jen vypíše míry, jejichž popis ve wiki se liší od `///`.

**Technické poznámky k míře patří do výrazu DAX** jako komentář `--`, ne do popisu `///`. Popis vidí uživatel v tooltipu Power BI, smí v něm být jen text pro uživatele. Oddělovací bannery sekcí (`/// ####`) se do TMDL nepíšou vůbec, TMDL je přilepí k popisu následující míry.

## Formát

Blok leží v sekci `## Ukazatele` mezi značkami:

```markdown
<!-- ukazatele:start - generuje skill pankostka-powerbi-wiki, ručně se píše jen sloupec Popis -->
<!-- ukazatele:end -->
```

Text nad značkami píše člověk a skript ho nemění. Mimo značky skript nezapisuje nic. **Značky vkládá člověk**, nebo AI při zakládání nového článku. Do rozeditovaného článku je AI nevkládá. Skript rozpozná i starší text za `ukazatele:start` a při zápisu ho nahradí současným.

| Sloupec | Obsah |
| --- | --- |
| Adresář | `displayFolder`, celá cesta s `\`, vyplněný v každém řádku |
| Ukazatel | název míry přesně jako v modelu |
| Popis | jedna až dvě věty pro uživatele, aby se vešly do tooltipu |

- **Adresář v každém řádku**, ne jen u prvního ve skupině. Řádek tak nezávisí na sousedech a skript ho spáruje i po ruční úpravě.
- **Pořadí jako v seznamu polí:** na každé úrovni nejdřív míry, pak podsložky, obojí abecedně podle české kolace. Jinak `#`, `Ø` a diakritika skončí jinde než v Power BI.
- **Jen viditelné míry.** Skryté a míry ve složkách `hide` a `skryto` do tabulky nepatří.

## Párování a přejmenování

Řádek se páruje s mírou **podle názvu**. Nová míra dostane jako počáteční popis svůj `///` z TMDL, takže se tabulka naplní i poprvé. Míra, která z modelu zmizela, z tabulky vypadne a skript vypíše její popis, aby se neztratil. Když zároveň nějaká míra přibyla, ohlásí možné přejmenování. **Popis sám nepřenáší**, přejmenování potvrzuje člověk.

`lineageTag` jako skrytý klíč v buňce je zamítnutý: HTML komentář v buňce ruší při editaci v Obsidianu.

## Popis

- Prostý text. Povolené jsou jen `zpětné apostrofy` kolem názvů měr a wikilinky. Do `///` půjdou jako prostý text, tooltip v Power BI Markdown neumí.
- Svislítko v buňce se píše `\|`, i v aliasu wikilinku. Obsidian to v tabulce vyžaduje.
- **Prázdná buňka znamená, že míra nemá popis.**
- Delší vysvětlení patří do textu nad tabulkou nebo do sekce Na co si dát pozor.

**Návrhy AI k popisům nepatří do buňky.** Synchronizace by je poslala do modelu dřív, než je člověk přečte. Patří do calloutu `Návrh AI` pod blokem, mimo značky, jeden řádek na míru:

```markdown
> [!navrh-ai] Návrh AI
> - `#Klientů LY△` - Rozdíl počtu klientů proti stejnému dni loni.
```

Člověk návrh přijme přesunem do buňky a smazáním řádku z calloutu.

## DAX

Pod tabulkou, uvnitř značek, je jeden sbalený callout `> [!dax]- Výpočty (DAX)`. V něm u každé míry název tučně a blok kódu `dax`, ve stejném pořadí jako tabulka. Komentáře `--` se zobrazí i tady, a to je v pořádku: kdo čte DAX, je čtenář i pro ně.

Jeden callout, ne callout na míru: dvacet sbalených calloutů pod sebou je delší než tabulka.

## Spuštění

```
python ${CLAUDE_SKILL_DIR}/scripts/measures_table.py <adresář kostky> <Faktovka> --check
python ${CLAUDE_SKILL_DIR}/scripts/measures_table.py <adresář kostky> <Faktovka>
```

Adresář kostky obsahuje `<Kostka>.SemanticModel` a `Wiki<Kostka>/`. `--check` nic nezapíše. Návratový kód `0` znamená, že blok je aktuální nebo byl zapsán, `1` že by se při `--check` změnil, `2` chybu, třeba chybějící značky.

## Otevřené

- ⚠️ Ověřit, že podokno Data v Power BI Desktop řadí stejně jako seznam polí v Excelu, podle kterého je pořadí ověřené.
- Zápis popisu z wiki do `///` v TMDL.
