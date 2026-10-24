"""Draws the three POKéMON CENTER fronts (9.4.0), 80x72 with transparency, to gba/data/center_<style>.png:
A a raised arch carrying the emblem, B a scalloped striped awning, C a glass atrium between two red wings.
export.js draws one over each CENTER (5x4 tiles, rising 8 px above). Run by hand: python3 tools/art/centers.py data"""
import sys, math
from PIL import Image

W, H = 80, 72
O = (38, 38, 56)          # outline #262638
# Snapped to the colours the towns already use (map_0), so a CENTER adds only its outline to a town's palette banks.
P = dict(
    o=O, r1=(240, 112, 96), r2=(232, 72, 72), r3=(176, 40, 56), r4=(136, 40, 48),
    w1=(248, 248, 248), w2=(208, 216, 224), w3=(168, 168, 192),
    b1=(184, 224, 255), b2=(88, 160, 240), b3=(48, 80, 160),
    y1=(248, 216, 96), g1=(120, 200, 74), g2=(40, 144, 80),
)

class Img:
    def __init__(s): s.px = [[None] * W for _ in range(H)]
    def set(s, x, y, c):
        if 0 <= x < W and 0 <= y < H: s.px[y][x] = P[c]
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def hl(s, x0, x1, y, c): s.rect(x0, y, x1, y, c)
    def vl(s, x, y0, y1, c): s.rect(x, y0, x, y1, c)
    def disc(s, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.6: s.set(x, y, c)
    def outline(s):
        # 1px outline on every empty pixel touching the building (4-neighbour), as the hand art does
        add = []
        for y in range(H):
            for x in range(W):
                if s.px[y][x] is None and any(0 <= x + dx < W and 0 <= y + dy < H and s.px[y + dy][x + dx] not in (None, O)
                                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((x, y))
        for x, y in add: s.px[y][x] = O
    def save(s, path):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for y in range(H):
            for x in range(W):
                if s.px[y][x]: im.putpixel((x, y), s.px[y][x] + (255,))
        im.save(path)

FONT = {'P': ['11.', '1.1', '11.', '1..', '1..'], 'C': ['.11', '1..', '1..', '1..', '.11'], '.': ['.', '.', '.', '.', '1']}
def text(im, x, y, s, c):
    for ch in s:
        g = FONT[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == '1': im.set(x + i, y + j, c)
        x += len(g[0]) + 1

def ball(im, cx, cy, r):
    # the Poke Ball emblem: white disc, dark ring, band and button
    im.disc(cx, cy, r + 1, 'o'); im.disc(cx, cy, r, 'w1')
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r: im.set(x, y, 'r2')
    for x in range(cx - r, cx - r // 2):
        for y in range(cy - r, cy):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and y < cy - r // 2: im.set(x, y, 'r1')
    im.hl(cx - r, cx + r, cy, 'o')
    im.disc(cx, cy, 3, 'o'); im.disc(cx, cy, 2, 'w1'); im.set(cx - 1, cy - 1, 'w2')

def walls(im, x0, x1, y0, y1):
    # siding like the town's houses: white boards with a grey seam every 3 rows, shade on the right, stone footing
    im.rect(x0, y0, x1, y1, 'w1')
    for y in range(y0 + 2, y1 - 4, 3): im.hl(x0, x1, y, 'w2')
    im.vl(x1, y0, y1, 'w2'); im.vl(x1 - 1, y0, y1, 'w2')
    im.hl(x0, x1, y0, 'w3'); im.hl(x0, x1, y0 + 1, 'w2')          # eaves shadow
    footing(im, x0, x1, y1 - 3, y1)

def footing(im, x0, x1, y0, y1):
    im.rect(x0, y0, x1, y1, 'w3')
    im.hl(x0, x1, y0, 'w2')
    for y in range(y0 + 1, y1 + 1, 2):
        off = 0 if (y - y0) % 4 == 1 else 3
        for x in range(x0 + off, x1 + 1, 6): im.set(x, y, 'o')

def shingles(im, x0, y0, x1, y1, inside=None):
    # roof tiles: rows of 4 with a highlight on top, a dark lip below and staggered seams
    for y in range(y0, y1 + 1):
        rr, row = (y - y0) % 4, (y - y0) // 4
        for x in range(x0, x1 + 1):
            if inside and not inside(x, y): continue
            c = 'r1' if rr == 0 else 'r3' if rr == 3 else 'r2'
            if rr in (1, 2) and (x + row * 4) % 8 == 0: c = 'r3'
            im.set(x, y, c)

def window(im, x0, y0, w, h):
    im.rect(x0, y0, x0 + w - 1, y0 + h - 1, 'o')
    im.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2, 'b2')
    im.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + 2, 'b1')
    for k in range(min(w, h) - 3): im.set(x0 + 2 + k, y0 + h - 3 - k, 'b1')
    im.hl(x0 + 1, x0 + w - 2, y0 + h - 2, 'b3')
    im.vl(x0 + w // 2, y0 + 1, y0 + h - 2, 'o')
    im.hl(x0 - 1, x0 + w, y0 - 1, 'w2')                          # lintel

def planter(im, x0, y0, w):
    # flower box under a window: dark box, leaves, red and yellow flowers
    im.rect(x0, y0, x0 + w - 1, y0 + 3, 'o')
    im.rect(x0 + 1, y0, x0 + w - 2, y0 + 1, 'g2')
    for x in range(x0 + 1, x0 + w - 1, 2): im.set(x, y0 - 1, 'g1')
    for i, x in enumerate(range(x0 + 2, x0 + w - 2, 3)): im.set(x, y0 - 1, 'r1' if i % 2 else 'y1')
    im.rect(x0 + 1, y0 + 2, x0 + w - 2, y0 + 2, 'r3')

def doors(im, cx, y0, y1, half=8):
    x0, x1 = cx - half, cx + half - 1
    im.rect(x0 - 1, y0 - 1, x1 + 1, y1, 'w3')
    im.rect(x0, y0, x1, y1, 'o')
    for a, b in ((x0 + 1, cx - 2), (cx + 1, x1 - 1)):
        im.rect(a, y0 + 1, b, y1, 'b2')
        im.rect(a, y0 + 1, b, y0 + 3, 'b1')
        im.vl(a + 1, y0 + 4, y1 - 3, 'b1')
        im.hl(a, b, y1 - 1, 'b3')
    im.vl(cx - 1, y0 + 1, y1, 'o'); im.vl(cx, y0 + 1, y1, 'o')

def sign(im, x, y, bg='w1', fg='r2'):
    im.rect(x, y, x + 13, y + 6, 'o'); im.rect(x + 1, y + 1, x + 12, y + 5, bg)
    text(im, x + 3, y + 1, 'P.C', fg)

# ---- A: Sinnoh-style, raised arch carrying a big emblem ----
def center_a():
    im = Img()
    walls(im, 4, 75, 36, 70)
    shingles(im, 2, 14, 77, 25)
    im.rect(1, 26, 78, 32, 'r2'); im.hl(1, 78, 26, 'r1'); im.hl(1, 78, 29, 'w1'); im.hl(1, 78, 32, 'r3')
    for x in range(5, 77, 8): im.vl(x, 27, 28, 'r3'); im.vl(x, 30, 31, 'r3')
    im.rect(2, 33, 77, 35, 'r4')
    arch = lambda x, y: y >= 3 + int(11 * (1 - math.sqrt(max(0, 1 - ((x - 39.5) / 18) ** 2))))
    shingles(im, 22, 3, 57, 25, arch)
    for x in range(22, 58):
        top = next(y for y in range(3, 26) if arch(x, y)); im.set(x, top, 'r1'); im.set(x, top + 1, 'r1')
    ball(im, 40, 20, 10)
    window(im, 9, 44, 14, 13); window(im, 57, 44, 14, 13)
    planter(im, 8, 59, 16); planter(im, 56, 59, 16)
    sign(im, 33, 38)
    im.rect(28, 45, 51, 47, 'r2'); im.hl(28, 51, 45, 'r1'); im.hl(28, 51, 47, 'r3')
    doors(im, 40, 49, 70)
    im.outline(); return im

# ---- B: Gen 2 style, scalloped striped awning roof ----
def center_b():
    im = Img()
    walls(im, 5, 74, 30, 70)                  # the wall runs up under the awning, so the roof sits on it
    for x in range(3, 77):
        c = 'r2' if (x // 4) % 2 == 0 else 'r1'
        im.vl(x, 10, 30, c)
    for y in range(13, 30, 4): im.hl(3, 76, y, 'r3')
    im.hl(3, 76, 10, 'w1')
    for k in range(5):
        cx = 3 + 74 * (k + 0.5) / 5
        for x in range(int(cx - 7), int(cx + 8)):
            d = abs(x - cx) / 7.5
            if d <= 1:
                b = 31 + int(6 * math.sqrt(1 - d * d))
                im.vl(x, 31, b, 'w1' if k % 2 else 'r2'); im.set(x, b, 'r3' if k % 2 == 0 else 'w2')
                im.set(x, b + 1, 'o'); im.set(x, b + 2, 'w3')                          # edge and shadow on the wall
    im.hl(3, 76, 30, 'r4')
    for x in (4, 75): im.vl(x, 31, 37, 'r4')                                          # awning brackets
    im.disc(40, 14, 13, 'o'); im.disc(40, 14, 12, 'r1')
    ball(im, 40, 14, 9)
    window(im, 10, 45, 13, 12); window(im, 57, 45, 13, 12)
    planter(im, 9, 58, 15); planter(im, 56, 58, 15)
    sign(im, 33, 39, 'b2', 'w1')
    doors(im, 40, 47, 70, half=9)
    im.outline(); return im

# ---- C: glass atrium between two red wings ----
def center_c():
    im = Img()
    for x0, x1 in ((2, 24), (55, 77)):
        walls(im, x0 + 1, x1 - 1, 34, 70)
        shingles(im, x0, 22, x1, 31)
        im.rect(x0, 32, x1, 33, 'r4')
        window(im, x0 + 5, 45, 13, 12); planter(im, x0 + 4, 58, 15)
    # atrium glass, darker towards the bottom, on a stone plinth between two pillars
    dome = lambda x: 4 + int(14 * (1 - math.sqrt(max(0, 1 - ((x - 39.5) / 15.5) ** 2))))
    for x in range(25, 55):
        top = dome(x)
        im.vl(x, top, 66, 'b2'); im.vl(x, 50, 66, 'b3')
        im.set(x, top, 'b1'); im.set(x, top + 1, 'b1')
    for x in range(27, 54, 5): im.vl(x, dome(x) + 2, 64, 'b3')
    for y in (24, 34): im.hl(25, 54, y, 'b3')
    for k in range(10): im.set(30 + k, 30 - k, 'b1'); im.set(31 + k, 30 - k, 'b1')
    for x0 in (23, 55):
        im.rect(x0, 16, x0 + 1, 70, 'w2'); im.vl(x0, 16, 70, 'w1'); im.rect(x0 - 1, 14, x0 + 2, 15, 'w3')
    footing(im, 23, 56, 66, 70)
    im.rect(25, 36, 54, 41, 'r2'); im.hl(25, 54, 36, 'r1'); im.hl(25, 54, 41, 'r3')
    ball(im, 40, 37, 7)
    doors(im, 40, 48, 70, half=8)
    sign(im, 58, 36, 'b2', 'w1')
    im.outline(); return im

out = sys.argv[1]
for name, fn in (('A', center_a), ('B', center_b), ('C', center_c)):
    fn().save(f'{out}/center_{name}.png')
