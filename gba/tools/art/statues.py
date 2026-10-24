"""The landmarks (9.4.1): every statue, clock, altar, grave, orb and shrine a region's data places as kind 'statue'
gets its own look, hand pixelled in the overworld's style (flat colours, light from the top left, the shared #262638
outline); statues of people and Pokémon are cast from their game sprites. A 32x32 look stands on two tiles side by
side, a 64x64 one (a town square's centre piece) on four by two; the rest rises into the rows above.
    python3 statues.py [OUT]       -> OUT/<look>.png (default gba/data/statues/) and OUT/../statues_sheet.png"""
import math, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'data', 'statues')
O = (38, 38, 56)
# Ramps, dark to light (the approved props' stone and wood, and their kin).
STONE = [(72, 76, 92), (112, 116, 132), (156, 160, 172), (204, 206, 212), (236, 236, 236)]
WOOD = [(92, 56, 36), (132, 84, 48), (176, 120, 72), (214, 164, 106)]
BRONZE = [(84, 52, 32), (140, 88, 44), (192, 132, 64), (232, 184, 112)]
METAL = [(40, 72, 152), (64, 112, 200), (112, 160, 232), (248, 248, 248)]
STEEL = [(64, 72, 88), (104, 112, 128), (152, 160, 176), (208, 214, 224)]
GOLD = [(152, 88, 24), (216, 152, 40), (255, 216, 96), (255, 248, 200)]
MOSS = [(52, 104, 52), (84, 148, 64), (132, 188, 84)]
LEAF = [(40, 92, 52), (63, 138, 72), (90, 172, 88), (124, 200, 106)]
RUST = [(92, 44, 32), (148, 72, 44), (188, 104, 60), (220, 148, 96)]
RUNE = (58, 176, 168)
WHITE = (248, 248, 248)

class S:
    def __init__(s, w=32, h=32):
        s.w, s.h = w, h
        s.px = [[None] * w for _ in range(h)]
    def set(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h and c: s.px[y][x] = c
    def get(s, x, y):
        return s.px[y][x] if 0 <= x < s.w and 0 <= y < s.h else None
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def box(s, x0, y0, x1, y1, R):
        """A lit block: face R[1..2], top edge and left edge light, right edge and bottom dark."""
        s.rect(x0, y0, x1, y1, R[2] if len(R) > 3 else R[1])
        s.rect(x0, y0, x1, y0, R[-1] if len(R) > 3 else R[2]); s.rect(x0, y0, x0, y1, R[-1] if len(R) > 3 else R[2])
        s.rect(x1, y0 + 1, x1, y1, R[1] if len(R) > 3 else R[0]); s.rect(x0 + 1, y1, x1, y1, R[0])
    def disc(s, cx, cy, rx, ry, R, lit=True):
        """A filled ellipse, lit from the top left."""
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if dx * dx + dy * dy <= 1:
                    k = dx + dy
                    i = len(R) - 1 if lit and k < -0.9 else len(R) - 2 if k < -0.1 else 1 if k < 0.8 else 0
                    s.set(x, y, R[max(0, min(len(R) - 1, i))])
    def line(s, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            s.set(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)
    def poly(s, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
                if ya != yb and min(ya, yb) <= y + 0.5 < max(ya, yb):
                    xs.append(xa + (y + 0.5 - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(round(a), round(b)): s.set(x, y, c)
    def outline(s):
        add = [(x, y) for y in range(s.h) for x in range(s.w) if s.px[y][x] is None and any(
            s.get(x + dx, y + dy) not in (None, O) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in add: s.px[y][x] = O
        return s
    def image(s):
        im = Image.new('RGBA', (s.w, s.h), (0, 0, 0, 0))
        for y in range(s.h):
            for x in range(s.w):
                if s.px[y][x]: im.putpixel((x, y), s.px[y][x] + (255,))
        return im

def hooh_figurehead():
    s = S()
    s.box(13, 20, 18, 30, WOOD)                         # the post
    # HO-OH carved in wood, wings raised, painted red and gold.
    s.poly([(4, 4), (13, 12), (13, 18), (6, 14)], WOOD[2]); s.poly([(27, 4), (18, 12), (18, 18), (25, 14)], WOOD[1])
    for k in range(3):
        s.line(6 + k * 2, 6 + k * 3, 12, 12 + k, (200, 64, 48)); s.line(25 - k * 2, 6 + k * 3, 19, 12 + k, (168, 48, 40))
    s.disc(15.5, 15, 4, 6, WOOD)
    s.disc(15.5, 7, 3, 3, WOOD); s.set(14, 6, O); s.rect(17, 7, 19, 7, GOLD[2])    # head, eye, beak
    s.rect(14, 3, 17, 3, (200, 64, 48)); s.set(13, 2, (200, 64, 48)); s.set(15, 1, GOLD[2])   # crest
    s.rect(12, 20, 19, 21, GOLD[1]); s.rect(12, 20, 19, 20, GOLD[2])                   # the brass band
    s.rect(13, 25, 18, 27, GOLD[1]); s.rect(14, 26, 17, 26, GOLD[3])                   # the plaque
    return s

def lab_terminal():
    s = S()
    s.box(4, 14, 27, 30, STEEL)                          # the desk
    s.box(7, 2, 24, 15, STEEL)                           # the monitor
    s.rect(9, 4, 22, 12, (16, 40, 24))
    for y, w in ((5, 10), (7, 7), (9, 12)):
        s.rect(10, y, 10 + w - 1, y, (96, 232, 120))
    s.set(11 + 9, 11, (160, 255, 176))                   # the cursor
    s.rect(7, 17, 24, 19, STEEL[1])
    for x in range(8, 24, 2): s.set(x, 18, STEEL[3])     # keys
    s.rect(20, 23, 25, 23, (200, 64, 48)); s.set(21, 25, (96, 232, 120)); s.set(23, 25, (248, 168, 64))
    s.line(27, 22, 30, 30, (40, 40, 48)); s.line(4, 24, 1, 30, (40, 40, 48))   # cables
    return s

def pickup_truck():
    s = S()
    s.box(0, 13, 31, 25, RUST)                           # the bed and body
    s.box(13, 5, 26, 14, RUST)                           # the cab
    s.rect(15, 7, 24, 12, (120, 160, 184)); s.rect(15, 7, 18, 9, (184, 216, 232))   # the window
    s.rect(1, 14, 12, 15, RUST[0])                       # the open bed
    s.rect(27, 16, 31, 18, (232, 216, 160))              # the headlight
    s.rect(0, 22, 31, 23, STEEL[2])                      # the bumper line
    for x, y in ((4, 18), (9, 20), (20, 17), (25, 21)): s.set(x, y, (120, 96, 72))   # rust patches
    for cx in (7, 25):
        s.disc(cx, 26.5, 4, 4, [(24, 24, 32), (48, 48, 60), (72, 72, 88)])
        s.rect(cx - 1, 26, cx, 27, STEEL[2])
    s.set(14, 30, (248, 136, 200))                       # something pink, underneath
    return s

def clone_tank():
    s = S()
    s.box(7, 26, 24, 30, STEEL); s.box(7, 1, 24, 5, STEEL)        # the caps
    s.rect(9, 6, 22, 25, (88, 200, 120))                          # the fluid
    s.rect(9, 6, 10, 25, (152, 240, 176)); s.rect(21, 6, 22, 25, (56, 152, 88))
    for x, y in ((13, 22), (18, 18), (12, 12), (17, 9)): s.set(x, y, (200, 255, 216))   # bubbles
    s.disc(16, 15, 3.5, 4.5, [(48, 120, 72), (64, 160, 96), (120, 200, 140)], lit=False)   # the copy floating inside
    s.set(15, 14, (248, 96, 96))                                  # one open eye
    s.line(25, 8, 30, 8, STEEL[1]); s.line(30, 8, 30, 30, STEEL[1]); s.line(1, 20, 6, 20, STEEL[1]); s.line(1, 20, 1, 30, STEEL[1])
    s.rect(11, 28, 20, 28, (248, 168, 64))                        # the warning label
    return s

def wooden_shrine():
    s = S()
    W = [(140, 96, 56), (184, 136, 84), (220, 180, 120), (240, 212, 160)]     # fresh wood, paler than old
    s.box(8, 14, 23, 28, W)
    s.poly([(5, 15), (16, 6), (27, 15)], W[1]); s.line(5, 15, 16, 6, W[3]); s.rect(5, 15, 27, 15, W[0])
    s.rect(13, 19, 18, 27, (64, 40, 32))                  # the open front
    s.box(6, 28, 25, 30, W)
    for x, y in ((3, 8), (27, 9), (24, 3), (6, 22), (28, 21), (11, 2)):        # the leaves, swirling
        s.set(x, y, LEAF[2]); s.set(x + 1, y, LEAF[3]); s.set(x, y + 1, LEAF[1])
    s.set(15, 23, (152, 232, 120)); s.set(16, 22, (200, 255, 176))           # a small green glint inside
    return s

def candy(s, x, y):
    s.set(x, y, (152, 104, 200)); s.set(x + 1, y, WHITE); s.set(x - 1, y, (120, 80, 168)); s.set(x + 2, y, (120, 80, 168))

def reverse_shard():
    s = S()
    V = [(40, 24, 64), (72, 40, 104), (112, 72, 152), (176, 136, 224)]
    s.poly([(16, 1), (24, 10), (20, 24), (12, 22), (9, 9)], V[1])
    s.poly([(16, 3), (21, 10), (18, 21), (14, 20), (12, 10)], V[0])
    s.line(16, 1, 9, 9, V[3]); s.line(9, 9, 12, 22, V[2])
    s.set(15, 9, (232, 200, 255)); s.set(17, 14, (200, 160, 248))
    for (x, y) in ((14, 12), (18, 12), (16, 11)): s.set(x, y, (160, 120, 220))   # your reflection, with wings
    s.rect(11, 29, 21, 30, (56, 40, 72)); s.rect(13, 28, 19, 28, (56, 40, 72))   # its shadow on the ground
    for x, y in ((6, 5), (27, 16), (7, 18), (25, 4)): s.set(x, y, V[3])
    return s

def orb(col):
    def make():
        s = S()
        s.box(11, 18, 20, 27, STONE); s.box(8, 27, 23, 30, STONE); s.box(9, 15, 22, 18, STONE)
        for x in (12, 18): s.set(x, 22, RUNE); s.set(x + 1, 23, RUNE)
        light = [tuple(min(255, int(c * f)) for c in col) for f in (0.55, 0.8, 1.0, 1.25)]
        s.disc(15.5, 9, 6.5, 6.5, light)
        s.set(13, 6, WHITE); s.set(14, 5, WHITE)
        for x, y in ((6, 4), (25, 6), (8, 13), (24, 13)): s.set(x, y, light[3])   # its glow
        return s
    return make

def festival_mirror():
    s = S()
    s.box(9, 26, 22, 30, WOOD); s.box(14, 22, 17, 26, GOLD)                # the stand
    s.disc(15.5, 11.5, 9, 11.5, GOLD)                                       # the frame
    s.disc(15.5, 11.5, 6.5, 9, [(48, 40, 80), (72, 64, 112), (104, 96, 152)], lit=False)
    s.poly([(10, 12), (15, 8), (21, 12), (15, 11)], (32, 24, 48))           # a darker bird, in the glass
    s.line(11, 5, 13, 3, (200, 200, 232)); s.set(15, 1, (248, 120, 152)); s.set(9, 0, LEAF[3]); s.set(22, 1, (255, 232, 96))   # ribbons
    return s

def plate_ring():
    s = S()
    s.box(3, 26, 28, 30, STONE)
    s.disc(15.5, 13.5, 13, 13, STONE)
    s.disc(15.5, 13.5, 8, 8, [(24, 20, 40)] * 4, lit=False)
    for k in range(18):                                   # eighteen empty sockets
        a = 2 * math.pi * k / 18
        s.set(round(15.5 + 10.5 * math.cos(a)), round(13.5 + 10.5 * math.sin(a)), STONE[0])
    s.set(15, 13, GOLD[2])                                # a gold mote in the middle
    return s

def origin_altar():
    s = S()
    W = [(176, 168, 152), (216, 208, 192), (240, 236, 224), (255, 255, 248)]
    s.box(1, 26, 30, 30, W); s.rect(1, 26, 30, 26, GOLD[2])           # three white steps, gold edged
    s.box(4, 22, 27, 26, W); s.rect(4, 22, 27, 22, GOLD[2])
    for k in range(9):                                                 # eighteen grooves, nine on each step
        s.rect(3 + k * 3, 28, 4 + k * 3, 29, W[0]); s.rect(6 + k * 2 + (k > 4), 24, 6 + k * 2 + (k > 4), 25, W[0]) if k < 9 else None
    s.box(10, 9, 21, 22, W)                                            # the stone
    s.disc(15.5, 9.5, 8, 8, GOLD)                                      # the golden wheel
    s.disc(15.5, 9.5, 5, 5, [W[2]] * 4, lit=False)
    for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0)):
        s.set(round(15.5 + dx * 0.6), round(9.5 + dy * 0.6), GOLD[2])
    s.disc(15.5, 9.5, 2, 2, [(88, 200, 96), (120, 232, 128), (200, 255, 200)])
    return s

def plate_shrine():
    s = S()
    s.box(5, 26, 26, 30, STONE)
    s.box(7, 12, 24, 26, STONE)
    s.poly([(3, 13), (16, 3), (29, 13)], (176, 96, 72)); s.line(3, 13, 16, 3, (208, 132, 100)); s.rect(3, 13, 29, 13, (120, 64, 52))
    for x0 in (9, 17):                                    # the two plate hollows
        s.rect(x0, 16, x0 + 5, 23, (72, 64, 96)); s.rect(x0, 16, x0 + 5, 16, O)
    for x, y in ((8, 25), (23, 15)): s.set(x, y, MOSS[1])
    return s

ROOT = os.path.join(HERE, '..', '..', '..')

def mon(num, size):
    """An official Pokémon sprite, cropped and scaled so its longer side is `size` (only ever carved, never shown as is)."""
    im = Image.open(os.path.join(ROOT, 'sprites', 'pokemon', '%d.png' % num)).convert('RGBA')
    im = im.crop(im.getbbox())
    k = size / max(im.size)
    size = (max(1, round(im.width * k)), max(1, round(im.height * k)))
    # Shrunk smoothly, then the edge made hard again: nearest-neighbour drops the sprite's lines at this scale.
    rgb = im.convert('RGB').resize(size, Image.BOX)
    alpha = im.getchannel('A').resize(size, Image.BOX).point(lambda a: 255 if a >= 110 else 0)
    rgb.putalpha(alpha)
    return rgb

def paste(s, im, x, y, ramp=None, flip=False):
    """Draws a picture at (x, y): as it is, or carved in `ramp`: one face, lit where the shape faces the top left,
    shaded where it faces the bottom right, its own dark lines cut in."""
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    on = lambda u, v: 0 <= u < im.width and 0 <= v < im.height and im.getpixel((u, v))[3] >= 128
    for v in range(im.height):
        for u in range(im.width):
            if not on(u, v):
                continue
            r, g, b, a = im.getpixel((u, v))
            if ramp is None:
                s.set(x + u, y + v, (r, g, b))
                continue
            l = (r * 3 + g * 6 + b) // 10
            c = ramp[0] if l < 60 else ramp[1] if l < 150 else ramp[2]
            if not on(u - 1, v - 1) or not on(u, v - 1):
                c = ramp[3]
            elif not on(u + 1, v + 1) or not on(u + 1, v):
                c = ramp[1]
            s.set(x + u, y + v, c)

def person(kind):
    """A person's standing frame from the last build's export (gba/generated), if there is one."""
    import json
    p = os.path.join(HERE, '..', '..', 'generated', 'export', 'data.json')
    return json.load(open(p, encoding='utf8'))['people'][kind]['down'][0]['px'] if os.path.exists(p) else None

def cast(s, frame, x, y, R, scale=2):
    """A person cast in stone or bronze at twice their size: their frame's light and dark on ramp R."""
    for v, row in enumerate(frame):
        for u, c in enumerate(row):
            if c:
                l = (c[0] * 3 + c[1] * 6 + c[2]) // 10
                col = R[0] if sum(c) < 90 else R[min(len(R) - 1, 1 + l * (len(R) - 1) // 256)]
                s.rect(x + u * scale, y + v * scale, x + u * scale + scale - 1, y + v * scale + scale - 1, col)

def plinth(s, x0, x1, top, R=STONE, bottom=None):
    """A two-step plinth from row `top` to the ground."""
    bottom = s.h - 2 if bottom is None else bottom
    mid = top + (bottom - top) // 3
    s.box(x0 + 3, top, x1 - 3, mid, R)
    s.box(x0, mid + 1, x1, bottom, R)
    s.rect(x0 + 1, mid + 2, x1 - 1, mid + 2, R[3])

# ---------------------------------------------------------------- the town squares' centre pieces (64x64)
def wren():
    s = S(64, 64)
    plinth(s, 6, 57, 42)
    f = person('rival')
    if f:
        cast(s, f, 16, 0, STONE)
    for k in range(8):                                  # the eight GYM LEADERS carved round the base, small figures
        x = 10 + k * 6
        s.set(x + 1, 52, STONE[3]); s.rect(x, 53, x + 2, 55, STONE[1]); s.rect(x, 56, x, 57, STONE[1]); s.rect(x + 2, 56, x + 2, 57, STONE[1])
    s.rect(24, 59, 39, 60, GOLD[1]); s.rect(25, 59, 38, 59, GOLD[2])     # the name plate
    return s

def arden():
    s = S(64, 64)
    plinth(s, 6, 57, 42)
    f = person('prof')
    if f:
        cast(s, f, 16, 0, BRONZE)
    s.rect(22, 50, 41, 56, GOLD[1]); s.rect(23, 51, 40, 51, GOLD[3])       # the plaque
    for x in range(24, 39, 3): s.rect(x, 53, x + 1, 53, GOLD[0])
    for x, y in ((14, 58), (15, 59), (17, 58), (46, 59), (47, 58)): s.set(x, y, STONE[0])   # what's scratched under it
    return s

def launch_board():
    s = S(64, 64)
    s.box(2, 56, 61, 62, STONE)                                            # the pad
    for lx in (8, 32): s.box(lx, 34, lx + 3, 56, STEEL)                    # legs
    s.box(1, 2, 43, 35, STEEL)                                             # the board
    s.rect(4, 5, 40, 32, (20, 24, 36))
    s.rect(6, 7, 38, 9, (64, 112, 200)); s.rect(6, 7, 20, 9, (112, 160, 232))   # NEXT LAUNCH
    big = {'4': ['1..1', '1..1', '1111', '...1', '...1'], '3': ['111.', '...1', '.11.', '...1', '111.'],
           '2': ['111.', '...1', '.11.', '1...', '1111'], '1': ['.1..', '11..', '.1..', '.1..', '111.']}
    for k, ch in enumerate('4321'):
        for y, row in enumerate(big[ch]):
            for x, c in enumerate(row):
                if c == '1':
                    s.rect(6 + k * 8 + x * 2 // 1 - x, 13 + y * 2, 6 + k * 8 + x, 14 + y * 2, (248, 168, 64) if k == 0 else (96, 224, 120))
    s.rect(6, 27, 38, 29, (48, 56, 80)); s.rect(6, 27, 28, 29, (248, 168, 64))  # the countdown bar
    # The rocket on its own stand, nose to the sky.
    s.box(46, 50, 61, 56, STEEL)
    s.rect(50, 14, 57, 49, WHITE); s.rect(50, 14, 51, 49, (208, 214, 224)); s.rect(56, 14, 57, 49, (176, 184, 200))
    s.poly([(50, 14), (53, 4), (54, 4), (58, 14)], (200, 64, 48)); s.line(51, 13, 53, 5, (232, 104, 80))
    s.disc(53.5, 24, 2.5, 2.5, [(40, 72, 152), (64, 112, 200), (112, 160, 232)])
    s.poly([(50, 40), (46, 50), (50, 47)], (200, 64, 48)); s.poly([(58, 40), (62, 50), (58, 47)], (168, 48, 40))
    s.rect(52, 34, 55, 34, (200, 64, 48))
    return s

def three_birds():
    s = S(64, 64)
    # A round fountain: stone basin, water, LUGIA rising from it, the three birds around the rim.
    s.disc(31.5, 54, 30, 9, STONE)
    s.disc(31.5, 52, 25, 6, [(56, 120, 200), (88, 152, 224), (136, 192, 240)], lit=False)
    for x, y in ((14, 52), (26, 50), (40, 53), (50, 51)): s.rect(x, y, x + 3, y, (200, 232, 252))
    s.rect(29, 42, 34, 51, (88, 152, 224)); s.rect(30, 42, 31, 51, (136, 192, 240))   # the spout it rises on
    paste(s, mon(249, 46), 14, 2, [(84, 88, 108), (150, 156, 176), (212, 216, 228), (244, 246, 250)])   # LUGIA, pale stone
    tint = lambda c: [tuple(int(v * f) for v in c) for f in (0.45, 0.7, 0.9, 1.0)]
    for num, x, y, flip, c in ((144, 0, 36, False, (176, 204, 228)), (145, 46, 36, True, (224, 212, 156)),
                               (146, 0, 4, False, (224, 172, 148))):     # the birds, stone with a hint of each one
        paste(s, mon(num, 18), x, y, tint(c), flip)
    return s

def town_clock():
    s = S(64, 64)
    s.box(14, 52, 49, 62, [(120, 64, 52), (164, 92, 72), (200, 128, 100)])   # the brick base
    for y in (55, 58):
        for x in range(16 + (y % 2) * 2, 48, 6): s.rect(x, y, x, y + 1, (120, 64, 52))
    s.box(27, 36, 36, 52, STEEL)                                           # the column
    s.rect(29, 38, 30, 50, STEEL[3])
    s.disc(31.5, 19.5, 18, 18, [(32, 56, 64), (48, 88, 96), (72, 120, 128), (104, 152, 160)])  # the iron case
    s.disc(31.5, 19.5, 14.5, 14.5, [(220, 214, 196), (240, 236, 220), (252, 252, 244)], lit=False)
    for k in range(12):                                                    # the hours
        a = 2 * math.pi * k / 12
        x, y = round(31.5 + 12 * math.sin(a)), round(19.5 - 12 * math.cos(a))
        s.set(x, y, O)
        if k % 3 == 0: s.set(x + (1 if k == 9 else -1 if k == 3 else 0), y + (1 if k == 0 else -1 if k == 6 else 0), O)
    s.line(31, 19, 31, 10, O); s.line(31, 19, 25, 23, O); s.set(31, 19, (200, 64, 48))   # hands, going backwards
    for x, y in ((28, 1), (35, 1)): s.rect(x, y, x + 1, y + 1, GOLD[2])
    s.poly([(26, 2), (31, 0), (37, 2)], GOLD[1])
    for x, y in ((6, 10), (56, 14), (10, 30), (54, 32)): s.set(x, y, (152, 232, 255)); s.set(x + 1, y + 1, (200, 248, 255))   # time shimmering
    for x in (6, 10, 52, 57): s.set(x, 61, (184, 152, 104)); s.set(x + 1, 62, (184, 152, 104))   # paw prints in the dust
    return s

def church_clock():
    s = S(64, 64)
    WALL = [(150, 136, 120), (190, 176, 156), (220, 208, 188), (240, 232, 216)]
    ROOF = [(96, 44, 44), (140, 64, 56), (176, 92, 76)]
    s.box(4, 34, 59, 62, WALL)                                             # the nave
    s.poly([(2, 35), (14, 22), (50, 22), (62, 35)], ROOF[1]); s.line(2, 35, 14, 22, ROOF[2]); s.line(14, 22, 50, 22, ROOF[2])
    s.rect(2, 35, 61, 35, ROOF[0])
    s.box(23, 8, 40, 40, WALL)                                             # the tower
    s.poly([(21, 9), (31, 0), (32, 0), (42, 9)], ROOF[1]); s.line(21, 9, 31, 0, ROOF[2])
    s.set(31, 0, GOLD[2]); s.set(32, 0, GOLD[2])
    for cx, cy, hx, hy in ((31.5, 18.5, (0, -5), (4, 0)), (31.5, 31, (-3, 3), (0, -4))):   # two faces, two times
        s.disc(cx, cy, 5.5, 5.5, [(208, 200, 184), (236, 232, 216), (248, 248, 240)], lit=False)
        x, y = round(cx), round(cy)
        s.line(x, y, x + hx[0], y + hx[1], O); s.line(x, y, x + hy[0], y + hy[1], O); s.set(x, y, GOLD[0])
    s.poly([(26, 62), (26, 47), (31, 42), (32, 42), (37, 47), (37, 62)], WOOD[1])   # the arched door
    s.line(31, 44, 31, 61, WOOD[0]); s.set(34, 54, GOLD[2])
    for wx in (9, 47):                                                     # stained glass
        s.poly([(wx, 56), (wx, 44), (wx + 3, 41), (wx + 6, 44), (wx + 6, 56)], (64, 96, 168))
        s.rect(wx + 1, 45, wx + 2, 49, (232, 104, 104)); s.rect(wx + 4, 45, wx + 5, 49, (248, 216, 96)); s.rect(wx + 1, 51, wx + 5, 54, (96, 192, 120))
    s.box(1, 60, 62, 62, STONE)
    return s

# ---------------------------------------------------------------- the big ones elsewhere (64x64)
def emerald_carving():
    s = S(64, 64)
    s.poly([(1, 24), (58, 14), (63, 62), (3, 62)], STONE[2])               # a fallen block of the SKY PILLAR, tilted
    s.line(1, 24, 58, 14, STONE[4]); s.line(1, 24, 3, 61, STONE[3]); s.line(58, 14, 63, 62, STONE[1])
    s.poly([(58, 14), (62, 12), (63, 62)], STONE[1])
    s.rect(4, 60, 62, 62, STONE[1])
    for x0, y0, x1, y1 in ((6, 30, 12, 26), (50, 44, 56, 54), (20, 58, 26, 52)): s.line(x0, y0, x1, y1, STONE[0])   # cracks
    RED = [(96, 40, 40), (156, 72, 64), (200, 112, 96), (232, 160, 136)]
    BLUE = [(40, 56, 104), (64, 96, 160), (104, 144, 200), (160, 192, 232)]
    GREEN = [(32, 80, 56), (56, 128, 88), (96, 176, 120), (152, 216, 160)]
    paste(s, mon(384, 46), 9, 20, GREEN)                                   # RAYQUAZA coiled across the top
    paste(s, mon(383, 24), 4, 34, RED)                                     # GROUDON
    paste(s, mon(382, 24), 34, 36, BLUE, flip=True)                        # KYOGRE
    for x, y in ((8, 59), (30, 61), (44, 58), (56, 60), (60, 40)): s.set(x, y, MOSS[1]); s.set(x + 1, y, MOSS[2]); s.set(x, y - 1, MOSS[2])
    return s

def ancient_tree():
    s = S(64, 64)
    for x0, y0, x1, y1 in ((22, 52, 4, 62), (26, 56, 14, 62), (40, 52, 60, 62), (37, 56, 50, 62), (31, 58, 31, 62)):   # roots
        for k in range(3): s.line(x0, y0 - k, x1, y1 - k, WOOD[1 if k else 0])
        s.line(x0, y0 - 3, x1, y1 - 3, WOOD[2])
    s.poly([(22, 30), (42, 30), (44, 58), (20, 58)], WOOD[1])              # the trunk
    s.rect(22, 30, 26, 57, WOOD[2]); s.line(34, 34, 36, 56, WOOD[0]); s.line(28, 40, 29, 52, WOOD[0])
    s.disc(31.5, 50, 3, 4, [(48, 28, 20)] * 3, lit=False)                 # a hollow
    s.set(31, 51, (232, 160, 232)); s.set(32, 50, WHITE)                  # the plate's glint in it
    for cx, cy, rx, ry in ((32, 16, 31, 16), (12, 24, 12, 9), (52, 24, 12, 9), (32, 6, 18, 7)):   # the great crown
        s.disc(cx, cy, rx, ry, LEAF)
    for x, y in ((14, 8), (30, 4), (44, 10), (8, 20), (22, 14), (38, 18), (54, 20)):
        s.rect(x, y, x + 2, y, LEAF[3]); s.set(x + 1, y + 1, LEAF[3])
    return s

def meteor_shard():
    s = S(64, 64)
    # The crater: scorched ground in a ring, a raised rim lit on the far side.
    s.disc(31.5, 52, 31, 11, [(92, 64, 48), (124, 92, 64), (156, 120, 84), (188, 156, 112)])
    s.disc(31.5, 53, 24, 7.5, [(44, 32, 36), (64, 44, 44), (84, 60, 52)], lit=False)
    for x, y in ((10, 48), (52, 50), (20, 59), (44, 60)): s.set(x, y, (56, 40, 40))
    V = [(56, 40, 80), (88, 64, 120), (128, 96, 168), (176, 144, 216)]
    s.poly([(26, 56), (28, 12), (34, 4), (38, 56)], V[1])                   # the big shard
    s.poly([(29, 56), (30, 14), (33, 9), (34, 56)], V[2]); s.line(31, 10, 30, 55, V[3])
    s.poly([(16, 57), (18, 34), (24, 28), (27, 57)], V[1]); s.line(19, 35, 18, 56, V[2])
    s.poly([(37, 57), (41, 26), (48, 33), (50, 57)], V[0]); s.line(42, 28, 41, 56, V[2])
    for x, y in ((32, 20), (33, 34), (21, 44), (44, 42), (31, 48)):
        s.set(x, y, (120, 232, 232)); s.set(x, y + 1, (64, 176, 200))    # the glowing core
    for x, y in ((10, 30), (54, 24), (14, 16), (50, 10)): s.set(x, y, V[3])   # sparks
    return s

# ---------------------------------------------------------------- altars the guardian stands on (32x32) and graves
def altar(gem):
    def make():
        s = S()
        R = [(40, 56, 112), (64, 88, 160), (104, 136, 208), (160, 188, 236)] if gem == 'diamond' else \
            [(120, 56, 96), (176, 88, 136), (220, 136, 176), (244, 192, 216)]
        s.box(2, 24, 29, 30, R)
        s.box(5, 14, 26, 24, R)
        s.box(3, 10, 28, 14, R)                     # the top, where the guardian stands (overworld::perch)
        if gem == 'diamond':
            s.poly([(16, 15), (20, 19), (16, 23), (12, 19)], (176, 232, 255)); s.line(16, 15, 12, 19, WHITE)
        else:
            s.disc(16, 19, 3.5, 3.5, [(232, 168, 216), (248, 208, 232), (255, 240, 248)])
        for x in (8, 23): s.set(x, 27, R[3]); s.set(x, 28, R[3])
        return s
    return make

def candy(s, x, y):
    s.set(x, y, (152, 104, 200)); s.set(x + 1, y, WHITE); s.set(x - 1, y, (120, 80, 168)); s.set(x + 2, y, (120, 80, 168))

def gravestone(s, top):
    s.poly([(10, 30), (10, top + 4), (13, top), (18, top), (21, top + 4), (21, 30)], STONE[2])
    s.line(10, top + 4, 13, top, STONE[4]); s.line(13, top, 18, top, STONE[4]); s.line(10, top + 4, 10, 29, STONE[3]); s.line(21, top + 4, 21, 29, STONE[1])

def nameless_grave():
    s = S()
    gravestone(s, 16)
    for x in (13, 15, 17, 19): s.set(x, 22, STONE[0])                       # "?????????"
    s.rect(12, 26, 19, 26, STONE[1])
    for x, y in ((4, 28), (7, 30), (24, 29), (27, 27), (3, 30), (26, 30), (13, 29), (18, 30), (25, 24)):   # RARE CANDY
        candy(s, x, y)
    return s

def flower_grave():
    s = S()
    gravestone(s, 17)
    s.rect(12, 22, 19, 22, STONE[1]); s.rect(12, 25, 17, 25, STONE[1])
    s.box(8, 28, 23, 30, STONE)
    for x, c in ((4, (248, 120, 152)), (7, (255, 232, 96)), (24, (248, 120, 152)), (27, (176, 136, 248))):  # fresh flowers
        s.line(x, 30, x, 26, LEAF[1]); s.set(x - 1, 27, LEAF[2])
        s.set(x, 24, c); s.set(x - 1, 25, c); s.set(x + 1, 25, c); s.set(x, 26, c); s.set(x, 25, (255, 248, 200))
    return s

LOOKS = {
    'wren': wren, 'hooh_figurehead': hooh_figurehead, 'emerald_carving': emerald_carving, 'launch_board': launch_board,
    'meteor_shard': meteor_shard, 'arden': arden, 'lab_terminal': lab_terminal, 'pickup_truck': pickup_truck,
    'clone_tank': clone_tank, 'church_clock': church_clock, 'wooden_shrine': wooden_shrine, 'ancient_tree': ancient_tree,
    'altar_diamond': altar('diamond'), 'altar_pearl': altar('pearl'), 'town_clock': town_clock,
    'nameless_grave': nameless_grave, 'flower_grave': flower_grave, 'reverse_shard': reverse_shard,
    'three_birds': three_birds, 'orb_ice': orb((120, 200, 248)), 'orb_lightning': orb((240, 208, 48)),
    'orb_fire': orb((232, 88, 48)), 'festival_mirror': festival_mirror, 'plate_ring': plate_ring,
    'origin_altar': origin_altar, 'plate_shrine': plate_shrine,
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    ims = {}
    for name, fn in LOOKS.items():
        ims[name] = fn().outline().image()
        ims[name].save(os.path.join(OUT, name + '.png'))
    if len(sys.argv) < 2:
        sys.exit()
    # A contact sheet on meadow grass, 4x, for review.
    cols = 7
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * 40, rows * 40), (90, 172, 88, 255))
    for i, im in enumerate(ims.values()):
        sheet.alpha_composite(im, ((i % cols) * 40 + 4, (i // cols) * 40 + 4))
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(OUT, '..', 'statues_sheet.png'))
