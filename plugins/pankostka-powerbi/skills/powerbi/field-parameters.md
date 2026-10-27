# Field parameters

Doplněk skillu `pankostka-powerbi`.

Field parameter (parametr polí) je kalkulovaná tabulka, ze které si uživatel ve sliceru vybírá, jaká míra nebo jaký atribut se ve vizuálu zobrazí. Fyzicky žije v modelu, ale obsahem je to **reportový** artefakt: vlastníkem seznamu je konkrétní report, ne model.

## Pojmenování

`powerbi/select-name` **`Select[Dim]<Rozsah>[_TI][A|B]`**: PascalCase, bez diakritiky, bez pomlčky (pomlčka je vyhrazená pro sufixy `-VZOR`, `-DRAFT` a `-TMP`).

| Část | Význam | Příklad |
| --- | --- | --- |
| `Select` | systémový prefix. Tabulky nejdou dát do display folderu, takže prefix je jediná páka, jak je v seznamu polí seřadit k sobě | - |
| `Dim` | **přítomné**: vybírá atributy dimenzí, **chybí**: vybírá míry. Zvláštní značka pro míry není potřeba, `Dim` odlišuje menšinový případ | `SelectProdej` (míry), `SelectDimDatum` (atributy) |
| `<Rozsah>` | doména. Pokud možno jméno existujícího objektu: faktovka u měr, dimenze u jednodimenzního seznamu, jinak téma reportu | `SelectProdej`, `SelectDimProdej` |
| `_TI` | seznam obsahuje **časové varianty jedné míry**, ne různé míry. `<Rozsah>` je pak jméno té základní míry. Podtržítko a pozice na konci drží `SelectTržba` a `SelectTržba_TI` v seznamu polí u sebe | `SelectTržba_TI` |
| `A`, `B` | **jen** když je stejný seznam potřeba dvakrát v jednom vizuálu (řádky i sloupce matice). Z názvu je pak vidět, že jde o pár se shodným obsahem | `SelectDimProdejA`, `SelectDimProdejB` |

**Sufix `All` nepoužívej.** "Všechno" je slib, který nejde dodržet: každý seznam je kurátorovaný, otázka je jen *pro co*. Rozsah pojmenuj podle reportu nebo tématu, tím seznam dostane vlastníka.

## Obsah

`powerbi/select-content`

- **Strop asi 30 položek.** Delší dropdown je nepoužitelný. Když je potřeba víc, rozděl seznam podle tématu.
- **Jen viditelné, smysluplné atributy.** Nikdy surrogátní klíče ani skryté sloupce. Z dimenze jeden reprezentant na úroveň: `Účet ČísNáz`, ne Číslo, Název a ČísNáz zvlášť.
- **Časové varianty do seznamu základních měr nepatří.** Míra a její varianty za minulý rok, YTD a klouzavé okno v jednom seznamu jsou kombinatorická past. Základní míry jdou do `Select<Faktovka>`, časový pohled do samostatného `Select<Základ>_TI` jako druhá osa vizuálu.
- Řazení drží skrytý sloupec `Order` s hodnotami `0..n` průběžně. Pořadí je business, ne abecední.

## Ve vizuálu

**V `projections` vizuálu jsou skutečná pole, parametr se uvádí zvlášť v bloku `fieldParameters`.** Sloupec field parameteru zapsaný přímo jako projekce Desktop odmítne hláškou "Can't determine relationships between the fields". `validate_pbir_corpus.py` tuhle chybu hlásí.

## Na co si dát pozor

- **Field parameter je vázaný na jednu základní míru, ne na model.** `NAMEOF` odkazuje na konkrétní míru, takže časový přepínač nad jednou mírou platí jen pro ni. Pro další základ musí existovat jeho vlastní varianty i tabulka `Select<Základ>_TI`. Přepínání času nezávislé na míře umí **jen** calculation group.
- **Hierarchii do field parameteru dát nelze.** `NAMEOF` bere jen sloupec nebo míru, hierarchie se musí rozepsat po úrovních.
- **Přejmenování míry nebo sloupce, který je v `NAMEOF`, shodí kalkulovanou tabulku při refreshi.** Je to hlasité, na rozdíl od mrtvých odkazů v PBIR, ale je to důvod navíc nepřejmenovávat bez potvrzení.
- **Sloupec se jmenuje stejně jako tabulka** a uživatel to jméno vidí jako výchozí titulek sliceru. Neřeš to přejmenováním sloupce, Desktop to jméno generuje a nástroje ho tak čekají. Titulek nastav ve vizuálu.
- Field parameter **nevstupuje do relací** a nepatří do `PBI_QueryOrder` (ta je jen pro tabulky se zdrojem v M). Do `model.tmdl` patří jako `ref table`.
- RLS na faktovku (`tablePermission ... = FALSE()`) field parameter neruší, `NAMEOF` je jen metadata. Míry v seznamu zůstanou a vrátí prázdno, což je záměr.
