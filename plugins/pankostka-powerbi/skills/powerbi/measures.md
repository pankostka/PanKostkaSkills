# Míry a time intelligence

Doplněk skillu `pankostka-powerbi`. Pozice zkratek v názvu míry (prefix `#` a `Ø`, suffix s tokenem, operátor za tokenem) je v `SKILL.md`.

## Časové tokeny

Posun v čase: **jeden krok zpět je `L<jednotka>`, dva a více kroků `<jednotka>-N`.** Pro dny a týdny se offsetový tvar používá i pro jeden krok (`D-1`, `W-1`), protože "LD" se nedá přečíst.

| Token | Význam |
| --- | --- |
| `LY` | stejné období minulý rok |
| `LQ` | stejné období minulý kvartál |
| `LM` | stejné období minulý měsíc |
| `Y-2`, `Y-3` | dva, tři roky zpět |
| `M-2`, `M-3` | dva, tři měsíce zpět |
| `D-1`, `W-1` | předchozí den, týden |
| `YTD` | kumulativně od začátku roku |
| `QTD`, `MTD` | kumulativně od začátku kvartálu, měsíce |
| `R12M` | klouzavých 12 měsíců. Obecně `R<N><jednotka>`, tedy i `R3M`, `R6M` |
| `<token>△` | absolutní rozdíl proti tomu období, ve stejné jednotce jako základ |
| `<token>%` | relativní změna proti tomu období |

**Kombinace tokenů: nejdřív kumulace, pak posun.** Tedy `YTD LY` (YTD loni), `R12M LY`. Ne naopak.

`YTD LY` a jeho `△` a `%` jsou u kumulativních ukazatelů povinná výbava, samotné `YTD` není proti čemu srovnat. Klouzavé okno se vždy srovnává proti předchozímu oknu (`R12M` proti `R12M LY`), nikdy proti základnímu období, to by srovnávalo měsíc s rokem.

## Pravidla pro DAX

1. **TI míra se vždy píše jako `CALCULATE([základní míra], <časová funkce>)`.** Nikdy nekopíruj tělo základní míry, jinak se pozdější změna základu do variant nepropíše.
2. **`△` a `%` se počítají z těch dvou měr**, ne znovu z faktovky. `%` se odvozuje z už existujícího `△`.
3. **V `%` je ve jmenovateli `ABS()`.** Ukazatele jako HV mohou být záporné. Bez `ABS` by ztráta zlepšená z -100 na -50 vyšla jako -50 %, tedy opačně, než jaká je skutečnost. `DIVIDE` vrátí BLANK při nulovém jmenovateli, takže se dělení nulou neřeší zvlášť.
4. **Na posuny používej `DATEADD`, ne `PREVIOUSMONTH` a `PREVIOUSYEAR`.** `PREVIOUSMONTH` vrátí celý předchozí měsíc bez ohledu na zvolenou granularitu, `DATEADD(..., -1, MONTH)` posune to, co je v kontextu. Pro rok je `DATEADD(..., -1, YEAR)` totéž co `SAMEPERIODLASTYEAR`, takže jedna funkce pokryje všechny posuny.
5. **Účetní rok předpokládej totožný s kalendářním**, pokud uživatel fiskální rok výslovně nezmíní. Pokud totožný není, patří do `DATESYTD` druhý parametr s koncem účetního roku.
6. **Nedokončené období.** `YTD LY` sebere celý loňský měsíc, i když letos jsou data jen k dnešku, a srovnání je pak systematicky pesimistické. Řeší se filtrem na příznak v date table (typicky `DimDatum[Bude] = "Bylo"`), případně odříznutím LY varianty na stejný den. V mírách to zabudované není, hlídá se to v reportu.

Vzory (`X` je základní míra, `DimDatum[Date]` klíč date table):

```dax
X LY      = CALCULATE([X], DATEADD(DimDatum[Date], -1, YEAR))
X LM      = CALCULATE([X], DATEADD(DimDatum[Date], -1, MONTH))
X Y-2     = CALCULATE([X], DATEADD(DimDatum[Date], -2, YEAR))
X YTD     = CALCULATE([X], DATESYTD(DimDatum[Date]))
X YTD LY  = CALCULATE([X YTD], DATEADD(DimDatum[Date], -1, YEAR))
X R12M    = CALCULATE([X], DATESINPERIOD(DimDatum[Date], MAX(DimDatum[Date]), -12, MONTH))
X LY△     = [X] - [X LY]
X LY%     = DIVIDE([X LY△], ABS([X LY]))
```

`formatString` je u `<token>` a `<token>△` stejný jako u základní míry (typicky `#,0`), u `<token>%` je to `0.0\ %;-0.0\ %;0.0\ %`. Display folder je stejný jako u základní míry.

## Explicitní míry, nebo calculation groups

**Time intelligence piš jako explicitní míry, i kdyby jich byly stovky.** Model to nebolí: míra je metadata, nevyhodnocuje se, dokud ji někdo nepoužije, a nemá vliv na velikost modelu ani na refresh. Přehlednost pro uživatele řeší display foldery. Jediná skutečná cena je délka souboru `.tmdl`.

Calculation group na TI **nepoužívej**. Její hlavní přínos je administrativní (ušetří ruční psaní desítek měr) a to neplatí, když míry generuje AI. Cena přitom zůstává: v celém modelu se vypnou implicitní míry (nikdo nepřetáhne surový sloupec do vizuálu a nenechá ho sečíst, což rozbije testovací sešity, které tenhle způsob předpokládají) a calculation item není adresovatelný jménem, musí být na ose, v legendě nebo ve sliceru.

Výjimkou jsou dva případy, kdy calculation group přináší **funkci**, kterou explicitní míra neumí:

- uživatel si přepíná časový pohled **interaktivně** ve sliceru a jeden vizuál se překreslí (explicitní míry na to potřebují odpojenou tabulku a `SWITCH`),
- dynamický formát přes `formatStringDefinition`, typicky přepínání jednotek tisíce a miliony.

Zbytkové riziko explicitních měr: změna definice (třeba že `%` má vracet BLANK) je hromadná úprava přes všechny míry. Je dohledatelná grepem, ale musí se projít **všechny**, opomenutá míra tiše vrací jiné číslo.

Tokeny platí v obou světech, názvy calculation items jsou tytéž zkratky. Kdyby k výjimce došlo, konvence se nemění.
