# Přepis nahrávky na text přes faster-whisper.
#
# Použití:
#   python transcribe.py <nahrávka> <výstup.txt> [--title TEXT] [--model large-v3] [--compute int8_float16] [--language cs] [--check]
#
# Nahrávku nejdřív převede ffmpeg na WAV 16 kHz mono s normalizací hlasitosti, pak ji přepíše model.
# Výstup je prostý text: hlavička a jeden úsek s časovou značkou na řádek. Zapisuje se průběžně,
# na konci se vypíše řádek DONE. S --check jen ověří prostředí a vypíše, co by udělal.
#
# Na rozdíl od kontrolních skriptů ostatních skillů potřebuje balíčky mimo standardní knihovnu:
# faster-whisper (s ním numpy) a pro GPU nvidia-cublas-cu12 a nvidia-cudnn-cu12. Viz SKILL.md.

import argparse, os, shutil, subprocess, sys, tempfile, wave

# Typografické znaky z Whisperu na znaky z klávesnice, stejně jako md/keyboard-chars.
CHARS = {"—": "-", "–": "-", "„": '"', "“": '"', "”": '"', "‚": "'", "‘": "'", "’": "'", "…": "...", "×": "x"}


def clean(text):
    for a, b in CHARS.items():
        text = text.replace(a, b)
    return text.strip()


def ts(seconds):
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def add_nvidia_to_path():
    # Knihovny CUDA z balíčků nvidia-* musí být v PATH dřív, než se načte ctranslate2.
    # os.add_dll_directory nestačí. Vrací nalezené složky.
    import site
    found = []
    roots = list(site.getsitepackages()) + [site.getusersitepackages()]
    for root in roots:
        for lib in ("cublas", "cudnn"):
            d = os.path.join(root, "nvidia", lib, "bin")
            if os.path.isdir(d) and d not in found:
                found.append(d)
    if found:
        os.environ["PATH"] = os.pathsep.join(found) + os.pathsep + os.environ.get("PATH", "")
    return found


def to_wav(src, dst):
    # Nahrávky z Teams a rekordérů bývají tiché, loudnorm je srovná. Přípona .mp3 někdy skrývá kodek mp2, ffmpeg to pozná sám.
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "16000", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", dst]
    subprocess.run(cmd, check=True)


def load_wav(path):
    import numpy as np
    with wave.open(path, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("out")
    ap.add_argument("--title", help="text za 'Přepis nahrávky' v hlavičce, výchozí je název nahrávky")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--compute", default="int8_float16", help="float16 potřebuje víc než 4 GB VRAM")
    ap.add_argument("--language", default="cs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--check", action="store_true", help="jen ověř prostředí a vypiš, co by se udělalo")
    a = ap.parse_args()

    title = a.title or os.path.splitext(os.path.basename(a.audio))[0]
    problems = []
    if not os.path.isfile(a.audio):
        problems.append(f"nahrávka neexistuje: {a.audio}")
    if shutil.which("ffmpeg") is None:
        problems.append("ffmpeg není v PATH")
    nvidia = add_nvidia_to_path() if a.device == "cuda" else []
    if a.device == "cuda" and not nvidia:
        problems.append("nenalezeny knihovny nvidia/cublas a nvidia/cudnn, nainstaluj nvidia-cublas-cu12 nvidia-cudnn-cu12")
    try:
        import faster_whisper  # noqa: F401
    except ImportError as e:
        problems.append(f"chybí faster-whisper pro {sys.executable}: {e}")
    if os.path.exists(a.out):
        problems.append(f"výstup už existuje a přepsal by se: {a.out}")

    print(f"python: {sys.executable}")
    print(f"nahrávka: {a.audio}")
    print(f"výstup: {a.out}")
    print(f"model: {a.model}, {a.device}, {a.compute}, jazyk {a.language}")
    for d in nvidia:
        print(f"PATH += {d}")
    for p in problems:
        print(f"PROBLÉM: {p}")
    if a.check:
        print("CHECK OK" if not problems else "CHECK FAILED")
        return 0 if not problems else 1
    if problems:
        return 1

    from faster_whisper import WhisperModel

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        to_wav(a.audio, wav)
        # Model dostane pole, ne cestu: cesta k souboru padá v knihovně av na av.open(... metadata_errors).
        data = load_wav(wav)

    model = WhisperModel(a.model, device=a.device, compute_type=a.compute)
    segments, info = model.transcribe(data, language=a.language, beam_size=5, vad_filter=True)

    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"Přepis nahrávky {title}\n\n")
        f.write(f"Strojový přepis nahrávky {os.path.basename(a.audio)} (faster-whisper {a.model}, jazyk {a.language}), délka {ts(info.duration)}. ")
        f.write("Nerozlišuje mluvčí, nekontrolováno, může obsahovat chyby v rozpoznání jmen a odborných pojmů.\n\n")
        for seg in segments:
            f.write(f"[{ts(seg.start)}] {clean(seg.text)}\n")
            f.flush()
            print(f"[{ts(seg.start)}] / {ts(info.duration)}", flush=True)
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
