# The POKéMON GYM fronts (9.3.5; approved in the 9.3.4 building-art round 8, plans/9.3.4-building-art/round8/gyms.py):
# three styles (a town's gym follows its CENTER's), each in every gym type's colours with its badge, and with the
# doorway over the building's door column (door+2 or door+3 of the 6x4 tiles), 96x72 with the roof 8 px above.
# Writes gba/data/gym_<style>_<theme>_d<col>.png:
#     python3 tools/art/gym_fronts.py
import os, math
from PIL import Image

O = (38, 38, 56)
BASE = dict(o=O, r1=(240, 112, 96), r2=(232, 72, 72), w1=(248, 248, 248), w2=(208, 216, 224), w3=(168, 168, 192),
            s1=(152, 168, 192), s2=(112, 128, 160), s3=(80, 88, 120), s4=(56, 64, 88),      # slate roof
            k1=(224, 216, 200), k2=(192, 184, 168), k3=(152, 144, 128),                     # stone
            y1=(248, 216, 96), y2=(216, 160, 48), y3=(152, 104, 32),                         # gold
            b1=(184, 224, 255), b2=(88, 160, 240), b3=(48, 80, 160))
THEME = {   # accent light/mid/dark per type
    'fire': ((248, 160, 72), (224, 72, 40), (152, 40, 32)),
    'water': ((120, 192, 248), (56, 120, 216), (32, 72, 144)),
    'grass': ((136, 216, 96), (64, 160, 64), (32, 104, 56)),
    'electric': ((248, 232, 120), (232, 192, 40), (160, 120, 16)),
    'ground': ((232, 200, 128), (200, 152, 80), (136, 96, 48)),
    'ghost': ((168, 144, 208), (112, 88, 160), (72, 52, 112)),
    'ice': ((200, 240, 248), (128, 200, 232), (72, 136, 184)),
    'dragon': ((160, 136, 232), (104, 72, 200), (64, 40, 136)),
    'flying': ((200, 224, 248), (136, 168, 232), (88, 112, 176)),
    'normal': ((232, 216, 184), (184, 160, 120), (128, 104, 72)),
    'rock': ((216, 192, 136), (176, 144, 88), (120, 96, 56)),
    'bug': ((200, 224, 96), (152, 184, 40), (96, 120, 24)),
    'steel': ((216, 224, 232), (160, 168, 192), (104, 112, 136)),
    'fairy': ((248, 200, 224), (232, 136, 184), (168, 80, 128)),
    'poison': ((200, 152, 224), (160, 80, 184), (104, 48, 128)),
    'fighting': ((232, 152, 104), (192, 72, 48), (128, 40, 32)),
    'psychic': ((248, 160, 200), (232, 88, 144), (160, 48, 96)),
    'dark': ((168, 144, 128), (112, 88, 72), (64, 52, 48)),
}

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

# ---- type icons, 9x9 ('1' accent mid, '2' accent light, '3' dark) ----
ICON = {
    'fire': ['....1....', '...121...', '..1221...', '..12221..', '.122221..', '.1222221.', '1122r2211', '.112r211.', '..11111..'],
    'water': ['....1....', '....1....', '...121...', '..12221..', '.1222221.', '.1222221.', '.1222221.', '..12221..', '...111...'],
    'grass': ['......11.', '....1122.', '...12221.', '..12221..', '.12221...', '.1221....', '.121.....', '1.1......', '1........'],
    'electric': ['.....111.', '....1221.', '...1221..', '..12211..', '.1222221.', '..11221..', '...1221..', '..1221...', '..111....'],
    'ground': ['.........', '....1....', '...121...', '..12221..', '..12221..', '.1222221.', '.1222221.', '122222221', '111111111'],
    'ghost': ['...111...', '..12221..', '.1222221.', '.12r2r21.', '.1222221.', '.1222221.', '.1222221.', '.1212121.', '.1.1.1.1.'],
    'ice': ['....1....', '.1..1..1.', '..1.1.1..', '...121...', '111222111', '...121...', '..1.1.1..', '.1..1..1.', '....1....'],
    'dragon': ['1.......1', '11.....11', '121...121', '.1211121.', '.1222221.', '..12r21..', '..12221..', '...121...', '....1....'],
    'flying': ['.......11', '.....1122', '...112221', '..1222221', '.12222211', '1222211..', '122211...', '.111.....', '.........'],
    'normal': ['...111...', '..12221..', '.1222221.', '122111221', '12211.221', '122111221', '.1222221.', '..12221..', '...111...'],
    'rock': ['...111...', '..12221..', '.1222211.', '.12221.1.', '122211..1', '12221.111', '1222.1221', '.1111221.', '....111..'],
    'bug': ['.1.....1.', '..1...1..', '..11111..', '.1222221.', '.1221221.', '112212211', '.1221221.', '.1222221.', '..11111..'],
    'steel': ['...111...', '..12221..', '.1221221.', '1221.1221', '121...121', '1221.1221', '.1221221.', '..12221..', '...111...'],
    'fairy': ['....1....', '...121...', '...121...', '111222111', '.1222221.', '..12221..', '.1221221.', '.121.121.', '.11...11.'],
    'poison': ['....1..1.', '...121...', '...121..1', '..12221..', '.1222221.', '.12r2221.', '.1222221.', '..12221..', '...111...'],
    'fighting': ['.1.1.1...', '1212121..', '1212121.1', '122222211', '122222221', '122222221', '.1222221.', '..12221..', '..11111..'],
    'psychic': ['..11111..', '.1222221.', '122111221', '121222121', '1212r2121', '121222121', '122111221', '.1222221.', '..11111..'],
    'dark': ['...111...', '..12211..', '.1221....', '.122.....', '.122.....', '.122.....', '.1221....', '..12211..', '...111...'],
}
def icon(im, x0, y0, t):
    for j, row in enumerate(ICON[t]):
        for i, ch in enumerate(row):
            if ch != '.': im.set(x0 + i, y0 + j, {'1': 'a2', '2': 'a1', '3': 'a3', 'r': 'y1'}[ch])

def badge(im, cx, cy, t):
    # gold-rimmed round badge carrying the type icon
    im.disc(cx, cy, 8, 'o'); im.disc(cx, cy, 7, 'y2'); im.disc(cx - 1, cy - 1, 6, 'y1'); im.disc(cx, cy, 5, 'w1')
    icon(im, cx - 4, cy - 4, t)

def shingles(im, x0, y0, x1, y1, inside=None, c=('s1', 's2', 's3')):
    for y in range(y0, y1 + 1):
        rr, row = (y - y0) % 4, (y - y0) // 4
        for x in range(x0, x1 + 1):
            if inside and not inside(x, y): continue
            col = c[0] if rr == 0 else c[2] if rr == 3 else c[1]
            if rr in (1, 2) and (x + row * 4) % 8 == 0: col = c[2]
            im.set(x, y, col)

def stone(im, x0, y0, x1, y1):
    # cut stone blocks 8x5 with mortar, lit top edge
    im.rect(x0, y0, x1, y1, 'k1')
    for y in range(y0, y1 + 1):
        r = (y - y0) % 5
        if r == 4: im.hl(x0, x1, y, 'k3')
        else:
            off = 0 if ((y - y0) // 5) % 2 == 0 else 4
            for x in range(x0 + off, x1 + 1, 8): im.set(x, y, 'k3')
        if r == 0: im.hl(x0, x1, y, 'w1')
    im.vl(x1, y0, y1, 'k2'); im.vl(x1 - 1, y0, y1, 'k2')

def footing(im, x0, x1, y0, y1):
    im.rect(x0, y0, x1, y1, 'k3'); im.hl(x0, x1, y0, 'k2')
    for y in range(y0 + 1, y1 + 1, 2):
        off = 0 if (y - y0) % 4 == 1 else 3
        for x in range(x0 + off, x1 + 1, 6): im.set(x, y, 'o')

def window(im, x0, y0, w, h):
    im.rect(x0, y0, x0 + w - 1, y0 + h - 1, 'o')
    im.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2, 'b2')
    im.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + 2, 'b1')
    for k in range(min(w, h) - 3): im.set(x0 + 2 + k, y0 + h - 3 - k, 'b1')
    im.hl(x0 + 1, x0 + w - 2, y0 + h - 2, 'b3')
    im.vl(x0 + w // 2, y0 + 1, y0 + h - 2, 'o')
    im.hl(x0 - 1, x0 + w, y0 - 1, 'k3')

def doors(im, cx, y0, y1, half=8):
    x0, x1 = cx - half, cx + half - 1
    im.rect(x0 - 1, y0 - 1, x1 + 1, y1, 'k3')
    im.rect(x0, y0, x1, y1, 'o')
    for a, b in ((x0 + 1, cx - 2), (cx + 1, x1 - 1)):
        im.rect(a, y0 + 1, b, y1, 'b2'); im.rect(a, y0 + 1, b, y0 + 3, 'b1')
        im.vl(a + 1, y0 + 4, y1 - 3, 'b1'); im.hl(a, b, y1 - 1, 'b3')
    im.vl(cx - 1, y0 + 1, y1, 'o'); im.vl(cx, y0 + 1, y1, 'o')

def banner(im, x0, y0, w, h):
    # hanging type-colour banner with a gold rod and a notched foot
    im.hl(x0 - 1, x0 + w, y0, 'y2'); im.set(x0 - 1, y0, 'y3'); im.set(x0 + w, y0, 'y3')
    im.rect(x0, y0 + 1, x0 + w - 1, y0 + h, 'a2'); im.vl(x0, y0 + 1, y0 + h, 'a1'); im.vl(x0 + w - 1, y0 + 1, y0 + h, 'a3')
    im.set(x0 + w // 2, y0 + h, None); im.set(x0 + w // 2 - 1, y0 + h, None)
    im.hl(x0 + 1, x0 + w - 2, y0 + 3, 'y1')

FONT = {'G': ['111', '100', '101', '101', '111'], 'Y': ['101', '101', '010', '010', '010'],
        'M': ['10001', '11011', '10101', '10001', '10001']}
def text(im, x, y, s, c):
    for ch in s:
        g = FONT[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == '1': im.set(x + i, y + j, c)
        x += len(g[0]) + 1

def plate(im, cx, y):
    im.rect(cx - 9, y, cx + 8, y + 7, 'o'); im.rect(cx - 8, y + 1, cx + 7, y + 6, 'y2'); im.hl(cx - 8, cx + 7, y + 1, 'y1')
    text(im, cx - 7, y + 2, 'GYM', 'o')

def pal(t):
    p = dict(BASE); p['a1'], p['a2'], p['a3'] = THEME[t]; return p

# ---- A: stone arena with a pediment badge and banners ----
def front_a(t, cx):
    im = Img(96, 72, pal(t))
    stone(im, 4, 34, 91, 70); footing(im, 4, 91, 67, 70)
    shingles(im, 2, 20, 93, 29)
    im.rect(1, 30, 94, 33, 's3'); im.hl(1, 94, 30, 's1'); im.hl(1, 94, 33, 's4')
    for x in range(4, 94, 6): im.vl(x, 31, 32, 's4')          # cornice dentils
    ped = lambda x, y: y >= 4 + abs(x - 47.5) * 0.62
    for x in range(26, 70):
        for y in range(4, 30):
            if ped(x, y): im.set(x, y, 'k1' if y > 6 + abs(x - 47.5) * 0.62 else 'w1')
    badge(im, 48, 20, t)
    for px in (cx - 15, cx + 10):                               # pillars by the door
        im.rect(px, 36, px + 4, 66, 'w1'); im.vl(px + 3, 36, 66, 'w2'); im.vl(px + 4, 36, 66, 'k2')
        im.rect(px - 1, 34, px + 5, 35, 'k2'); im.rect(px - 1, 66, px + 5, 66, 'k2')
    banner(im, 12, 36, 9, 18); banner(im, 75, 36, 9, 18)
    for wx in (23, 66):                                         # the window the doorway doesn't cover
        if wx + 8 < cx - 16 or wx > cx + 15: window(im, wx, 42, 7, 10)
    plate(im, cx, 37)
    doors(im, cx, 48, 70, half=7)
    im.outline(); return im

# ---- B: a hall under one big gable, the badge in the gable, brick in the type colour ----
def front_b(t, cx):
    im = Img(96, 72, pal(t))
    stone(im, 4, 38, 91, 70); footing(im, 4, 91, 67, 70)
    for x0 in (4, 70):                                           # type-colour panels either side
        im.rect(x0, 40, x0 + 21, 64, 'a2')
        for y in range(40, 65, 4): im.hl(x0, x0 + 21, y, 'a3')
        for y in range(40, 65):
            for x in range(x0 + (0 if (y // 4) % 2 else 4), x0 + 22, 8): im.set(x, y, 'a3')
        im.hl(x0, x0 + 21, 40, 'a1')
        window(im, x0 + 7, 46, 8, 10)
    gab = lambda x, y: y >= 2 + abs(x - 47.5) * 0.72
    shingles(im, 0, 2, 95, 35, gab)
    for x in range(0, 96):
        top = next((y for y in range(2, 36) if gab(x, y)), None)
        if top is not None: im.set(x, top, 's1'); im.set(x, top + 1, 's1')
    im.rect(0, 34, 95, 37, 's3'); im.hl(0, 95, 34, 's1'); im.hl(0, 95, 37, 's4')
    im.disc(48, 22, 11, 'o'); im.disc(48, 22, 10, 'w2')
    badge(im, 48, 22, t)
    plate(im, cx, 40)
    doors(im, cx, 50, 70, half=9)
    for x in (cx - 11, cx + 10): im.rect(x, 48, x + 1, 70, 'a3')
    im.outline(); return im

# ---- C: a domed stadium with a type-colour band and an arched gate ----
def front_c(t, cx):
    im = Img(96, 72, pal(t))
    stone(im, 2, 40, 93, 70); footing(im, 2, 93, 67, 70)
    dome = lambda x: 4 + int(30 * (1 - math.sqrt(max(0, 1 - ((x - 47.5) / 46) ** 2))))
    for x in range(2, 94):
        top = dome(x)
        for y in range(top, 40):
            rib = (x - 2) % 12 == 0
            c = 's1' if y <= top + 1 else 's3' if rib else 's2' if y < 30 else 's3'
            im.set(x, y, c)
    for y in range(29, 35): im.hl(2, 93, y, 'a2' if y not in (29, 34) else 'a3')
    im.hl(2, 93, 30, 'a1')
    for x in range(8, 90, 10): im.rect(x, 31, x + 1, 33, 'y1')   # lights along the band
    badge(im, 48, 17, t)
    # arched gate with the doors inside
    for x in range(cx - 14, cx + 14):
        d = abs(x - cx + .5) / 13.5
        if d <= 1:
            top = 44 + int(9 * (1 - math.sqrt(1 - d * d)))
            im.vl(x, top, 70, 'k3')
    doors(im, cx, 52, 70, half=8)
    plate(im, cx, 43)
    for x0 in (10, 76): window(im, x0, 46, 10, 10)
    for bx in (24, 65):                                         # the banners the gate doesn't cover
        if bx + 7 < cx - 14 or bx > cx + 13: banner(im, bx, 41, 7, 16)
    im.outline(); return im

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
    for name, fn in (('A', front_a), ('B', front_b), ('C', front_c)):
        for t in THEME:
            for col in (2, 3):
                fn(t, col * 16 + 8).save(os.path.join(out, 'gym_%s_%s_d%d.png' % (name, t, col)))
