# CHALLENGE TOWER fronts, round 1 (hand-pixelled): 112x144, transparent outside. Footprint 7x4 tiles, door in the
# middle column, the rest rises 5 tiles above. python3 towers.py OUTDIR
import sys, os
O = (38, 38, 56)
BASE = dict(o=O, r1=(240, 112, 96), r2=(232, 72, 72), w1=(248, 248, 248), w2=(208, 216, 224), w3=(168, 168, 192),
            s1=(152, 168, 192), s2=(112, 128, 160), s3=(80, 88, 120), s4=(56, 64, 88),      # slate roof
            k1=(224, 216, 200), k2=(192, 184, 168), k3=(152, 144, 128),                     # stone
            y1=(248, 216, 96), y2=(216, 160, 48), y3=(152, 104, 32),                         # gold
            b1=(184, 224, 255), b2=(88, 160, 240), b3=(48, 80, 160))

class Img:
    def __init__(s, w, h, pal, bg=None):
        s.w, s.h, s.P = w, h, pal
        s.px = [[bg] * w for _ in range(h)]
    def set(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.px[y][x] = s.P[c] if isinstance(c, str) else c
    def get(s, x, y): return s.px[y][x]
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def hl(s, x0, x1, y, c): s.rect(x0, y, x1, y, c)
    def vl(s, x, y0, y1, c): s.rect(x, y0, x, y1, c)
    def box(s, x0, y0, x1, y1, c): s.rect(x0, y0, x1, y1, 'o'); s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, c)
    def disc(s, cx, cy, r, c, ry=None):
        ry = ry or r
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if ((x - cx) / r) ** 2 + ((y - cy) / ry) ** 2 <= 1.0: s.set(x, y, c)
    def outline(s):
        add = [(x, y) for y in range(s.h) for x in range(s.w) if s.px[y][x] is None and any(
            0 <= x + dx < s.w and 0 <= y + dy < s.h and s.px[y + dy][x + dx] not in (None, O)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in add: s.px[y][x] = O
    def save(s, path, scale=1):
        im = Image.new('RGBA', (s.w, s.h), (0, 0, 0, 0))
        for y in range(s.h):
            for x in range(s.w):
                if s.px[y][x]: im.putpixel((x, y), s.px[y][x] + (255,))
        if scale > 1: im = im.resize((s.w * scale, s.h * scale), Image.NEAREST)
        im.save(path)
        return im

W, H = 112, 144
P = dict(BASE, r3=(176, 40, 56), r4=(136, 40, 48), v1=(200, 176, 248), v2=(152, 112, 224), v3=(112, 72, 176), v4=(72, 48, 120),
         c1=(248, 240, 255), c2=(216, 184, 255), m1=(240, 236, 248), m2=(208, 204, 224), m3=(160, 152, 184))

def door(im, cx, y1, arch=True):
    # double glass door with a gold frame, 16 wide, bottom at y1
    x0, x1, y0 = cx - 8, cx + 7, y1 - 22
    im.rect(x0, y0, x1, y1, 'o')
    if arch:
        for x in range(x0, x1 + 1):
            d = abs(x - (cx - 0.5))
            top = y0 - int(max(0, 6 - d * d / 9))
            im.vl(x, top, y0, 'o')
    im.rect(x0 + 1, y0, x1 - 1, y1, 'y2')
    im.rect(x0 + 2, y0 + 2, x1 - 2, y1, 'b2')
    im.vl(cx - 1, y0 + 2, y1, 'o'); im.vl(cx, y0 + 2, y1, 'y2')
    for x in (x0 + 3, cx + 2): im.vl(x, y0 + 4, y0 + 10, 'b1')
    im.hl(x0 + 2, x1 - 2, y0 + 2, 'b3')

def window(im, x, y, w=5, h=8, glow=False):
    im.rect(x - 1, y - 1, x + w, y + h, 'o')
    im.rect(x, y, x + w - 1, y + h - 1, 'v2' if glow else 'b2')
    im.vl(x, y, y + h - 1, 'v1' if glow else 'b1'); im.set(x + 1, y, 'c1' if glow else 'b1')
    im.hl(x, x + w - 1, y + h - 1, 'v3' if glow else 'b3')

def bricks(im, x0, y0, x1, y1, a='k1', b='k2', c='k3', bw=8, bh=4):
    im.rect(x0, y0, x1, y1, a)
    for y in range(y0, y1 + 1, bh):
        im.hl(x0, x1, y, b)
        off = 0 if (y - y0) // bh % 2 == 0 else bw // 2
        for x in range(x0 + off, x1 + 1, bw): im.vl(x, y, min(y1, y + bh - 1), b)
    im.vl(x1, y0, y1, c); im.vl(x1 - 1, y0, y1, b)

def crystal(im, cx, cy, s=6):
    # the SUMMONING crystal: a glowing violet diamond with a white core
    for dy in range(-s * 2, s * 2 + 1):
        w = s - abs(dy) // 2
        if w < 0: continue
        for dx in range(-w, w + 1):
            im.set(cx + dx, cy + dy, 'v2' if dx > 0 else 'v1')
    for dy in range(-s, s + 1):
        w = (s - abs(dy)) // 3
        for dx in range(-w, w + 1): im.set(cx + dx - 1, cy + dy, 'c1')

def banner(im, x, y0, y1, c='v2', d='v3'):
    im.rect(x - 1, y0 - 1, x + 5, y1, 'o')
    im.rect(x, y0, x + 4, y1 - 1, c); im.vl(x + 4, y0, y1 - 1, d)
    im.set(x + 2, y1, c); im.set(x + 2, y1 + 1, 'o'); im.set(x, y1, 'o'); im.set(x + 4, y1, 'o')
    im.rect(x + 1, y0 + 3, x + 3, y0 + 5, 'y1')

def plaque(im, cx, y):
    im.rect(cx - 13, y, cx + 12, y + 7, 'o'); im.rect(cx - 12, y + 1, cx + 11, y + 6, 'y1')
    im.hl(cx - 12, cx + 11, y + 6, 'y2')
    # TOWER in 3x5 letters
    F = {'T': ['111', '.1.', '.1.', '.1.', '.1.'], 'O': ['111', '1.1', '1.1', '1.1', '111'], 'W': ['1.1', '1.1', '1.1', '111', '1.1'],
         'E': ['111', '1..', '11.', '1..', '111'], 'R': ['11.', '1.1', '11.', '1.1', '1.1']}
    x = cx - 9
    for ch in 'TOWER':
        for j, row in enumerate(F[ch]):
            for i, v in enumerate(row):
                if v == '1': im.set(x + i, y + 1 + j, 'y3')
        x += 4

def a_spire():
    """A: stone keep with an arched door, a violet slate spire on top holding the summoning crystal."""
    im = Img(W, H, P)
    cx = 56
    # keep: stone, 2 storeys, from y 80 to 143
    bricks(im, 8, 82, 103, 139)
    im.rect(8, 136, 103, 143, 'k3'); im.hl(8, 103, 136, 'k2')
    for x in range(8, 104, 6): im.vl(x, 137, 143, 'k2')
    im.rect(4, 76, 107, 82, 's2'); im.hl(4, 107, 76, 's1'); im.hl(4, 107, 82, 's4')        # cornice
    for x in range(6, 106, 8): im.rect(x, 78, x + 3, 81, 's1')                                # crenels
    door(im, cx, 135)
    plaque(im, cx, 96)
    for x in (16, 30, 77, 91): window(im, x, 90, glow=True)
    for x in (16, 30, 77, 91): window(im, x, 112)
    banner(im, 37, 86, 104); banner(im, 71, 86, 104)
    # tower shaft
    bricks(im, 32, 30, 79, 75, 'm1', 'm2', 'm3', 8, 5)
    im.vl(32, 30, 75, 'm2')
    for y in (36, 54): window(im, cx - 3, y, 5, 10, glow=True)
    for y in (40, 58): window(im, 40, y, 3, 6); window(im, 69, y, 3, 6)
    im.rect(28, 70, 83, 75, 's2'); im.hl(28, 83, 70, 's1'); im.hl(28, 83, 75, 's4')
    # spire roof
    for y in range(14, 31):
        half = int(2 + (y - 14) * 1.65)
        im.hl(cx - half, cx + half - 1, y, 'v3')
        im.hl(cx - half, cx - 1, y, 'v2')
        if y % 4 == 0: im.hl(cx - half, cx + half - 1, y, 'v4')
    for y in range(14, 31): im.set(cx - int(2 + (y - 14) * 1.65), y, 'v1')
    im.hl(cx - 30, cx + 29, 30, 's4')
    im.vl(cx - 1, 9, 14, 'y2'); crystal(im, cx, 5, 3)
    im.outline()
    return im

def b_beacon():
    """B: a white marble column ringed with gold bands, a halo of violet light round a crystal at the top."""
    im = Img(W, H, P)
    cx = 56
    # wide base hall
    bricks(im, 6, 96, 105, 139, 'm1', 'm2', 'm3', 12, 6)
    im.rect(6, 136, 105, 143, 'k3'); im.hl(6, 105, 136, 'k2')
    im.rect(2, 90, 109, 96, 'v3'); im.hl(2, 109, 90, 'v2'); im.hl(2, 109, 96, 'v4')
    for x in range(4, 108, 6): im.set(x, 93, 'y1')
    # pillars
    for x in (14, 26, 82, 94):
        im.rect(x, 98, x + 4, 135, 'm1'); im.vl(x + 4, 98, 135, 'm3'); im.vl(x + 3, 98, 135, 'm2')
        im.rect(x - 1, 97, x + 5, 99, 'y1'); im.rect(x - 1, 133, x + 5, 135, 'y2')
    door(im, cx, 135)
    plaque(im, cx, 101)
    # column
    for y in range(22, 90):
        half = 20 if y > 30 else 20
        im.hl(cx - half, cx + half - 1, y, 'm1')
        im.hl(cx + half - 8, cx + half - 1, y, 'm2'); im.hl(cx + half - 3, cx + half - 1, y, 'm3')
        im.hl(cx - half, cx - half + 2, y, 'c1')
    for y in (38, 58, 78):
        im.rect(cx - 21, y, cx + 20, y + 3, 'y1'); im.hl(cx - 21, cx + 20, y + 3, 'y2'); im.hl(cx - 21, cx + 20, y, 'o')
    for y in (28, 46, 66):
        window(im, cx - 3, y, 5, 8, glow=True)
    for y in (48, 68): window(im, cx - 14, y, 3, 6); window(im, cx + 10, y, 3, 6)
    # crown: gold bowl, halo, crystal
    im.rect(cx - 24, 18, cx + 23, 22, 'y2'); im.hl(cx - 24, cx + 23, 18, 'y1'); im.hl(cx - 22, cx + 21, 22, 'y3')
    for x in range(cx - 18, cx + 18): 
        if x % 2: im.set(x, 17, 'y1')
    im.disc(cx - 0.5, 9, 17, 'v2', 6)
    im.disc(cx - 0.5, 9, 15, 'c2', 4)
    im.disc(cx - 0.5, 9, 13, None, 3)
    crystal(im, cx, 8, 4)
    im.outline()
    return im

def c_pagoda():
    """C: three stacked violet roofs with upturned eaves, gold finial and lanterns: a temple tower."""
    im = Img(W, H, P)
    cx = 56
    def roof(y0, y1, half, eave=5):
        for y in range(y0, y1 + 1):
            t = (y - y0) / max(1, y1 - y0)
            h = int(half * (0.55 + 0.45 * t))
            im.hl(cx - h, cx + h - 1, y, 'v3'); im.hl(cx - h, cx - 1, y, 'v2')
            if (y - y0) % 3 == 2: im.hl(cx - h, cx + h - 1, y, 'v4')
        # upturned tips
        for k in range(eave):
            im.set(cx - half - k, y1 - k // 2, 'v2'); im.set(cx + half - 1 + k, y1 - k // 2, 'v3')
        im.hl(cx - half - eave + 1, cx + half + eave - 2, y1 + 1, 'o')
        im.hl(cx - half + 1, cx + half - 2, y1 + 1, 'y2')
    def storey(y0, y1, half, n):
        im.rect(cx - half, y0, cx + half - 1, y1, 'm1')
        im.vl(cx + half - 1, y0, y1, 'm3'); im.vl(cx + half - 2, y0, y1, 'm2')
        im.rect(cx - half, y0, cx - half + 2, y1, 'r3')
        im.rect(cx + half - 3, y0, cx + half - 1, y1, 'r4')
        step = (2 * half) // (n + 1)
        for i in range(1, n + 1): window(im, cx - half + i * step - 2, y0 + 3, 4, y1 - y0 - 6, glow=True)
    # ground storey
    bricks(im, 10, 100, 101, 139)
    im.rect(10, 136, 101, 143, 'k3'); im.hl(10, 101, 136, 'k2')
    for x in (12, 97): im.rect(x, 100, x + 3, 135, 'r3'); im.vl(x + 3, 100, 135, 'r4')
    door(im, cx, 135, arch=False)
    plaque(im, cx, 104)
    for x in (22, 32, 76, 86): window(im, x, 112)
    roof(84, 98, 46, 6)
    storey(66, 83, 30, 3)
    roof(52, 65, 36, 5)
    storey(38, 51, 22, 2)
    roof(26, 37, 27, 4)
    # finial with the crystal
    im.rect(cx - 2, 14, cx + 1, 26, 'y2'); im.vl(cx - 2, 14, 26, 'y1')
    for y in (18, 22): im.rect(cx - 4, y, cx + 3, y + 1, 'y1')
    crystal(im, cx, 7, 3)
    # lanterns hanging from the lower eaves
    for x in (cx - 44, cx + 40):
        im.vl(x + 1, 99, 101, 'o'); im.rect(x, 102, x + 3, 107, 'r2'); im.hl(x, x + 3, 102, 'y1'); im.hl(x, x + 3, 107, 'y2')
    im.outline()
    return im

def save(im, path):
    from PIL import Image
    out = Image.new('RGBA', (im.w, im.h), (0, 0, 0, 0))
    for y in range(im.h):
        for x in range(im.w):
            if im.px[y][x]: out.putpixel((x, y), im.px[y][x] + (255,))
    out.save(path)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for k, f in (('A', a_spire), ('B', b_beacon), ('C', c_pagoda)):
        save(f(), os.path.join(out, 'tower_%s.png' % k))
