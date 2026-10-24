"""The landmarks (9.4.1): every statue, clock, altar, grave, orb and shrine a region's data places as kind 'statue'
gets its own 32x32 look, hand pixelled in the overworld's style (flat colours, light from the top left, the shared
#262638 outline). Each stands on two tiles side by side; the top half rises into the row above.
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
    def __init__(s):
        s.px = [[None] * 32 for _ in range(32)]
    def set(s, x, y, c):
        if 0 <= x < 32 and 0 <= y < 32 and c: s.px[y][x] = c
    def get(s, x, y):
        return s.px[y][x] if 0 <= x < 32 and 0 <= y < 32 else None
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
        add = [(x, y) for y in range(32) for x in range(32) if s.px[y][x] is None and any(
            s.get(x + dx, y + dy) not in (None, O) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in add: s.px[y][x] = O
        return s
    def image(s):
        im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        for y in range(32):
            for x in range(32):
                if s.px[y][x]: im.putpixel((x, y), s.px[y][x] + (255,))
        return im

def plinth(s, x0, x1, top, R=STONE):
    """A two-step stone plinth from row `top` to the ground (row 30)."""
    s.box(x0 + 2, top, x1 - 2, top + 4, R)
    s.box(x0, top + 5, x1, 30, R)
    s.rect(x0 + 1, top + 6, x1 - 1, top + 6, R[3])

def figure(s, cx, top, R, coat=False):
    """A person carved or cast: head, shoulders, arms at the sides, legs, lit from the top left."""
    s.disc(cx, top + 3, 3, 3.2, R)
    s.rect(cx - 1, top + 6, cx + 1, top + 6, R[1])                     # neck
    s.poly([(cx - 5, top + 8), (cx + 5, top + 8), (cx + 4, top + 16), (cx - 4, top + 16)], R[2])   # body
    s.rect(cx - 5, top + 7, cx + 5, top + 7, R[3])                     # shoulders catch the light
    s.rect(cx - 6, top + 8, cx - 6, top + 14, R[3]); s.rect(cx + 6, top + 8, cx + 6, top + 14, R[1])  # arms
    if coat:
        s.poly([(cx - 5, top + 15), (cx + 5, top + 15), (cx + 6, top + 20), (cx - 6, top + 20)], R[2])
        s.line(cx, top + 9, cx, top + 20, R[1])
    s.rect(cx - 3, top + 17, cx - 1, top + 21, R[2]); s.rect(cx + 1, top + 17, cx + 3, top + 21, R[1])  # legs
    s.rect(cx + 1, top + 8, cx + 4, top + 16, R[1]) if not coat else None   # the shaded side

def stone_figure(s, people_frame):
    """WREN: the rival's standing frame (16x21, from the game's people), turned to stone, on the plinth."""
    for y, row in enumerate(people_frame):
        for x, c in enumerate(row):
            if c:
                l = (c[0] * 3 + c[1] * 6 + c[2]) // 10
                s.set(8 + x, 1 + y, STONE[min(4, 1 + l * 4 // 256)] if sum(c) > 90 else STONE[0])

# ---------------------------------------------------------------- the looks
def wren(rival=None):
    s = S()
    plinth(s, 3, 28, 21)
    if rival:
        stone_figure(s, rival)
    else:
        figure(s, 16, 0, STONE)
    for k in range(8):                                  # the eight GYM LEADERS carved round the base
        x = 6 + k * 3
        s.set(x, 28, STONE[1]); s.set(x, 27, STONE[1]); s.set(x, 26, STONE[3])
    return s

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

def emerald_carving():
    s = S()
    s.poly([(1, 14), (29, 10), (31, 30), (2, 30)], STONE[2])                # a fallen block, tilted
    s.line(1, 14, 29, 10, STONE[4]); s.line(1, 14, 2, 30, STONE[3]); s.line(29, 10, 31, 30, STONE[1])
    s.rect(3, 29, 30, 30, STONE[1])
    for x, y in ((6, 27), (20, 28), (27, 25)): s.set(x, y, MOSS[1]); s.set(x + 1, y, MOSS[2])
    s.disc(8, 21, 4, 4, [(152, 48, 40), (200, 72, 56), (232, 112, 80)])     # GROUDON's sign
    s.disc(24, 20, 4, 4, [(40, 72, 152), (64, 112, 200), (112, 160, 232)])  # KYOGRE's
    for i in range(13):                                                     # RAYQUAZA between, coiling
        x = 10 + i; y = 17 + round(2.4 * math.sin(i / 2.0))
        s.set(x, y, (48, 160, 96)); s.set(x, y + 1, (32, 112, 72))
    s.set(23, 15, GOLD[2])
    return s

def launch_board():
    s = S()
    for lx in (5, 24): s.box(lx, 20, lx + 2, 30, STEEL)
    s.box(1, 3, 30, 21, STEEL)
    s.rect(3, 5, 28, 19, (24, 28, 40))                  # the screen
    for x, y in ((6, 8), (6, 9)): pass
    digits = {'4': ['1.1', '1.1', '111', '..1', '..1'], '3': ['111', '..1', '.11', '..1', '111'],
              '2': ['111', '..1', '111', '1..', '111'], '1': ['.1.', '11.', '.1.', '.1.', '111']}
    for k, ch in enumerate('4321'):
        for y, row in enumerate(digits[ch]):
            for x, c in enumerate(row):
                if c == '1': s.set(5 + k * 4 + x, 7 + y, (248, 168, 64) if k == 0 else (96, 224, 120))
    # a little rocket, going up
    s.rect(24, 8, 25, 13, WHITE); s.set(24, 7, WHITE); s.set(25, 7, (200, 64, 48))
    s.set(23, 13, (200, 64, 48)); s.set(26, 13, (200, 64, 48)); s.set(24, 14, (248, 168, 64)); s.set(25, 15, (248, 216, 96))
    s.rect(5, 15, 21, 16, (64, 112, 200)); s.rect(5, 15, 15, 16, (112, 160, 232))  # the countdown bar
    return s

def meteor_shard():
    s = S()
    V = [(56, 40, 80), (88, 64, 120), (128, 96, 168), (176, 144, 216)]
    s.poly([(12, 30), (14, 6), (19, 2), (21, 30)], V[1])                     # the big shard
    s.poly([(14, 30), (15, 7), (17, 5), (17, 30)], V[2])
    s.line(15, 6, 15, 29, V[3])
    s.poly([(5, 30), (6, 18), (10, 15), (12, 30)], V[1]); s.line(7, 18, 7, 29, V[2])
    s.poly([(21, 30), (23, 14), (27, 18), (28, 30)], V[0]); s.line(23, 15, 23, 29, V[2])
    for x, y in ((16, 12), (17, 18), (8, 22), (24, 21), (16, 24)):
        s.set(x, y, (120, 232, 232)); s.set(x, y + 1, (64, 176, 200))       # the glowing core
    s.rect(3, 30, 29, 30, STONE[1])                                         # the scorched ground it stands in
    return s

def arden():
    s = S()
    plinth(s, 4, 27, 21)
    figure(s, 16, 0, BRONZE, coat=True)
    s.rect(11, 25, 20, 28, GOLD[1]); s.rect(12, 26, 19, 26, GOLD[3]); s.rect(12, 27, 17, 27, GOLD[0])   # the plaque
    s.set(9, 29, STONE[0]); s.set(10, 30, STONE[0]); s.set(22, 29, STONE[0])                          # the scratches
    s.set(13, 3, O); s.set(18, 3, O)                     # spectacles glint
    s.rect(13, 2, 18, 2, BRONZE[0])
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

def church_clock():
    s = S()
    s.box(2, 25, 29, 30, STONE)                           # the steps
    s.box(9, 8, 22, 25, STONE)                            # the tower, front
    s.poly([(22, 9), (27, 12), (27, 26), (22, 26)], STONE[1])   # its side, in shade
    s.poly([(8, 9), (15, 0), (23, 9)], (160, 72, 64)); s.line(8, 9, 15, 0, (200, 104, 88))
    s.poly([(23, 9), (15, 0), (28, 12)], (120, 52, 48))
    s.disc(15.5, 14.5, 4.5, 4.5, [(208, 200, 184), (236, 232, 216), (248, 248, 240)], lit=False)   # the front face
    s.set(15, 14, O); s.line(15, 14, 15, 11, O); s.line(15, 14, 17, 14, O)
    s.disc(24.5, 16, 1.6, 3.5, [(176, 168, 152), (208, 200, 184)], lit=False)                       # the side face
    s.set(24, 15, O); s.set(25, 17, O)
    s.box(13, 20, 18, 25, WOOD)                           # the door
    s.set(15, 4, GOLD[2]); s.set(16, 4, GOLD[1])          # a bell
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

def ancient_tree():
    s = S()
    s.disc(16, 9, 15, 9, LEAF)                            # the crown
    for x, y in ((8, 5), (20, 4), (13, 10), (24, 11), (5, 12)): s.set(x, y, LEAF[3]); s.set(x + 1, y, LEAF[3])
    s.poly([(11, 16), (21, 16), (22, 27), (10, 27)], WOOD[1])                 # the trunk
    s.rect(11, 16, 13, 27, WOOD[2]); s.line(17, 18, 18, 26, WOOD[0])
    for pts in (((10, 25), (3, 30)), ((12, 27), (8, 30)), ((21, 25), (29, 30)), ((19, 27), (23, 30))):   # roots
        s.line(*pts[0], *pts[1], WOOD[1]); s.line(pts[0][0], pts[0][1] - 1, pts[1][0], pts[1][1] - 1, WOOD[2])
    s.set(16, 29, (232, 160, 232)); s.set(15, 29, WHITE)  # the plate's glint in its roots
    return s

def altar(gem):
    def make():
        s = S()
        R = [(40, 56, 112), (64, 88, 160), (104, 136, 208), (160, 188, 236)] if gem == 'diamond' else \
            [(120, 56, 96), (176, 88, 136), (220, 136, 176), (244, 192, 216)]
        s.box(3, 22, 28, 30, R)
        s.box(6, 8, 25, 22, R)
        s.box(4, 5, 27, 9, R)
        if gem == 'diamond':
            s.poly([(16, 11), (21, 16), (16, 21), (11, 16)], (176, 232, 255)); s.line(16, 11, 11, 16, WHITE)
        else:
            s.disc(16, 16, 4.5, 4.5, [(232, 168, 216), (248, 208, 232), (255, 240, 248)])
        for x in (9, 23): s.set(x, 26, R[3]); s.set(x, 27, R[3])
        return s
    return make

def town_clock():
    s = S()
    s.box(8, 24, 23, 30, [(120, 64, 52), (164, 92, 72), (200, 128, 100)])   # the brick base
    for x in range(10, 22, 4): s.set(x, 27, (120, 64, 52))
    s.box(14, 13, 17, 24, STEEL)                          # the post
    s.disc(15.5, 7.5, 7, 7, [(32, 56, 64), (48, 88, 96), (72, 120, 128)])  # the iron case
    s.disc(15.5, 7.5, 5, 5, [(220, 214, 196), (240, 236, 220), (252, 252, 244)], lit=False)
    s.set(15, 7, O); s.line(15, 7, 15, 4, O); s.line(15, 7, 13, 9, O)     # hands, running backwards
    s.set(9, 3, (152, 232, 255)); s.set(22, 12, (152, 232, 255))          # a shimmer of time
    for x in (5, 26): s.set(x, 29, (184, 152, 104)); s.set(x, 30, (184, 152, 104))   # paw prints in the dust
    return s

def candy(s, x, y):
    s.set(x, y, (152, 104, 200)); s.set(x + 1, y, WHITE); s.set(x - 1, y, (120, 80, 168)); s.set(x + 2, y, (120, 80, 168))

def nameless_grave():
    s = S()
    s.poly([(9, 30), (9, 8), (12, 4), (19, 4), (22, 8), (22, 30)], STONE[2])
    s.line(9, 8, 12, 4, STONE[4]); s.line(12, 4, 19, 4, STONE[4]); s.line(9, 8, 9, 29, STONE[3]); s.line(22, 8, 22, 29, STONE[1])
    q = ['.111.', '1...1', '...1.', '..1..', '.....', '..1..']                 # "?????????"
    for y, row in enumerate(q):
        for x, c in enumerate(row):
            if c == '1': s.set(14 + x, 9 + y, STONE[0])
    s.rect(11, 18, 20, 18, STONE[1])
    for x, y in ((4, 28), (7, 30), (24, 29), (27, 27), (3, 30), (26, 30), (13, 29), (18, 30), (25, 24)):   # RARE CANDY
        candy(s, x, y)
    return s

def flower_grave():
    s = S()
    s.poly([(10, 28), (10, 10), (13, 6), (18, 6), (21, 10), (21, 28)], STONE[2])
    s.line(10, 10, 13, 6, STONE[4]); s.line(13, 6, 18, 6, STONE[4]); s.line(10, 10, 10, 27, STONE[3]); s.line(21, 10, 21, 27, STONE[1])
    s.rect(12, 13, 19, 13, STONE[1]); s.rect(12, 16, 17, 16, STONE[1]); s.rect(12, 19, 18, 19, STONE[1])
    s.box(8, 27, 23, 30, STONE)
    for x, c in ((4, (248, 120, 152)), (7, (255, 232, 96)), (24, (248, 120, 152)), (27, (176, 136, 248))):  # fresh flowers
        s.line(x, 30, x, 26, LEAF[1]); s.set(x - 1, 27, LEAF[2])
        s.set(x, 24, c); s.set(x - 1, 25, c); s.set(x + 1, 25, c); s.set(x, 26, c); s.set(x, 25, (255, 248, 200))
    return s

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

def three_birds():
    s = S()
    plinth(s, 2, 29, 23)
    for x in range(4, 28):                                # stone waves
        s.set(x, 22 - (1 if (x // 3) % 2 else 0), STONE[3])
    s.disc(16, 13, 4, 7, STONE)                           # LUGIA rising in the middle
    s.poly([(12, 9), (3, 3), (6, 12)], STONE[3]); s.poly([(20, 9), (29, 3), (26, 12)], STONE[2])
    s.disc(16, 5, 2.5, 2.5, STONE); s.set(17, 5, (88, 120, 200))
    for cx, cy, eye in ((5, 15, (120, 200, 248)), (16, 20, (248, 216, 64)), (27, 15, (248, 104, 64))):   # the three birds
        s.line(cx - 3, cy - 2, cx, cy, STONE[3]); s.line(cx + 3, cy - 2, cx, cy, STONE[2])   # wings up
        s.line(cx - 4, cy - 3, cx - 3, cy - 3, STONE[3]); s.line(cx + 3, cy - 3, cx + 4, cy - 3, STONE[2])
        s.rect(cx, cy, cx, cy + 2, STONE[2]); s.set(cx, cy - 1, eye)
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

def rival_frame():
    """The rival's standing frame from the last build's export (gba/generated), if there is one."""
    import json
    p = os.path.join(HERE, '..', '..', 'generated', 'export', 'data.json')
    return json.load(open(p, encoding='utf8'))['people']['rival']['down'][0]['px'] if os.path.exists(p) else None

LOOKS = {
    'wren': lambda: wren(rival_frame()), 'hooh_figurehead': hooh_figurehead, 'emerald_carving': emerald_carving, 'launch_board': launch_board,
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
