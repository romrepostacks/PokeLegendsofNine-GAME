#!/usr/bin/env python3
"""An autoplayer for the real ROM: it reads the game state (test_pilot.inc's table), walks with BFS over the
maps (world.py), mashes A through text, lets battle_patch.inc pick moves, heals, grinds when it loses, and
logs what happens (and where it gets stuck) for a playtest report.
    python3 tools/pilot/pilot.py WORK OUT --style smart [--frames N] [--sav START.sav]"""
import argparse, collections, json, os, random, struct, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world as W
from emu import Emu, SRAM

DIRS = {'D': (0, 1), 'U': (0, -1), 'L': (-1, 0), 'R': (1, 0)}
FACE = ['D', 'U', 'L', 'R']
OPP = {'D': 'U', 'U': 'D', 'L': 'R', 'R': 'L'}
LEDGE = {W.LEDGE_D: 'D', W.LEDGE_R: 'R', W.LEDGE_L: 'L'}
WIND = {W.WU: 'U', W.WD: 'D', W.WL: 'L', W.WR: 'R'}
STYLES = {'smart': 1, 'masher': 2, 'catcher': 3}

class Stuck(Exception):
    pass

class Pilot:
    def __init__(self, emu, world, out, style='smart', seed=0, run_wild=True):
        self.e, self.w, self.out = emu, world, out
        self.style = style
        self.rnd = random.Random(seed)
        self.run_wild = run_wild
        self.blocked = {}            # (map, x, y) -> frame until which it's treated as solid
        self.bad_links = {}          # (map, link index) -> progress key when it bounced us
        self.events = []
        self.fails = {}
        self.failed = {}
        self.lost = False
        self.shop_ok = None
        self.talked = set()
        self.retries = 0
        self.rotate_party = style in ('smart', 'catcher', 'twoteam') and not os.environ.get('PILOT_NOROTATE')
        self.style_all = style in ('all', 'catcher')
        self.fight_all = style in ('all', 'catcher', 'smart', 'masher', 'twoteam', 'solo')
        self.log_f = open(os.path.join(out, 'log.txt'), 'a')
        self.shots = 0
        self.last_progress = None
        t = emu.t
        self.addr = t['addr']
        leaders = collections.defaultdict(list)
        for m in world.maps:
            for tr in m['trainers']:
                if tr['role'] == 'LEADER':
                    leaders[m['region']].append(tr['id'])
        self.leaders = leaders

    # ----- logging -----
    def log(self, kind, **kw):
        m, x, y = self.e.pos()
        rec = dict(f=self.e.frames, kind=kind, map=m, name=self.w.maps[m]['name'] if 0 <= m < len(self.w.maps) else '?', x=x, y=y, **kw)
        self.events.append(rec)
        self.log_f.write(json.dumps(rec) + '\n'); self.log_f.flush()
        return rec

    def shot(self, tag):
        self.shots += 1
        name = '%05d-%s.png' % (self.shots, tag)
        self.e.shot(os.path.join(self.out, name))
        return name

    # ----- state -----
    def pos(self):
        return self.e.pos()

    def facing(self):
        return self.e.g('facing', 1, False)

    def story(self):
        return self.e.g('story', 4, False)

    def beaten(self, tid):
        return self.e.bit('beaten', tid)

    def badges(self, region):
        return sum(self.beaten(t) for t in self.leaders[region])

    def progress_key(self):
        b = self.e.bits('beaten', 256)
        return (self.story(), self.e.bits('flags', 16), b, self.e.g('party_count', 1, False))

    def able(self):
        p = self.e.party()
        return sum(m['hp'] for m in p), sum(m['max_hp'] for m in p), p

    # ----- low level moves -----
    def idle(self):
        """True if we're walking around: a tap turns us (it changes `facing`)."""
        f = self.facing()
        d = 'L' if FACE[f] != 'L' else 'R'
        self.e.press(d, 3)
        self.e.wait(10)
        return self.facing() != f

    def settle(self, limit=2400):       # a legend at the cap can take ~1500 presses (Deoxys recovers)
        """Presses A (and now and then B) until we're walking again. Returns how many presses it took."""
        n = 0
        while not self.idle():
            if self.e.crashed():
                raise Stuck('crash')
            if self.naming():
                self.leave_naming()
                n += 1
                continue
            self.e.press('B' if n % 12 == 11 or (n > 60 and n % 2) else 'A', 4)
            self.e.wait(16)
            n += 1
            if n % 150 == 0:
                self.shot('settle')
            if n >= limit:
                raise Stuck('no way out of a screen after %d presses' % n)
        return n

    def naming(self):
        # Two white boxes (the name, the letter board) wherever the area tints the background.
        return all(self.e.color(x, y) == (255, 255, 255) for x, y in ((20, 146), (220, 146), (20, 62), (220, 62), (225, 30), (15, 30)))

    def leave_naming(self):
        # The naming screen (a nickname): B back to an empty name, then once more keeps the species' name.
        # A NUZLOCKE nickname is a must: type one letter and OK it.
        for i in range(15):
            self.e.press('B', 3); self.e.wait(6)
            if not self.naming():
                return
        self.e.press('A', 3); self.e.wait(6); self.e.press('S', 3); self.e.wait(6); self.e.press('A', 3); self.e.wait(20)

    def step(self, d):
        """One step (holding B to run). Returns the new position, or None if we didn't move."""
        before = self.pos()
        keys = d + ('B' if not self.w.maps[before[0]]['room'] else '')
        f = self.e.hold_until(keys, 40, self.addr + self.e.t['map'], 6)
        after = self.pos()
        if after != before:
            return after
        self.e.wait(1)
        return None

    # ----- maps -----
    def solid_actors(self, mi):
        m = self.w.maps[mi]
        s = set()
        for p in m['people']:
            if not p['wander']:
                s.add((p['x'], p['y']))
        for t in m['trainers']:
            if t['scene']:
                continue
            if t['vanish'] and self.beaten(t['id']):
                continue
            s.add((t['x'], t['y']))
        for it in m['items']:
            if not self.e.bit('picked', it['id']):
                s.add((it['x'], it['y']))
        return s

    def link_at(self, mi, x, y):
        m = self.w.maps[mi]
        for k, l in enumerate(m['links']):
            if l['ox'] <= x < l['ox'] + l['w'] and l['oy'] <= y < l['oy'] + l['h']:
                return k, l
        return None, None

    def neighbours(self, mi, x, y, actors, surf, now):
        m = self.w.maps[mi]
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < m['w'] and 0 <= ny < m['h']):
                k, l = self.link_at(mi, nx, ny)
                if l is None or l['to'] < 0:
                    continue
                if (mi, k) in self.bad_links and self.bad_links[(mi, k)] == self.last_progress:
                    continue
                tb = self.w.beh(l['to'], nx - l['ox'], ny - l['oy'])
                if tb in (W.WALK, W.GRASS) or (surf and tb == W.WATER):
                    yield d, ('link', k), None
                continue
            if (nx, ny) in actors or self.blocked.get((mi, nx, ny), -1) > now:
                continue
            b = m['beh'][ny * m['w'] + nx]
            if b in (W.WALK, W.GRASS) or self.gate_open(m, nx, ny):
                yield d, (nx, ny), b
            elif b in WIND:
                # The current carries you on until the next tile is blocked (pr_overworld.cpp): you land at its end.
                cx, cy = nx, ny
                while self.w.beh(mi, cx, cy) in WIND:
                    wx, wy = DIRS[WIND[self.w.beh(mi, cx, cy)]]
                    tx, ty = cx + wx, cy + wy
                    if not (0 <= tx < m['w'] and 0 <= ty < m['h']) or (tx, ty) in actors or \
                            m['beh'][ty * m['w'] + tx] not in (W.WALK, W.GRASS) and m['beh'][ty * m['w'] + tx] not in WIND:
                        break
                    cx, cy = tx, ty
                yield d, (cx, cy), b
            elif b == W.WATER and surf:
                yield d, (nx, ny), b
            elif b in LEDGE and LEDGE[b] == d:
                bx, by = nx + dx, ny + dy
                if 0 <= bx < m['w'] and 0 <= by < m['h'] and m['beh'][by * m['w'] + bx] in (W.WALK, W.GRASS) and (bx, by) not in actors:
                    yield d, (bx, by), b
            elif b == W.DOOR:
                yield d, ('door', nx, ny), b
            elif b == W.MAT and m['room']:
                yield d, ('mat', nx, ny), b

    def gate_open(self, m, x, y):
        for g in m['gates']:
            if g['y'] == y and g['x0'] <= x <= g['x1']:
                return any(t['elite'] == g['elite'] and self.beaten(t['id']) for t in m['trainers'])
        return False

    def bfs(self, mi, start, goal, surf=False, avoid_grass=False):
        """goal(node) -> bool, node a (x, y) or ('link', k) / ('door', x, y) / ('mat', x, y). Returns the
        directions to the nearest goal, or None."""
        actors = self.solid_actors(mi)
        now = self.e.frames
        prev = {start: None}
        dq = collections.deque([start])
        found = None
        while dq:
            n = dq.popleft()
            if n != start and goal(n):
                found = n
                break
            if not isinstance(n[0], int):
                continue
            for d, nn, b in self.neighbours(mi, n[0], n[1], actors, surf, now):
                if nn not in prev:
                    prev[nn] = (n, d)
                    dq.append(nn)
        if found is None:
            return None
        path = []
        n = found
        while prev[n]:
            n, d = prev[n][0], prev[n][1]
            path.append(d)
        return path[::-1]

    def walk(self, path, max_steps=None):
        """Walks a path; stops at the first step that doesn't go as planned. Returns True if it all went."""
        for i, d in enumerate(path):
            if max_steps is not None and i >= max_steps:
                return False
            m0, x0, y0 = self.pos()
            p = self.step(d)
            if p is None:
                # Blocked (someone walked in the way) or a screen came up (text, a battle).
                if self.idle():
                    dx, dy = DIRS[d]
                    self.blocked[(m0, x0 + dx, y0 + dy)] = self.e.frames + 400
                    return False
                self.after_screen()
                return False
            if p[0] != m0:
                self.on_map_change(m0, p[0])
                return False
            exp = (x0 + DIRS[d][0], y0 + DIRS[d][1])
            if self.w.beh(m0, *exp) in WIND:
                for _ in range(40):     # ride the current to its end before the next step
                    q = self.pos(); self.e.wait(8)
                    if self.pos() == q:
                        break
                continue
            if (p[1], p[2]) != exp and not self.w.beh(m0, *exp) in LEDGE:
                # A wind current, or something moved us.
                self.after_screen()
                return False
        return True

    def on_map_change(self, a, b):
        self.log('map', frm=self.w.maps[a]['name'])
        self.after_screen()

    def after_screen(self):
        """Something took over: text, a battle, a scene. Mash through it and note what changed."""
        before_hp = self.able()
        money0 = self.e.g('money', 4, False)
        m0 = self.pos()
        k0 = self.progress_key()
        f0 = self.e.frames
        n = self.settle()
        if n > 2:
            hp, mx, party = self.able()
            k1 = self.progress_key()
            rec = dict(presses=n, frames=self.e.frames - f0, hp=hp, max_hp=mx, levels=[p['level'] for p in party])
            if k1 != k0:
                rec['progress'] = True
            self.log('screen', **rec)
        hp, mx, party = self.able()
        moved = self.area_of(self.pos()[0]) != self.area_of(m0[0])
        lost = moved and hp == mx and n > 20 and (self.e.g('money', 4, False) < money0 or before_hp[0] < before_hp[1])
        if lost:
            self.lost = True
            self.log('whiteout', money=money0 - self.e.g('money', 4, False))
            self.shot('whiteout')
        return n

    # ----- going places -----
    def area_of(self, mi):
        m = self.w.maps[mi]
        return m['exit_map'] if m['room'] else mi

    def area_route(self, src, dst):
        """Area-level BFS over links (respecting what we know is shut). Returns [(map, link index or
        ('door', x, y) or ('mat',)), ...] hops."""
        prev = {src: None}
        dq = collections.deque([src])
        while dq:
            a = dq.popleft()
            if a == dst:
                break
            m = self.w.maps[a]
            hops = []
            hops = self.hops(a)
            for b, hop in hops:
                if b not in prev:
                    prev[b] = (a, hop)
                    dq.append(b)
        if dst not in prev:
            return None
        out = []
        n = dst
        while prev[n]:
            a, hop = prev[n]
            out.append((a, hop))
            n = a
        return out[::-1]

    def hops(self, a):
        """Where one hop from map a goes: links, doors, a room's mat, and a rift to the area's twin."""
        m = self.w.maps[a]
        if m['room']:
            return [(m['exit_map'], ('mat',))]
        out = []
        for k, l in enumerate(m['links']):
            if l['to'] >= 0 and self.bad_links.get((a, k), 'open') != self.last_progress:
                out.append((l['to'], ('link', k)))
        for d in m['doors']:
            out.append((d['room'], ('door', d['x'], d['y'])))
        if m.get('twin', -1) >= 0:
            for p in m['people']:
                if p['role'] == 'TWIN' and self.bad_links.get((a, 'twin'), 'open') != self.last_progress:
                    out.append((m['twin'], ('person', p['x'], p['y'])))
                    break
        return out

    def go_hop(self, hop):
        """From the current map, take one hop (a link, a door, or a room's mat)."""
        mi, x, y = self.pos()
        surf = bool(self.e.g('surfing', 1, False))
        if hop[0] == 'person':
            p = next(p for p in self.w.maps[mi]['people'] if (p['x'], p['y']) == (hop[1], hop[2]))
            before = self.pos()[0]
            self.talk_person(mi, p)
            if self.pos()[0] == before:
                self.bad_links[(mi, 'twin')] = self.last_progress
                self.log('rift_failed')
                return None
            return True
        if hop[0] == 'link':
            goal = lambda n: n == ('link', hop[1])
        elif hop[0] == 'door':
            goal = lambda n: n == ('door', hop[1], hop[2])
        else:
            goal = lambda n: isinstance(n[0], str) and n[0] == 'mat'
        path = self.bfs(mi, (x, y), goal, surf)
        if path is None and not surf:
            path = self.bfs(mi, (x, y), goal, True)
            if path is not None:
                return self.walk_surfing(path)
        if path is None:
            return None
        return self.walk(path)

    def walk_surfing(self, path):
        # Walk to the water's edge, face it and press A (SURF), then go on.
        mi, x, y = self.pos()
        m = self.w.maps[mi]
        for i, d in enumerate(path):
            nx, ny = x + DIRS[d][0], y + DIRS[d][1]
            if 0 <= nx < m['w'] and 0 <= ny < m['h'] and m['beh'][ny * m['w'] + nx] == W.WATER:
                if not self.walk(path[:i]):
                    return False
                self.e.press(d, 3); self.e.wait(12)
                self.e.press('A'); self.e.wait(30)
                self.settle()
                if not self.e.g('surfing', 1, False):
                    self.log('cant_surf')
                    self.blocked[(mi, nx, ny)] = self.e.frames + 100000
                    return False
                self.log('surf')
                return self.walk(path[i:])
            x, y = nx, ny
        return self.walk(path)

    def goto_tile(self, mi, tx, ty, adjacent=True, tries=100):     # each battle on the way costs a try
        """Gets to (tx, ty) on map mi (next to it, facing it, when adjacent). Returns True when there."""
        for attempt in range(tries):
            cm, x, y = self.pos()
            if cm == mi:
                if adjacent:
                    if abs(x - tx) + abs(y - ty) == 1:
                        d = [k for k, v in DIRS.items() if (x + v[0], y + v[1]) == (tx, ty)][0]
                        self.e.wait(18)
                        if FACE[self.facing()] != d:
                            self.e.press(d, 3); self.e.wait(12)
                        return True
                    goal = lambda n, tx=tx, ty=ty: isinstance(n[0], int) and abs(n[0] - tx) + abs(n[1] - ty) == 1
                else:
                    if (x, y) == (tx, ty):
                        return True
                    goal = lambda n, tx=tx, ty=ty: n == (tx, ty)
                surf = bool(self.e.g('surfing', 1, False))
                path = self.bfs(cm, (x, y), goal, surf)
                if path is None and not surf:
                    path = self.bfs(cm, (x, y), goal, True)
                    if path is not None:
                        self.walk_surfing(path)
                        continue
                if path is None:
                    return False
                self.walk(path)
                continue
            gm = self.gym_of(cm)
            if gm is not None and (x, y) != gm.start and not self.gym_run(cm, leave=True):
                return False        # a puzzle gym's way out is the solver's, not a straight walk to the mat
            route = self.area_route(cm, mi)
            if not route:
                return False
            r = self.go_hop(route[0][1])
            if r is None:
                # Can't reach that hop from here: treat the link as shut for now.
                if route[0][1][0] == 'link':
                    self.bad_links[(cm, route[0][1][1])] = self.last_progress
                return False
            if r is False and route[0][1][0] == 'link' and self.pos()[0] == cm and self.at_link_edge(cm, route[0][1][1]):
                # Didn't cross: maybe a gate said no. Three times and it's shut until something changes.
                key = (cm, route[0][1][1])
                self.fails[key] = self.fails.get(key, 0) + 1
                if self.fails[key] >= 3:
                    self.bad_links[key] = self.last_progress
                    self.fails[key] = 0
                    self.log('shut', link=self.w.maps[cm]['links'][key[1]]['name'])
        return False

    def at_link_edge(self, mi, k):
        _, x, y = self.pos()
        l = self.w.maps[mi]['links'][k]
        return any(l['ox'] <= x + dx < l['ox'] + l['w'] and l['oy'] <= y + dy < l['oy'] + l['h'] for dx, dy in DIRS.values())

    def talk(self):
        self.e.press('A'); self.e.wait(20)
        return self.after_screen()

    # ----- the plan -----
    KEY_ROLES = ('RIVAL', 'LEADER', 'ELITE', 'CHAMPION')

    def region_now(self):
        return self.w.maps[self.area_of(self.pos()[0])]['region']

    def hops_from(self, src):
        """Area-hop distances from src (rooms count as a hop)."""
        dist = {src: 0}
        dq = collections.deque([src])
        while dq:
            a = dq.popleft()
            for b, hop in self.hops(a):
                if b not in dist:
                    dist[b] = dist[a] + 1
                    dq.append(b)
        return dist

    def goals(self):
        """What a player would head for next, nearest first: an unbeaten rival, leader, Elite Four or Champion,
        an area not yet visited, an uncaught legend, or (style 'all') any trainer and item ball."""
        rg = self.region_now()
        dist = self.hops_from(self.pos()[0])
        visited = self.e.bits('visited', 128)
        out = []
        for mi, d in dist.items():
            m = self.w.maps[mi]
            if m['region'] != rg:
                continue
            for t in m['trainers']:
                if t['scene'] or self.beaten(t['id']):
                    continue
                if t['role'] == 'TOWER':
                    continue        # the CHALLENGE TOWER's floors: adventure mode, not the story
                if t['role'] in self.KEY_ROLES or self.fight_all or (m['flags'] & 8):
                    out.append((d, 0, ('trainer', mi, t['x'], t['y'], t['title'])))
            if not m['room'] and not (visited[mi >> 3] >> (mi & 7)) & 1 and not (m['flags'] & (32 | 64)):
                out.append((d, 1, ('visit', mi, m['spawn'][0], m['spawn'][1], m['name'])))
            if not m['room'] and m.get('legend_xy', (-1, -1))[0] >= 0:
                out.append((d, 2, ('legend', mi, m['legend_xy'][0], m['legend_xy'][1], m['legend'])))
            if self.style_all:
                for it in m['items']:
                    if not self.e.bit('picked', it['id']):
                        out.append((d, 3, ('item', mi, it['x'], it['y'], it['item'])))
            for p in m['people']:
                if p['role'] in self.SPECIAL and (mi, p['x'], p['y']) not in self.talked:
                    out.append((d, 2, ('person', mi, p['x'], p['y'], p['role'])))
        if self.champion(rg):
            role = self.TRAVEL.get(rg)
            for mi in dist:
                if self.w.maps[mi]['region'] == rg and role:
                    for p in self.w.maps[mi]['people']:
                        if p['role'] == role:
                            out.append((999, 9, ('travel', mi, p['x'], p['y'], role)))
        out.sort(key=lambda g: (g[0], g[1]))
        return [g[2] for g in out if g[2] not in self.failed.get(self.last_progress, set())]

    SPECIAL = ('MEW_SIGHT', 'SEED', 'TREE', 'PLATE', 'PROF')
    TRAVEL = {1: 'FERRY', 2: 'CAPTAIN', 3: 'PILOT', 4: 'GUIDE_ON', 5: 'GUIDE_ON', 6: 'GUIDE_ON', 7: 'GUIDE_ON', 8: 'GUIDE_ON'}
    CHAMP_FLAG = {2: 4, 3: 8, 4: 11, 5: 14, 6: 17, 7: 19, 8: 23, 9: 26}

    def champion(self, rg):
        if rg == 1:
            return bool(self.story() & (1 << 14))
        f = self.CHAMP_FLAG[rg]
        return bool(self.e.bit('flags', f))

    def heal(self):
        """To the nearest POKéMON CENTER and its nurse."""
        dist = self.hops_from(self.pos()[0])
        best = None
        for mi, d in dist.items():
            m = self.w.maps[mi]
            if m['room']:
                for p in m['people']:
                    if p['role'] == 'NURSE' and (best is None or d < best[0]):
                        best = (d, mi, p)
        if best is None:
            self.log('no_center')
            return False
        d, mi, p = best
        if not self.talk_person(mi, p):
            return False
        hp, mx, party = self.able()
        self.log('heal', hp=hp, max_hp=mx)
        return hp == mx

    def person_spot(self, mi, p):
        """Where to stand to talk to someone (across a counter in front of them, if there is one)."""
        dx, dy = DIRS[p['facing'][0]]
        if self.w.beh(mi, p['x'] + dx, p['y'] + dy) == W.COUNTER:
            return p['x'] + 2 * dx, p['y'] + 2 * dy, OPP[p['facing'][0]]
        return None

    def talk_person(self, mi, p, b_only=False):
        spot = self.person_spot(mi, p)
        if spot:
            if not self.goto_tile(mi, spot[0], spot[1], adjacent=False):
                return False
            self.e.wait(18)
            self.e.press(spot[2], 3); self.e.wait(12)
        elif not self.goto_tile(mi, p['x'], p['y']):
            return False
        if b_only:
            # A to start, then only B: through the text and back out of any menu (a mart's BUY).
            self.e.press('A'); self.e.wait(20)
            for i in range(60):
                if self.idle():
                    break
                self.e.press('B'); self.e.wait(14)
            return True
        self.talk()
        return True

    def nearest_role(self, role):
        dist = self.hops_from(self.pos()[0])
        best = None
        for mi, d in dist.items():
            for p in self.w.maps[mi]['people']:
                if p['role'] == role and (best is None or d < best[0]):
                    best = (d, mi, p)
        return best

    # Items by item_id (pr_ids.h) and their prices.
    POKEBALL, POTION, SUPERPOTION, HYPERPOTION, REVIVE, GREATBALL, ULTRABALL, MAXPOTION = 0, 1, 2, 7, 8, 13, 14, 17
    PRICE = {0: 200, 1: 300, 2: 700, 7: 1200, 8: 1500, 13: 600, 14: 1200, 17: 2500}

    def need_shop(self):
        it = self.e.items(32)
        balls = it[self.POKEBALL] + it[self.GREATBALL] + it[self.ULTRABALL]
        meds = it[self.POTION] + it[self.SUPERPOTION] + it[self.HYPERPOTION] + it[self.MAXPOTION]
        return self.e.g('money', 4, False) >= 1500 and (balls < 5 or meds < 4)

    def shop(self):
        """To the nearest POKé MART: the clerk (free POKé BALLS the first time in a town), then a sensible basket.
        (The buying itself is written straight into the bag: what the BUY menu would do.)"""
        best = self.nearest_role('CLERK')
        if not best:
            return False
        d, mi, p = best
        if not self.talk_person(mi, p, b_only=True):
            return False
        b = self.badges(1)
        ball = self.ULTRABALL if b >= 5 else self.GREATBALL if b >= 2 else self.POKEBALL
        med = self.MAXPOTION if b >= 6 else self.HYPERPOTION if b >= 5 else self.SUPERPOTION if b >= 2 else self.POTION
        money = self.e.g('money', 4, False)
        budget = money * 7 // 10
        it = bytearray(self.e.items(32))
        bought = {}
        for item, want in ((med, 8), (ball, 10), (self.REVIVE, 3 if b >= 5 else 0)):
            while it[item] < want and budget >= self.PRICE[item] and it[item] < 99:
                it[item] += 1; budget -= self.PRICE[item]; money -= self.PRICE[item]
                bought[item] = bought.get(item, 0) + 1
        self.e.write(self.addr + self.e.t['items'], bytes(it))
        self.e.write(self.addr + self.e.t['money'], struct.pack('<I', money))
        self.log('shop', bought=bought, money=money)
        return True

    def rotate(self, cap=None):
        """The PC: the highest-level Pokémon from the boxes into the party (what a player does as new catches
        outgrow the old team). Written straight into the save data."""
        t = self.e.t
        sz = t['mon_size']
        cap = cap or self.party_cap()
        n = self.e.g('party_count', 1, False)
        party = self.e.read(self.addr + t['party'], sz * 12)
        box = self.e.read(self.addr + t['box'], sz * 420)
        mons = [party[i * sz:(i + 1) * sz] for i in range(n)] + [box[i * sz:(i + 1) * sz] for i in range(420)]
        lvl = lambda r: struct.unpack_from('<H', r, t['m_level'])[0]
        live = [r for r in mons if lvl(r)]
        live.sort(key=lambda r: -lvl(r))
        keep, rest = live[:cap], live[cap:]
        if [bytes(r) for r in keep] == [bytes(r) for r in mons[:n]]:
            return
        newp = b''.join(keep) + bytes(sz * (12 - len(keep)))
        newb = b''.join(rest) + bytes(sz * (420 - len(rest)))
        self.e.write(self.addr + t['party'], newp)
        self.e.write(self.addr + t['box'], newb)
        self.e.write(self.addr + t['party_count'], bytes([len(keep)]))
        self.log('rotate', party=[(struct.unpack_from('<H', r, 0)[0], lvl(r)) for r in keep])

    def party_cap(self):
        # 9.0.1: 12 (two teams of six) from the fourth VELLORIN badge, as in the game; 'solo' keeps one.
        if self.style == 'solo':
            return 1
        return 12 if self.badges(1) >= 4 else 6

    def need_heal(self):
        hp, mx, party = self.able()
        if not party:
            return False
        lead_low = party[0]['hp'] * 5 < party[0]['max_hp'] * 2      # a player heals a lead under 40% before the next fight
        return mx and (hp * 10 < mx * 6 or lead_low or sum(1 for p in party if p['hp']) * 3 < len(party) * 2)

    def set_policy(self, grinding=False):
        n = self.e.g('party_count', 1, False)
        base = STYLES[self.style if self.style in STYLES else 'smart']
        if self.style in ('smart', 'twoteam'):
            base = 3        # catches what it hasn't got (a team that keeps up with the badge levels), runs from the rest
        run = self.run_wild and not grinding and self.style != 'masher'
        self.e.set_policy(base | (0x80 if run else 0))
        self.e.write(SRAM + 0x7E05, bytes([1 if self.style == 'twoteam' else 0]))   # the team prompt alternates

    def grind(self, levels=3, max_frames=60000):
        """Walks up and down the nearest tall grass until the party's average level is `levels` higher."""
        self.set_policy(grinding=True)
        f0 = self.e.frames
        _, _, party = self.able()
        start = sum(p['level'] for p in party) / max(1, len(party))
        dist = self.hops_from(self.pos()[0])
        best = None
        for mi, d in sorted(dist.items(), key=lambda kv: kv[1]):
            m = self.w.maps[mi]
            if m['room'] or m['region'] != self.region_now():
                continue
            for i, b in enumerate(m['beh']):
                if b == W.GRASS:
                    best = (mi, i % m['w'], i // m['w'])
                    break
            if best:
                break
        if not best:
            self.log('no_grass')
            return False
        self.log('grind_start', level=start, at=self.w.maps[best[0]]['name'])
        while self.e.frames - f0 < max_frames:
            if self.need_heal():
                self.heal()
                self.set_policy(grinding=True)
            if not self.goto_tile(best[0], best[1], best[2], adjacent=False):
                break
            for d in 'LRLRUDUD':
                self.walk([d, OPP[d]])
            _, _, party = self.able()
            avg = sum(p['level'] for p in party) / max(1, len(party))
            if avg >= start + levels:
                break
        _, _, party = self.able()
        avg = sum(p['level'] for p in party) / max(1, len(party))
        self.log('grind_end', level=avg, frames=self.e.frames - f0)
        self.set_policy()
        return True

    def do_goal(self, g):
        kind, mi, x, y, what = g
        if kind == 'visit':
            # Getting into the area is the point; its spawn may be far from where we come in.
            ok = self.goto_tile(mi, x, y, adjacent=False, tries=8)
            return ok or self.area_of(self.pos()[0]) == mi
        if kind in ('person', 'travel'):
            p = next(p for p in self.w.maps[mi]['people'] if (p['x'], p['y']) == (x, y))
            k0 = self.progress_key()
            r0 = self.region_now()
            ok = self.talk_person(mi, p)
            if self.progress_key() != k0 or self.region_now() != r0:
                self.talked.add((mi, x, y))
            if kind == 'travel':
                self.log('travel', ok=ok, region=self.region_now())
            return ok
        if kind == 'item':
            if not self.goto_tile(mi, x, y):
                return False
            self.talk()
            return True
        if self.gym_of(mi) is not None:
            # 9.6.0: a puzzle gym (9.4.0): in at the door, then the solver's way to the leader, fighting the juniors.
            if self.pos()[0] != mi and not self.goto_tile(mi, *self.w.maps[mi]['spawn'], adjacent=False, tries=8):
                return False
            if not self.gym_run(mi):
                return False
        if not self.goto_tile(mi, x, y):
            return False
        before = self.progress_key()
        self.talk()
        return True

    def gym_of(self, mi):
        """The solver's Gym for a puzzle gym room (tools/gym/solver.py, data/gym_layouts.json), else None."""
        m = self.w.maps[mi]
        lead = [t for t in m['trainers'] if t['role'] == 'LEADER']
        if not m.get('room') or not lead:
            return None
        if not hasattr(self, '_gyms'):
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gym'))
            from solver import Gym
            L = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'gym_layouts.json')))
            # The layouts go by area; a gym's trainers know their town by its map (area_maps[area]).
            wd = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'generated', 'include', 'pr_world_data.h')).read()
            area_maps = [int(v) for v in wd[wd.index('area_maps[] = {') + 15:].split('}')[0].split(',')]
            self._gyms = {area_maps[int(a)]: Gym(int(a), dict(g, states=[tuple(x) for x in g['states']])) for a, g in L.items()}
        return self._gyms.get(lead[0]['area'])

    def gym_run(self, mi, leave=False):
        """From the rug, plays the solver's shortest way to the leader with the juniors as they are now
        (or, with leave, from wherever the last run ended back to the rug, as the door's mat is beside it)."""
        from collections import deque
        from solver import D4
        gm = self.gym_of(mi)
        m = self.w.maps[mi]
        ids = []
        for jx, jy in gm.juniors:
            t = next((t for t in m['trainers'] if t['role'] == 'JUNIOR' and (t['x'], t['y']) == (jx, jy)), None)
            ids.append(t['id'] if t else -1)
        beaten = lambda: sum(1 << i for i, t in enumerate(ids) if t < 0 or self.beaten(t))
        # (Off the rug, after a loss or a reload, it starts from where we stand with the room as it began.)
        b0 = beaten()
        st0 = (tuple(self.pos()[1:]), 0, b0, gm.boulders0, gm.pits0, 1 if gm.cfg['gate'] == 'juniors' and b0 == (1 << len(ids)) - 1 else 0, 0)
        last = getattr(self, '_gym_last', None)
        if last and last[0] == mi and last[1][0] == st0[0]:
            st0 = last[1][:2] + (b0,) + last[1][3:]      # the room as the last run left it (boulders, switches)
        done = (lambda st: st[0] == gm.start) if leave else gm.at_goal
        prev, q, path = {st0: None}, deque([st0]), None
        while q:
            st = q.popleft()
            if done(st):
                path = []
                while prev[st]:
                    st, keys, after = prev[st][0], prev[st][1], st
                    path.append((keys, after))
                path.reverse()
                break
            for keys, n in [(k, gm.step(st, d)) for k, d in zip('UDLR', D4)] + gm.labeled_actions(st):
                if n and n not in prev:
                    prev[n] = (st, keys)
                    q.append(n)
        if path is None:
            self.log('gym_no_route', area=gm.area)
            return False
        for n, (keys, after) in enumerate(path):
            way = keys[-1] if keys != 'A' else None
            if way and FACE[self.facing()] != way:
                self.e.press(way, 1); self.e.wait(16)
            self.e.press('A' if keys[0] == 'A' else way, 1); self.e.wait(120)
            want = after[2]
            for _ in range(600):
                if beaten() & want == want or self.pos()[0] != mi:
                    break
                self.e.press('A'); self.e.wait(20)
            if beaten() != b0:
                self.settle()       # the battle's end: EXP, new moves, the junior's last words
                b0 = beaten()
            for _ in range(10):     # a device's text ("You turned the pedestal's dial."), as gymtest does
                if self.idle():
                    break
                self.e.press('B'); self.e.wait(30)
            if self.pos()[0] != mi:
                self.log('gym_out', area=gm.area, step=n)      # lost a battle (or the floor gave way)
                return False
            if tuple(self.pos()[1:]) != after[0]:
                self.log('gym_off_route', area=gm.area, step=n, at=self.pos()[1:], want=after[0]); self.shot('gym_off')
                return False
            self._gym_last = (mi, after)
        if leave:
            self._gym_last = None       # out by the mat, the room resets
        self.log('gym_leave' if leave else 'gym_route', area=gm.area, steps=len(path))
        return True

    def play(self, max_frames, checkpoint=None):
        """Plays until max_frames, the end of the main story, or stuck."""
        self.set_policy()
        self.e.write(self.addr + self.e.t['opt'], bytes([2]))     # TEXT SPEED: FAST, as most players set it
        while self.e.frames < max_frames:
            if self.e.crashed():
                self.log('crash'); self.shot('crash')
                return 'crash'
            key = self.progress_key()
            if key != self.last_progress:
                if self.last_progress is not None:
                    self.log('progress', badges=[self.badges(r) for r in range(1, 10)], party=[(p['species'], p['level']) for p in self.able()[2]])
                    if checkpoint:
                        checkpoint(self)
                self.last_progress = key
                self.retries = 0
                if self.rotate_party:
                    self.rotate()
                self.set_policy()
            if self.e.g("party_count", 1, False) > self.party_cap():
                self.rotate()       # over what the game allows (6, or 12 from the fourth badge)
            if self.need_heal():
                if not self.heal():
                    self.log('heal_failed')
            if self.need_shop() and self.shop_ok != self.last_progress:
                if not self.shop():
                    self.shop_ok = self.last_progress
            hp_before = self.able()[0]
            gs = self.goals()
            if not gs and self.failed.get(self.last_progress) and self.retries < 6:
                # Everything left beat us or was out of reach: level up a bit and try it all again, as a player would.
                self.retries += 1
                self.log('retry', n=self.retries)
                self.failed.pop(self.last_progress)
                self.bad_links.clear()
                self.grind(4)
                continue
            if not gs:
                self.log('no_goals'); self.shot('no_goals')
                return 'no_goals'
            g = gs[0]
            self.log('goal', goal=list(g))
            self.lost = False
            m0 = self.pos()
            k0 = self.progress_key()
            try:
                ok = self.do_goal(g)
            except Stuck as s:
                self.log('stuck', why=str(s)); self.shot('stuck')
                return 'stuck'
            if self.whited_out(hp_before):
                self.log('lost', goal=list(g))
                self.shot('lost')
                self.grind()
                continue
            if self.progress_key() == k0 and (not ok or g[0] != 'visit'):
                self.failed.setdefault(self.last_progress, set()).add(g)
                self.log('goal_failed', goal=list(g))
        return 'time'

    def whited_out(self, hp_before):
        lost, self.lost = self.lost, False
        return lost
