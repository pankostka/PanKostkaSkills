# HeliosGreenXmlTask a XML rozhraní

Doplněk skillu `pankostka-nephrite`. `HeliosGreenXmlTask.exe` je konzolová utilita, která pošle aplikačnímu serveru Heliosu XML zprávu a odpověď uloží do souboru. Používá se v jobech plánovače, ale poběží odkudkoli, kde je dostupná adresa aplikačního serveru, i z notebooku. Na databázový server ji kvůli tomu dávat není potřeba. Podrobný popis je v nápovědě Heliosu na stránkách `HELIOS XML Task (utilita HeliosXmlTask.exe)`, `XML rozhraní - zpráva RETRIEVE` a `Offline export a import záznamů`, viz Dokumentace Heliosu ve `SKILL.md`.

```
HeliosGreenXmlTask.exe <příkaz.xml> [<odpověď.xml>]
```

Nápověda chce verzi aspoň 1.2.2, starší může zatuhnout. Od 1.2.5 vrací návratové kódy: `0` úspěch, `18` chybný vstupní soubor, `65` server zprávu odmítl, `66` operace neskončila úspěchem (auditlog není Success), `128` neočekávaná chyba včetně chybného přihlášení.

## Příkazový soubor

Soubor `<shortcut>` má dvě části: `<connection>` (URL aplikace, databázový profil, uživatel, šifrované heslo, jazyk) a `<commands>` s jedním nebo víc příkazy. **Nejsnáz ho vytvoří Helios sám** funkcí Vytvoření odkazu nad přehledem funkcí. Na záložce Připojení a přihlášení zvol Zadat parametry ručně a vyplň heslo, Helios ho uloží zašifrované. Odkaz vytvořený volbou Vzdálené přihlášení se nepřihlásil (`ServiceGate.LogOn ... Chybné přihlašovací údaje`). Heslo jde zašifrovat i utilitou `MakePass` z adresáře Tools aplikačního serveru.

`nephrite/xmltask-secret` **Soubor s heslem do repa nepatří.** Kdo ho má, může ho upravit a spustit pod tím účtem cokoli. Do repa patří jen část `<commands>` nebo celý soubor s heslem nahrazeným zástupným textem. Pracovní kopie s heslem smaž hned po běhu a heslo nevypisuj ani do logu, při čtení souboru ho nahraď třeba `sed -E 's/(name="Password" value=")[^"]*/\1***/'`.

## Příkazy

V `<command>` může být libovolná zpráva XML rozhraní, nejen spuštění funkce:

| Zpráva | Co dělá |
| --- | --- |
| `RUN` | spustí funkci (`FUNCTIONID`, `CLASSID`, `FOLDERID`) nad záznamy `<RECORD SUBJECTID CLASSID/>`, nad filtrem `<FILTER FILTERID/>`, nebo bez vstupu; parametry jdou v `<params><rows><row>` nebo jako uložené parametry `<storedParams><RECORD SUBJECTID CLASSID="1496"/></storedParams>` |
| `RETRIEVE` | vrátí celé záznamy včetně vztahů a `USERDATA`, výběr části záznamu řídí atributy `masterOnly`, `explicitRelationList` a další |
| `INSERTUPDATE` | zapíše záznamy přes aplikační logiku, stejný formát jako soubor offline importu |
| `BROWSE`, `QUERYSELECT` | vrátí data přehledu, resp. výsledek SELECTu |

**`INSERTUPDATE` je podporovaná cesta k zápisu do tříd Heliosu**, včetně systémových, kam se z SQL zapisovat nesmí (`nephrite/no-write-system`). Projde editačními pravidly, triggery i kontrolou práv a zapíše se do auditlogu.

## Offline export a import z jobu

**Offline import jde spustit z jobu.** Podle nápovědy se založí klon funkce 2612 Offline import nad cílovou třídou a soubor se předá parametrem `file_name`. Cesta musí být dostupná z aplikačního serveru, ne z místa, kde běží utilita. Volba Vždy vkládat je parametr `alwaysInsert`. Zatím nevyzkoušeno.

**Offline export (funkce 2471) z jobu soubor neuloží.** Proběhne a auditlog je v pořádku, ale parametr `FileHandling = DOWNLOAD` posílá soubor ke klientovi, který tu není. Náhradou je zpráva `RETRIEVE`: vrátí totéž co offline export, jen bez práv a s kořenem `RETRIEVERESULT` místo `INSERTUPDATE`. Převod na soubor pro import je popsaný u šablon v `grid-template.md`.

## Výstup utility

**Utilita zapisuje do odpovědi tabulátor a konec řádku v hodnotě atributu nevyescapované.** Parser XML je podle normy převede na mezery, takže se při dalším čtení tiše změní data: u šablony přehledu se rozpadne seznam filtrů v `s_mark` (oddělovač je tabulátor) a výrazy ve sloupcích ztratí zalomení. Před dalším zpracováním je proto v hodnotách atributů nahraď za `&#x9;`, `&#xD;` a `&#xA;`, jak je zapisuje offline export. Výpis na konzoli je escapovaný správně, chyba je jen v souboru.

Výsledek běhu funkce je i v auditlogu (`lcs.auditlog_hlavicka`, `funject` = číslo funkce, offline import je `2612`), číslo auditlogu vypíše utilita na konzoli.
