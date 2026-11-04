---
name: pankostka-audio-text
description: Přepis nahrávky schůzky (mp3, m4a, wav) na text lokálně přes faster-whisper na GPU - prostředí a jeho pasti (verze Pythonu, VRAM, knihovny CUDA v PATH, tichá nahrávka, kodek mp2), skript transcribe.py, výstup .txt s časovými značkami vedle zápisu ze schůzky, zápis z přepisu jako koncept. Použij, když uživatel chce přepsat nahrávku nebo z ní udělat zápis ze schůzky. S argumentem (cesta k nahrávce) ověří prostředí a vypíše, co by udělal; s --make nahrávku přepíše.
argument-hint: "[<nahrávka> [--make]]"
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/transcribe.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/transcribe.py *)
---

# Audio-text - přepis nahrávky

Jak z nahrávky schůzky vznikne textový přepis a z něj zápis. Přepis běží lokálně přes [faster-whisper](https://github.com/SYSTRAN/faster-whisper), nahrávka tedy neopouští počítač. Pravidla pro zápis jako článek (jazyk, odkazy, adresář) jsou ve skillu `pankostka-md`.

Argument: `$ARGUMENTS`

## Přepis a zápis

Ze schůzky vznikají tři soubory a každý má jinou roli:

| Soubor | Role | Příklad |
| --- | --- | --- |
| nahrávka | zdroj, mimo git | `2026-10-27 Nahrávka-TMP.mp3` |
| přepis | strojový podklad, nečte se jako dokumentace | `2026-10-27 Přepis.txt` |
| zápis | článek, ve kterém se hledá a na který se odkazuje | `2026-10-27 Harmonogram přechodu.md` |

`audio-text/txt-output` **Přepis je `.txt`, ne `.md`.** Je to podklad pro zápis, ne článek. Obsidian soubor `.txt` nezobrazí ve stromu ani v něm nehledá, takže výsledky hledání ukážou jen zápis. Kontrola `pankostka-md` se ho netýká, a proto může mít jeden úsek na řádek tak, jak ho vrátí model. V `.md` by Markdown řádky jdoucí po sobě spojil do jednoho odstavce a kontrola by hlásila stovky `md/no-hard-wrap`. Formát `.srt` se nehodí: čte se hůř a má smysl jen k přehrávání spolu s nahrávkou.

`audio-text/next-to-minutes` **Přepis leží v adresáři zápisu, vedle něj.** Patří k jedné schůzce a s jejím zápisem se přesune i smaže. Nahrávka leží tamtéž.

`audio-text/audio-tmp` **Nahrávka má sufix `-TMP`.** Je velká, binární a do gitu nepatří, viz `pankostka-git`. Přepis i zápis v gitu jsou.

`audio-text/link-from-minutes` **Odkaz vede ze zápisu na přepis, ne obráceně.** Zápis na začátku řekne, že vychází ze strojového přepisu, a odkáže na něj standardním odkazem, třeba `[automatického přepisu](2026-10-27%20Přepis.txt)`. Přepis je prostý text, odkaz v něm by nefungoval.

`audio-text/minutes-draft` **Zápis z přepisu je koncept k ověření účastníky.** Přepis nerozlišuje mluvčí a komolí jména, názvy firem, čísla a odborné pojmy. Zápis proto:

- přiřazuje úkoly ke jménům jen tam, kde to plyne z kontextu, a to výslovně řekne,
- místo, kterému z přepisu nejde rozumět, označí jako nejasné, místo aby ho domýšlel,
- na začátku má upozornění, že jde o koncept ze strojového přepisu.

Když projekt vede slovník častých chyb přepisu (zkomolená jména, pojmy), použij ho při psaní zápisu. Slovník patří do projektu, ne do tohoto skillu, protože jména jsou u každého zákazníka jiná.

## Prostředí

Skript potřebuje `ffmpeg` v `PATH` a Python s balíčky:

```bash
python -m pip install faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Na rozdíl od kontrolních skriptů ostatních skillů to bez balíčků mimo standardní knihovnu nejde. Pasti, ověřené na Windows 11 s GPU se 4 GB VRAM:

- **Verze Pythonu.** Na nejnovějším Pythonu se nemusí sestavit balíček `av`, na kterém faster-whisper stojí. Pak použij starší Python, který má hotová kola (ověřeno: 3.13 funguje, 3.15 ne), a skript spusť jeho `python.exe`, ne výchozím `python`.
- **Paměť GPU.** `compute_type="float16"` na 4 GB VRAM skončí na `CUDA out of memory`. Výchozí `int8_float16` se do 4 GB vejde i s modelem `large-v3`.
- **Knihovny CUDA.** Bez složek `nvidia/cublas/bin` a `nvidia/cudnn/bin` v `PATH` spadne model na `cublas64_12.dll is not found`. `os.add_dll_directory` nestačí. Skript je do `PATH` doplní sám z `site-packages` a vypíše je. Když je nenajde, zastaví se. V Bashi na Windows piš cestu do `PATH` jako `/c/Users/...`, ne `C:/Users/...`: dvojtečka za `C` rozdělí `PATH`.
- **Cesta k souboru v modelu.** Předání cesty k nahrávce padá v knihovně `av` na `av.open(... metadata_errors)`. Skript proto nahrávku převede přes `ffmpeg` na WAV a modelu předá pole vzorků.
- **Tichá nahrávka.** Nahrávky z Teams a rekordérů mívají kolem -53 LUFS a model v tichu vynechává. Skript hlasitost normalizuje filtrem `loudnorm`.
- **Kodek pod příponou.** Soubor `.mp3` někdy obsahuje kodek mp2. `ffmpeg` to pozná sám, jen se nespoléhej na příponu.

Na GPU se 4 GB trvají dvě hodiny nahrávky s `large-v3` přibližně hodinu.

## Postup

1. Ověř prostředí a cesty:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/transcribe.py <nahrávka> <přepis.txt> --check
   ```

   Vypíše Python, model, doplněné složky `PATH` a případné problémy, třeba už existující výstup, a skončí `CHECK OK` nebo `CHECK FAILED`.

2. Spusť přepis **na pozadí**, trvá desítky minut:

   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/transcribe.py <nahrávka> <přepis.txt> --title 2026-10-27
   ```

   Přepis se zapisuje průběžně, skript vypisuje časovou značku zpracovaného úseku a na konci `DONE`. Na ten řádek čekej, neptej se opakovaně na stav. Další přepínače: `--model` (výchozí `large-v3`), `--compute` (výchozí `int8_float16`), `--language` (výchozí `cs`), `--device cpu` bez GPU.

3. Z přepisu napiš zápis podle vzoru projektu a pravidel výše.

## Argumenty

- Bez argumentu skill jen načte zásady.
- S cestou k nahrávce spusť krok 1 a vypiš, kam by přepis vznikl, podle `audio-text/next-to-minutes`. **Nic nepřepisuj.**
- S `--make` za cestou, nebo na pokyn slovy jako *přepiš nahrávku*, proveď kroky 1 a 2. Zápis ze schůzky piš, jen když o něj uživatel požádá.
