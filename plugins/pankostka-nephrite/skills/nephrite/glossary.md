# Pojmy Heliosu

Doplněk skillu `pankostka-nephrite`. Čísla pořadačů a dalších objektů se liší mezi databázemi a patří do repa projektu nebo organizace.

| Pojem | Popis |
| --- | --- |
| CN | Sloupec `cislo_nonsubjektu`. Primární klíč pro nonsubjektové třídy. Jako sufix sloupce znamená vazbu na nonsubjektovou tabulku: `UhradaCN`, `FrcCN`. |
| CS | Sloupec `cislo_subjektu`. Primární klíč pro subjektové třídy. Jako sufix sloupce znamená vazbu na subjektovou tabulku: `DoklCS`, `OrgCS`. |
| DUZP | Datum uskutečnění zdanitelného plnění. U dokladů bez DPH datum případu. |
| DVZ | Dynamický vztah. Umožňuje provázat dva doklady přes mezitabulku M:N. |
| FD | Faktura došlá. |
| FV | Faktura vydaná. |
| GUNID | Globální identifikátor záznamu (třeba `00000A00001T003KW7`), podle kterého XML rozhraní a offline import dohledávají záznam, když třída nemá jiné klíčové atributy. Při importu s volbou Vždy vkládat dostane záznam nový GUNID. |
| HeliosGreenXmlTask | Konzolová utilita, která pošle aplikačnímu serveru XML zprávu (spuštění funkce, `RETRIEVE`, `INSERTUPDATE`) podle příkazového souboru a odpověď uloží do souboru. Používá se v jobech. Viz `xml-task.md`. |
| Odkaz na funkci | Příkazový soubor pro `HeliosGreenXmlTask` vytvořený v Heliosu funkcí Vytvoření odkazu: přihlášení se šifrovaným heslem a příkaz `RUN`. |
| Offline export, offline import | Základní operace nad přehledem: export záznamů do XML souboru (zpráva `RETRIEVE` převedená na `INSERTUPDATE`) a jeho import do téže nebo jiné databáze. Třídy, vztahy a kategorie zapisuje symbolicky, takže sedí i mezi databázemi. |
| Šablona přehledu | Uložené sloupce, řazení a filtry přehledu jedné třídy (třída 20 Šablony, `nazev_pbl = 'gsb'`). Viz `grid-template.md`. |
| ManVysl | Manažerská výsledovka. Uživatelsky udržovaný číselník řádků manažerského výkazu, jiný pohled na náklady a výnosy než legislativní účtová osnova. Kde je vedená a v jakém pořadači, patří do repa projektu. |
| NO | Nákladový okruh. Číselník v Heliosu, účetní dimenze. |
| NSP | Procedura, kterou uživatel spouští jako **funkci nad přehledem**. Má povinnou signaturu `(@System_InputRecordNumber INT, @System_ResultRecordNumber INT OUTPUT)`. **Pozor na kolizi:** v datovém skladu znamená `nsp` plnicí proceduru (`nsp10`, `nsp20`, `nsp30`). |
| Pořadač | Číselná řada v rámci třídy. Čísla pořadačů se liší mezi databázemi. |
| PRVD | Prvotní doklad: doklad, který se účtuje, tedy z něj vzniká zápis do účetního deníku. FV, FD, interní doklad, výdejka a podobně. |
| Stav skladu | Tabulka `lcs.stav_sk`, jeden řádek za kombinaci kmenové karty (`zdroj`) a skladu. Řídí sledování šarží a dalších dimenzí, kmenová karta pro ně nese jen výchozí hodnotu. |
| Třída | Třída eviduje doklady stejného typu (FV, FD, výdejky). Pro třídu je buď jedna tabulka, nebo dvě u položkových tříd. Subjektová třída má ještě duplicitní řádek v tabulce `lcs.subjekty` kvůli jednoznačnosti v rámci celé databáze. |
| UD | Účetní druh. Uživatelsky definovaný číselník v Heliosu. |
| UDA | Uživatelsky definované atributy. Tabulka se stejným názvem jako třída, jen s prefixem `UDA_`. Zakládá je správce, ne vývojář. |
| UDF | Uživatelsky definovaný formulář: formulářová šablona třídy (třída 983 Šablony formulářů) vytvořená ve FormBuilderu, uložená v `lcs.noris_form_templates`. Nezaměňovat s uživatelskou funkcí v SQL. Viz `user-form.md`. |
| FormBuilder | Nástroj Heliosu na úpravu vzhledu formuláře (`FormBuilder.exe` u klienta, nebo `NorisWin32.exe /fb`). Ukládá formulářové šablony do databáze. |
| Útvar | Číselník v Heliosu, účetní dimenze. V manažerské výsledovce druhý rozlišovací znak vedle účtu. |
