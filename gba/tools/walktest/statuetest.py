#!/usr/bin/env python3
"""Statue test (9.4.1): for every landmark (a statue_<look> person), starts on the tile below its left end in
mGBA, checks that tile's statue blocks you (Up doesn't move you) and that A there reads its text. OUT gets
s<n>.png (the view, then the text) for each.
    python3 tools/walktest/statuetest.py [OUT]
Needs what walktest.py needs."""
import os, struct, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walktest
from gymtest import Live, BOOT

def shot(live, path):
    live.send('p ' + path + '.ppm', 'w 1')
    live.mem(0, 1)                                 # wait for the harness to write it
    return Image.open(path + '.ppm').convert('RGB')

def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'statuetest-out')
    os.makedirs(out, exist_ok=True)
    work = tempfile.mkdtemp(prefix='statuetest-')
    rom, harness = walktest.build(work, 'test_statue.inc')
    def boot(n):
        sav = os.path.join(work, 's%d.sav' % n)
        blank = bytearray(b'\xff' * 0x8000)
        blank[0x7E00:0x7E02] = struct.pack('<h', n)
        open(sav, 'wb').write(blank)
        return Live(harness, rom, sav)
    live = boot(1)
    live.send('w 30')
    live.close()
    raw = open(os.path.join(work, 's1.sav'), 'rb').read()
    at, count = struct.unpack('<I', raw[0x7E20:0x7E24])[0], struct.unpack('<h', raw[0x7E2C:0x7E2E])[0]
    print(count, 'landmarks')
    bad = []
    for n in range(1, count + 1):
        live = boot(n)
        live.send(*BOOT)
        m, x, y = struct.unpack('<hhh', live.mem(at, 6))
        view = shot(live, os.path.join(work, 'v%d' % n))
        live.send('k U 2', 'w 30')
        blocked = struct.unpack('<hhh', live.mem(at, 6)) == (m, x, y)
        live.send('k A 1', 'w 40')
        talk = shot(live, os.path.join(work, 't%d' % n))
        live.close()
        crashed = open(os.path.join(work, 's%d.sav' % n), 'rb').read()[0x7E10:0x7E14] == b'CRSH'
        said = sum(1 for px in talk.crop((0, 112, 240, 160)).getdata() if px[0] > 240 and px[1] > 240) > 400
        why = 'crash' if crashed else None if blocked and said else 'walked through' if not blocked else 'no text'
        print(n, 'map %d (%d,%d)' % (m, x, y - 1), why or 'ok', flush=True)
        bad += [n] * bool(why)
        pair = Image.new('RGB', (480, 160))
        pair.paste(view, (0, 0)); pair.paste(talk, (240, 0))
        pair.resize((960, 320), Image.NEAREST).save(os.path.join(out, 's%d.png' % n))
    print('bad:', bad or 'none')

if __name__ == '__main__':
    main()
