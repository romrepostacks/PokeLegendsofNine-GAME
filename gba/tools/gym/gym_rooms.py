# 9.4.0: draws every gym room from gba/data/gym_layouts.json (tested by solver.py) and writes what the ROM needs:
#   gba/data/gym_<area>_<state>.png        the room in each state (era, tide, season...), without people
#   gba/data/gym_<area>_<state>_alt.png    the same with every changing tile switched (fences down, pits filled,
#                                          cracked floor broken, gas cleared, vines and jets open, fans off)
#   gba/data/gym_<area>_<state>_rock.png   the same with a boulder on every tile one could be pushed to
#   gba/data/gym_puzzles.json              each room's tiles per state, its juniors and rules (solver.Gym)
# Run from the repo root: python3 gba/tools/gym/gym_rooms.py
import json, math, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solver import Gym, frame, ARROW

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
O = (38, 38, 56)

def C(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
# per type: floor kind, block kind, floor f1 f2 f3, block k1 k2 k3, accent a1 a2 a3, wall w1 w2
T = {
 'fire':     ('slab',  'rock',    '#b08068 #986c58 #704c40', '#584858 #403848 #282030', '#f8a048 #e04828 #982820', '#b06048 #804038'),
 'water':    ('tile',  'pillar',  '#e8f0f8 #c8dcf0 #98b8d8', '#e0e8f0 #b0c0d8 #7888a8', '#78c0f8 #3878d8 #204890', '#a8d0f0 #6098d0'),
 'grass':    ('lawn',  'hedge',   '#88c860 #70b050 #488840', '#88d860 #40a040 #206838', '#88d860 #40a040 #206838', '#c8b080 #987858'),
 'ground':   ('sand',  'rock',    '#e0c890 #c8a870 #987848', '#b08858 #886840 #604828', '#e8b060 #c07830 #804818', '#c09868 #886038'),
 'rock':     ('slab',  'rock',    '#c8b8a0 #b0a088 #807060', '#a09080 #786858 #504038', '#d8a878 #a87848 #704828', '#a89880 #706050'),
 'ghost':    ('dark',  'grave',   '#68587e #584a6e #3c3050', '#a8a0b8 #807890 #585068', '#c890f8 #8858d0 #583890', '#504060 #382848'),
 'electric': ('metal', 'crate',   '#d8dce4 #c0c4d0 #9098a8', '#d8d8e0 #a8a8b8 #707080', '#f8e060 #e0b020 #a07810', '#b8c0d0 #8890a8'),
 'ice':      ('tile',  'ice',     '#e8f4fc #d0e8f8 #a8c8e8', '#e0f8ff #a8d8f0 #68a8d0', '#b0e8f8 #60b8e0 #3080b0', '#c8e0f0 #90b8d8'),
 'dragon':   ('slab',  'rock',    '#8898a0 #708088 #505c68', '#687880 #4c5864 #343c48', '#a080f0 #6848c8 #402888', '#607078 #404c58'),
 'normal':   ('wood',  'crate',   '#d8b888 #c0a070 #906c48', '#c8a070 #a07850 #704c30', '#f0d080 #c8a048 #886828', '#d8c8b0 #a89880'),
 'flying':   ('marble','pillar',  '#f0f0f8 #d8dcec #a8b0c8', '#f0f0f8 #c8cce0 #9098b8', '#a8d8f8 #6898e0 #3860a8', '#c8d8f0 #98a8d0'),
 'fighting': ('wood',  'crate',   '#d0a070 #b88858 #886040', '#c89060 #a06840 #704428', '#f08060 #c84830 #882820', '#c8a888 #987058'),
 'steel':    ('metal', 'crate',   '#c0c8d0 #a8b0c0 #788090', '#b8c0c8 #8890a0 #586070', '#a8c8e8 #6890b8 #406080', '#9098a8 #687080'),
 'psychic':  ('tile',  'crystal', '#f0d8f0 #e0c0e0 #b090c0', '#f8b8e0 #d878b8 #a04888', '#f898c8 #e05898 #a03068', '#d8b8d8 #a888b0'),
 'bug':      ('lawn',  'hedge',   '#b8c868 #a0b050 #708038', '#e8d070 #c8a038 #886818', '#c8e070 #90b830 #587820', '#c8b070 #987840'),
 'fairy':    ('tile',  'crystal', '#fce8f0 #f4d0e0 #d8a8c0', '#ffd8ec #f0a8cc #c070a0', '#ffb0d8 #f078b0 #b84880', '#f8d8e8 #d0a0b8'),
 'poison':   ('dark',  'crystal', '#8870a0 #705888 #504068', '#c088d8 #9058b0 #603880', '#c880e0 #9040c0 #602890', '#705880 #504060'),
}
WALKER = set('_oLjguTJSEQ1230=sHlkNRe')

class Room:
    def __init__(s, rows, theme, dark=False):
        s.rows, s.t = rows, theme
        s.W, s.H = len(rows[0]) * 16, len(rows) * 16
        fk, bk, f, b, a, w = T[theme]
        s.fk, s.bk = fk, bk
        s.P = dict(o=O, w1=(248, 248, 248), w2=(208, 216, 224), w3=(168, 168, 192),
                   y1=(248, 216, 96), y2=(216, 160, 48), y3=(152, 104, 32), r1=(240, 112, 96), r2=(232, 72, 72), r3=(176, 40, 56))
        for k, v in zip(('f1', 'f2', 'f3'), f.split()): s.P[k] = C(v)
        for k, v in zip(('k1', 'k2', 'k3'), b.split()): s.P[k] = C(v)
        for k, v in zip(('a1', 'a2', 'a3'), a.split()): s.P[k] = C(v)
        for k, v in zip(('wl1', 'wl2'), w.split()): s.P[k] = C(v)
        s.px = [[O] * s.W for _ in range(s.H)]
        s.lights = []
        s.raft = False
        s.wrap = 0          # > 0: noise repeats every this many pixels (a big room has to share its tiles)
        s.unlit = False
    def set(s, x, y, c):
        if 0 <= x < s.W and 0 <= y < s.H and c is not None: s.px[y][x] = s.P[c] if isinstance(c, str) else c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def hl(s, x0, x1, y, c): s.rect(x0, y, x1, y, c)
    def vl(s, x, y0, y1, c): s.rect(x, y0, x, y1, c)
    def disc(s, cx, cy, r, c, ry=None):
        ry = ry or r
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if ((x - cx) / r) ** 2 + ((y - cy) / ry) ** 2 <= 1.0: s.set(x, y, c)
    def at(s, x, y):
        return s.rows[y][x] if 0 <= y < len(s.rows) and 0 <= x < len(s.rows[0]) else '#'
    def darken(s, x0, x1, y, k=0.75):
        for x in range(x0, x1 + 1):
            if 0 <= x < s.W and 0 <= y < s.H:
                p = s.px[y][x]; s.px[y][x] = tuple(int(c * k) for c in p)
    def mix(s, a, b, t):
        A, B = (s.P[a] if isinstance(a, str) else a), (s.P[b] if isinstance(b, str) else b)
        return tuple(int(A[i] + (B[i] - A[i]) * t) for i in range(3))

    # ---------- floor ----------
    def floor_px(s, x, y):
        k = s.fk
        hx, hy = (x % s.wrap, y % s.wrap) if s.wrap else (x, y)
        h = ((hx * 73856093) ^ (hy * 19349663)) % 97
        if k == 'slab':
            return 'f3' if x % 16 == 15 or y % 16 == 15 else 'f1' if x % 16 == 0 or y % 16 == 0 else ('f3' if h == 3 else 'f2')
        if k == 'tile':
            c = 'f3' if x % 8 == 7 or y % 8 == 7 else 'f2' if (x // 8 + y // 8) % 2 else 'f1'
            if c != 'f3' and (x % 8) == (y % 8) and x % 8 < 3: c = 'w1'
            return c
        if k == 'lawn':
            return 'f3' if h in (0, 19) else 'f2' if h in (5, 31, 44) else 'a1' if h == 27 else 'f1'
        if k == 'sand':
            return 'f3' if h in (0, 7) else 'f2' if h in (3, 11, 50, 61) else 'f1'
        if k == 'wood':
            r = y % 8
            if r == 7: return 'f3'
            if (x + (y // 8) * 11) % 32 == 0: return 'f3'
            return 'f1' if r == 0 else 'f2' if h in (1, 2, 3) else 'f1' if r < 3 else 'f2'
        if k == 'metal':
            if x % 16 in (0, 15) or y % 16 in (0, 15): return 'f3'
            if x % 16 in (2, 13) and y % 16 in (2, 13): return 'w1'
            return 'f1' if (x % 16) + (y % 16) < 6 else 'f2'
        if k == 'marble':
            c = 'f3' if x % 16 == 15 or y % 16 == 15 else 'f1'
            if c == 'f1' and ((x * 3 + y * 7) % 41 == 0 or (x + 2 * y) % 37 == 0): c = 'f2'
            return c
        if k == 'dark':
            c = 'f3' if x % 16 == 15 or y % 16 == 15 or (x % 16 == 7 and (y // 16) % 2) else 'f2' if h in (2, 9, 13) else 'f1'
            return c
    def floor(s):
        for y in range(32, s.H - 16):
            for x in range(16, s.W - 16): s.set(x, y, s.floor_px(x, y))
        cx = (len(s.rows[0]) // 2) * 16
        Ly = next(y for y, r in enumerate(s.rows) if 'L' in r)
        Lx = s.rows[Ly].index('L')
        X, Y = Lx * 16, Ly * 16
        if s.at(Lx, Ly + 0) == 'L' and s.at(Lx - 1, Ly) in '_H' and Ly <= 3:   # the leader's dais carpet
            s.rect(X - 26, Y + 2, X + 41, Y + 15, 'o'); s.rect(X - 25, Y + 3, X + 40, Y + 14, 'y2'); s.rect(X - 23, Y + 4, X + 38, Y + 13, 'r2'); s.hl(X - 23, X + 38, Y + 4, 'r1')

    def walls(s):
        s.rect(16, 0, s.W - 17, 31, 'wl1')
        for y in range(4, 32):
            for x in range(16, s.W - 16):
                if (y - 4) % 7 == 6 or (x + ((y - 4) // 7) * 8) % 16 == 0: s.set(x, y, 'wl2')
        s.rect(16, 0, s.W - 17, 3, 'o'); s.rect(16, 28, s.W - 17, 31, 'a3'); s.hl(16, s.W - 17, 28, 'a2')
        cx = s.W // 2
        s.disc(cx, 15, 8, 'o'); s.disc(cx, 15, 7, 'y2'); s.disc(cx - 1, 14, 6, 'y1'); s.disc(cx, 15, 5, 'a2'); s.disc(cx - 1, 14, 2, 'a1')
        for bx in (40, s.W - 49):
            s.hl(bx - 1, bx + 9, 6, 'y2')
            s.rect(bx, 7, bx + 8, 24, 'a2'); s.vl(bx, 7, 24, 'a1'); s.vl(bx + 8, 7, 24, 'a3'); s.hl(bx + 1, bx + 7, 10, 'y1')
            s.set(bx + 4, 24, 'wl1'); s.set(bx + 3, 24, 'wl1'); s.set(bx + 5, 24, 'wl1')
        s.rect(14, 0, 15, s.H - 15, 'wl2'); s.rect(s.W - 16, 0, s.W - 15, s.H - 15, 'wl2')
        s.rect(14, s.H - 16, s.W - 15, s.H - 15, 'wl2')
        mx = s.rows[-1].index('M') * 16
        for x in range(mx, mx + 16): s.rect(x, s.H - 16, x, s.H - 1, 'a3' if (x // 2) % 2 else 'a2')

    # ---------- blocks ----------
    def blk(s, ch): return s.at(*ch) in 'xI' if isinstance(ch, tuple) else False
    def block(s, x, y, ill=False):
        X, Y = x * 16, y * 16
        same = lambda c: c in ('xI' if not ill else 'xI')
        L, R, U, D = same(s.at(x - 1, y)), same(s.at(x + 1, y)), same(s.at(x, y - 1)), same(s.at(x, y + 1))
        k = s.bk
        if k == 'hedge':
            s.darken(X, X + 15, Y + 16, 0.7)
            x0, x1 = X, X + 15
            for xx in range(x0, x1 + 1):
                e = min(xx - x0 if not L else 9, x1 - xx if not R else 9)
                top = Y + (0 if U else 1 + (2 - e if e < 2 else 0))
                bot = Y + (15 if D else 14 - (1 - e if e < 1 else 0))
                if not U: s.set(xx, top, 'o')
                if not D: s.set(xx, bot, 'o')
                s.vl(xx, top + (0 if U else 1), bot - (0 if D else 1), 'k3')
                for yy in range(top + (0 if U else 1), bot - (0 if D else 1)):
                    hsh = ((xx % s.wrap if s.wrap else xx) * 7 + (yy % s.wrap if s.wrap else yy) * 13) % 11
                    if hsh < 5: s.set(xx, yy, 'k2')
                    if hsh == 0 or (not U and yy < top + 3 and hsh < 7): s.set(xx, yy, 'k1')
                if not L and xx == x0 or not R and xx == x1: s.vl(xx, top, bot, 'o')
            return
        if k == 'rock':
            s.darken(X, X + 15, Y + 16, 0.7)
            x0, x1 = X + (0 if L else 1), X + (15 if R else 14)
            y0, y1 = Y + (0 if U else 1), Y + (15 if D else 14)
            s.rect(x0, y0, x1, y1, 'o')
            s.rect(x0 + (0 if L else 1), y0 + (0 if U else 1), x1 - (0 if R else 1), y1 - (0 if D else 1), 'k2')
            if not U: s.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 4, 'k1')
            if not D: s.rect(x0 + 1, y1 - 3, x1 - 1, y1 - 1, 'k3')
            for xx in range(x0 + 2, x1 - 1, 5): s.set(xx, Y + 8 + (xx % 3), 'k3')
            if s.t in ('fire',):
                for xx in range(x0 + 2, x1 - 1):
                    if (xx * 5 + y) % 7 < 2: s.set(xx, Y + 9, 'a2')
            return
        if k == 'grave':
            s.darken(X + 2, X + 13, Y + 16, 0.6)
            s.rect(X + 3, Y + 3, X + 12, Y + 15, 'o'); s.rect(X + 4, Y + 2, X + 11, Y + 2, 'o')
            s.rect(X + 4, Y + 3, X + 11, Y + 14, 'k2'); s.rect(X + 4, Y + 3, X + 7, Y + 14, 'k1')
            s.hl(X + 6, X + 9, Y + 7, 'k3'); s.vl(X + 7, Y + 5, Y + 11, 'k3')
            s.hl(X + 2, X + 13, Y + 15, 'o')
            return
        if k == 'crystal':
            s.darken(X, X + 15, Y + 16, 0.7)
            s.rect(X + 1, Y + 1, X + 14, Y + 14, 'o')
            for yy in range(Y + 2, Y + 14):
                for xx in range(X + 2, X + 14):
                    d = (xx - X) + (yy - Y)
                    s.set(xx, yy, 'k1' if d < 10 else 'k2' if d < 20 else 'k3')
            s.vl(X + 7, Y + 2, Y + 13, 'k3'); s.hl(X + 2, X + 13, Y + 7, 'k3'); s.set(X + 4, Y + 4, 'w1'); s.set(X + 10, Y + 10, 'k1')
            return
        if k == 'ice':
            s.darken(X, X + 15, Y + 16, 0.8)
            s.rect(X, Y, X + 15, Y + 15, 'o'); s.rect(X + 1, Y + 1, X + 14, Y + 14, 'k2'); s.rect(X + 1, Y + 1, X + 14, Y + 5, 'k1')
            for k_ in range(6): s.set(X + 3 + k_, Y + 11 - k_, 'w1')
            return
        if k == 'pillar':
            s.darken(X + 1, X + 14, Y + 16, 0.7)
            s.rect(X + 2, Y, X + 13, Y + 15, 'o'); s.rect(X + 3, Y + 1, X + 12, Y + 14, 'k2'); s.rect(X + 3, Y + 1, X + 6, Y + 14, 'k1')
            s.vl(X + 12, Y + 1, Y + 14, 'k3'); s.rect(X + 1, Y, X + 14, Y + 2, 'o'); s.rect(X + 2, Y + 1, X + 13, Y + 1, 'k1')
            s.rect(X + 1, Y + 13, X + 14, Y + 15, 'o'); s.hl(X + 2, X + 13, Y + 14, 'k3')
            return
        # crate
        s.darken(X, X + 15, Y + 16, 0.7)
        s.rect(X, Y, X + 15, Y + 15, 'o'); s.rect(X + 1, Y + 1, X + 14, Y + 14, 'k2')
        s.rect(X + 1, Y + 1, X + 14, Y + 3, 'k1'); s.hl(X + 1, X + 14, Y + 8, 'k3'); s.vl(X + 5, Y + 4, Y + 14, 'k3'); s.vl(X + 10, Y + 4, Y + 14, 'k3')

    # ---------- mechanics ----------
    def water(s, x, y, deep=False):
        X, Y = x * 16, y * 16
        c1, c2 = ((88, 160, 240), (184, 224, 255)) if not deep else ((40, 72, 152), (88, 136, 216))
        s.rect(X, Y, X + 15, Y + 15, c1)
        for yy in range(Y, Y + 16):
            for xx in range(X, X + 16):
                if (xx + yy * 2) % 16 in (0, 1) and yy % 6 == 2: s.set(xx, yy, c2)
        W = lambda c: c in '~D<>^v' and s.flowbase() == 'water' or c in '~D'
        if not W(s.at(x, y - 1)) and s.at(x, y - 1) != '#': s.rect(X, Y, X + 15, Y + 2, 'k1' if s.bk == 'pillar' else (200, 192, 176)); s.hl(X, X + 15, Y + 3, 'o')
        if not W(s.at(x - 1, y)): s.vl(X, Y, Y + 15, 'o')
        if not W(s.at(x + 1, y)): s.vl(X + 15, Y, Y + 15, 'o')
        if not W(s.at(x, y + 1)): s.hl(X, X + 15, Y + 15, 'o')
        if deep:
            for r in (6, 4): pass
            s.disc(X + 7.5, Y + 8, 5, (24, 40, 96), 3); s.disc(X + 7.5, Y + 8, 3, (16, 24, 64), 2)
            s.hl(X + 4, X + 11, Y + 3, c2)
    def flowbase(s):
        return {'water': 'water', 'fairy': 'petal', 'ground': 'sand', 'steel': 'belt', 'bug': 'silk', 'flying': 'wind', 'fire': 'wind',
                'dragon': 'wind'}.get(s.t, 'belt')
    def arrow(s, x, y, d):
        X, Y = x * 16, y * 16
        base = s.flowbase()
        if base == 'water':
            s.water(x, y)
            col, col2 = (232, 248, 255), (184, 224, 255)
            if s.raft:
                s.dock(x, y); col, col2 = (248, 232, 160), (112, 72, 40)
        elif base == 'wind':
            under = s.at(x, y)  # wind over a pit or floor: draw what's under from neighbours
            if 'p' in (s.at(x - 1, y), s.at(x + 1, y), s.at(x, y - 1), s.at(x, y + 1)) or s.t == 'fire' and 'K' in (s.at(x - 1, y), s.at(x + 1, y)):
                (s.lava if s.t == 'fire' else s.pit)(x, y, skip_edges=True)
            col, col2 = (248, 248, 255), (200, 220, 248)
        elif base == 'belt':
            s.rect(X, Y, X + 15, Y + 15, (72, 76, 92)); s.rect(X + 1, Y + 1, X + 14, Y + 14, (104, 112, 128))
            for k in range(0, 16, 4):
                if d in '<>': s.vl(X + ((k + 2) % 16), Y + 1, Y + 14, (80, 84, 100))
                else: s.hl(X + 1, X + 14, Y + ((k + 2) % 16), (80, 84, 100))
            col, col2 = s.P['a1'], s.P['a2']
        elif base == 'sand':
            for yy in range(Y, Y + 16):
                for xx in range(X, X + 16):
                    if (xx * 3 + yy * 5) % 9 == 0: s.set(xx, yy, 'f3')
            col, col2 = s.P['a2'], s.P['a3']
        elif base == 'silk':
            col, col2 = (248, 248, 248), (200, 200, 216)
            if d in '<>': s.hl(X, X + 15, Y + 8, col2); s.hl(X, X + 15, Y + 7, col)
            else: s.vl(X + 8, Y, Y + 15, col2); s.vl(X + 7, Y, Y + 15, col)
        else:  # petal
            for (dx, dy) in ((3, 4), (11, 10), (8, 2)): s.disc(X + dx, Y + dy, 1.5, 'a1')
            col, col2 = s.P['a2'], s.P['a3']
        shape = [(0, -4), (-1, -3), (0, -3), (1, -3), (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2), (-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        rot = {'^': lambda a, b: (a, b), 'v': lambda a, b: (a, -b), '<': lambda a, b: (b, a), '>': lambda a, b: (-b, a)}[d]
        pts = set()
        for a, b in shape:
            u, v = rot(a, b)
            for du in (0, 1):
                for dv in (0, 1): pts.add((u * 2 + du - 1, v * 2 + dv + 1 if d in '^v' else v * 2 + dv))
        if d in '<>': pts = {(u + (2 if d == '<' else 0), v) for u, v in pts}
        if base != 'silk':
            for u, v in pts:
                for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (u + du, v + dv) not in pts: s.set(X + 8 + u + du, Y + 8 + v + dv, O)
        for u, v in pts: s.set(X + 8 + u, Y + 8 + v, col)
    def pit(s, x, y, skip_edges=False):
        X, Y = x * 16, y * 16
        if s.t in ('flying', 'psychic', 'bug'):
            sky = s.t == 'flying'
            c = (96, 152, 232) if sky else (24, 20, 48)
            s.rect(X, Y, X + 15, Y + 15, c)
            for yy in range(Y, Y + 16):
                for xx in range(X, X + 16):
                    hsh = ((xx * 73856093) ^ (yy * 19349663)) % 61
                    if sky and hsh < 2: s.set(xx, yy, (176, 208, 248))
                    if not sky and hsh == 0: s.set(xx, yy, (248, 240, 200))
                    if not sky and hsh == 1: s.set(xx, yy, (160, 160, 220))
            if sky and (x * 5 + y * 3) % 5 == 0: s.disc(X + 8, Y + 11, 5, (200, 224, 252), 2)
        elif s.t == 'water' or s.t == 'dragon':
            s.rect(X, Y, X + 15, Y + 15, (120, 104, 88))
            for yy in range(Y, Y + 16):
                for xx in range(X, X + 16):
                    if ((xx * 7) ^ (yy * 13)) % 17 == 0: s.set(xx, yy, (96, 84, 72))
            return
        else:
            s.rect(X, Y, X + 15, Y + 15, (24, 20, 28))
        if skip_edges: return
        if s.at(x, y - 1) not in 'p<>^v': s.rect(X, Y, X + 15, Y + 3, s.mix('f3', O, 0.4)); s.hl(X, X + 15, Y, 'o')
    def lava(s, x, y, skip_edges=False):
        X, Y = x * 16, y * 16
        for yy in range(Y, Y + 16):
            for xx in range(X, X + 16):
                w = math.sin(xx / 3.0 + yy / 5.0) + math.sin(yy / 2.3 - xx / 7.0)
                s.set(xx, yy, (248, 216, 96) if w > 1.3 else (248, 136, 40) if w > 0.2 else (216, 72, 32) if w > -1.0 else (168, 40, 24))
        if skip_edges: return
        if s.at(x, y - 1) not in 'KY<>^v': s.rect(X, Y, X + 15, Y + 2, s.mix('f3', O, 0.3)); s.hl(X, X + 15, Y + 3, 'o')
        if s.at(x - 1, y) not in 'KY<>^v' and s.at(x - 1, y) != '#': s.vl(X, Y, Y + 15, 'o')
        if s.at(x + 1, y) not in 'KY<>^v' and s.at(x + 1, y) != '#': s.vl(X + 15, Y, Y + 15, 'o')
    def flame(s, x, y, X=None, Y=None, big=True):
        X = x * 16 if X is None else X; Y = y * 16 if Y is None else Y
        s.lights.append((X + 8, Y + 6, 40 if big else 30))
        rows = ['......1......', '.....121.....', '....12221....', '...1223221...', '..122333221..', '..123343321..', '.12334443321.',
                '.12344444321.', '.12344444321.', '..123444321..', '...1233321...', '....11111....']
        col = {'1': (152, 40, 32), '2': (224, 72, 40), '3': (248, 160, 72), '4': (248, 232, 152)}
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != '.': s.set(X + 1 + i, Y + 2 + j, col[ch])
    def brazier(s, x, y):
        X, Y = x * 16, y * 16
        s.darken(X + 3, X + 12, Y + 16, 0.6)
        s.rect(X + 3, Y + 9, X + 12, Y + 15, 'o'); s.rect(X + 4, Y + 10, X + 11, Y + 14, (112, 112, 128)); s.hl(X + 4, X + 11, Y + 10, (168, 168, 184))
        if s.unlit: s.rect(X + 5, Y + 8, X + 10, Y + 9, (64, 56, 56)); return
        s.flame(x, y, X - 0, Y - 9, big=False)
    def sconce(s, x, y):
        X, Y = x * 16, y * 16 - 16
        s.rect(X + 6, Y + 8, X + 9, Y + 15, 'o'); s.rect(X + 7, Y + 9, X + 8, Y + 14, (152, 104, 64))
        s.rect(X + 4, Y + 7, X + 11, Y + 9, 'o')
        s.flame(x, y, X + 1 - 2, Y - 6, big=False)
    def lantern(s, x, y):
        X, Y = x * 16, y * 16
        s.lights.append((X + 8, Y + 7, 34))
        s.darken(X + 4, X + 11, Y + 16, 0.6)
        s.vl(X + 7, Y + 11, Y + 15, 'o'); s.vl(X + 8, Y + 11, Y + 15, 'o')
        s.rect(X + 4, Y + 2, X + 11, Y + 11, 'o'); s.rect(X + 5, Y + 3, X + 10, Y + 10, (248, 216, 120)); s.rect(X + 6, Y + 4, X + 9, Y + 8, (255, 248, 200))
        s.hl(X + 3, X + 12, Y + 1, 'o')
    def gate(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X, Y + 1, X + 15, Y + 15, 'o')
        for k in range(1, 15, 3): s.rect(X + k, Y + 2, X + k + 1, Y + 14, 'k2'); s.vl(X + k, Y + 2, Y + 14, 'k1')
        s.rect(X, Y + 4, X + 15, Y + 5, 'k3'); s.rect(X, Y + 11, X + 15, Y + 12, 'k3')
        s.rect(X + 6, Y + 6, X + 9, Y + 10, 'y2'); s.set(X + 7, Y + 8, 'o')
    def fence(s, x, y, col):
        X, Y = x * 16, y * 16
        if col == 'F' and s.t in ('fighting', 'fairy', 'normal'): return s.gate(x, y)
        c = {'F': ((248, 120, 120), (232, 48, 48)), 'f': ((136, 184, 255), (48, 104, 232)), 'G': ((144, 232, 136), (40, 168, 72))}[col]
        horiz = s.at(x - 1, y) in 'PFfG' or s.at(x + 1, y) in 'PFfG'
        for k in range(16):
            if horiz:
                yy = Y + 7 + int(2 * math.sin(k * 1.3 + x))
                s.set(X + k, yy, c[0]); s.set(X + k, yy + 1, c[1]); s.set(X + k, Y + 4 + (k * 5 % 3), c[1])
            else:
                xx = X + 7 + int(2 * math.sin(k * 1.3 + y))
                s.set(xx, Y + k, c[0]); s.set(xx + 1, Y + k, c[1])
        s.lights.append((X + 8, Y + 8, 14))
    def pylon(s, x, y):
        X, Y = x * 16, y * 16
        s.darken(X + 2, X + 13, Y + 16, 0.6)
        s.rect(X + 4, Y - 6, X + 11, Y + 15, 'o'); s.rect(X + 5, Y - 5, X + 10, Y + 14, (120, 128, 144)); s.vl(X + 5, Y - 5, Y + 14, (176, 184, 200))
        for k in (Y - 3, Y + 3, Y + 9): s.hl(X + 5, X + 10, k, (232, 176, 48))
        s.disc(X + 7.5, Y - 6, 3, 'o'); s.disc(X + 7.5, Y - 6, 2, (248, 232, 120))
        s.rect(X + 3, Y + 13, X + 12, Y + 15, 'o'); s.lights.append((X + 8, Y - 6, 16))
    def switch(s, x, y, n):
        X, Y = x * 16, y * 16
        c = {'1': ((248, 120, 120), (200, 40, 40)), '2': ((136, 184, 255), (40, 96, 216)), '3': ((144, 232, 136), (40, 152, 64))}[n]
        s.rect(X + 2, Y + 3, X + 13, Y + 13, 'o'); s.rect(X + 3, Y + 4, X + 12, Y + 12, (176, 176, 192))
        s.rect(X + 5, Y + 6, X + 10, Y + 10, c[1]); s.rect(X + 5, Y + 6, X + 10, Y + 7, c[0])
    def boulder(s, x, y):
        X, Y = x * 16, y * 16
        s.darken(X + 1, X + 14, Y + 15, 0.6)
        if s.t in ('ground',) and s.fk == 'sand' and 'R' in ''.join(s.rows):   # hay bale on the farm
            s.rect(X + 1, Y + 2, X + 14, Y + 14, 'o'); s.rect(X + 2, Y + 3, X + 13, Y + 13, (232, 200, 96))
            for k in range(Y + 4, Y + 13, 3): s.hl(X + 2, X + 13, k, (192, 152, 56))
            s.vl(X + 5, Y + 3, Y + 13, (152, 96, 40)); s.vl(X + 10, Y + 3, Y + 13, (152, 96, 40))
            return
        s.disc(X + 7.5, Y + 8, 7, 'o'); s.disc(X + 7.5, Y + 8, 6, (152, 136, 120)); s.disc(X + 6, Y + 6, 3.5, (200, 184, 168))
        s.set(X + 9, Y + 10, (104, 92, 80)); s.set(X + 10, Y + 9, (104, 92, 80)); s.set(X + 4, Y + 11, (104, 92, 80))
    def plate(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X + 2, Y + 2, X + 13, Y + 13, 'o'); s.rect(X + 3, Y + 3, X + 12, Y + 12, (208, 184, 120)); s.rect(X + 5, Y + 5, X + 10, Y + 10, (168, 136, 72))
    def pad(s, x, y, ch):
        X, Y = x * 16, y * 16
        c = {'a': ((136, 232, 255), (48, 160, 216)), 'b': ((255, 168, 232), (216, 64, 168)), 'c': ((248, 232, 120), (216, 160, 32))}[ch]
        s.disc(X + 7.5, Y + 8, 7, 'o', 5); s.disc(X + 7.5, Y + 8, 6, c[1], 4); s.disc(X + 7.5, Y + 8, 4, c[0], 2.5); s.disc(X + 7.5, Y + 8, 1.5, (255, 255, 255), 1)
        s.lights.append((X + 8, Y + 8, 18))
    def cracked(s, x, y):
        X, Y = x * 16, y * 16
        if s.t == 'fire' or s.t == 'rock' and False:
            pass
        dark = s.mix('f3', O, 0.5)
        for (a, b) in ((3, 4), (4, 5), (5, 5), (6, 6), (7, 6), (8, 7), (8, 8), (9, 9), (10, 9), (11, 10), (7, 7), (6, 8), (5, 9), (5, 10), (9, 5), (10, 4), (11, 3)):
            s.set(X + a, Y + b, dark)
        if s.t in ('fire',): s.set(X + 8, Y + 8, (248, 136, 40)); s.set(X + 6, Y + 7, (248, 136, 40)); s.set(X + 10, Y + 9, (248, 136, 40))
    def note(s, x, y):
        X, Y = x * 16, y * 16
        black = (x + y) % 2 == 0 and (x % 7) not in (3,)
        k = (x * 3 + y * 5) % 7
        cols = [(248, 120, 120), (248, 184, 96), (248, 232, 120), (136, 216, 120), (120, 184, 248), (168, 136, 240), (240, 136, 216)]
        s.rect(X + 1, Y + 1, X + 14, Y + 14, 'o'); s.rect(X + 2, Y + 2, X + 13, Y + 13, (248, 248, 248)); s.rect(X + 2, Y + 11, X + 13, Y + 13, (208, 208, 224))
        c = cols[k]
        s.rect(X + 6, Y + 3, X + 7, Y + 9, c); s.disc(X + 5, Y + 9, 2, c, 1.5); s.rect(X + 8, Y + 3, X + 9, Y + 4, c)
    def vines(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X, Y, X + 15, Y + 15, (24, 64, 40))
        for k in range(0, 16, 4):
            for yy in range(Y, Y + 16):
                xx = X + k + 1 + int(1.5 * math.sin(yy / 2.0 + k))
                s.set(xx, yy, (56, 136, 64)); s.set(xx + 1, yy, (40, 104, 56))
                if (yy + k) % 6 == 0: s.disc(xx + 1, yy, 1.6, (120, 200, 96))
        s.hl(X, X + 15, Y + 15, 'o'); s.hl(X, X + 15, Y, 'o')
    def bog(s, x, y):
        X, Y = x * 16, y * 16
        for yy in range(Y, Y + 16):
            for xx in range(X, X + 16):
                w = math.sin(xx / 2.5 + yy / 4.0) + math.cos(yy / 3.0 - xx / 5.0)
                s.set(xx, yy, (136, 72, 168) if w > 0.9 else (104, 56, 136) if w > -0.6 else (80, 40, 104))
        if (x * 7 + y * 3) % 3 == 0: s.disc(X + 5, Y + 6, 2, (200, 136, 232)); s.set(X + 4, Y + 5, (248, 232, 255))
        if s.t == 'dragon':
            for yy in range(Y, Y + 16):
                for xx in range(X, X + 16):
                    p = s.px[yy][xx]; s.px[yy][xx] = (p[2] // 2, p[0] // 2 + 40, p[1] // 2 + 20)
    def gas(s, x, y):
        X, Y = x * 16, y * 16
        for (dx, dy, r) in ((5, 6, 5), (11, 8, 5), (7, 11, 4), (10, 4, 3)):
            s.disc(X + dx, Y + dy, r, (176, 104, 200)); s.disc(X + dx - 1, Y + dy - 1, r - 2, (216, 160, 232))
    def tallgrass(s, x, y):
        X, Y = x * 16, y * 16
        wheat = s.t in ('grass', 'ground', 'fairy') and s.fk != 'dark' and s.t != 'fire'
        if s.t == 'fairy':   # flower beds
            s.rect(X, Y, X + 15, Y + 15, (96, 176, 88))
            for (dx, dy, c) in ((3, 3, (248, 136, 184)), (11, 4, (248, 232, 120)), (7, 9, (255, 255, 255)), (3, 12, (200, 152, 248)), (12, 12, (248, 136, 184))):
                s.disc(X + dx, Y + dy, 2, c); s.set(X + dx, Y + dy, (248, 216, 96))
            return
        if s.t == 'water':   # dry lakebed reeds (the present)
            s.rect(X, Y, X + 15, Y + 15, (176, 160, 120))
            for k in range(1, 16, 4): s.vl(X + k, Y + 6, Y + 14, (112, 136, 72)); s.set(X + k, Y + 5, (152, 112, 64))
            return
        base = (216, 176, 80) if s.t in ('grass', 'ground') and wheat else (88, 152, 72)
        if s.t == 'fire': base = (200, 136, 72)
        tip = tuple(min(255, c + 40) for c in base); dk = tuple(c * 3 // 5 for c in base)
        s.rect(X, Y, X + 15, Y + 15, dk)
        for k in range(0, 16, 2):
            h = 9 + (k * 7 + y) % 5
            s.vl(X + k, Y + 15 - h, Y + 15, base); s.set(X + k, Y + 15 - h, tip); s.set(X + k + 1, Y + 14 - h // 2, tip)
    def pearl(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X + 2, Y + 9, X + 13, Y + 15, 'o'); s.rect(X + 3, Y + 10, X + 12, Y + 14, (248, 200, 224))
        s.disc(X + 7.5, Y + 6, 4.5, 'o'); s.disc(X + 7.5, Y + 6, 3.5, (248, 248, 255)); s.set(X + 6, Y + 4, (255, 255, 255)); s.set(X + 9, Y + 8, (216, 208, 240))
        s.lights.append((X + 8, Y + 6, 18))
    def pedestal(s, x, y):
        X, Y = x * 16, y * 16
        s.darken(X + 2, X + 13, Y + 16, 0.6)
        s.rect(X + 3, Y + 6, X + 12, Y + 15, 'o'); s.rect(X + 4, Y + 7, X + 11, Y + 14, (208, 200, 184)); s.hl(X + 4, X + 11, Y + 7, (248, 240, 224))
        s.disc(X + 7.5, Y + 4, 4, 'o'); s.disc(X + 7.5, Y + 4, 3, 'a2'); s.set(X + 6, Y + 3, 'a1')
        s.vl(X + 7, Y + 1, Y + 4, 'o'); s.hl(X + 7, X + 9, Y + 4, 'o')
        s.lights.append((X + 8, Y + 4, 16))
    def generator(s, x, y):
        X, Y = x * 16, y * 16
        s.darken(X, X + 15, Y + 16, 0.6)
        s.rect(X + 1, Y + 1, X + 14, Y + 15, 'o'); s.rect(X + 2, Y + 2, X + 13, Y + 14, (96, 104, 120)); s.rect(X + 2, Y + 2, X + 13, Y + 4, (144, 152, 168))
        s.rect(X + 4, Y + 6, X + 11, Y + 11, (24, 32, 40)); s.vl(X + 6, Y + 7, Y + 10, (248, 232, 96)); s.vl(X + 9, Y + 7, Y + 10, (120, 248, 200))
        s.lights.append((X + 8, Y + 8, 22))
    def fan(s, x, y):
        X, Y = x * 16, y * 16
        s.disc(X + 7.5, Y + 8, 7, 'o'); s.disc(X + 7.5, Y + 8, 6, (176, 184, 200))
        for a in range(0, 360, 90):
            for r in range(1, 6):
                ang = math.radians(a + r * 12)
                s.set(int(X + 7.5 + r * math.cos(ang)), int(Y + 8 + r * math.sin(ang)), (88, 96, 120))
        s.disc(X + 7.5, Y + 8, 1.5, (248, 216, 96))
    def windmill(s, x, y):
        X, Y = x * 16 + 8, y * 16 + 8
        for a in (45, 135, 225, 315):
            for r in range(2, 22):
                for w in range(-4, 5):
                    ang = math.radians(a); px_ = X + r * math.cos(ang) - w * math.sin(ang); py = Y + r * math.sin(ang) + w * math.cos(ang)
                    c = O if abs(w) == 4 or r == 21 else (120, 72, 40) if w == 0 else (248, 240, 224) if (r // 3) % 2 else (216, 200, 176)
                    if w <= 0 or r > 4: s.set(int(px_), int(py), c)
        s.disc(X, Y, 3, 'o'); s.disc(X, Y, 2, (200, 104, 64))
    def magnet(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X + 1, Y + 1, X + 14, Y + 14, 'o'); s.rect(X + 2, Y + 2, X + 7, Y + 13, (232, 72, 72)); s.rect(X + 8, Y + 2, X + 13, Y + 13, (72, 120, 232))
        s.hl(X + 2, X + 13, Y + 2, (248, 200, 200)); s.set(X + 4, Y + 7, (255, 255, 255)); s.set(X + 11, Y + 7, (255, 255, 255))
    def drift(s, x, y):
        X, Y = x * 16, y * 16
        s.disc(X + 7.5, Y + 10, 7.5, 'o', 5.5); s.disc(X + 7.5, Y + 10, 6.5, (248, 252, 255), 4.5); s.hl(X + 3, X + 12, Y + 13, (200, 224, 240))
    def ice(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X, Y, X + 15, Y + 15, (200, 232, 248))
        for yy in range(Y, Y + 16):
            for xx in range(X, X + 16):
                if (xx - yy) % 16 in (0, 1) and (xx // 16 + yy // 16) % 2 == 0: s.set(xx, yy, (240, 252, 255))
                elif (xx + 3 * yy) % 29 == 0: s.set(xx, yy, (160, 208, 232))
    def rockice(s, x, y):
        s.ice(x, y); s.boulder(x, y)
    def high(s, x, y):
        X, Y = x * 16, y * 16
        top = s.mix('k1', (255, 255, 255), 0.1) if s.fk != 'sand' else s.P['k1']
        s.rect(X, Y, X + 15, Y + 15, top)
        for yy in range(Y, Y + 16):
            for xx in range(X, X + 16):
                if ((xx * 73856093) ^ (yy * 19349663)) % 37 == 0: s.set(xx, yy, 'k1')
        if s.at(x, y - 1) not in 'Hslu' and s.at(x, y - 1) != '#': s.hl(X, X + 15, Y, 'o'); s.hl(X, X + 15, Y + 1, (255, 255, 255))
        if s.at(x - 1, y) not in 'HslLju#': s.vl(X, Y, Y + 15, 'o')
        if s.at(x + 1, y) not in 'HslLju#': s.vl(X + 15, Y, Y + 15, 'o')
        below = s.at(x, y + 1)
        if below not in 'HslLju' and below != '#':
            s.rect(X, Y + 8, X + 15, Y + 15, 'k2'); s.hl(X, X + 15, Y + 8, 'o'); s.hl(X, X + 15, Y + 15, 'o')
            for xx in range(X + 1, X + 16, 4): s.vl(xx, Y + 9, Y + 14, 'k3')
            s.hl(X, X + 15, Y + 9, 'k1')
            s.darken(X, X + 15, Y + 16, 0.7); s.darken(X, X + 15, Y + 17, 0.8)
    def ledge(s, x, y):
        s.high(x, y)
        X, Y = x * 16, y * 16
        s.rect(X, Y + 8, X + 15, Y + 15, 'k2'); s.hl(X, X + 15, Y + 8, 'o'); s.hl(X, X + 15, Y + 15, 'o')
        for k in range(3): s.set(X + 7 + k - 1, Y + 11 + (1 if k != 1 else 2), (255, 255, 255)); s.set(X + 7, Y + 11, (255, 255, 255))
    def stairs(s, x, y):
        # steps cut into the cliff: the high side is the neighbour on high ground, the treads drop toward the low side
        X, Y = x * 16, y * 16
        hi_n = s.at(x, y - 1) in 'Hl'
        s.rect(X, Y, X + 15, Y + 15, 'k2')
        s.vl(X, Y, Y + 15, 'o'); s.vl(X + 15, Y, Y + 15, 'o'); s.vl(X + 1, Y, Y + 15, 'k3'); s.vl(X + 14, Y, Y + 15, 'k3')
        for k in range(4):
            t = k if hi_n else 3 - k             # 0 = top tread (highest)
            yy = Y + k * 4
            s.rect(X + 2, yy, X + 13, yy + 2, s.mix('k1', (255, 255, 255), 0.3 - t * 0.07))
            s.hl(X + 2, X + 13, yy + 3, s.mix('k3', O, 0.25 + t * 0.05))
        if hi_n: s.hl(X, X + 15, Y + 15, 'o')
        else: s.hl(X, X + 15, Y, 'o')
    def dock(s, x, y):
        X, Y = x * 16, y * 16
        if s.t == 'water' or s.at(x - 1, y) == '~' or s.at(x + 1, y) == '~' or s.at(x, y - 1) == '~': s.water(x, y)
        s.rect(X, Y + 1, X + 15, Y + 14, (152, 104, 64))
        for k in range(0, 16, 4): s.rect(X, Y + 1 + k * 13 // 16, X + 15, Y + 1 + k * 13 // 16, (112, 72, 40))
        for k in range(3): s.hl(X, X + 15, Y + 2 + k * 4, (200, 152, 96))
        s.hl(X, X + 15, Y + 1, O); s.hl(X, X + 15, Y + 14, O)
        for k in range(1, 16, 5): s.vl(X + k, Y + 2, Y + 13, (112, 72, 40))
        if s.at(x, y + 1) not in '=': s.rect(X + 2, Y + 14, X + 3, Y + 15, (96, 64, 40)); s.rect(X + 12, Y + 14, X + 13, Y + 15, (96, 64, 40))
    def statue(s, x, y):
        X, Y = x * 16, y * 16 - 8
        s.darken(X + 2, X + 13, Y + 24, 0.6)
        s.rect(X + 2, Y + 14, X + 13, Y + 23, 'o'); s.rect(X + 3, Y + 15, X + 12, Y + 22, (224, 216, 200)); s.hl(X + 3, X + 12, Y + 15, (248, 248, 248))
        if s.t == 'dragon':   # a dragon's head on the plinth
            pts = ['....oo....oo', '...oaaooooaao', '..oaaaaaaaaao', '.oaawaaaaaaao', 'oaaaaaaaaaao.', 'ooaaaoaaaaao.', '..oo.oaaaao..', '.....oaaao...', '.....ooooo...']
            for j, r in enumerate(pts):
                for i, ch in enumerate(r):
                    if ch == 'o': s.set(X + 1 + i, Y + 5 + j, O)
                    if ch == 'a': s.set(X + 1 + i, Y + 5 + j, 'a2' if j > 2 else 'a1')
                    if ch == 'w': s.set(X + 1 + i, Y + 5 + j, (248, 232, 96))
            return
        s.disc(X + 7.5, Y + 8, 6, 'o'); s.disc(X + 7.5, Y + 8, 5, (192, 184, 168)); s.disc(X + 6.5, Y + 7, 3, (224, 216, 200))
        s.hl(X + 2, X + 13, Y + 8, 'o'); s.disc(X + 7.5, Y + 8, 1.5, 'o'); s.set(X + 7, Y + 8, 'a2')
    def illusion(s, x, y):
        s.block(x, y)
        X, Y = x * 16, y * 16
        for yy in range(Y + 1, Y + 15):
            for xx in range(X + 1, X + 15):
                if (xx + yy) % 4 == 0: p = s.px[yy][xx]; s.px[yy][xx] = tuple(min(255, c + 70) for c in p)
    def invisible(s, x, y):
        X, Y = x * 16, y * 16
        if s.reveal:   # the lit view shows where the hidden walls are
            for yy in range(Y, Y + 16):
                for xx in range(X, X + 16):
                    if (xx + yy) % 2 == 0: p = s.px[yy][xx]; s.px[yy][xx] = tuple(min(255, int(c * 0.6 + 110)) for c in p)
            s.hl(X, X + 15, Y, (255, 255, 255)); s.hl(X, X + 15, Y + 15, (255, 255, 255)); s.vl(X, Y, Y + 15, (255, 255, 255)); s.vl(X + 15, Y, Y + 15, (255, 255, 255))
            return
        for k in range(0, 16, 3):
            for (a, b) in ((X + k, Y), (X + k, Y + 15), (X, Y + k), (X + 15, Y + k)):
                p = s.px[b][a]; s.px[b][a] = tuple(min(255, c + 45) for c in p)
    def rug(s, x, y):
        X, Y = x * 16, y * 16
        s.rect(X - 16, Y + 1, X + 31, Y + 15, 'o'); s.rect(X - 15, Y + 2, X + 30, Y + 14, 'a3'); s.rect(X - 13, Y + 4, X + 28, Y + 12, 'a2')

    # ---------- people ----------

def ground_under(rows, x, y):
    l, r = rows[y][x - 1], rows[y][x + 1]
    for c in 'H=i':
        if l == c and r == c or (l == c and r in '#u') or (r == c and l in '#u'): return c
    return '_'

FACING = {(0, 1): 'down', (0, -1): 'up', (-1, 0): 'left', (1, 0): 'right'}

def picture(full, g):
    """The room (framed rows) without its people, as a Room you can draw more on."""
    r = Room(full, g['theme'])
    r.raft = g['raft']
    r.wrap = 32 if len(full) * len(full[0]) > 400 else 0
    r.reveal = False
    r.walls(); r.floor()
    for y, row in enumerate(full):
        for x, ch in enumerate(row):
            if ch == '#' or y < 2: continue
            base = ground_under(full, x, y) if ch in 'Ljgu{}!`' else ch
            if base == 'H': r.high(x, y)
            elif base == 'K': r.lava(x, y)
            elif base == 'Z': r.bog(x, y)
            elif base == '~': r.water(x, y)
            elif base == 'i': r.ice(x, y)
            if ch == 'o': r.rug(x, y)
    for y, row in enumerate(full):
        for x, ch in enumerate(row):
            if y < 2 or ch == '#': continue
            f = {'x': r.block, 'I': r.illusion, 'X': r.invisible, 'D': lambda a, b: r.water(a, b, True), 'p': r.pit,
                 'Y': lambda a, b: (r.lava(a, b), r.flame(a, b)) if 'K' in (full[b][a - 1], full[b][a + 1]) else r.brazier(a, b),
                 'T': lambda a, b: r.sconce(a, b) if b == 2 else r.brazier(a, b), 'J': r.lantern, 'F': lambda a, b: r.fence(a, b, 'F'), 'f': lambda a, b: r.fence(a, b, 'f'),
                 'G': lambda a, b: r.fence(a, b, 'G'), '1': lambda a, b: r.switch(a, b, '1'), '2': lambda a, b: r.switch(a, b, '2'),
                 '3': lambda a, b: r.switch(a, b, '3'), 'P': r.pylon, 'E': r.generator, 'q': r.plate,
                 'a': lambda a, b: r.pad(a, b, 'a'), 'b': lambda a, b: r.pad(a, b, 'b'), 'c': lambda a, b: r.pad(a, b, 'c'),
                 'k': r.cracked, 'N': r.note, '+': r.note, 'V': r.vines, 'z': r.gas, 'R': r.tallgrass, 'Q': r.pearl, 'S': r.pedestal,
                 'n': r.fan, 'e': r.magnet, 'd': lambda a, b: (r.ice(a, b), r.drift(a, b)), 'r': r.rockice,
                 's': r.stairs, 'l': r.ledge, '=': r.dock, 'u': r.statue,
                 '>': lambda a, b: r.arrow(a, b, '>'), '<': lambda a, b: r.arrow(a, b, '<'), '^': lambda a, b: r.arrow(a, b, '^'),
                 'v': lambda a, b: r.arrow(a, b, 'v')}.get(ch)
            if f: f(x, y)
    for y, row in enumerate(full):
        for x, ch in enumerate(row):
            if ch == 'W': r.windmill(x, y)
    if g['mirror']:   # mirror-glass floor: silver streaks
        for y in range(32, r.H - 16):
            for x in range(16, r.W - 16):
                if full[y // 16][x // 16] in '_jgLo' and (x + y) % 40 in (0, 1, 2, 6):
                    p = r.px[y][x]; r.px[y][x] = tuple(min(255, int(c * 0.7 + 90)) for c in p)
    return r

def save(r, name):
    im = Image.new('RGB', (r.W, r.H))
    im.putdata([c for row in r.px for c in row])
    im.save(os.path.join(DATA, name))

def puzzle(area, g):
    gm = Gym(area, dict(g, states=[tuple(s) for s in g['states']]))
    W, H = gm.W, gm.H
    lv = lambda p: gm.plev.get(p, 0)
    # What each tile needs to know (from the first state, as solver.Gym works it out): the low 14 bits are a vine's or
    # jet's junior, a gas cloud's valve, a fan lane's switch, or the tile a pad or dive spot leads to (0x3fff: none);
    # 0x4000 marks a pit or boulder up on high ground.
    aux = [0x3fff] * (W * H)
    for (x, y), i in gm.guard.items(): aux[y * W + x] = i
    for (x, y), i in gm.valve.items(): aux[y * W + x] = i
    for (x, y), sw in gm.lane.items(): aux[y * W + x] = sw
    for (a, b) in list(gm.pads.items()) + list(gm.dpair.items()): aux[a[1] * W + a[0]] = b[1] * W + b[0]
    for (x, y), v in gm.plev.items(): aux[y * W + x] |= 0x4000 * v
    # Where a boulder can ever be, in each state (only those tiles get a boulder picture: tiles are scarce).
    rock_at = [set() for _ in gm.variants]
    if gm.boulders0:
        seen, _, _ = gm.explore(limit=2000000)
        for st in seen:
            rock_at[st[6]].update(st[3])
    rows = []
    for k, full in enumerate(gm.variants):
        base = [''.join(('H' if lv((x, y)) else '_') if c == 'O' else c for x, c in enumerate(row)) for y, row in enumerate(full)]
        save(picture(base, g), 'gym_%d_%d.png' % (area, k))
        alt = []
        for y, row in enumerate(base):
            out = ''
            for x, c in enumerate(row):
                if c in 'FfGzVY': c = '_'
                elif c == 'p' and gm.boulders0: c = 'H' if lv((x, y)) else '_'   # filled (only boulders fill pits)
                elif c == 'k': c = 'p'
                elif c in ARROW and gm.cfg['over'] == 'p': c = 'p'
                out += c
            alt.append(out)
        save(picture(alt, g), 'gym_%d_%d_alt.png' % (area, k))
        r = picture(base, g)
        for (x, y) in rock_at[k]: r.boulder(x, y)
        save(r, 'gym_%d_%d_rock.png' % (area, k))
        rows.append(full)
    cfg = gm.cfg
    return dict(w=W, h=H, theme=g['theme'], states=rows, aux=aux,
                juniors=[[x, y, FACING[f]] for (x, y), f in zip(gm.juniors, gm.facing)],
                leader=list(gm.leader), guide=list(gm.guide[0]), start=list(gm.start),
                surf=bool(cfg['surf']), dive=bool(cfg['dive']), raft=bool(cfg.get('raft')), over=cfg['over'],
                fans=cfg['fans'] if cfg['fans'] is not None else -1, pulse=cfg.get('pulse', 0), gate=cfg['gate'] or '',
                R=cfg['R'], J=cfg['J'], Y=cfg['Y'], e=cfg['e'], S=cfg.get('S', ''), era_by=cfg.get('era_by', ''),
                step_aside=bool(cfg.get('step_aside')), dark='fog' if g['dark'] == 'fog' else bool(g['dark']))

if __name__ == '__main__':
    L = json.load(open(os.path.join(DATA, 'gym_layouts.json')))
    out = {a: puzzle(int(a), g) for a, g in L.items()}
    with open(os.path.join(DATA, 'gym_puzzles.json'), 'w') as f:
        json.dump(out, f, separators=(',', ':'))
    print('gyms', len(out))
