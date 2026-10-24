# SUMMONING CHAMBERS, round 2: Kyogre and Rayquaza redrawn after Kyle's notes, and six more legendaries.
# python3 chambers2.py OUTDIR [names...]
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path

def kyogre():
    """Kyogre sits IN the water: the dais is a deep round pool in a ring of rune stones, open sea all round."""
    r = Room(382)
    D1, D2, D3, D4, D5 = (120, 192, 248), (56, 120, 216), (32, 72, 160), (24, 48, 112), (16, 32, 80)
    S1, S2, S3 = (208, 216, 224), (152, 168, 192), (112, 128, 160)
    r.rect(0, 0, W - 1, H - 1, D3)
    for y in range(34, H, 6):
        for x in range((y * 5) % 22, W, 22):
            r.hl(x, x + 6, y, D2); r.hl(x + 2, x + 4, y - 1, D1)
    # sea-cave mouth: rock arch, open water beyond it, light coming in
    r.rect(0, 0, W - 1, 31, S3)
    for x in range(0, W, 10):
        h = 6 + (x * 13) % 12
        r.rect(x, 0, x + 9, h, (88, 100, 132)); r.hl(x, x + 9, h, S2)
    for x in range(0, W, 6):                                                    # wet rock base meeting the sea
        r.vl(x, 24 + (x * 7) % 5, 31, (88, 100, 132)); r.set(x, 23 + (x * 7) % 5, S2)
    r.hl(0, W - 1, 31, D1)
    # the pool: a ring of standing rune stones round deep, dark water
    r.ell(LX, LY + 4, 62, 24, O); r.ell(LX, LY + 4, 61, 23, S2)
    r.ell(LX, LY + 1, 61, 22, S1)
    r.ell(LX, LY + 2, 53, 17, O); r.ell(LX, LY + 2, 52, 16, D5)
    r.ring(LX, LY + 2, 44, 12, D4, 2)
    r.front = []
    for k in range(10):
        a = k * math.pi / 5 + 0.15
        x, y = LX + 57 * math.cos(a), LY + 2 + 20 * math.sin(a)
        if math.sin(a) > 0: r.front.append((int(x) - 3, int(y) - 9, int(x) + 3, int(y) + 2))
        r.rect(int(x) - 3, int(y) - 9, int(x) + 3, int(y) + 2, O); r.rect(int(x) - 2, int(y) - 8, int(x) + 2, int(y) + 1, S2)
        r.vl(int(x) - 2, int(y) - 8, int(y) + 1, S1); r.rect(int(x) - 1, int(y) - 5, int(x), int(y) - 3, D1)
    # causeway up to the pool's edge
    path(r, S1, S2, x0=108, x1=131, y0=84, slabs=S2)
    for y in range(84, 192, 4): r.set(107, y, D1); r.set(132, y, D1)
    # coral, kelp, rocks
    for x, y, c, l in ((34, 80, (240, 112, 128), (255, 176, 176)), (204, 96, (248, 160, 72), (255, 216, 144)), (44, 168, (240, 112, 128), (255, 176, 176))):
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.45
            for t in range(14):
                r.set(x + math.cos(a) * t, y + math.sin(a) * t, c); r.set(x + math.cos(a) * t + 1, y + math.sin(a) * t, c)
            r.set(x + math.cos(a) * 14, y + math.sin(a) * 14, l)
    for x in (190, 200, 210):
        for y in range(150, 186):
            r.set(x + 3 * math.sin(y / 5 + x), y, (64, 160, 112)); r.set(x + 1 + 3 * math.sin(y / 5 + x), y, (40, 112, 88))
    for x, y in ((70, 128), (172, 140), (22, 118)): r.blob(x, y, 7, S3, O, S2)
    mat(r, D2, D1)
    return r

def rayquaza():
    """Open air on the tower's crown: a round marble roof with a gold rim and broken parapet, sky on every side."""
    r = Room(384)
    K = [(168, 216, 255), (144, 200, 252), (120, 184, 248)]
    C1, C2, C3 = (248, 248, 255), (216, 228, 244), (176, 192, 224)
    M1, M2, M3 = (240, 236, 248), (208, 204, 224), (160, 152, 184)
    G1, G2, G3 = (248, 216, 96), (216, 160, 48), (152, 104, 32)
    for y in range(H):
        r.hl(0, W - 1, y, K[0] if y < 60 else K[1] if y < 130 else K[2])
    # the cloud sea far below, and wind streaks
    for k in range(18):
        x, y = r.rnd.randint(-20, 260), r.rnd.randint(120, 215)
        r.blob(x, y, r.rnd.randint(10, 18), C2, C3, C1)
    for k in range(9):
        x, y = r.rnd.randint(0, 200), r.rnd.randint(4, 110)
        r.hl(x, x + r.rnd.randint(14, 30), y, C1)
    for x, y in ((24, 30), (210, 18), (196, 58)): r.blob(x, y, 9, C2, C3, C1)
    # the crown: a round marble roof seen from above
    cx, cy, rx, ry = 120, 104, 92, 96
    r.ell(cx, cy + 6, rx + 2, ry + 2, O); r.ell(cx, cy + 6, rx + 1, ry + 1, M3)      # the drum's side
    r.ell(cx, cy, rx + 2, ry, O); r.ell(cx, cy, rx + 1, ry - 1, G2); r.ell(cx, cy, rx - 2, ry - 4, G1)
    r.ell(cx, cy, rx - 5, ry - 7, O); r.ell(cx, cy, rx - 6, ry - 8, M1)
    for k in range(1, 4): r.ring(cx, cy, (rx - 6) * k / 4, (ry - 8) * k / 4, M2)
    for k in range(16):
        a = k * math.pi / 8
        for t in range(18, 86, 2): r.set(cx + t * math.cos(a), cy + t * math.sin(a) * (ry - 8) / (rx - 6), M2)
    # broken parapet: stone merlons round the rim, some fallen
    for k in range(28):
        a = k * 2 * math.pi / 28
        if k in (7, 8, 19, 23): continue          # fallen
        x, y = cx + (rx - 1) * math.cos(a), cy + (ry - 2) * math.sin(a)
        if y > 170 and abs(x - 120) < 24: continue  # the stairs
        r.rect(int(x) - 3, int(y) - 6, int(x) + 3, int(y) + 1, O); r.rect(int(x) - 2, int(y) - 5, int(x) + 2, int(y), M1)
        r.hl(int(x) - 2, int(x) + 2, int(y), M3)
    for x, y in ((40, 70), (176, 150)): r.blob(x, y, 4, M2, O, M1)
    # the dais with the crystal's ring of light, and the stair hatch you came up
    dais(r, M1, M3, G1, (72, 232, 128), (232, 255, 200))
    r.ring(LX, LY, 46, 17, (200, 176, 248)); r.ring(LX, LY, 48, 18, (152, 112, 224))
    r.rect(104, 186, 135, 207, O); r.rect(105, 187, 134, 207, M3)
    for y in range(189, 208, 4): r.hl(105, 134, y, M2); r.hl(105, 134, y + 1, (112, 104, 136))
    # clouds drifting across the near edge
    for x, y in ((-6, 186), (238, 176), (16, 120)): r.blob(x, y, 14, C2, C3, C1)
    return r

def lugia():
    """A storm grotto under the islands: dark sea, a whirlpool round the dais, spray from the falls."""
    r = Room(249)
    D1, D2, D3, D4 = (104, 176, 200), (48, 112, 152), (32, 72, 112), (20, 44, 72)
    R1, R2, R3 = (120, 128, 144), (88, 92, 112), (60, 64, 84)
    F = (232, 244, 255)
    r.rect(0, 0, W - 1, H - 1, D3)
    for y in range(34, H, 7):
        for x in range((y * 3) % 26, W, 26): r.hl(x, x + 8, y, D2)
    r.rect(0, 0, W - 1, 31, R3)
    for x in range(0, W, 14):
        r.blob(x, 10 + (x * 7) % 12, 9, R2, O, R1)
    for fx in (30, 210):
        r.rect(fx - 8, 0, fx + 8, 40, D1)
        for x in range(fx - 8, fx + 9, 3): r.vl(x, 0, 40, F)
        r.ell(fx, 42, 16, 6, F); r.ell(fx, 42, 12, 4, D1)
    r.hl(0, W - 1, 31, O)
    # whirlpool
    for t in range(0, 900):
        a = t / 40.0; rr = 8 + 60 * t / 900
        r.set(LX + rr * math.cos(a), LY + 4 + rr * math.sin(a) * 0.45, D1 if t % 3 else F)
    # rock causeway of stepping slabs
    for k, y in enumerate(range(180, 86, -16)):
        x = 120 + (5 if k % 2 else -5)
        r.ell(x, y + 2, 14, 7, O); r.ell(x, y + 2, 13, 6, R3); r.ell(x, y, 13, 6, R2); r.hl(x - 8, x + 3, y - 3, R1)
    dais(r, R1, R3, (176, 184, 200), (88, 160, 240), F)
    for x, y in ((40, 100), (200, 120), (60, 172), (184, 176)): r.blob(x, y, 10, R2, O, R1)
    for _ in range(40):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(34, 207)
        r.set(x, y, F)
    mat(r, D2, D1)
    return r

def dialga():
    """Temple of time: steel-blue flagstones, a great clock on the back wall, gears set in the floor."""
    r = Room(483)
    B1, B2, B3, B4 = (176, 200, 232), (128, 160, 208), (88, 112, 168), (56, 72, 120)
    S1, S2 = (208, 216, 232), (152, 160, 184)
    T1, T2 = (120, 240, 232), (48, 176, 200)
    r.rect(0, 0, W - 1, H - 1, B3)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, B4)
        for x in range((8 if (y // 16) % 2 else 0), W, 16): r.vl(x, y, y + 15, B4); r.hl(x + 1, x + 14, y + 1, B2)
    r.rect(0, 0, W - 1, 31, B4)
    for x in range(0, W, 20): r.rect(x + 2, 0, x + 6, 31, B3); r.vl(x + 2, 0, 31, B2)
    # the clock face
    r.ell(120, 14, 30, 22, O); r.ell(120, 14, 29, 21, S1); r.ell(120, 14, 24, 17, (232, 236, 248))
    for k in range(12):
        a = k * math.pi / 6
        r.set(120 + 21 * math.cos(a), 14 + 15 * math.sin(a), B4); r.set(120 + 20 * math.cos(a), 14 + 14 * math.sin(a), B4)
    for t in range(14): r.set(120 + t * 0.2, 14 - t * 0.8, O)
    for t in range(18): r.set(120 + t * 0.9, 14 + t * 0.15, O)
    r.hl(0, W - 1, 31, O)
    # gears in the floor
    def gear(cx, cy, rad, c, d):
        r.ell(cx, cy, rad + 3, (rad + 3) * 0.5, O)
        for k in range(10):
            a = k * math.pi / 5
            r.ell(cx + (rad + 2) * math.cos(a), cy + (rad + 2) * 0.5 * math.sin(a), 2.5, 1.5, c)
        r.ell(cx, cy, rad, rad * 0.5, c); r.ring(cx, cy, rad * 0.6, rad * 0.3, d); r.ell(cx, cy, 3, 1.5, d)
    for x, y, rad in ((44, 90, 18), (196, 100, 14), (54, 170, 12), (190, 168, 20)): gear(x, y, rad, S2, B4)
    for x in (16, 224):
        for y in (60, 140):
            r.rect(x - 7, y - 26, x + 7, y + 8, O); r.rect(x - 6, y - 25, x + 6, y + 7, S1); r.vl(x + 6, y - 25, y + 7, S2)
            r.rect(x - 8, y - 28, x + 8, y - 24, B2)
    path(r, B2, B4, slabs=B3)
    dais(r, S1, S2, B2, T2, T1)
    mat(r, B4, T2)
    return r

def palkia():
    """Torn space: pearly flagstones split by cracks full of stars, fragments of floor drifting off."""
    r = Room(484)
    P1, P2, P3, P4 = (252, 232, 244), (232, 196, 220), (200, 152, 192), (144, 104, 152)
    V = (32, 24, 56); ST = (248, 248, 255)
    r.rect(0, 0, W - 1, H - 1, P2)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, P3)
        for x in range(0, W, 16): r.vl(x, y, y + 15, P3); r.hl(x + 1, x + 14, y + 1, P1)
    # rifts of open space
    for sx, sy, ln in ((20, 60, 40), (160, 120, 56), (40, 140, 50), (200, 40, 30)):
        x, y = sx, sy
        for t in range(ln):
            w = 1 + int(5 * math.sin(math.pi * t / ln))
            r.hl(int(x) - w - 2, int(x) + w + 2, int(y), (200, 120, 232)); r.hl(int(x) - w - 1, int(x) + w + 1, int(y), O); r.hl(int(x) - w, int(x) + w, int(y), V)
            if t % 5 == 2: r.set(x, y, ST)
            x += r.rnd.choice((-1, 0, 1)); y += 1
    r.rect(0, 0, W - 1, 31, V)
    for _ in range(50): r.set(r.rnd.randint(0, 239), r.rnd.randint(0, 30), ST)
    for x in range(0, W, 30):
        r.rect(x + 8, 10, x + 20, 31, P3); r.vl(x + 8, 10, 31, P1); r.hl(x + 6, x + 22, 10, P1)   # broken pillars
    r.hl(0, W - 1, 31, O)
    for x, y in ((24, 182), (214, 186), (210, 80)):                  # drifting fragments
        r.rect(x - 9, y - 5, x + 9, y + 5, O); r.rect(x - 8, y - 4, x + 8, y + 4, P1); r.hl(x - 8, x + 8, y + 4, P3)
    path(r, P1, P3, slabs=P2)
    dais(r, P1, P4, P3, (232, 96, 176), (255, 216, 248))
    mat(r, P4, (232, 96, 176))
    return r

def giratina():
    """The Distortion World: a grey-violet void, islands hanging upside down, a crooked path."""
    r = Room(487)
    V1, V2, V3 = (64, 60, 84), (44, 40, 64), (30, 28, 46)
    L1, L2, L3 = (136, 144, 120), (96, 104, 88), (64, 72, 64)
    R1, G1 = (216, 64, 64), (232, 192, 72)
    r.rect(0, 0, W - 1, H - 1, V2)
    for y in range(0, H, 9):
        for x in range((y * 7) % 30, W, 30): r.hl(x, x + 10, y, V1)
    # upside-down islands across the back, trees hanging
    for x, y, w in ((30, 4, 26), (120, 8, 34), (206, 2, 24)):
        r.ell(x, y, w, 7, O); r.ell(x, y, w - 1, 6, L2); r.hl(x - w + 2, x + w - 2, y - 2, L1)
        for k in range(-w + 8, w - 6, 9):
            r.vl(x + k, y + 6, y + 16, (88, 64, 56)); r.ell(x + k, y + 18, 4, 3, O); r.ell(x + k, y + 18, 3, 2, (72, 120, 88))
    # floating chunks, a crooked path of slabs to a cracked dais
    for x, y in ((40, 120), (196, 90), (60, 182), (190, 170)):
        r.ell(x, y + 4, 16, 7, O); r.ell(x, y + 4, 15, 6, L3); r.ell(x, y, 16, 6, O); r.ell(x, y, 15, 5, L2); r.hl(x - 10, x + 4, y - 3, L1)
    for k, y in enumerate(range(184, 80, -13)):
        x = 120 + [0, 8, 2, -8, -2, 6, 0, -4][k % 8]
        r.rect(x - 11, y - 5, x + 11, y + 5, O); r.rect(x - 10, y - 4, x + 10, y + 4, L2); r.hl(x - 10, x + 10, y - 4, L1); r.hl(x - 10, x + 10, y + 4, L3)
    dais(r, L2, L3, G1, R1, (255, 168, 120))
    for t in range(60):                                                  # shadow tendrils
        a = t / 9.0
        r.set(LX - 50 + t * 1.6, LY + 24 + 6 * math.sin(a), V3); r.set(LX - 50 + t * 1.6, LY + 25 + 6 * math.sin(a), V3)
    mat(r, L3, R1)
    return r

def arceus():
    """The Hall of Origin: white stone and gold, the seventeen plates set in a ring round the dais."""
    r = Room(493)
    Wt1, Wt2, Wt3 = (252, 252, 244), (228, 228, 216), (192, 188, 176)
    G1, G2, G3 = (255, 232, 128), (232, 184, 64), (176, 128, 40)
    r.rect(0, 0, W - 1, H - 1, Wt2)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, Wt3)
        for x in range(0, W, 32): r.vl(x, y, y + 15, Wt3)
        r.hl(0, W - 1, y + 1, Wt1)
    r.rect(0, 0, W - 1, 31, Wt1)
    for x in range(8, W, 28):
        r.rect(x, 0, x + 10, 31, Wt2); r.vl(x, 0, 31, Wt1); r.vl(x + 10, 0, 31, Wt3); r.rect(x - 2, 0, x + 12, 3, G2)
    r.hl(0, W - 1, 31, G3)
    # golden steps up to the dais
    for k, y in enumerate(range(80, 192, 8)):
        r.rect(100, y, 139, y + 7, O); r.rect(101, y, 138, y + 6, Wt1); r.hl(101, 138, y + 6, Wt3); r.set(101, y + 1, G1); r.set(138, y + 1, G2)
    r.vl(99, 80, 191, G2); r.vl(140, 80, 191, G2)
    dais(r, Wt1, Wt3, G2, G1, (255, 255, 224))
    plates = [(248, 248, 240), (232, 72, 40), (56, 120, 216), (248, 208, 48), (64, 168, 64), (152, 216, 240), (192, 64, 48), (160, 64, 176),
              (208, 176, 96), (160, 184, 248), (232, 96, 152), (168, 184, 40), (184, 160, 96), (112, 88, 152), (104, 72, 208), (80, 64, 56), (176, 176, 200), (248, 152, 200)]
    for k, c in enumerate(plates[:17]):
        a = k * 2 * math.pi / 17 - math.pi / 2
        x, y = LX + 64 * math.cos(a), LY + 30 * math.sin(a) + 4
        if y < 34: continue
        r.rect(int(x) - 4, int(y) - 3, int(x) + 4, int(y) + 3, O); r.rect(int(x) - 3, int(y) - 2, int(x) + 3, int(y) + 2, c)
        r.set(int(x) - 2, int(y) - 1, (255, 255, 255))
    for x in (30, 210):
        for y in (96, 168):
            r.ell(x, y, 10, 5, O); r.ell(x, y, 9, 4, G2); r.ell(x, y - 2, 6, 2, G1)
    mat(r, G3, G1)
    return r

def zapdos():
    """A storm-struck power plant: hazard-striped floor, humming generators, sparks."""
    r = Room(145)
    M1, M2, M3, M4 = (192, 196, 208), (152, 156, 176), (112, 116, 136), (72, 76, 96)
    Y1, Y2 = (248, 224, 72), (216, 168, 32)
    E = (255, 255, 200)
    r.rect(0, 0, W - 1, H - 1, M3)
    for y in range(32, H, 8):
        r.hl(0, W - 1, y, M4)
        for x in range(0, W, 24): r.vl(x, y, y + 7, M4)
    r.rect(0, 0, W - 1, 31, M4)
    for x in range(4, W, 40):
        r.rect(x, 2, x + 32, 29, O); r.rect(x + 1, 3, x + 31, 28, M2); r.rect(x + 4, 6, x + 28, 12, (40, 48, 64))
        for k in range(5): r.vl(x + 6 + 5 * k, 7, 11, Y1 if k % 2 else (120, 240, 120))
        r.ell(x + 16, 21, 6, 5, O); r.ell(x + 16, 21, 5, 4, Y2); r.ell(x + 15, 20, 2, 2, E)
    r.hl(0, W - 1, 31, O)
    # hazard stripes either side of the walkway
    for x0 in (88, 140):
        for y in range(80, 192):
            for x in range(x0, x0 + 12): r.set(x, y, Y1 if ((x + y) // 4) % 2 else (40, 40, 48))
    path(r, M2, M4, x0=104, x1=135, slabs=M3)
    dais(r, M2, M4, Y2, Y1, E)
    # coils with sparks
    def bolt(x, y):
        for k in range(10): r.set(x + (k % 3) - 1, y + k, E); r.set(x + (k % 3), y + k, Y1)
    for x, y in ((36, 110), (204, 110), (36, 170), (204, 170)):
        r.rect(x - 9, y - 20, x + 9, y + 6, O); r.rect(x - 8, y - 19, x + 8, y + 5, M2)
        for yy in range(y - 17, y + 4, 3): r.hl(x - 8, x + 8, yy, (184, 112, 56))
        r.ell(x, y - 22, 7, 4, O); r.ell(x, y - 22, 6, 3, M1); bolt(x + 10, y - 30)
    mat(r, M4, Y2)
    return r

ROOMS = dict(kyogre=kyogre, rayquaza=rayquaza, lugia=lugia, dialga=dialga, palkia=palkia, giratina=giratina, arceus=arceus, zapdos=zapdos)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        r = ROOMS[name]()
        r.save(os.path.join(out, 'chamber2_%s.png' % name))
        if hasattr(r, 'front'): open(os.path.join(out, 'chamber2_%s_front.txt' % name), 'w').write(repr(r.front))
