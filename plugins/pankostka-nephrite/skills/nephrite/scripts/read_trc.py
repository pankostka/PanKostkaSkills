#!/usr/bin/env python3
"""Rozbor trace ze SQL Profileru (soubor .trc) bez SQL Serveru, ze skillu pankostka-nephrite.

Použití: read_trc.py <soubor.trc> [počet dotazů ve výpisu, výchozí 25]
Výstup: časový rozsah, součet doby dotazů proti délce trace, mezery mezi dotazy a dotazy seskupené podle textu s nahrazenými literály, seřazené podle doby.

Formát .trc: za hlavičkou souboru jde řada sloupců ve tvaru ID sloupce (2 bajty), délka (1 bajt, 0xFF = následuje délka na 4 bajtech) a hodnota.
Událost začíná sloupcem 0xFFF6, jehož hodnota nese třídu události. Doba (sloupec 13) je v mikrosekundách.
Čte jen události RPC:Completed (10) a SQL:BatchCompleted (12). Ověřeno na trace z Profileru nad SQL Server 2019.
Jen standardní knihovna.
"""
import re
import struct
import sys
from collections import defaultdict

COL_TEXT, COL_SPID, COL_DURATION, COL_START, COL_READS, COL_WRITES, COL_CPU = 1, 12, 13, 14, 16, 17, 18
EVENT_START = 0xFFF6
COMPLETED = (10, 12)


def read_events(path):
    data = open(path, "rb").read()
    pos = data.find(b"\xf6\xff\x06")  # první událost
    events, cur = [], None
    while 0 <= pos < len(data) - 3:
        col = struct.unpack_from("<H", data, pos)[0]
        ln = data[pos + 2]
        pos += 3
        if ln == 0xFF:
            ln = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        val = data[pos:pos + ln]
        pos += ln
        if col == EVENT_START:
            if cur:
                events.append(cur)
            cur = {"ev": struct.unpack_from("<H", val, 0)[0]}
        elif cur is None:
            continue
        elif col == COL_TEXT:
            cur["text"] = val.decode("utf-16-le", "replace")
        elif col in (COL_DURATION, COL_READS, COL_WRITES, COL_CPU, COL_SPID) and ln in (4, 8):
            cur[col] = struct.unpack("<q" if ln == 8 else "<i", val)[0]
        elif col == COL_START and ln == 16:
            y, m, _, d, h, mi, s, ms = struct.unpack("<8H", val)
            cur["start"] = h * 3600 + mi * 60 + s + ms / 1000
    if cur:
        events.append(cur)
    return events


def norm(text):
    text = re.sub(r"'[^']*'", "'?'", text)
    text = re.sub(r"\b\d+(\.\d+)?\b", "#", text)
    return re.sub(r"\s+", " ", text).strip()[:250]


def hms(sec):
    return f"{int(sec // 3600):02}:{int(sec % 3600 // 60):02}:{sec % 60:06.3f}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    events = read_events(sys.argv[1])
    done = [e for e in events if e["ev"] in COMPLETED]
    times = sorted(e["start"] for e in events if "start" in e)
    if not times:
        print("V souboru nejsou žádné události s časem začátku.")
        sys.exit(1)
    span = times[-1] - times[0]
    db = sum(e.get(COL_DURATION, 0) for e in done) / 1e6
    gaps = sum(b - a for a, b in zip(times, times[1:]) if b - a > 1)
    print(f"Trace {hms(times[0])} až {hms(times[-1])}, {span:.0f} s, událostí {len(events)}, dokončených dotazů {len(done)}")
    print(f"Doba dotazů v databázi celkem {db:.1f} s, tj. {100 * db / span if span else 0:.1f} % délky trace")
    print(f"Mezery nad 1 s mezi událostmi celkem {gaps:.0f} s (trace bez provozu, nebo čekání mimo databázi)")
    print()
    groups = defaultdict(lambda: [0, 0.0, 0, 0])
    for e in done:
        g = groups[norm(e.get("text", ""))]
        g[0] += 1
        g[1] += e.get(COL_DURATION, 0) / 1e6
        g[2] += e.get(COL_READS, 0)
        g[3] += e.get(COL_CPU, 0)
    print("počet | doba s | čtení | CPU ms | dotaz")
    for text, (n, dur, reads, cpu) in sorted(groups.items(), key=lambda x: -x[1][1])[:top]:
        print(f"{n} | {dur:.2f} | {reads} | {cpu} | {text}")


if __name__ == "__main__":
    main()
