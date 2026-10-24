"""Draws the three POKéMON CENTER interiors (9.4.0), one per exterior style (tools/art/centers.py):
A arch (classic yellow tiles), B striped awning (cottage), C glass atrium (indoor park). Each is the 14x9-tile room,
224x144, written to gba/data/center_room_<style>.png, and its tile rows to gba/data/center_rooms.json, which
export.js uses for the room's collision. Run by hand when the art changes: python3 tools/art/center_rooms.py data
The nurse stands at (7,2), the MOVE TUTOR is placed by build_assets.py, and (1,7) is the secret editor's corner."""
import sys, math, json
from PIL import Image

W, H, T = 224, 144, 16

STYLES = {
    # A: classic (arch exterior): warm yellow tiles, red counter, Poke Ball on the floor
    'A': dict(o=(38, 38, 56), wl1=(248, 232, 200), wl2=(232, 208, 168), trim=(200, 72, 56), trim2=(152, 48, 48),
              f1=(248, 224, 128), f2=(232, 200, 96), f3=(200, 160, 72), em=(224, 112, 64),
              ct=(248, 248, 248), cf=(224, 64, 48), cf2=(168, 32, 40), acc=(80, 144, 224), acc2=(176, 224, 248),
              wd1=(184, 120, 72), wd2=(128, 80, 48), g1=(104, 200, 96), g2=(40, 128, 72), y=(248, 208, 80)),
    # B: cottage (striped-awning exterior): plank floor, striped awning over the counter, round rug
    'B': dict(o=(38, 38, 56), wl1=(248, 240, 224), wl2=(224, 200, 184), trim=(224, 64, 48), trim2=(248, 248, 248),
              f1=(208, 152, 96), f2=(184, 128, 80), f3=(136, 88, 56), em=(224, 64, 48),
              ct=(248, 232, 200), cf=(248, 112, 88), cf2=(200, 72, 56), acc=(240, 144, 176), acc2=(248, 200, 216),
              wd1=(160, 104, 64), wd2=(112, 72, 48), g1=(120, 200, 96), g2=(48, 136, 72), y=(248, 216, 96)),
    # C: modern (glass-atrium exterior): pale blue stone, glass back wall, white counter with blue trim, teal emblem
    'C': dict(o=(38, 38, 56), wl1=(200, 232, 248), wl2=(136, 192, 232), trim=(72, 120, 200), trim2=(48, 80, 152),
              f1=(232, 240, 248), f2=(208, 220, 236), f3=(168, 184, 208), em=(64, 176, 160),
              ct=(248, 248, 248), cf=(224, 232, 240), cf2=(72, 120, 200), acc=(64, 176, 160), acc2=(160, 232, 216),
              wd1=(200, 144, 88), wd2=(136, 88, 56), g1=(104, 200, 96), g2=(40, 128, 72), y=(248, 208, 80)),
}

class Room:
    def __init__(s, st):
        s.st, s.k = STYLES[st], st
        s.im = Image.new('RGB', (W, H), STYLES[st]['o'])
        s.p = s.im.load()
    def c(s, name): return s.st[name]
    def set(s, x, y, c):
        if 0 <= x < W and 0 <= y < H: s.p[x, y] = s.c(c) if isinstance(c, str) else c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def box(s, x0, y0, x1, y1, fill):
        s.rect(x0, y0, x1, y1, 'o'); s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill)
    def disc(s, cx, cy, r, c, ry=None):
        ry = ry or r
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if ((x - cx) / r) ** 2 + ((y - cy) / ry) ** 2 <= 1.0: s.set(x, y, c)
    def shadow(s, x0, x1, y):
        for x in range(x0, x1 + 1):
            if s.p[x, y] in (s.c('f1'), s.c('f2')): s.set(x, y, 'f3')

    # ---- floor, walls, emblem ----
    def floor(s):
        for y in range(32, 128):
            for x in range(16, 208):
                if s.k == 'A':      # 8px tiles with light top-left edge and grout
                    c = 'f3' if x % 8 == 7 or y % 8 == 7 else 'f1' if x % 8 == 0 or y % 8 == 0 else 'f2'
                elif s.k == 'B':    # planks 6px tall, staggered seams
                    row = (y - 32) // 6
                    c = 'f3' if (y - 32) % 6 == 5 else 'f1' if (y - 32) % 6 == 0 else 'f2'
                    if (x + row * 13) % 40 == 0: c = 'f3'
                else:               # big polished slabs with a diagonal shine
                    c = 'f3' if x % 16 == 15 or y % 16 == 15 else 'f1'
                    if c == 'f1' and ((x % 16) - (y % 16)) in (2, 3) and (x % 16) < 8: c = 'wl1'
                    elif c == 'f1' and (x // 16 + y // 16) % 2: c = 'f2'
                s.set(x, y, c)
    def walls(s):
        s.rect(0, 0, W - 1, H - 1, 'o')
        s.rect(16, 4, 207, 31, 'wl1')
        if s.k == 'A':
            s.rect(16, 18, 207, 18, 'ct'); s.rect(16, 19, 207, 28, 'trim')
            for x in range(16, 208, 16): s.rect(x, 20, x, 27, 'trim2')
            s.rect(16, 4, 207, 5, 'wl2'); s.rect(16, 29, 207, 31, 'trim2')
        elif s.k == 'B':
            for x in range(16, 208):
                if (x // 6) % 2: s.rect(x, 4, x, 16, 'wl2')
            s.rect(16, 17, 207, 18, 'wd2'); s.rect(16, 19, 207, 31, 'wd1')
            for x in range(16, 208, 8): s.rect(x, 19, x, 31, 'wd2')
        else:                         # glass wall: sky panes with mullions
            s.rect(16, 4, 207, 24, 'wl2')
            for x in range(16, 208, 24): s.rect(x, 4, x + 1, 24, 'trim')
            for k in range(14): s.set(30 + k, 20 - k, 'wl1'); s.set(126 + k, 20 - k, 'wl1')
            s.rect(16, 25, 207, 31, 'cf'); s.rect(16, 25, 207, 25, 'trim'); s.rect(16, 31, 207, 31, 'f3')
        # side and bottom walls: a lip of wall colour on the room edge
        s.rect(14, 4, 15, 129, 'wl2'); s.rect(208, 4, 209, 129, 'wl2'); s.rect(14, 128, 209, 129, 'wl2')
    def emblem(s, cx, cy):
        e = 'em'
        if s.k == 'B':   # round red-and-white rug with the ball on it
            s.disc(cx, cy, 24, 'o', 18); s.disc(cx, cy, 23, 'trim2', 17)
            for y in range(cy - 17, cy):
                for x in range(cx - 23, cx + 24):
                    if ((x - cx) / 23) ** 2 + ((y - cy) / 17) ** 2 <= 1: s.set(x, y, 'cf')
            s.rect(cx - 23, cy - 1, cx + 23, cy + 1, 'o')
            s.disc(cx, cy, 6, 'o', 5); s.disc(cx, cy, 4, 'trim2', 3)
            return
        # floor inlay: ring, band and centre button in the emblem colour
        for y in range(cy - 19, cy + 20):
            for x in range(cx - 25, cx + 26):
                d = ((x - cx) / 24) ** 2 + ((y - cy) / 18) ** 2
                if 0.72 < d <= 1: s.set(x, y, e)
        s.rect(cx - 21, cy - 1, cx + 21, cy + 1, e)
        s.disc(cx, cy, 7, e, 6); s.disc(cx, cy, 4, 'f1', 3)

    # ---- furniture, each on its tile (tx, ty) ----
    def counter(s, tx0, tx1, ty):
        x0, x1, y = tx0 * T, tx1 * T + 15, ty * T
        s.shadow(x0, x1, y + 16)
        s.box(x0, y - 2, x1, y + 15, 'cf')
        s.rect(x0 + 1, y - 1, x1 - 1, y + 4, 'ct'); s.rect(x0 + 1, y + 5, x1 - 1, y + 5, 'o')
        s.rect(x0 + 1, y + 13, x1 - 1, y + 14, 'cf2')
        if s.k == 'A':
            s.rect(x0 + 1, y + 8, x1 - 1, y + 9, 'ct')
        elif s.k == 'B':
            for x in range(x0 + 1, x1, 8): s.rect(x, y + 6, x, y + 12, 'cf2')
        else:
            s.rect(x0 + 1, y + 9, x1 - 1, y + 10, 'acc')
        for x in (x0, x1 - 15):   # the counter ends (C) a shade darker
            s.rect(x + 1, y + 6, x + 14, y + 12, 'cf2')
            s.rect(x + 3, y + 8, x + 12, y + 10, 'ct')
    def awning(s, x0, x1, y0):
        for x in range(x0, x1 + 1):
            c = 'trim' if (x // 6) % 2 else 'trim2'
            d = (x - x0) % 12
            bottom = y0 + 7 + (2 if 3 <= d <= 8 else 1 if d in (2, 9) else 0)
            s.rect(x, y0, x, bottom, c); s.set(x, bottom + 1, 'o')
        s.rect(x0, y0 - 1, x1, y0 - 1, 'o')
    def healer(s, tx, ty):
        x, y = tx * T, ty * T - 10
        s.shadow(x, x + 15, y + 26)
        s.box(x, y, x + 15, y + 25, 'ct'); s.rect(x + 1, y + 1, x + 14, y + 3, 'acc')
        s.box(x + 3, y + 5, x + 12, y + 12, 'acc2'); s.rect(x + 4, y + 6, x + 11, y + 7, 'ct')
        for i, cx in enumerate((x + 4, x + 8, x + 11)):
            for cy in (y + 16, y + 20):
                s.disc(cx, cy, 1.6, 'o'); s.set(cx, cy, 'cf'); s.set(cx, cy + 1, 'ct')
    def pc(s, tx, ty):
        x, y = tx * T, ty * T - 8
        s.shadow(x, x + 15, y + 24)
        s.box(x + 1, y + 10, x + 14, y + 23, 'wl2'); s.rect(x + 3, y + 14, x + 12, y + 15, 'o')
        s.box(x + 2, y, x + 13, y + 10, 'ct'); s.rect(x + 4, y + 2, x + 11, y + 7, 'acc')
        s.rect(x + 5, y + 3, x + 7, y + 3, 'acc2')
    def shelf(s, tx, ty):
        x, y = tx * T, ty * T - 10
        s.shadow(x, x + 15, y + 26)
        s.box(x, y, x + 15, y + 25, 'wd1')
        for k, sy in enumerate((y + 2, y + 10, y + 18)):
            s.rect(x + 1, sy + 6, x + 14, sy + 7, 'wd2')
            for i, bx in enumerate(range(x + 2, x + 14, 2)):
                s.rect(bx, sy, bx, sy + 5, ('cf', 'acc', 'g1', 'y', 'trim2', 'acc2')[(i + k) % 6])
    def seat(s, tx, ty, col):
        x, y = tx * T, ty * T
        s.shadow(x + 2, x + 13, y + 15)
        s.box(x + 1, y + 2, x + 14, y + 13, col)
        s.rect(x + 2, y + 3, x + 13, y + 4, 'ct'); s.rect(x + 2, y + 11, x + 13, y + 12, 'o')
    def table(s, tx, ty):
        x, y = tx * T, ty * T
        s.shadow(x + 1, x + 14, y + 15)
        s.box(x, y + 2, x + 15, y + 11, 'acc2'); s.rect(x + 2, y + 3, x + 6, y + 3, 'ct')
        s.rect(x + 2, y + 12, x + 3, y + 14, 'o'); s.rect(x + 12, y + 12, x + 13, y + 14, 'o')
    def plant(s, tx, ty):
        x, y = tx * T, ty * T - 6
        s.shadow(x + 3, x + 12, y + 22)
        s.box(x + 4, y + 13, x + 11, y + 21, 'cf' if s.k != 'C' else 'wd1'); s.rect(x + 5, y + 14, x + 10, y + 14, 'ct')
        for a in range(-50, 231, 20):
            r = math.radians(a)
            for t in range(2, 11):
                s.set(int(x + 8 + t * math.cos(r)), int(y + 11 - t * math.sin(r) * 0.85), 'g1' if t < 7 else 'g2')
        s.set(x + 8, y + 9, 'g2')
    def rug(s, tx0, tx1, ty):
        x0, x1, y = tx0 * T, tx1 * T + 15, ty * T
        s.box(x0, y + 2, x1, y + 13, 'trim')
        s.rect(x0 + 2, y + 4, x1 - 2, y + 11, 'trim2' if s.k == 'A' else 'em')
        for x in range(x0 + 4, x1 - 2, 8): s.set(x, y + 7, 'y'); s.set(x, y + 8, 'y')
    def poster(s, tx, ty):
        x, y = tx * T, ty * T - 6
        s.box(x + 2, y, x + 13, y + 13, 'ct'); s.disc(x + 7.5, y + 6.5, 4, 'o')
        s.disc(x + 7.5, y + 6.5, 3, 'ct'); s.rect(x + 5, y + 4, x + 10, y + 6, 'cf'); s.rect(x + 4, y + 6, x + 11, y + 6, 'o')
    def wallmap(s, tx, ty):
        x, y = tx * T, ty * T - 6
        s.box(x, y, x + 15, y + 12, 'wd1'); s.rect(x + 2, y + 2, x + 13, y + 10, 'acc2')
        s.rect(x + 4, y + 4, x + 9, y + 8, 'g1'); s.rect(x + 10, y + 3, x + 12, y + 5, 'g1')
    def door(s):
        s.rect(96, 128, 127, 143, 'f3'); s.rect(97, 129, 126, 143, 'f2')
        for x0 in (98, 113):
            s.box(x0, 130, x0 + 12, 141, 'trim'); s.rect(x0 + 2, 132, x0 + 10, 139, 'trim2')

    # ---- extra pieces for the per-style layouts ----
    def border(s):
        # a darker band of floor tiles around the walls, like the reference rooms
        for y in range(32, 128):
            for x in range(16, 208):
                if x < 24 or x > 199 or y > 119:
                    if s.p[x, y] in (s.c('f1'), s.c('f2')): s.set(x, y, 'f3' if (x + y) % 8 < 4 else 'f2')
    def clock(s, tx, ty):
        x, y = tx * T + 8, ty * T + 2
        s.disc(x, y, 6, 'o'); s.disc(x, y, 5, 'ct'); s.rect(x, y - 4, x, y, 'o'); s.rect(x, y, x + 3, y, 'o')
    def window(s, tx, ty, w=2):
        x0, y0, x1 = tx * T + 2, ty * T - 10, tx * T + w * 16 - 3
        s.box(x0, y0, x1, y0 + 18, 'acc2'); s.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 4, 'ct')
        for k in range(6): s.set(x0 + 4 + k, y0 + 14 - k, 'ct')
        s.rect((x0 + x1) // 2, y0 + 1, (x0 + x1) // 2, y0 + 17, 'o')
        for x in (x0 - 1, x0, x1, x1 + 1): s.rect(x, y0 - 1, x, y0 + 19, 'trim')     # curtains
        s.rect(x0 - 2, y0 - 2, x1 + 2, y0 - 1, 'wd2')
    def fireplace(s, tx, ty):
        x, y = tx * T, ty * T - 12
        s.shadow(x, x + 31, y + 28)
        s.box(x, y, x + 31, y + 27, 'wl2')
        for yy in range(y + 2, y + 26, 4):
            for xx in range(x + 1 + ((yy // 4) % 2) * 3, x + 31, 6): s.set(xx, yy, 'f3')
        s.box(x + 8, y + 10, x + 23, y + 27, 'o')
        for k in range(4):
            s.rect(x + 11 + k * 3, y + 22 - k % 2 * 3, x + 12 + k * 3, y + 26, 'cf'); s.set(x + 11 + k * 3, y + 24, 'y')
        s.rect(x - 1, y - 2, x + 32, y, 'wd1'); s.rect(x - 1, y + 1, x + 32, y + 1, 'wd2')
    def sofa(s, tx, ty, h=2):
        x, y = tx * T, ty * T
        s.shadow(x + 1, x + 14, y + h * 16)
        s.box(x + 1, y, x + 14, y + h * 16 - 1, 'cf2'); s.rect(x + 2, y + 1, x + 6, y + h * 16 - 2, 'cf')
        for k in range(1, h): s.rect(x + 7, y + k * 16, x + 13, y + k * 16, 'cf2')
        s.rect(x + 2, y + 1, x + 13, y + 2, 'acc2')
    def armchair(s, tx, ty, col='acc'):
        x, y = tx * T, ty * T
        s.shadow(x + 2, x + 13, y + 15)
        s.box(x + 1, y + 1, x + 14, y + 14, col); s.rect(x + 4, y + 5, x + 11, y + 12, 'acc2'); s.rect(x + 1, y + 1, x + 14, y + 4, 'cf2')
    def roundtable(s, tx, ty):
        x, y = tx * T + 8, ty * T + 7
        s.shadow(x - 6, x + 6, ty * T + 15)
        s.disc(x, y, 8, 'o', 6); s.disc(x, y, 7, 'ct', 5); s.disc(x, y + 2, 7, 'acc2', 2)
        s.rect(x - 1, y + 7, x + 1, y + 8, 'o')
        s.disc(x - 2, y - 1, 2, 'cf', 1); s.set(x + 3, y - 1, 'y')
    def tree(s, tx, ty):
        # a 2x2 indoor tree in a big planter
        x, y = tx * T, ty * T - 8
        s.shadow(x + 4, x + 27, y + 40)
        s.box(x + 6, y + 28, x + 25, y + 39, 'wd1'); s.rect(x + 7, y + 29, x + 24, y + 30, 'wd2')
        s.rect(x + 15, y + 18, x + 16, y + 28, 'wd2')
        for cx, cy, r in ((16, 12, 11), (8, 16, 7), (24, 16, 7), (16, 4, 6)):
            s.disc(x + cx, y + cy, r + 1, 'o'); 
        for cx, cy, r in ((16, 12, 11), (8, 16, 7), (24, 16, 7), (16, 4, 6)):
            s.disc(x + cx, y + cy, r, 'g2'); s.disc(x + cx - 2, y + cy - 2, r - 3, 'g1')
    def bed(s, tx0, tx1, ty):
        # long planter bed with flowers
        x0, x1, y = tx0 * T + 1, tx1 * T + 14, ty * T + 2
        s.shadow(x0, x1, y + 13)
        s.box(x0, y + 4, x1, y + 12, 'wd1'); s.rect(x0 + 1, y + 5, x1 - 1, y + 5, 'wd2')
        for x in range(x0 + 1, x1):
            s.set(x, y + 3, 'g2'); s.set(x, y + 2 - (x % 3 == 0), 'g1')
            if x % 3 == 1: s.set(x, y + 1, ('em', 'y', 'cf2', 'ct')[(x // 3) % 4]); s.set(x, y, 'g1')
    def bench(s, tx0, tx1, ty):
        x0, x1, y = tx0 * T + 1, tx1 * T + 14, ty * T + 4
        s.shadow(x0, x1, y + 11)
        s.box(x0, y, x1, y + 6, 'wd1'); s.rect(x0 + 1, y + 1, x1 - 1, y + 1, 'f1')
        for x in range(x0 + 6, x1, 12): s.rect(x, y + 1, x, y + 5, 'wd2')
        for x in (x0 + 2, x1 - 3): s.rect(x, y + 7, x + 1, y + 10, 'o')
    def light(s):
        # sunlight falling through the glass roof: pale diagonal bands on the floor
        for y in range(32, 128):
            for x in range(16, 208):
                if (x + y // 2) % 64 < 10 and s.p[x, y] in (s.c('f1'), s.c('f2')): s.set(x, y, 'wl1')
    def arm(s, tx, ty):
        # a side arm of the U-shaped counter: runs from the back wall down to the front counter
        x, y = tx * T, ty * T - 2
        s.box(x, y, x + 15, y + 18, 'cf'); s.rect(x + 3, y + 1, x + 12, y + 17, 'ct')
        s.rect(x + 2, y + 1, x + 2, y + 17, 'o'); s.rect(x + 13, y + 1, x + 13, y + 17, 'o')
    def sofa_h(s, tx0, tx1, ty, col='cf2', cush='cf'):
        x0, x1, y = tx0 * T + 1, tx1 * T + 14, ty * T + 1
        s.shadow(x0, x1, y + 14)
        s.box(x0, y, x1, y + 13, col); s.rect(x0 + 1, y + 1, x1 - 1, y + 4, col)
        for cx in range(x0 + 3, x1 - 3, 14): s.box(cx, y + 5, min(cx + 12, x1 - 3), y + 11, cush)
        s.rect(x0 + 1, y + 1, x1 - 1, y + 1, 'acc2')
    def coffee(s, tx, ty):
        x, y = tx * T, ty * T
        s.shadow(x + 1, x + 14, y + 13)
        s.box(x + 1, y + 3, x + 14, y + 11, 'wd1'); s.rect(x + 2, y + 4, x + 13, y + 5, 'f1')
        s.set(x + 5, y + 7, 'ct'); s.set(x + 6, y + 7, 'ct'); s.set(x + 10, y + 6, 'cf')
    def platform(s, x0, y0, x1, y1, inner):
        # raised lounge: green carpet framed in wood, a tall front riser and a shadow on the plank floor, so it reads as a step up
        s.rect(x0, y0, x1, y1 - 5, 'wd2'); s.rect(x0, y0, x1, y0 + 1, 'f1')
        s.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 8, 'g2')
        for y in range(y0 + 5, y1 - 8, 6):
            for x in range(x0 + 5 + ((y - y0) // 6 % 2) * 4, x1 - 3, 8): s.set(x, y, 'g1'); s.set(x + 1, y + 1, 'g1'); s.set(x - 1, y + 1, 'g1'); s.set(x, y + 2, 'g1')
        s.rect(x0, y1 - 5, x1, y1 - 5, 'f1')
        s.rect(x0, y1 - 4, x1, y1, 'wd1'); s.rect(x0, y1 - 1, x1, y1, 'wd2')
        for x in range(x0 + 7, x1, 12): s.rect(x, y1 - 4, x, y1, 'wd2')
        s.rect(x0, y1 + 1, x1, y1 + 1, 'o')
        s.shadow(x0, x1, y1 + 2); s.shadow(x0, x1, y1 + 3)
        side = x1 + 1 if inner == x1 else x0 - 1
        s.rect(side, y0, side, y1 + 1, 'o')
        if inner == x1:
            for y in range(y0 + 2, y1 + 4): s.shadow(side + 1, side + 2, y)
    def railing(s, x, y0, y1):
        # low wooden rail on the aisle side of the lounge: posts every 12px and a capped top rail
        x = x - 2 if x > 112 else x - 1
        s.rect(x, y0, x + 2, y1, 'o'); s.rect(x + 1, y0, x + 1, y1, 'wd1')
        for y in range(y0, y1 + 1, 12): s.rect(x - 1, y, x + 3, y + 3, 'o'); s.rect(x, y + 1, x + 2, y + 2, 'f1')
        s.rect(x - 1, y1, x + 3, y1 + 4, 'o'); s.rect(x, y1 + 1, x + 2, y1 + 2, 'f1')
    def grass(s, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                h = (x * 7 + y * 13) % 41
                s.set(x, y, 'g2' if h in (0, 9) else 'em' if h == 17 else 'y' if h == 29 else 'g1')
        s.rect(x0, y0, x1, y0, 'g2')
    def bush(s, tx, ty):
        x, y = tx * T + 8, ty * T + 8
        s.disc(x, y, 8, 'o', 7); s.disc(x, y, 7, 'g2', 6); s.disc(x - 2, y - 2, 4, 'g1', 3)
        s.set(x + 3, y - 1, 'em'); s.set(x - 3, y + 2, 'y')
    def lamp(s, tx, ty):
        x, y = tx * T + 7, ty * T - 10
        s.rect(x, y + 6, x + 1, y + 25, 'o'); s.rect(x - 2, y + 24, x + 3, y + 25, 'o')
        s.box(x - 3, y, x + 4, y + 6, 'y'); s.rect(x - 2, y + 1, x + 3, y + 2, 'ct')

    def runner(s, x0, x1, y0, y1):
        s.rect(x0, y0, x1, y1, 'trim2'); s.rect(x0 + 2, y0, x1 - 2, y1, 'trim')
        for y in range(y0 + 3, y1, 6): s.set(x0 + 1, y, 'y'); s.set(x1 - 1, y, 'y')

# Room rows per style (for js/app.js later). Kept fixed in all three: door MM at x6-7, nurse at (7,2) behind the
# counter, and the secret-menu corner (1,7) as open floor.
# Game tile rows (js/app.js TILE_CLS): the counter's arms are 'C', seats and sofas 'q', trees, beds, bushes, lamps
# and the fireplace 'T' (solid, nothing to read).
LAYOUTS = {
    'A': ['##############', '##n###K###m###', '#k__p_h_h___P#', '#___CccccC___#', '#p__________p#',
          '#qgq______qgq#', '#____________#', '#____________#', '######MM######'],
    'B': ['##############', '###ww#n##ww###', '#k_P_Ch_C__TT#', '#____CccC____#', '#q_q______q_q#',
          '#qtq______qtq#', '#qqq______qqq#', '#____________#', '######MM######'],
    'C': ['##############', '######n#######', '#TT_Ch__CP_TT#', '#TT_CcccC__TT#', '#TT________TT#',
          '#TT________TT#', '#___q____q___#', '#_TT______TT_#', '######MM######'],
}
TUTOR = {'A': (11, 6), 'B': (11, 7), 'C': (11, 6)}   # build_assets.py reads these from the JSON

def check(rows, tutor):
    # self-check: from the door every spot that matters can be reached
    walk = lambda x, y: rows[y][x] in '_oM'
    seen, todo = {(6, 7)}, [(6, 7)]
    while todo:
        x, y = todo.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= ny < len(rows) and 0 <= nx < len(rows[0]) and (nx, ny) not in seen and walk(nx, ny):
                seen.add((nx, ny)); todo.append((nx, ny))
    pc = next((x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == 'P')
    for spot in ((1, 7), (7, 4), (pc[0], pc[1] + 1)): assert spot in seen, spot
    assert any((tutor[0] + dx, tutor[1] + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    assert rows[2][7] == '_' and rows[3][7] == 'c' and walk(*tutor)

def build(st):
    r = Room(st)
    r.walls(); r.floor()
    if st == 'A':
        r.border(); r.emblem(112, 98)
        r.runner(100, 123, 120, 127)
        r.poster(2, 1); r.clock(6, 1); r.wallmap(10, 1)
        r.shelf(1, 2); r.plant(4, 2); r.healer(6, 2); r.healer(8, 2); r.pc(12, 2)
        r.counter(4, 9, 3)
        r.plant(1, 4); r.plant(12, 4)
        for x0 in (1, 10):
            r.rect(x0 * T + 1, 5 * T + 1, x0 * T + 46, 5 * T + 15, 'acc'); r.rect(x0 * T + 3, 5 * T + 3, x0 * T + 44, 5 * T + 13, 'acc2')
            r.seat(x0, 5, 'cf'); r.table(x0 + 1, 5); r.seat(x0 + 2, 5, 'y')
    elif st == 'B':
        r.emblem(112, 104)
        r.window(3, 1); r.window(9, 1); r.poster(6, 1)
        r.shelf(1, 2); r.pc(3, 2); r.healer(6, 2); r.fireplace(11, 2)
        r.arm(5, 2); r.arm(8, 2); r.counter(5, 8, 3)
        for x0, inner in ((16, 63), (160, 160)):
            r.platform(x0, 63, x0 + 47, 111, inner)
        for t in (1, 10):
            r.armchair(t, 4, 'acc'); r.armchair(t + 2, 4, 'acc'); r.coffee(t + 1, 5); r.sofa_h(t, t + 2, 6)
        for x0, inner in ((16, 63), (160, 160)): r.railing(inner, 64, 98)
    else:
        r.light()
        for x0, x1 in ((16, 63), (160, 207)): r.grass(x0, 66, x1, 127)
        r.emblem(112, 104)
        r.poster(6, 1)
        r.tree(1, 2); r.tree(11, 2)
        r.healer(5, 2); r.pc(9, 2)
        r.arm(4, 2); r.arm(8, 2); r.counter(4, 8, 3)
        r.bed(1, 1, 4); r.bed(12, 12, 4); r.lamp(2, 4); r.lamp(11, 4)
        for t in (1, 2, 11, 12): r.bush(t, 5)
        for t in (2, 3, 10, 11): r.bush(t, 7)
        for x in range(18, 206, 24):                       # ivy hanging from the glass wall
            for k in range(0, 10 + (x % 5) * 2): r.set(x + (k % 3 == 1), 5 + k, 'g2' if k % 2 else 'g1')
        r.bench(4, 4, 6); r.bench(9, 9, 6)
    r.door()
    return r.im

out = sys.argv[1]
for st in 'ABC':
    check(LAYOUTS[st], TUTOR[st])
    build(st).save(f'{out}/center_room_{st}.png')
json.dump({st: {'rows': LAYOUTS[st], 'tutor': TUTOR[st]} for st in 'ABC'}, open(f'{out}/center_rooms.json', 'w'), indent=1)
