#!/usr/bin/env python3
"""Story soft-lock check: plays the whole game's progression on the map data alone (no emulator, ~1 min) and
reports anything a player could never reach, or could walk into and never walk out of.
    python3 tools/pilot/storycheck.py [GBA_DIR]        (after `make`, which writes generated/)

It floods every tile you can walk to from DUSKMERE HOLLOW with what you hold so far, beats every trainer and
catches every legend it can stand next to (it assumes you win), then opens what that unlocks (SURF after
TIDALKEEP, DIVE after RIMEFALL, badge gates, gym and rival gates, shrine gates, the ferries and guides to the
next region) and floods again, until nothing new opens. The rules are pr_overworld.cpp's and pr_field.cpp's;
gyms count as beaten once you're inside (tools/gym/solver.py checks their puzzles).
Then, for every one-way step it took (a ledge, a wind current, a VISITED cliff, a dive), it checks you can still
get back to the start with what you held at that moment. Exit status 1 if anything is unreachable or a trap."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world as W

DIRS = ((0, 1), (0, -1), (-1, 0), (1, 0))
LEDGE = {W.LEDGE_D: (0, 1), W.LEDGE_R: (1, 0), W.LEDGE_L: (-1, 0)}
WIND = {W.WU: (0, -1), W.WD: (0, 1), W.WL: (-1, 0), W.WR: (1, 0)}
WALKABLE = (W.WALK, W.GRASS, W.DOOR, W.MAT, W.WU, W.WD, W.WL, W.WR)
F_CHAMPION, F_SHRINE, F_TOWER_TOWN = 4, 256, 32
KEY_ROLES = ('LEADER', 'RIVAL', 'ELITE', 'CHAMPION')
# The ships between regions (pr_field.cpp ferry/captain/pilot): the same role at both ports, the lower region's
# CHAMPION only (going up). GUIDE_ON / GUIDE_BACK (region_guide) do the same from GENOVA on.
PAIRS = {'FERRY': 1, 'CAPTAIN': 2, 'PILOT': 3}


class State:
    def __init__(self, w):
        self.w = w
        self.beaten, self.picked, self.visited, self.legends = set(), set(), set(), set()

    def copy(self):
        s = State(self.w)
        s.beaten, s.picked, s.visited, s.legends = set(self.beaten), set(self.picked), set(self.visited), set(self.legends)
        return s.refresh()

    def refresh(self):
        """Works out what the sets unlock, once per stage (the checks below are slow)."""
        rgs = {m['region'] for m in self.w.maps if not m['room']}
        self.can_surf, self.can_dive = self._surf(), self._dive()
        self.badge_n = {rg: self._badges(rg) for rg in rgs}
        self.champ = {rg: self._champion(rg) for rg in rgs}
        self.shrine = {rg: self._shrines(rg) for rg in rgs}
        return self

    def surf(self): return self.can_surf
    def dive(self): return self.can_dive
    def badges(self, rg): return self.badge_n[rg]
    def champion(self, rg): return self.champ[rg]
    def shrines(self, rg): return self.shrine[rg]

    def cleared(self, name):
        return any(m['leader_id'] >= 0 and m['leader_id'] in self.beaten for m in self.w.maps if not m['room'] and m['name'] == name)

    # pr_field.cpp can_surf / can_dive: the HM, or that gym beaten.
    def _surf(self):
        return self.cleared('TIDALKEEP CITY') or any(i[3] == 'HM03' for i in self.picked)

    def _dive(self):
        return self.cleared('RIMEFALL TOWN') or any(i[3] == 'HM08' for i in self.picked)

    def _badges(self, rg):
        return sum(1 for m in self.w.maps if not m['room'] and m['gate'] == 'GYM' and m['region'] == rg and m['leader_id'] in self.beaten)

    def _champion(self, rg):
        return any(m['leader_id'] in self.beaten for m in self.w.maps if not m['room'] and m['region'] == rg and m['flags'] & F_CHAMPION)

    def _shrines(self, rg):
        return all(m['leader_id'] < 0 or m['leader_id'] in self.beaten or m['index'] in self.legends
                   for m in self.w.maps if not m['room'] and m['region'] == rg and m['flags'] & F_SHRINE)


class Check:
    def __init__(self, gba_dir):
        self.w = w = W.load(gba_dir)
        raw = W.parse(os.path.join(gba_dir, 'generated', 'include', 'pr_world_data.h'))
        pairs = lambda name: [tuple(v) for v in zip(*[iter(W.rows(raw.get(name, '')))] * 2)]
        for m in w.maps:
            m['dive_spots'] = set(pairs('map%d_dive' % m['index'])) if not m['room'] else set()
            m['shafts'] = pairs('map%d_shafts' % m['index']) if not m['room'] else []
        self.start = (0,) + w.maps[0]['spawn']
        self.room_of, self.people_at, self.trainer_at, self.item_at = {}, set(), {}, {}
        for m in w.maps:
            mi = m['index']
            self.people_at |= {(mi, p['x'], p['y']) for p in m['people'] if not p['wander']}
            self.trainer_at.update({(mi, t['x'], t['y']): t for t in m['trainers'] if not t['scene']})
            self.item_at.update({(mi, i['x'], i['y']): (mi, i['x'], i['y'], i['item']) for i in m['items']})
        for m in w.maps:
            for d in m['doors']:
                self.room_of[(m['index'], d['x'], d['y'])] = d['room']

    # ----- what's in the way -----
    def solid(self, s, mi, x, y):
        k = (mi, x, y)
        if k in self.people_at:
            return True
        t = self.trainer_at.get(k)
        if t and not (t['vanish'] and t['id'] in s.beaten):
            return True
        i = self.item_at.get(k)
        return i is not None and i not in s.picked

    def beh(self, mi, x, y):
        return self.w.beh(mi, x, y)

    def open_tile(self, s, mi, x, y, surfing):
        b = self.beh(mi, x, y)
        if b is None or self.solid(s, mi, x, y):
            return False
        if b == W.ITEM:
            return (mi, x, y) in self.item_at
        return b in WALKABLE or (b == W.WATER and surfing)

    def link_at(self, mi, x, y):
        for l in self.w.maps[mi]['links']:
            if l['ox'] <= x < l['ox'] + l['w'] and l['oy'] <= y < l['oy'] + l['h']:
                return l
        return None

    def link_open(self, s, mi, l):
        m, to = self.w.maps[mi], self.w.maps[l['to']]
        if l['badges'] and s.badges(to['region']) < l['badges']:
            return False
        if l['need'] == 'VISITED' and l['to'] not in s.visited:
            return False
        if l['need'] == 'SHRINES' and not s.shrines(m['region']):
            return False
        if to['flags'] & F_TOWER_TOWN and not s.champion(1):
            return False
        if l['gate'] and m['leader_id'] >= 0 and m['leader_id'] not in s.beaten:
            return False
        return True

    def landing(self, mi):
        """Where fast travel puts you: by the CENTER, else the spawn (pr_field.cpp fast_travel)."""
        m = self.w.maps[mi]
        for d in m['doors']:
            if d['kind'] == 'CENTER':
                return (mi, d['x'], d['y'] + 1)
        return (mi,) + m['spawn']

    # ----- one step -----
    def edges(self, s, n):
        """(node, one_way) for each step from node n with state s. Rooms are one node: (map, -1, -1)."""
        mi, x, y = n
        m = self.w.maps[mi]
        if m['room']:
            ex, ey = m['exit']
            yield (m['exit_map'], ex, ey + 1), False
            return
        surfing = s.surf()
        b0 = self.beh(mi, x, y)
        if b0 == W.DOOR and (mi, x, y) in self.room_of:
            yield (self.room_of[(mi, x, y)], -1, -1), False
        if b0 in WIND:
            # The current carries you on until the next tile is blocked.
            dx, dy = WIND[b0]
            if self.open_tile(s, mi, x + dx, y + dy, False):
                yield (mi, x + dx, y + dy), True
            return
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < m['w'] and 0 <= ny < m['h']):
                l = self.link_at(mi, nx, ny)
                if l and l['to'] >= 0 and self.link_open(s, mi, l):
                    tx, ty = nx - l['ox'], ny - l['oy']
                    if self.open_tile(s, l['to'], tx, ty, surfing):
                        yield (l['to'], tx, ty), l['need'] == 'VISITED'
                continue
            b = self.beh(mi, nx, ny)
            if b in LEDGE:
                if LEDGE[b] == (dx, dy) and self.open_tile(s, mi, nx + dx, ny + dy, False):
                    yield (mi, nx + dx, ny + dy), True
                continue
            if self.open_tile(s, mi, nx, ny, surfing):
                yield (mi, nx, ny), False
        # DIVE down at a dive spot, up at a light shaft (pr_field.cpp layer_spot).
        if (x, y) in m['dive_spots'] and m['dive'] >= 0 and s.dive():
            yield self.layer(mi, m['dive'], 'shafts', x, y), True
        if m['surface'] >= 0 and any((x, y) == p for p in m['shafts']):
            yield self.layer(mi, m['surface'], 'dive_spots', x, y), True
        # People who take you somewhere: a rift to the twin, a ship or guide to the next region.
        for p in m['people']:
            if abs(p['x'] - x) + abs(p['y'] - y) != 1:
                continue
            if p['role'] == 'TWIN' and m.get('twin', -1) >= 0:
                t = self.w.maps[m['twin']]
                tx = t['w'] - 1 - x if (m['flags'] | t['flags']) & 512 else x
                if self.open_tile(s, m['twin'], tx, y, False):
                    yield (m['twin'], tx, y), True
            if p['role'] in PAIRS:
                lo = PAIRS[p['role']]
                if m['region'] == lo and s.champion(lo):
                    yield self.travel(lo + 1, p['role']), True
                elif m['region'] == lo + 1:
                    yield self.travel(lo, p['role']), True
            elif p['role'] == 'GUIDE_ON' and s.champion(m['region']):
                yield self.travel(m['region'] + 1, 'GUIDE_BACK'), True
            elif p['role'] == 'GUIDE_BACK':
                yield self.travel(m['region'] - 1, 'GUIDE_ON'), True

    def travel(self, rg, role):
        for m in self.w.maps:
            if not m['room'] and m['region'] == rg and any(p['role'] == role for p in m['people']):
                return self.landing(m['index'])

    def layer(self, frm, to, key, x, y):
        f, t = self.w.maps[frm], self.w.maps[to]
        px, py = (2 * x * t['w'] + f['w']) // (2 * f['w']), (2 * y * t['h'] + f['h']) // (2 * f['h'])
        pts = list(t[key]) or [t['spawn']]
        bx, by = min(pts, key=lambda p: abs(p[0] - px) + abs(p[1] - py))
        return (to, bx, by)

    # ----- what you gain standing somewhere -----
    def gains(self, s, reached):
        changed = False
        for mi, x, y in list(reached):
            m = self.w.maps[mi]
            if mi not in s.visited:
                s.visited.add(mi); changed = True
            if m['room']:
                for t in m['trainers']:
                    if t['role'] != 'TOWER' and t['id'] not in s.beaten:
                        s.beaten.add(t['id']); changed = True
                continue
        for mi in s.visited:
            m = self.w.maps[mi]
            if m['room']:
                continue
            for t in m['trainers']:
                if t['id'] not in s.beaten and not t['scene'] and self.beside(reached, mi, t['x'], t['y']):
                    s.beaten.add(t['id']); changed = True
            for i in m['items']:
                k = (mi, i['x'], i['y'], i['item'])
                if k not in s.picked and self.beside(reached, mi, i['x'], i['y']):
                    s.picked.add(k); changed = True
            lx, ly = m.get('legend_xy', (-1, -1))
            if lx >= 0 and mi not in s.legends and self.beside(reached, mi, lx, ly):
                s.legends.add(mi); changed = True
        return changed

    @staticmethod
    def beside(reached, mi, x, y):
        return any((mi, x + dx, y + dy) in reached for dx, dy in DIRS)

    # ----- the whole game -----
    def run(self):
        s = State(self.w).refresh()
        reached = {self.start: 0}
        one_way = {}          # landing -> the stage it was first stepped to
        snaps = [s.copy()]
        stage = 0
        frontier = collections.deque([self.start])
        while True:
            while frontier:
                n = frontier.popleft()
                for nn, ow in self.edges(s, n):
                    if ow and nn not in one_way:
                        one_way[nn] = stage
                    if nn not in reached:
                        reached[nn] = stage
                        frontier.append(nn)
            if not self.gains(s, reached):
                break
            s.refresh()
            stage += 1
            snaps.append(s.copy())
            frontier.extend(reached)      # retry every edge with what's open now
        self.s, self.reached, self.snaps = s, reached, snaps
        self.one_way = one_way
        return s

    def back_to_start(self, s, nodes_from):
        """Every node in nodes_from that can't walk back to the start under s."""
        good = set()
        bad = []
        for n in nodes_from:
            if n in good:
                continue
            seen, dq, ok = {n}, collections.deque([n]), False
            while dq and not ok:
                c = dq.popleft()
                for nn, _ in self.edges(s, c):
                    if nn == self.start or nn in good:
                        ok = True
                        break
                    if nn not in seen:
                        seen.add(nn)
                        dq.append(nn)
            if ok:
                good |= seen
            else:
                bad.append((n, seen))
        return bad

    def report(self):
        w, s, out = self.w, self.s, []
        areas = [m for m in w.maps if not m['room'] and m['index'] not in s.visited]
        for m in areas:
            out.append('UNREACHED  map %d %s (region %d)' % (m['index'], m['name'], m['region']))
        for m in w.maps:
            if m['index'] not in s.visited and m['room']:
                continue
            for t in m['trainers']:
                if t['role'] in KEY_ROLES and not t['scene'] and t['id'] not in s.beaten:
                    out.append('UNBEATEN   %s %s on map %d %s' % (t['role'], t['title'], m['index'], m['name']))
            if not m['room'] and m.get('legend_xy', (-1, -1))[0] >= 0 and m['index'] not in s.legends:
                out.append('NO LEGEND  %s on map %d %s' % (m['legend'], m['index'], m['name']))
        for rg in sorted({m['region'] for m in w.maps if not m['room']}):
            if not s.champion(rg):
                out.append('NO CHAMPION region %d' % rg)
        # Traps: after each one-way step, can you walk back with what you held right then?
        by_stage = collections.defaultdict(set)
        for b, st in self.one_way.items():
            by_stage[st].add(b)
        traps = {}
        for st, nodes in sorted(by_stage.items()):
            for n, seen in self.back_to_start(self.snaps[st], nodes):
                # Tall grass or water you can fish/surf means a wild battle to lose: whiting out walks you home.
                if any(self.beh(*c) == W.GRASS for c in seen if c[1] >= 0):
                    continue
                key = (n[0], min(seen))
                if key not in traps:
                    traps[key] = (n, st, len(seen))
        for (mi, _), (n, st, size) in sorted(traps.items()):
            out.append('TRAP       map %d %s: land at %s (stage %d), %d tiles, no way back' % (mi, w.maps[mi]['name'], n[1:], st, size))
        missed = sum(1 for m in w.maps for i in m['items'] if (m['index'], i['x'], i['y'], i['item']) not in s.picked)
        print('%d stages, %d of %d maps reached, %d trainers beaten, %d legends, %d item balls out of reach' % (
            len(self.snaps), len(s.visited), len(w.maps), len(s.beaten), len(s.legends), missed))
        return out


if __name__ == '__main__':
    c = Check(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
    c.run()
    problems = c.report()
    for p in problems:
        print(p)
    print('OK: the story plays through, no traps' if not problems else '%d problems' % len(problems))
    sys.exit(1 if problems else 0)
