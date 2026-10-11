#!/usr/bin/env python3
"""Plays one region from its start (test_pilot.inc builds the save) or a whole game from a new game, with pilot.py.
    python3 tools/pilot/chapter.py WORK OUT --region R --style smart [--frames N]
    python3 tools/pilot/chapter.py WORK OUT --newgame [--nuzlocke] [--skip] --style masher"""
import shutil, argparse, json, os, re, struct, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world, pilot
from emu import Emu

TEAMS = {
    # Eight: nine or ten fighters against a full team of six crash the battle (the sprite limit).
    'smart': ['GARCHOMP', 'METAGROSS', 'GYARADOS', 'TYRANITAR', 'VOLCARONA', 'GARDEVOIR', 'LUCARIO', 'EXCADRILL'],
    'masher': ['GARCHOMP', 'METAGROSS', 'GYARADOS', 'TYRANITAR', 'VOLCARONA', 'GARDEVOIR'],
    'catcher': ['RAICHU', 'ARCANINE', 'STARMIE', 'GENGAR', 'MACHAMP', 'NIDOKING'],
    'twoteam': ['GARCHOMP', 'METAGROSS', 'GYARADOS', 'TYRANITAR', 'VOLCARONA', 'GARDEVOIR', 'LUCARIO', 'EXCADRILL', 'SALAMENCE', 'HYDREIGON', 'DRAGONITE', 'ROSERADE'],
    'solo': ['CHARIZARD'],
    'speed': ['GARCHOMP', 'METAGROSS', 'GYARADOS', 'TYRANITAR', 'VOLCARONA', 'GARDEVOIR'],
}

def species_ids(gba):
    s = open(os.path.join(gba, 'generated', 'include', 'pr_ids.h')).read()
    body = s[s.index('enum class species_id'):]
    body = body[body.index('{') + 1:body.index('}')]
    names = [x.strip().split('=')[0].strip() for x in body.split(',') if x.strip()]
    return {n: i for i, n in enumerate(names)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('work'); ap.add_argument('out')
    ap.add_argument('--region', type=int, default=0)
    ap.add_argument('--newgame', action='store_true')
    ap.add_argument('--nuzlocke', action='store_true')
    ap.add_argument('--skip', action='store_true')
    ap.add_argument('--style', default='smart')
    ap.add_argument('--frames', type=int, default=3000000)
    ap.add_argument('--state', default='')
    ap.add_argument('--sav', default='', help='carry on from this game save (savestates do not survive a ROM rebuild)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--team', type=int, default=0, help='party size (default: the style\'s team)')
    ap.add_argument('--level', type=int, default=0)
    ap.add_argument('--shots', type=int, default=0, help='also a screenshot every N frames (for the first 300000)')
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    gba = os.path.join(a.work, 'gba')
    rom, harness = os.path.join(gba, 'party-royale.gba'), os.path.join(a.work, 'harness')
    w = world.load(gba)
    sav = os.path.join(out, 'game.sav')
    if a.sav:
        data = bytearray(open(a.sav, 'rb').read())
        data[0x7E10:0x7E14] = b'\xff' * 4     # a crash mark left by the run it came from
        open(sav, 'wb').write(data)
    elif not a.state:
        data = bytearray(b'\xff' * 0x8000)
        if not a.newgame:
            ids = species_ids(gba)
            team = [ids[n] for n in TEAMS.get(a.style, TEAMS['smart'])]
            if a.team:
                team = (team * 2)[:a.team]
            level = a.level or max(5, 100 * (a.region - 1))
            data[0x7E02:0x7E04] = struct.pack('<h', 1000 + a.region)
            req = struct.pack('<4H', len(team), level, 1 if (a.skip or a.style == 'speed') else 0, 5000) + \
                  struct.pack('<12H', *(team + [0] * (12 - len(team))))
            data[0x7F00:0x7F00 + len(req)] = req
        open(sav, 'wb').write(data)
    e = Emu(harness, rom, sav)
    e.wait(300 + a.seed * 37)     # a different seed waits a little longer at the title: the game's dice roll differently
    e.table()
    P = pilot.Pilot(e, w, out, style=a.style, seed=a.seed, run_wild=a.style != 'masher')
    if a.shots:
        wait, last = e.wait, [0]
        def shooting_wait(n):
            wait(n)
            if e.frames - last[0] >= a.shots and e.frames < 300000:
                last[0] = e.frames
                e.shot(os.path.join(out, 'f%07d.png' % e.frames))
        e.wait = shooting_wait
    t0 = time.time()
    if a.state:
        e.load_state(a.state)
        e.frames = json.load(open(a.state + '.json'))['frames']
    elif a.newgame:
        # NEW GAME: the kind of adventure, SKIP STORY TEXT, the intro, a name, and on to the starter.
        e.press('A'); e.wait(40); e.press('A'); e.wait(40)
        if a.nuzlocke:
            e.press('D', 3); e.wait(10)
        e.press('A'); e.wait(40)
        if a.skip:
            e.press('U', 3); e.wait(10)
        e.press('A'); e.wait(60)
        P.shot('newgame')
        for i in range(30):
            e.press('A'); e.wait(30)
        # The name: five letters, then OK.
        for i in range(5):
            e.press('A'); e.wait(8)
        e.press('S', 3); e.wait(8); e.press('A'); e.wait(60)
    else:
        e.press('A'); e.wait(60); e.press('A'); e.wait(200)
    P.shot('start')
    n = [0]
    def checkpoint(p):
        n[0] += 1
        path = os.path.join(out, 'cp%03d.state' % n[0])
        e.save_state(path)
        json.dump({'frames': e.frames}, open(path + '.json', 'w'))
    try:
        P.settle()
        r = P.play(a.frames, checkpoint)
    except pilot.Stuck as s:
        P.log('stuck', why=str(s)); r = 'stuck'
    P.shot('end')
    party = e.party()
    res = dict(result=r, frames=e.frames, wall=round(time.time() - t0), pos=e.pos(), region=P.region_now(),
               badges=[P.badges(rg) for rg in range(1, 10)], party=[(p['species'], p['level']) for p in party],
               champion=[P.champion(rg) for rg in range(1, 10)])
    json.dump(res, open(os.path.join(out, 'result.json'), 'w'))
    print(json.dumps(res))
    e.close()

if __name__ == '__main__':
    main()
