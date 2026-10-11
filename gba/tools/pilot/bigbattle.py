#!/usr/bin/env python3
"""The big-battle check: a party of N against the Genova route trainer at (83,33) on its first route, for each N given.
Before 9.0.1 ten against five crashed ("No more sprite items available").
    python3 tools/pilot/bigbattle.py WORK OUT 8,9,10"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world, pilot
from emu import Emu
from chapter import TEAMS, species_ids

work, out, ns = sys.argv[1], os.path.abspath(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')]
gba = os.path.join(work, 'gba')
w = world.load(gba)
ids = species_ids(gba)
allen = next((i, t['x'], t['y']) for i, m in enumerate(w.maps) for t in m['trainers'] if (t['area'], t['x'], t['y']) == (395, 83, 33))
bad = 0
for n in ns:
    d = os.path.join(out, 'party%d' % n); os.makedirs(d, exist_ok=True)
    sav = bytearray(b'\xff' * 0x8000)
    team = [ids[s] for s in (TEAMS['smart'] * 2)[:n]]
    sav[0x7E02:0x7E04] = struct.pack('<h', 1005)
    sav[0x7F00:0x7F00 + 32] = struct.pack('<4H', n, 400, 1, 5000) + struct.pack('<12H', *(team + [0] * (12 - n)))
    open(os.path.join(d, 'game.sav'), 'wb').write(sav)
    e = Emu(os.path.join(work, 'harness'), os.path.join(gba, 'party-royale.gba'), os.path.join(d, 'game.sav'))
    e.wait(300); e.table(); e.press('A'); e.wait(60); e.press('A'); e.wait(200)
    P = pilot.Pilot(e, w, d, style='smart'); P.settle(); P.last_progress = P.progress_key(); P.set_policy()
    P.goto_tile(*allen)
    res = 'ok'
    for i in range(500):
        if e.crashed():
            res = 'CRASH'; P.shot('crash'); bad += 1; break
        if i == 12:
            P.shot('battle')
            oam = e.read(0x07000000, 1024)
            used = sum(1 for k in range(128) if (oam[k * 8 + 1] & 3) != 2)     # attr0 bits 8-9 == 2: hidden
            print(n, 'sprites on screen', used, flush=True)
        if i > 20 and P.idle(): break
        e.press('A'); e.wait(16)
    print(n, res, flush=True)
    e.close()
sys.exit(1 if bad else 0)
