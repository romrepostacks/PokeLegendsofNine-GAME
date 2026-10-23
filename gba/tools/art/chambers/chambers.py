# SUMMONING CHAMBERS, round 1 (hand-pixelled): one room per legendary, 15x13 tiles (240x208), same shape as today's
# chamber: you come in on the mat at the bottom middle, the legendary waits on the dais at tile (7, 3).
# python3 chambers.py OUTDIR [names...]
import sys, os, math, random
from PIL import Image

W, H = 240, 208
O = (38, 38, 56)
LX, LY = 120, 62            # the dais centre (under the legendary at tile 7, 3)

class Room:
    def __init__(s, seed):
        s.px = [[O] * W for _ in range(H)]
        s.rnd = random.Random(seed)
    def set(s, x, y, c):
        if 0 <= x < W and 0 <= y < H: s.px[int(y)][int(x)] = c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(H - 1, y1) + 1):
            for x in range(max(0, x0), min(W - 1, x1) + 1): s.px[y][x] = c
    def hl(s, x0, x1, y, c): s.rect(x0, y, x1, y, c)
    def vl(s, x, y0, y1, c): s.rect(x, y0, x, y1, c)
    def ell(s, cx, cy, rx, ry, c):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1: s.set(x, y, c)
    def ring(s, cx, cy, rx, ry, c, w=1.0):
        for y in range(int(cy - ry - 2), int(cy + ry + 3)):
            for x in range(int(cx - rx - 2), int(cx + rx + 3)):
                d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
                if abs(d - 1) * min(rx, ry) <= w / 2 + 0.3: s.set(x, y, c)
    def speck(s, x0, y0, x1, y1, c, n, on=None):
        for _ in range(n):
            x, y = s.rnd.randint(x0, x1), s.rnd.randint(y0, y1)
            if on is None or s.px[y][x] == on: s.set(x, y, c)
    def blob(s, cx, cy, r, c, edge=None, light=None):
        # a lumpy rounded shape (rock, cloud, coral) with a 1 px outline and a lit top-left
        pts = [(cx + s.rnd.uniform(-r, r) * 0.5, cy + s.rnd.uniform(-r, r) * 0.3, r * s.rnd.uniform(0.55, 0.8)) for _ in range(4)]
        inside = lambda x, y: any((x - a) ** 2 + ((y - b) * 1.3) ** 2 <= q * q for a, b, q in pts)
        cells = [(x, y) for y in range(int(cy - r * 1.4), int(cy + r * 1.4)) for x in range(int(cx - r * 1.6), int(cx + r * 1.6)) if inside(x, y)]
        for x, y in cells: s.set(x, y, c)
        if light:
            for x, y in cells:
                if not inside(x - 2, y - 2): s.set(x, y, light)
        for x, y in cells:
            if not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): s.set(x, y, edge or O)
    def save(s, path):
        im = Image.new('RGB', (W, H))
        im.putdata([c for row in s.px for c in row])
        im.save(path)

def mat(r, c1, c2):
    r.rect(112, 192, 127, 207, O); r.rect(113, 193, 126, 206, c1)
    for y in range(195, 205, 3): r.hl(115, 124, y, c2)

def dais(r, top, side, rim, glow, glow2):
    # a round dais seen from above-front, with the summoning ring on it
    r.ell(LX, LY + 6, 38, 18, O); r.ell(LX, LY + 6, 37, 17, side)
    r.ell(LX, LY, 38, 16, O); r.ell(LX, LY, 37, 15, top)
    r.ring(LX, LY, 34, 13, rim)
    r.ring(LX, LY, 26, 9, glow, 2); r.ring(LX, LY, 26, 9, glow2, 0.6)
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        r.set(LX + 30 * math.cos(a), LY + 11 * math.sin(a), glow2); r.set(LX + 30 * math.cos(a) + 1, LY + 11 * math.sin(a), glow)

def path(r, c, edge, x0=104, x1=135, y0=80, y1=191, slabs=None):
    r.rect(x0 - 1, y0, x1 + 1, y1, O); r.rect(x0, y0, x1, y1, c)
    if slabs:
        for y in range(y0 + 15, y1, 16): r.hl(x0, x1, y, slabs)
        for y in range(y0, y1, 16):
            off = 8 if (y // 16) % 2 else 0
            for x in range(x0 + off + 15, x1, 16): r.vl(x, y, y + 14, slabs)
    r.vl(x0, y0, y1, edge); r.vl(x1, y0, y1, edge)

# ---------------------------------------------------------------- the legendaries

def groudon():
    r = Room(383)
    B1, B2, B3 = (88, 72, 80), (64, 52, 64), (48, 40, 52)
    L1, L2, L3 = (255, 232, 120), (248, 144, 48), (208, 64, 40)
    r.rect(0, 0, W - 1, H - 1, B2)
    r.speck(0, 32, W - 1, H - 1, B3, 1400); r.speck(0, 32, W - 1, H - 1, B1, 600)
    # lava rivers either side, flowing down from the back wall
    for side in (-1, 1):
        for y in range(28, H):
            cx = 120 + side * (78 + 10 * math.sin(y / 17.0 + side))
            w = 16 + 4 * math.sin(y / 9.0)
            r.hl(int(cx - w - 2), int(cx + w + 2), y, L3)
            r.hl(int(cx - w), int(cx + w), y, L2)
            if y % 7 < 3: r.hl(int(cx - w / 3), int(cx + w / 3), y, L1)
    # back wall: cracked rock with three lava falls
    r.rect(0, 0, W - 1, 31, B3)
    for x in range(0, W, 12):
        h = 6 + (x * 7) % 9
        r.rect(x, 24 - h, x + 10, 31, B1); r.hl(x, x + 10, 24 - h, (120, 100, 104)); r.vl(x + 10, 24 - h, 31, B3)
    for fx in (42, 198):
        r.rect(fx - 10, 0, fx + 10, 31, L3); r.rect(fx - 8, 0, fx + 8, 31, L2)
        for y in range(0, 32, 5): r.hl(fx - 3, fx + 3, y, L1)
    r.hl(0, W - 1, 31, O)
    # basalt causeway and an obsidian dais with a magma ring
    path(r, B1, B3, slabs=B3)
    for y in range(90, 190, 16): r.speck(105, y, 134, y + 14, (120, 100, 104), 6)
    dais(r, (56, 48, 64), (36, 30, 44), (96, 84, 100), L3, L1)
    # cooled lava rocks and vents
    for x, y in ((40, 70), (196, 74), (30, 150), (206, 140), (66, 186), (172, 182)):
        r.blob(x, y, 9, B1, O, (120, 100, 104))
    for x, y in ((70, 110), (168, 120)):
        r.ell(x, y, 6, 3, O); r.ell(x, y, 5, 2, L3); r.ell(x, y, 2, 1, L1)
    mat(r, L3, L2)
    return r

def kyogre():
    r = Room(382)
    D1, D2, D3, D4 = (120, 192, 248), (56, 120, 216), (32, 72, 160), (24, 48, 112)
    S1, S2, S3 = (208, 216, 224), (152, 168, 192), (112, 128, 160)
    r.rect(0, 0, W - 1, H - 1, D3)
    for y in range(34, H, 6):
        for x in range((y * 5) % 22, W, 22):
            r.hl(x, x + 6, y, D2); r.hl(x + 2, x + 4, y - 1, D1)
    # back wall: a sea cave with a curtain waterfall
    r.rect(0, 0, W - 1, 31, D4)
    for x in range(0, W, 10):
        h = 10 + (x * 13) % 14
        r.rect(x, 0, x + 9, 31 - h, S3); r.hl(x, x + 9, 31 - h, S2)
    r.rect(96, 0, 143, 31, D2)
    for x in range(96, 144, 4): r.vl(x, 0, 31, D1 if x % 8 else S1)
    r.hl(90, 149, 31, S1)
    r.hl(0, W - 1, 31, O)
    # pale stone causeway over the water, a shell-white dais ringed with blue light
    path(r, S1, S2, slabs=S2)
    for y in range(80, 192, 4): r.set(103, y, D1); r.set(136, y, D1)
    dais(r, (232, 236, 244), S2, S3, D2, D1)
    # coral, kelp and rocks breaking the surface
    for x, y, c, l in ((34, 70, (240, 112, 128), (255, 176, 176)), (204, 84, (248, 160, 72), (255, 216, 144)), (44, 162, (240, 112, 128), (255, 176, 176))):
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.45
            for t in range(14):
                r.set(x + math.cos(a) * t, y + math.sin(a) * t, c); r.set(x + math.cos(a) * t + 1, y + math.sin(a) * t, c)
            r.set(x + math.cos(a) * 14, y + math.sin(a) * 14, l)
    for x in (190, 200, 210):
        for y in range(150, 186):
            r.set(x + 3 * math.sin(y / 5 + x), y, (64, 160, 112)); r.set(x + 1 + 3 * math.sin(y / 5 + x), y, (40, 112, 88))
    for x, y in ((70, 120), (172, 134), (22, 112)): r.blob(x, y, 7, S3, O, S2)
    for x, y in ((60, 92), (182, 108), (150, 176), (84, 180)): r.ring(x, y, 3, 3, D1)
    mat(r, D2, D1)
    return r

def rayquaza():
    r = Room(384)
    K1, K2, K3 = (168, 216, 255), (120, 184, 248), (88, 144, 224)
    C1, C2 = (248, 248, 255), (208, 220, 240)
    J1, J2, J3 = (120, 200, 152), (64, 152, 112), (40, 104, 88)
    G1, G2 = (248, 216, 96), (216, 160, 48)
    # sky in flat bands (no dithering), clouds as the floor
    for y in range(H):
        r.hl(0, W - 1, y, K1 if y < 18 else K2 if y < 70 else K3)
    for k in range(26):
        x, y = r.rnd.randint(-10, 250), r.rnd.randint(40, 200)
        r.blob(x, y, r.rnd.randint(8, 14), C2, (152, 176, 216), C1)
    # back: the tops of SKY PILLAR's broken columns against the sky
    for x, h in ((16, 26), (52, 18), (188, 22), (222, 28)):
        r.rect(x, 32 - h, x + 14, 31, J2); r.vl(x, 32 - h, 31, J1); r.vl(x + 14, 32 - h, 31, J3)
        r.hl(x - 2, x + 16, 32 - h, J1); r.hl(x - 2, x + 16, 33 - h, O)
        for y in range(36 - h, 31, 6): r.hl(x + 1, x + 13, y, J3)
    r.hl(0, W - 1, 31, (152, 176, 216))
    # a jade platform with gold edging, the dais with a green ring
    r.rect(80, 30, 159, 191, O); r.rect(81, 31, 158, 190, J2)
    for y in range(31, 191, 12):
        r.hl(81, 158, y, J3)
        for x in range(81 + (6 if (y // 12) % 2 else 0), 158, 12): r.vl(x, y, y + 11, J3)
    r.vl(81, 31, 190, G1); r.vl(158, 31, 190, G2); r.vl(82, 31, 190, J1)
    for y in range(40, 190, 18):
        r.rect(77, y, 80, y + 5, G1); r.rect(159, y, 162, y + 5, G2)
    dais(r, J1, J3, G1, (72, 232, 128), (232, 255, 200))
    # meteor shard on the platform
    for x, y in ((96, 160), (144, 168)):
        r.ell(x, y, 4, 3, O); r.ell(x, y, 3, 2, (160, 96, 200)); r.set(x - 1, y - 1, (232, 200, 255))
    mat(r, J3, G1)
    return r

def mewtwo():
    r = Room(150)
    M1, M2, M3, M4 = (200, 208, 224), (160, 168, 192), (120, 128, 152), (80, 88, 112)
    P1, P2 = (248, 176, 232), (200, 104, 200)
    G1, G2 = (152, 248, 168), (64, 184, 120)
    r.rect(0, 0, W - 1, H - 1, M2)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, M3)
        for x in range(0, W, 16):
            r.vl(x, y, y + 15, M3); r.set(x + 2, y + 2, M1); r.set(x + 13, y + 2, M1); r.set(x + 2, y + 13, M4); r.set(x + 13, y + 13, M4)
    # cracked floor and loose cables
    for sx, sy in ((30, 120), (200, 96), (60, 176)):
        x, y = sx, sy
        for _ in range(18):
            r.set(x, y, M4); x += r.rnd.choice((-1, 0, 1, 1)); y += r.rnd.choice((0, 1))
    for y in range(36, H, 1):
        r.set(22 + 6 * math.sin(y / 11), y, (56, 56, 72)); r.set(218 + 5 * math.sin(y / 9), y, (56, 56, 72))
    # back wall: machines and a row of broken tanks with green fluid
    r.rect(0, 0, W - 1, 31, M4)
    for x in range(0, W, 30):
        r.rect(x + 2, 4, x + 27, 29, M3); r.rect(x + 3, 5, x + 26, 28, M1 if (x // 30) % 2 else M2)
        for k in range(3): r.rect(x + 6 + 7 * k, 8, x + 9 + 7 * k, 10, (248, 88, 88) if (x + k) % 3 == 0 else G1)
    for tx in (50, 190):
        r.rect(tx - 12, 0, tx + 12, 40, O); r.rect(tx - 11, 0, tx + 11, 39, (88, 152, 136))
        r.rect(tx - 11, 22, tx + 11, 39, G2); r.hl(tx - 11, tx + 11, 22, G1)
        for y in range(2, 22, 4): r.set(tx - 8, y, (200, 240, 232))
        r.rect(tx - 13, 38, tx + 13, 44, M4); r.hl(tx - 13, tx + 13, 38, M3)
        for k in range(5): r.set(tx - 4 + 2 * k, 12 + (k * 5) % 9, O)       # a crack in the glass
    r.hl(0, W - 1, 31, O)
    # the containment pad with pink rings
    path(r, M3, M4, x0=108, x1=131, slabs=M4)
    dais(r, M1, M3, M4, P2, P1)
    r.ring(LX, LY, 14, 5, P2)
    for x, y in ((40, 160), (200, 160)):
        r.rect(x - 12, y - 10, x + 12, y + 8, O); r.rect(x - 11, y - 9, x + 11, y + 7, M3); r.rect(x - 9, y - 7, x + 9, y - 1, (40, 64, 72))
        r.hl(x - 7, x + 1, y - 5, G1); r.hl(x - 7, x + 5, y - 3, G2)
    mat(r, P2, P1)
    return r

def hooh():
    r = Room(250)
    W1, W2, W3 = (216, 160, 104), (184, 128, 80), (136, 88, 56)
    R1, R2, R3 = (232, 88, 64), (192, 56, 48), (136, 40, 40)
    G1, G2, G3 = (255, 232, 128), (240, 184, 64), (184, 120, 40)
    r.rect(0, 0, W - 1, H - 1, W2)
    for y in range(32, H, 8):
        r.hl(0, W - 1, y, W3)
        for x in range((y // 8) * 37 % 48, W, 48): r.vl(x, y, y + 7, W3)
        r.hl(0, W - 1, y + 1, W1)
    # back wall: red lacquered beams, the great bell in the middle
    r.rect(0, 0, W - 1, 31, R2)
    for x in range(0, W, 24): r.rect(x, 0, x + 4, 31, R3); r.vl(x + 1, 0, 31, R1)
    r.rect(0, 0, W - 1, 4, R3); r.hl(0, W - 1, 4, G2)
    r.ell(120, 8, 18, 14, O); r.ell(120, 8, 17, 13, G2); r.rect(102, 8, 138, 24, O); r.rect(103, 8, 137, 23, G2)
    r.rect(103, 8, 108, 23, G1); r.rect(132, 8, 137, 23, G3); r.hl(100, 140, 24, O); r.hl(101, 139, 23, G3)
    r.hl(0, W - 1, 31, O)
    # rainbow-ringed golden dais, a red carpet up to it
    path(r, R2, R3, x0=110, x1=129)
    r.vl(112, 80, 191, G2); r.vl(127, 80, 191, G2)
    dais(r, G2, G3, G1, (248, 96, 72), (255, 248, 200))
    for k, c in enumerate(((248, 88, 88), (248, 176, 72), (248, 232, 96), (120, 216, 104), (88, 160, 240), (168, 112, 224))):
        r.ring(LX, LY, 20 - k * 1.5, 7 - k * 0.5, c)
    # lanterns and fallen autumn leaves
    for x in (34, 206):
        for y in (70, 150):
            r.vl(x, y - 14, y - 9, O); r.ell(x, y, 7, 6, O); r.ell(x, y, 6, 5, R1); r.ell(x - 2, y - 2, 2, 2, G1); r.hl(x - 5, x + 5, y + 5, O)
    for _ in range(60):
        x, y = r.rnd.randint(4, 235), r.rnd.randint(36, 200)
        if 100 < x < 140: continue
        c = r.rnd.choice(((232, 88, 64), (240, 152, 48), (248, 200, 72)))
        r.set(x, y, c); r.set(x + 1, y, c); r.set(x, y + 1, (136, 40, 40))
    mat(r, R2, G2)
    return r

def darkrai():
    r = Room(491)
    V1, V2, V3 = (40, 36, 72), (28, 24, 52), (18, 16, 36)
    S1, S2, S3 = (104, 96, 136), (72, 64, 104), (48, 44, 80)
    E1, E2 = (248, 72, 88), (160, 32, 64)
    r.rect(0, 0, W - 1, H - 1, V2)
    for _ in range(120):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(0, 207)
        r.set(x, y, V1 if r.rnd.random() < 0.7 else S1)
    # swirls of dark fog
    for cx, cy, rad in ((50, 110, 30), (190, 130, 34), (80, 180, 22), (170, 60, 20)):
        for t in range(0, 400):
            a = t / 30.0; rr = rad * t / 400
            r.set(cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.5, V1)
    # back wall: nothing but a crescent moon and watching eyes
    r.rect(0, 0, W - 1, 31, V3)
    r.ell(186, 14, 11, 11, (232, 232, 248)); r.ell(192, 11, 10, 10, V3)
    for x, y in ((28, 14), (70, 20), (150, 10), (218, 24)):
        r.hl(x, x + 3, y, E2); r.hl(x + 1, x + 2, y, E1); r.hl(x + 8, x + 11, y, E2); r.hl(x + 9, x + 10, y, E1)
    r.hl(0, W - 1, 31, S3)
    # floating stepping stones to a cracked dark dais
    for k, y in enumerate(range(176, 84, -18)):
        x = 120 + (6 if k % 2 else -6)
        r.ell(x, y + 3, 14, 6, O); r.ell(x, y + 3, 13, 5, S3)
        r.ell(x, y, 14, 6, O); r.ell(x, y, 13, 5, S2); r.hl(x - 8, x + 2, y - 3, S1)
    dais(r, S2, S3, S1, E2, E1)
    for k in range(7):
        a = k * 0.9
        r.set(LX + 20 * math.cos(a), LY + 7 * math.sin(a), V3); r.set(LX + 21 * math.cos(a), LY + 7 * math.sin(a), V3)
    mat(r, S3, E2)
    return r

ROOMS = dict(groudon=groudon, kyogre=kyogre, rayquaza=rayquaza, mewtwo=mewtwo, **{'ho-oh': hooh}, darkrai=darkrai)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber_%s.png' % name))
