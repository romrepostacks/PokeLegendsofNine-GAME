#!/usr/bin/env python3
"""Gym test (9.3.4): plays each gym in mGBA along the shortest route tools/gym/solver.py finds (juniors already
beaten, so no battles), then checks you ended up beside the leader where the solver did. A gym whose engine and
solver disagree (or that crashes) fails; the last frame of each is left in OUT/g<area>.ppm.
    python3 tools/walktest/gymtest.py [OUT] [areas...]
Needs what walktest.py needs."""
import json, os, shutil, struct, subprocess, sys, tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'gym'))
import walktest
from solver import Gym, D4

BOOT = ['w 300', 'k A', 'w 60', 'k A', 'w 200']     # title, CONTINUE

def route(gm):
    """The shortest way to the leader with every junior beaten: [(keys, state after)]."""
    beaten = (1 << len(gm.juniors)) - 1
    st0 = (gm.start, 0, beaten, gm.boulders0, gm.pits0, 1 if gm.cfg['gate'] == 'juniors' else 0, 0)
    prev = {st0: None}
    q = deque([st0])
    while q:
        st = q.popleft()
        if gm.at_goal(st):
            path = []
            while prev[st]:
                st, keys, after = prev[st][0], prev[st][1], st
                path.append((keys, after))
            return path[::-1]
        moves = [(k, gm.step(st, d)) for k, d in zip('UDLR', D4)] + gm.labeled_actions(st)
        for keys, n in moves:
            if n and n not in prev:
                prev[n] = (st, keys)
                q.append(n)
    return None

def script(gm, path):
    lines, facing = list(BOOT), 'U'
    for keys, after in path:
        way = keys[-1] if keys != 'A' else None
        if way and way != facing:
            lines += ['k %s 1' % way, 'w 16']        # from a standstill, a new way first turns you
            facing = way
        lines += ['k %s 1' % ('A' if keys[0] == 'A' else way), 'w 120', 'k B 1', 'w 30', 'k B 1', 'w 30']
    return lines

def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'gymtest-out')
    only = set(int(a) for a in sys.argv[2:])
    os.makedirs(out, exist_ok=True)
    work = tempfile.mkdtemp(prefix='gymtest-')
    rom, harness = walktest.build(work, 'test_gym.inc')
    L = {int(a): dict(g, states=[tuple(x) for x in g['states']])
         for a, g in json.load(open(os.path.join(HERE, '..', '..', 'data', 'gym_layouts.json'))).items()}
    # Where game_state is (test_gym.inc writes it at boot): map, x, y are its first fields.
    sav = os.path.join(out, 'addr.sav')
    open(sav, 'wb').write(b'\xff' * 0x8000)
    subprocess.run([harness, rom, sav], input='w 30\n', text=True, check=True)
    at = struct.unpack('<I', open(sav, 'rb').read()[0x7E20:0x7E24])[0]
    os.remove(sav)
    bad = []
    for area in sorted(only or L):
        gm = Gym(area, L[area])
        path = route(gm)
        sav = os.path.join(out, 'g%d.sav' % area)
        blank = bytearray(b'\xff' * 0x8000)
        blank[0x7E00:0x7E02] = struct.pack('<h', area + 1)
        open(sav, 'wb').write(blank)
        lines = script(gm, path) + ['p %s' % os.path.join(out, 'g%d.ppm' % area), 'm %x 6' % at]
        res = subprocess.run([harness, rom, sav], input='\n'.join(lines) + '\n', text=True, capture_output=True, check=True)
        raw = bytes.fromhex(res.stdout.split()[-1])
        m, x, y = struct.unpack('<hhh', raw)
        want = path[-1][1][0]
        crashed = open(sav, 'rb').read()[0x7E10:0x7E14] == b'CRSH'
        ok = not crashed and (x, y) == want
        print('%4d %-9s %s  %d steps, at %s (solver %s)%s' % (area, L[area]['theme'], 'ok' if ok else 'FAIL', len(path), (x, y), want,
                                                            ' CRASH' if crashed else ''), flush=True)
        if not ok:
            bad.append(area)
        os.remove(sav)
    shutil.rmtree(work)
    print('failing:', bad or 'none')
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
