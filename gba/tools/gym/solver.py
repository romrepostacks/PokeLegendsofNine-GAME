# Plays every gym's mechanic and checks it (the gyms' smoke test): python3 gba/tools/gym/solver.py [areas...]
# Rules (the engine's, src/pr_gym.cpp, follows them; 9.3.4 gyms):
#  - Start on the rug 'o'. Goal: stand next to the leader 'L'. Leaving by the mat resets the room.
#  - Solid: walls x, statues u, people L j g, pylons P, generators E, pedestals S, pearls Q, braziers T, rocks r, fans n,
#    windmill W, lava K, invisible walls X. Illusions I are walkable. Juniors see 5 tiles in the way they face
#    (through floor, grass and water) and battle you when you step into that line.
#  - Fences F f G: switch 1 lowers F, 2 lowers f, 3 lowers G (and raises the others). Fighting/fairy/normal F is a
#    gate: it opens once every plate q holds a boulder, every pearl Q is lit, or every junior is beaten (cfg gate).
#  - Boulders O are pushed one tile; into a pit p they fill it (floor). They can't go onto mats =, water or ice. Ice i: you slide until blocked or off ice;
#    rock r stops you before it, a drift d or stop-plate e stops you on it.
#  - Arrows > < ^ v move you on until you're off them. Over pits (cfg over='p') they only carry you while their
#    fans are on; with them off the tiles are pits.
#  - Water ~ needs SURF (cfg surf); dive spots D link in pairs, in reading order. Pads a b c link in pairs.
#  - Bog Z, a wrong note N, or a hole sends you back to the rug. Vines V and flame jets Y (cfg Y='jet') open when
#    the nearest junior is beaten. Gas z clears when the nearest valve S is turned.
#  - High ground H/l: you change level only on stairs s, or by dropping south off a ledge l.
#  - Cracked floor k breaks behind you; stepping on a broken tile drops you to the rug and the room resets.
#  - Tesla coils (cfg pulse n): F is down for n steps, then f for n steps, and so on.
#  - Gate juniors (cfg step_aside) stand in the way until beaten.
#  - Rooms with two states (era, tide, season, sundial): A on a pedestal S (or a switch 1/2) swaps them.
import json, os, sys
from collections import deque

SOLID = set('#xuLgjPESQTrnWKX{}!`')
JF = {'{': (-1, 0), '}': (1, 0), '!': (0, 1), '`': (0, -1)}
D4 = ((0, -1), (0, 1), (-1, 0), (1, 0))
ARROW = {'^': (0, -1), 'v': (0, 1), '<': (-1, 0), '>': (1, 0)}

def frame(rows):
    w = len(rows[0]) + 2
    return ['#' * w] * 2 + ['#' + r + '#' for r in rows] + ['#' * (w // 2) + 'M' + '#' * (w - w // 2 - 1)]

def default_cfg(area):
    return dict(surf=area >= 7, dive=area >= 26, R='walk', J='solid', Y='solid', over='_', fans=None, e='stop', gate=None)

class Gym:
    def __init__(s, area, g):
        s.area = area
        s.cfg = dict(default_cfg(area), **g.get('cfg', {}))
        for r in g['rows']: assert len(r) == len(g['rows'][0]), (area, r, len(r))
        s.variants = [frame([''.join(sub.get(c, c) for c in row) for row in g['rows']]) for _, sub in g['states']] or [frame(g['rows'])]
        s.rows = s.variants[0]
        s.H, s.W = len(s.rows), len(s.rows[0])
        R = s.rows
        find = lambda ch: [(x, y) for y in range(s.H) for x in range(s.W) if R[y][x] == ch]
        s.start = find('o')[0]
        s.leader = find('L')[0]
        s.juniors = sorted(find('j') + find('{') + find('}') + find('!') + find('`'), key=lambda p: (p[1], p[0]))
        s.guide = find('g')
        s.boulders0 = tuple(sorted(find('O')))
        s.pits0 = frozenset(find('p'))
        s.plates = find('q')
        s.pearls = find('Q')
        s.peds = find('S')
        raw = frame(g['rows']); s.dives = [(x, y) for y in range(s.H) for x in range(s.W) if raw[y][x] == 'D']   # dive spots exist even where a state hides them
        s.pads = {}
        for ch in 'abc':
            p = find(ch)
            if p: assert len(p) == 2, (area, 'pad', ch, p); s.pads[p[0]] = p[1]; s.pads[p[1]] = p[0]
        s.dpair = {}
        for i in range(0, len(s.dives) - 1, 2): s.dpair[s.dives[i]] = s.dives[i + 1]; s.dpair[s.dives[i + 1]] = s.dives[i]
        s.facing = [s.face(j) for j in s.juniors]
        s.sight = [s.sightline(j, f) for j, f in zip(s.juniors, s.facing)]
        near = lambda p, pts: min(range(len(pts)), key=lambda i: abs(pts[i][0] - p[0]) + abs(pts[i][1] - p[1])) if pts else None
        s.guard = {p: near(p, s.juniors) for p in find('V') + find('Y')} if s.juniors else {}
        s.valve = {p: near(p, s.peds) for p in find('z')}
        for (gx, gy), (vx, vy) in s.cfg.get('valves', []): s.valve[(gx + 1, gy + 2)] = s.peds.index((vx + 1, vy + 2))   # explicit gas -> valve
        s.era = len(s.variants) > 1
        s.plev = {p: 1 if any(s.ch(p[0] + dx, p[1]) in 'Hls' for dx in (-1, 1)) else 0 for p in list(s.pits0) + list(s.boulders0)}   # a crevasse in high ground fills to high ground
        s.lane = {}
        for (x, y, swn) in s.cfg.get('lanes', []):
            p0 = (x + 1, y + 2); stack = [p0]
            while stack:
                p = stack.pop()
                if p in s.lane or s.ch(*p) not in ARROW: continue
                s.lane[p] = swn
                stack += [(p[0] + dx, p[1] + dy) for dx, dy in D4]

    def ch(s, x, y, var=0):
        return s.variants[var][y][x] if 0 <= x < s.W and 0 <= y < s.H else '#'
    def face(s, j):
        if s.rows[j[1]][j[0]] in JF: return JF[s.rows[j[1]][j[0]]]
        best = None
        for d in ((0, 1), (-1, 0), (1, 0), (0, -1)):
            n = 0
            for k in range(1, 6):
                c = s.ch(j[0] + d[0] * k, j[1] + d[1] * k)
                if c in '_~=oiHkRIq123abc+<>^vdlseD': n += 1
                else: break
            if best is None or n > best[0]: best = (n, d)
        return best[1]
    def sightline(s, j, d):
        out = []
        for k in range(1, 6):
            p = (j[0] + d[0] * k, j[1] + d[1] * k)
            if s.ch(*p) in SOLID or s.ch(*p) in 'OFfGVYzlsp<>^v': break   # the engine sees over floor, grass, water, ice only
            out.append(p)
        return out

    def level(s, c): return 1 if c in 'Hl' else 2 if c == 's' else 0
    def lv(s, p, var=0): return s.plev.get(p, 0) if s.ch(*p, var) in 'pO' else s.level(s.ch(*p, var))
    def fence_up(s, c, sw, act):
        if c not in 'FfG': return False
        if c == 'F' and s.cfg['gate']: return not s.gate_open(act)
        if s.cfg.get('pulse'): return c != ('F' if sw < s.cfg['pulse'] else 'f')   # tesla coils: F and f take turns, every pulse steps
        return {'F': 1, 'f': 2, 'G': 3}[c] != sw
    def gate_open(s, act):
        g = s.cfg['gate']
        return bool(act & 1) if g in ('plates', 'pearls', 'juniors') else False

    def solid(s, p, st):
        pos, sw, beaten, boulders, pits, act, var = st
        c = s.ch(*p, var)
        if c == 'O' and p not in boulders: c = '_'
        if p in boulders: return 'boulder'
        if c == 'p' or c in ARROW and s.cfg['over'] == 'p' and not s.arrow_on(p, sw):
            return p in pits or c in ARROW
        if s.cfg.get('step_aside') and p in s.juniors: return not (beaten >> s.juniors.index(p)) & 1   # a gate junior steps aside once beaten
        if c in SOLID or c == '#' or c == 'M': return True
        if c in 'FfG': return s.fence_up(c, sw, act)
        if c in '~D': return not s.cfg['surf']
        if c in ARROW and s.cfg['over'] == '~' and not s.cfg['surf'] and not s.cfg.get('raft'): return True
        if c == 'R': return s.cfg['R'] == 'solid'
        if c == 'J': return s.cfg['J'] == 'solid'
        if c in 'VY':
            if c == 'Y' and s.cfg['Y'] == 'sun': return var == 0
            if c == 'Y' and s.cfg['Y'] == 'solid': return True
            gi = s.guard.get(p)
            return gi is None or not (beaten >> gi) & 1
        if c == 'z':
            vi = s.valve.get(p)
            return vi is None or not (act >> (vi + 1)) & 1
        if c == 'e' and s.cfg['e'] == 'mag': return False
        return False
    def arrow_on(s, p, sw):
        if p in s.lane: return s.lane[p] == sw
        return s.fans_on(sw)
    def fans_on(s, sw):
        return s.cfg['fans'] is None or sw == s.cfg['fans']

    def spotted(s, p, beaten):
        for i, line in enumerate(s.sight):
            if not (beaten >> i) & 1 and p in line: beaten |= 1 << i
        return beaten

    def step(s, st, d, forbid=None):
        pos, sw, beaten, boulders, pits, act, var = st
        t = (pos[0] + d[0], pos[1] + d[1])
        sol = s.solid(t, st)
        if sol == 'boulder':
            b2 = (t[0] + d[0], t[1] + d[1])
            if s.lv(t, var) != s.lv(b2, var) and s.ch(*b2, var) != 's': return None
            c2 = s.ch(*b2, var)
            st2 = (pos, sw, beaten, tuple(x for x in boulders if x != t), pits, act, var)
            if b2 in pits:
                pits = pits - {b2}; boulders = tuple(x for x in boulders if x != t)
            elif s.solid(b2, st2) or c2 in '~DZNi=' or c2 in ARROW: return None   # boulders stop at water, ice and mats =
            else: boulders = tuple(sorted([x for x in boulders if x != t] + [b2]))
            if s.plates and all(q in boulders for q in s.plates) and s.cfg['gate'] == 'plates': act |= 1
            st = (pos, sw, beaten, boulders, pits, act, var)
        elif sol: return None
        a, b = s.ch(*pos, var), s.ch(*t, var)
        la, lb = s.lv(pos, var), s.lv(t, var)
        if la != 2 and lb != 2 and la != lb and not (a == 'l' and d == (0, 1) and lb == 0): return None
        if forbid and t in forbid: return None
        if s.ch(*pos, var) == 'k': pits = pits | {pos}
        if b == 'k' and t in pits: return (s.start, sw, beaten, s.boulders0, s.pits0, act, var)
        pos = t
        beaten = s.spotted(pos, beaten)
        # forced movement
        for _ in range(80):
            c = s.ch(*pos, var)
            if c == 'i' or c == 'e' and s.cfg['e'] == 'mag':
                n = (pos[0] + d[0], pos[1] + d[1])
                stn = (pos, sw, beaten, boulders, pits, act, var)
                if s.solid(n, stn) or s.ch(*n, var) in 'r~D' or s.ch(*n, var) in ARROW or s.lv(n, var) != s.lv(pos, var) and 's' not in (s.ch(*n, var), s.ch(*pos, var)): break   # a slide stops at a cliff
                if forbid and n in forbid: return None
                pos = n; beaten = s.spotted(pos, beaten)
                if s.ch(*pos, var) in 'de' and s.cfg['e'] != 'mag' or s.ch(*pos, var) == 'd': break
                continue
            if c in ARROW and (s.cfg['over'] != 'p' or s.arrow_on(pos, sw)):
                d = ARROW[c]; n = (pos[0] + d[0], pos[1] + d[1])
                stn = (pos, sw, beaten, boulders, pits, act, var)
                if s.solid(n, stn): break
                if forbid and n in forbid: return None
                pos = n; beaten = s.spotted(pos, beaten)
                continue
            break
        c = s.ch(*pos, var)
        if c in 'ZN' or c == 'p' and pos in pits: pos = s.start
        if c in s.cfg.get('reset', ''): pos = s.start
        if pos in s.pads: pos = s.pads[pos]
        if s.cfg.get('pulse'): sw = (sw + 1) % (2 * s.cfg['pulse'])
        if c in '123':
            if s.era and s.cfg.get('era_by') == 'switch': var = (var + 1) % len(s.variants)
            else: sw = int(c)
        if c == 'J' and s.cfg['J'] == 'step': act |= 1 << (10 + [i for i, p in enumerate(s.lanterns()) if p == pos][0])
        if s.cfg['gate'] == 'juniors' and beaten == (1 << len(s.juniors)) - 1: act |= 1
        return (pos, sw, beaten, boulders, pits, act, var)
    def lanterns(s): return [(x, y) for y in range(s.H) for x in range(s.W) if s.rows[y][x] == 'J']

    def actions(s, st):
        return [n for _, n in s.labeled_actions(st)]
    def labeled_actions(s, st):
        """What A does here, as (keys, state): 'A' + the way you face a pedestal or pearl, or 'A' on a dive spot."""
        pos, sw, beaten, boulders, pits, act, var = st
        out = []
        for name, d in zip('UDLR', D4):
            t = (pos[0] + d[0], pos[1] + d[1])
            c = s.ch(*t, var)
            if c == 'S':
                i = s.peds.index(t)
                if s.era and not s.cfg.get('era_by'): out.append(('A' + name, (pos, sw, beaten, boulders, pits, act, (var + 1) % len(s.variants))))
                elif s.cfg.get('S') == 'fans': out.append(('A' + name, (pos, 0 if sw == s.cfg['fans'] else s.cfg['fans'], beaten, boulders, pits, act, var)))
                else: out.append(('A' + name, (pos, sw, beaten, boulders, pits, act | (1 << (i + 1)), var)))
            if c == 'Q':
                i = s.pearls.index(t); a2 = act | (1 << (20 + i))
                if all((a2 >> (20 + k)) & 1 for k in range(len(s.pearls))) and s.cfg['gate'] == 'pearls': a2 |= 1
                out.append(('A' + name, (pos, sw, beaten, boulders, pits, a2, var)))
        if s.ch(*pos, var) == 'D' and s.cfg['dive'] and pos in s.dpair:
            out.append(('A', (s.dpair[pos], sw, beaten, boulders, pits, act, var)))
        return out

    def start_state(s):
        return (s.start, 0, 0, s.boulders0, s.pits0, 0, 0)
    def at_goal(s, st):
        p = st[0]
        return abs(p[0] - s.leader[0]) + abs(p[1] - s.leader[1]) == 1

    def explore(s, forbid=None, limit=400000, no_mech=False):
        st0 = s.start_state()
        seen = {st0: None}; q = deque([st0]); edges = {}
        while q:
            st = q.popleft()
            nxt = [s.step(st, d, forbid) for d in D4] + ([] if no_mech else s.actions(st))
            if no_mech: nxt = [n for n in nxt if n and n[1:] == st[1:] or (n and n[2] != st[2] and n[1] == st[1] and n[5] == st[5] and n[6] == st[6])]
            edges[st] = [n for n in nxt if n]
            for n in edges[st]:
                if n not in seen:
                    seen[n] = st; q.append(n)
                    if len(seen) > limit: return seen, edges, True
        return seen, edges, False

    def check(s):
        rep = []
        seen, edges, capped = s.explore()
        goals = [st for st in seen if s.at_goal(st)]
        ok = bool(goals)
        if not ok: rep.append('LEADER UNREACHABLE')
        # soft lock: every state must still reach the leader or the exit
        back = {}
        for a, ns in edges.items():
            for n in ns: back.setdefault(n, []).append(a)
        good = set(st for st in seen if s.at_goal(st) or st[0] == s.start)
        q = deque(good)
        while q:
            st = q.popleft()
            for a in back.get(st, []):
                if a not in good: good.add(a); q.append(a)
        stuck = [st for st in seen if st not in good]
        # after the leader, the way out must still be open
        home = set(st for st in seen if st[0] == s.start)
        q = deque(home)
        while q:
            st = q.popleft()
            for a in back.get(st, []):
                if a not in home: home.add(a); q.append(a)
        trapped = [st for st in goals if st not in home]
        if goals and len(trapped) == len(goals): rep.append('no way back out after the leader')
        if stuck: rep.append(f'SOFT LOCK in {len(stuck)} states, e.g. at {stuck[0][0]}')
        # coverage: tiles you can stand on, devices you can use
        stood = set(st[0] for st in seen)
        walk = [(x, y) for y in range(2, s.H - 1) for x in range(s.W) if s.rows[y][x] in '_=Hksq123abc+IedR~D<>^v' and not (s.rows[y][x] == 'R' and s.cfg['R'] == 'solid') and not (s.rows[y][x] in '~D' and not s.cfg['surf']) and not (s.rows[y][x] == 'e' and s.cfg['e'] == 'mag')]
        never = [p for p in walk if p not in stood and s.rows[p[1]][p[0]] not in '<>^v' and len(set(v[p[1]][p[0]] for v in s.variants)) == 1]   # tiles that change with the state (blades, gates) are not floor to cover
        if never: rep.append(f'{len(never)} tiles never reachable, e.g. {never[:4]}')
        for name, pts in (('switch', [(x, y) for y in range(s.H) for x in range(s.W) if s.rows[y][x] in '123']), ('pad', list(s.pads)), ('plate', s.plates)):
            miss = [p for p in pts if p not in stood]
            if miss: rep.append(f'{name} never reached: {miss}')
        for name, pts in (('pedestal', s.peds), ('pearl', s.pearls)):
            miss = [p for p in pts if not any(abs(p[0] - a[0]) + abs(p[1] - a[1]) == 1 for a in stood)]
            if miss: rep.append(f'{name} never reached: {miss}')
        if s.guide and not any(abs(s.guide[0][0] - a[0]) + abs(s.guide[0][1] - a[1]) == 1 for a in stood): rep.append('guide unreachable')
        # every junior must be fought: avoiding their line of sight must make the leader unreachable
        for i, (j, line) in enumerate(zip(s.juniors, s.sight)):
            if not line: rep.append(f'junior {j} sees nothing'); continue
            sn, _, _ = s.explore(forbid=set(line) - {s.start}, limit=200000)
            if any(s.at_goal(st) for st in sn): rep.append(f'junior {j} can be walked past')
        # the mechanic must matter: without switches/pedestals/pads/pushing, the leader must be out of reach
        mech = s.cfg.get('mech', True)
        if mech and ok:
            sn, _, _ = s.explore(no_mech=True, limit=200000)
            if any(s.at_goal(st) for st in sn) and s.mechanic_kind() in ('switch', 'era', 'objects', 'boulders'):
                rep.append('mechanic not needed: leader reachable without using it')
        steps = None
        if goals:
            st = min(goals, key=lambda g: s.depth(seen, g)); steps = s.depth(seen, st)
        return ok and not stuck, rep, steps, len(seen), capped
    def depth(s, seen, st):
        n = 0
        while seen[st] is not None: st = seen[st]; n += 1
        return n
    def mechanic_kind(s):
        R = ''.join(s.rows)
        if s.era: return 'era'
        if any(c in R for c in '123'): return 'switch'
        if 'O' in R: return 'boulders'
        if any(c in R for c in 'SQ'): return 'objects'
        return 'other'

if __name__ == '__main__':
    L = {int(a): dict(g, states=[tuple(x) for x in g['states']]) for a, g in
         json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'gym_layouts.json'))).items()}
    only = set(int(a) for a in sys.argv[1:]) or set(L)
    bad = 0
    for area in sorted(only):
        gm = Gym(area, L[area])
        good, rep, steps, n, capped = gm.check()
        flag = 'PASS' if good and not rep else 'FAIL'
        bad += flag == 'FAIL'
        print(f'{area:4d} {L[area]["theme"]:9s} {flag}  moves {steps}  states {n}{" (capped)" if capped else ""}' + ''.join('\n       - ' + r for r in rep))
    print('failing:', bad)
    sys.exit(1 if bad else 0)
