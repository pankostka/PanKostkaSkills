# Pojmy datového skladu

Doplněk skillu `pankostka-dwh`. Zkratky konkrétních společností a zdrojů sem nepatří, jsou v repu organizace nebo projektu.

| Pojem | Popis |
| --- | --- |
| Alloc | Prefix alokační tabulky (allocation): `s20.Alloc<Entita>`, plní ji `nsp20Alloc<Entita>`. Drží podíly, podle kterých se částka faktovky rozpočítá na prvky dimenze, a každá faktovka, která rozpad potřebuje, z ní jen čte. Jinak by stejný výpočet žil v několika procedurách a rozešel se. Není to dimenze ani faktovka. Plní se mezi faktovkami: po těch, ze kterých čte, a před těmi, které ji používají. |
| Datamart | Sada faktových a dimenzních tabulek nad jedním tématem, tedy to, co uživatel vidí v reportu. V kontextu datového skladu se pro totéž běžně říká **kostka**, v Power BI **sémantický model**, zkráceně **model** nebo **dataset**. |
| Degenerate dimension | Degenerovaná dimenze. Atribut uložený přímo ve faktovce bez vlastní dimenzní tabulky, typicky číslo dokladu nebo řádku dokladu. Nemá žádné další atributy, takže samostatná tabulka by jen opakovala faktovku řádek po řádku. Slouží k seskupení řádků a k dohledání dokladu ve zdrojovém systému. |
| Junk dimension | Dimenze sesbíraná z příznaků a indikátorů s malým počtem hodnot (ano/ne, stav, typ), které nepatří k žádné jiné dimenzi. Řádek je jedna kombinace hodnot, faktovka na ni vede jediným klíčem. Nahrazuje řadu volných sloupců ve faktovce nebo řadu drobných dimenzí. |
| Key = -1 | Řádek dimenze pro neznámou hodnotu. Existuje proto, aby faktovky nepotřebovaly outer join. Nemají ho fixní dimenze ani dimenze, jejichž hodnota je ve faktovce vždy vyplněná. |
| Kostka | Totéž co datamart. **Pozor na kolizi:** stejné slovo nese i název konkrétního sémantického modelu (`KostkaAXMain`), tedy technického objektu, ne tématu. Dokumentaci kostek řeší skill `pankostka-powerbi-wiki`. |
| SpolZkratka | Zkratka společnosti používaná v názvech objektů: `s20.DimUcet_AX`, `nsp30AXMain`. Samotné hodnoty patří do repa organizace. |
| nsp10, nsp20, nsp30 | Prefix plnicí procedury datového skladu: `nsp10HN_Mena`, `nsp20DimUcet`, `nsp30AXMain`. Číslo je vrstva. **Pozor na kolizi:** v Heliosu znamená `NSP` uživatelskou funkci nad přehledem. |
| s10, s20, s30 | Schémata vrstev datového skladu: stage, star, mart. Číslo drží pořadí plnění. |
