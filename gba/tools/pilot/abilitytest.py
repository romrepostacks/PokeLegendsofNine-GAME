#!/usr/bin/env python3
"""The 9.6.0 abilities check: one POKéMON with each ability that came in 9.6.0, six at a time, against the Genova
route trainer at (83,33) (bigbattle.py's), with the pilot picking moves. Fails on a crash or a battle that never ends.
    python3 tools/pilot/abilitytest.py WORK OUT"""
import json, os, re, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world, pilot
from emu import Emu

work, out = sys.argv[1], os.path.abspath(sys.argv[2])
gba = os.path.join(work, 'gba')
w = world.load(gba)
src = open(os.path.join(gba, 'tools', 'build_assets.py')).read()
new = src[src.index('# 9.6.0: the rest.'):src.index('# 9.6.0: what this game')]
names = re.findall(r"'([^']+)': \('[A-Z_]+'", new)
exp = os.path.join(out, 'export')
if not os.path.exists(os.path.join(exp, 'data.json')):
    os.makedirs(exp, exist_ok=True)
    subprocess.run(['node', os.path.join(gba, 'tools', 'export.js'), exp, '0'], check=True, stdout=subprocess.DEVNULL)
species = json.load(open(os.path.join(exp, 'data.json')))['species']
picks = []
for n in names:
    i = next((i for i, s in enumerate(species) if s['ability']['n'] == n), None)
    if i is not None:
        picks.append((n, i))
print(len(picks), 'abilities', flush=True)
allen = next((t['x'], t['y']) for m in w.maps for t in m['trainers'] if (t['area'], t['x'], t['y']) == (395, 83, 33))
bad = 0
for b in range(0, len(picks), 6):
    group = picks[b:b + 6]
    d = os.path.join(out, 'b%02d' % (b // 6)); os.makedirs(d, exist_ok=True)
    sav = bytearray(b'\xff' * 0x8000)
    team = [i for _, i in group]
    sav[0x7E02:0x7E04] = struct.pack('<h', 1005)
    sav[0x7F00:0x7F00 + 32] = struct.pack('<4H', len(team), 400, 1, 5000) + struct.pack('<12H', *(team + [0] * (12 - len(team))))
    open(os.path.join(d, 'game.sav'), 'wb').write(sav)
    e = Emu(os.path.join(work, 'harness'), os.path.join(gba, 'party-royale.gba'), os.path.join(d, 'game.sav'))
    e.wait(300); e.table(); e.press('A'); e.wait(60); e.press('A'); e.wait(200)
    P = pilot.Pilot(e, w, d, style='smart'); P.settle(); P.last_progress = P.progress_key(); P.set_policy()
    P.goto_tile(*allen)
    res = 'NO END'
    for i in range(3000):
        if e.crashed():
            res = 'CRASH'; P.shot('crash'); break
        if i > 20 and P.idle():
            res = 'ok'; break
        e.press('A'); e.wait(16)
    bad += res != 'ok'
    print(b // 6, res, ', '.join(n for n, _ in group), flush=True)
    e.close()
sys.exit(1 if bad else 0)
