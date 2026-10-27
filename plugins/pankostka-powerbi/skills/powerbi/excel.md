# Excel nad sémantickým modelem

Doplněk skillu `pankostka-powerbi`.

Kontingenční tabulka v Excelu napojená na publikovaný model se ptá jazykem MDX a chová se jinak než vizuál v Power BI. Platí to pro tabulku klikanou ručně i generovanou skriptem.

**Ukazatel dej do tabulky dřív než řádky.** Bez ukazatele Excel nemá podle čeho vynechat prázdné kombinace (`NON EMPTY`) a vypíše všechny prvky dimenze, u dimenze dokladů tedy statisíce řádků, a Excel přestane reagovat. S ukazatelem a filtrem se tatáž tabulka postaví za pár sekund. Filtry nastav úplně nejdřív.

**`ManualUpdate` tomu nezabrání.** U tabulky nad OLAP zdrojem se Excel na model ptá po každém přidaném poli i v ručním režimu, takže pořadí polí rozhoduje, i když se tabulka sestavuje skriptem přes COM.

**Mezisoučty vypni hned při přidání pole**, ne až nakonec. V tabulkovém tvaru s několika atributy v řádcích jinak první dotaz počítá mezisoučet za každou úroveň.

**Celkový součet vypni u míry v různých měnách.** Míra v původní měně (třeba částka v měně výpisu) se přes měny sčítat nedá. Součet eur s dolary je číslo bez významu, a přitom vypadá jako výsledek.

**Skrytý sloupec s `isAvailableInMdx: false` v Excelu není vidět.** To je záměr u skrytých sloupců faktovek. Na dimenzích se vlastnost nenastavuje, jejich atributy kontingenční tabulky používají.

**OLS v Excelu shodí tabulku, RLS ne.** Podrobnosti jsou v `roles.md`.
