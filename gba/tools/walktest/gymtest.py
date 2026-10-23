#!/usr/bin/env python3
"""Gym test (9.3.4): plays each gym in mGBA along the shortest route tools/gym/solver.py finds (juniors already
beaten, so no battles), then checks you ended up beside the leader where the solver did. A gym whose engine and
solver disagree (or that crashes) fails; the last frame of each is left in OUT/g<area>.ppm.
With --fight the juniors start unbeaten: each must spot you where the solver says, walk up and battle (A is mashed
until the game marks them beaten), and after every step you must stand where the solver does.
    python3 tools/walktest/gymtest.py [--fight] [OUT] [areas...]
GYMTEST_SHOTS=1 keeps a screenshot of every step and battle frame in OUT (and the build) for a failing gym.
Needs what walktest.py needs."""
import json, os, shutil, struct, subprocess, sys, tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'gym'))
import walktest
from solver import Gym, D4

BOOT = ['w 300', 'k A', 'w 60', 'k A', 'w 200']     # title, CONTINUE

def route(gm, fight=False):
    """The shortest way to the leader, juniors beaten (or not, if fight): [(keys, state after)]."""
    beaten = 0 if fight else (1 << len(gm.juniors)) - 1
    st0 = (gm.start, 0, beaten, gm.boulders0, gm.pits0, 1 if gm.cfg['gate'] == 'juniors' and not fight else 0, 0)
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

class Live:
    """The harness driven a line at a time, so the test can look at memory between key presses."""
    def __init__(s, harness, rom, sav):
        s.p = subprocess.Popen([harness, rom, sav], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    def send(s, *lines):
        s.p.stdin.write('\n'.join(lines) + '\n'); s.p.stdin.flush()
    def mem(s, ad, n):
        s.send('m %x %d' % (ad, n))
        return bytes.fromhex(s.p.stdout.readline().strip())
    def close(s):
        s.p.stdin.close(); s.p.wait()

def fight(gm, path, live, at, bits_at, ids, shots=None):
    """Plays path with the juniors unbeaten. Returns None, or what went wrong."""
    def beaten():
        raw = live.mem(bits_at, 256)
        return sum(1 << i for i, t in enumerate(ids) if raw[t >> 3] >> (t & 7) & 1)
    live.send(*BOOT)
    for n, (keys, after) in enumerate(path):
        way = keys[-1] if keys != 'A' else None
        if way and 'DULR'[live.mem(at + 6, 1)[0]] != way:   # a junior who walked up turned you to face them
            live.send('k %s 1' % way, 'w 16')
        live.send('k %s 1' % ('A' if keys[0] == 'A' else way), 'w 120')
        if shots: live.send('p %s_%02d_pre.ppm' % (shots, n))
        want = after[2]
        fought = beaten() != want
        for _ in range(400):                       # a battle: walk-up, texts, moves, the win
            got = beaten()
            if got & ~want: return 'step %d (%s): junior bits %s, solver %s' % (n, keys, bin(got), bin(want))
            if got == want: break
            if shots: live.send('p %s_%02d_%03d.ppm' % (shots, n, _))
            live.send('k A 1', 'w 20')
        else:
            return 'step %d (%s): battle never ended (bits %s, want %s)' % (n, keys, bin(beaten()), bin(want))
        live.send('k B 1', 'w 30', 'k B 1', 'w 30', 'k B 1', 'w %d' % (240 if fought else 60))   # the way back from a battle fades in
        if shots: live.send('p %s_%02d.ppm' % (shots, n))
        m, x, y = struct.unpack('<hhh', live.mem(at, 6))
        if (x, y) != after[0]: return 'step %d (%s): at %s, solver %s' % (n, keys, (x, y), after[0])
    if beaten() != (1 << len(ids)) - 1: return 'reached the leader with juniors %s unbeaten' % bin(beaten())
    return None

def main():
    args = sys.argv[1:]
    battles = '--fight' in args
    args = [a for a in args if a != '--fight']
    out = os.path.abspath(args[0] if args else 'gymtest-out')
    only = set(int(a) for a in args[1:])
    os.makedirs(out, exist_ok=True)
    work = tempfile.mkdtemp(prefix='gymtest-')
    rom, harness = walktest.build(work, 'test_gym.inc')
    L = {int(a): dict(g, states=[tuple(x) for x in g['states']])
         for a, g in json.load(open(os.path.join(HERE, '..', '..', 'data', 'gym_layouts.json'))).items()}
    # Where game_state is (test_gym.inc writes it at boot): map, x, y are its first fields.
    sav = os.path.join(out, 'addr.sav')
    open(sav, 'wb').write(b'\xff' * 0x8000)
    subprocess.run([harness, rom, sav], input='w 30\n', text=True, check=True)
    at, bits_at = struct.unpack('<II', open(sav, 'rb').read()[0x7E20:0x7E28])
    os.remove(sav)
    bad = []
    for area in sorted(only or L):
        gm = Gym(area, L[area])
        path = route(gm, battles)
        sav = os.path.join(out, 'g%d.sav' % area)
        blank = bytearray(b'\xff' * 0x8000)
        blank[0x7E00:0x7E04] = struct.pack('<hh', area + 1, 1 if battles else 0)
        open(sav, 'wb').write(blank)
        if battles:
            live = Live(harness, rom, sav)
            live.send('w 30')                          # test_setup has written the junior ids by now
            ids = [i for i in struct.unpack('<4h', live.mem(0x0E007E28, 8)) if i >= 0]
            why = 'juniors: game %d, solver %d' % (len(ids), len(gm.juniors)) if len(ids) != len(gm.juniors) else None
            live.close()
            if not why:
                live = Live(harness, rom, sav)        # a fresh boot, so BOOT's timing holds
                why = fight(gm, path, live, at, bits_at, ids, os.environ.get('GYMTEST_SHOTS') and os.path.join(out, 'g%d' % area))
                live.send('p %s' % os.path.join(out, 'g%d.ppm' % area))
                live.close()
            if not why and open(sav, 'rb').read()[0x7E10:0x7E14] == b'CRSH': why = 'CRASH'
            print('%4d %-9s %s  %d steps, %d juniors%s' % (area, L[area]['theme'], 'FAIL' if why else 'ok', len(path), len(gm.juniors),
                                                         ': ' + why if why else ''), flush=True)
            if why: bad.append(area)
            os.remove(sav)
            continue
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
    if not os.environ.get("GYMTEST_SHOTS"): shutil.rmtree(work)
    else: print("kept", work)
    print('failing:', bad or 'none')
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
