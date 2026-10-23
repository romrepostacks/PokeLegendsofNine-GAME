# SUMMONING CHAMBERS, round 3: eight more legendaries. python3 chambers3.py OUTDIR [names...]
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path

def tree(r, x, y, c1, c2, c3, trunk=(112, 80, 56)):
    r.rect(x - 2, y, x + 2, y + 12, O); r.rect(x - 1, y, x + 1, y + 11, trunk)
    r.blob(x, y - 4, 13, c2, c3, c1)

def articuno():
    """An ice cavern: frozen floor with long cracks, icicles from the back wall, snow drifts and ice crystals."""
    r = Room(144)
    I1, I2, I3, I4 = (232, 244, 255), (192, 224, 248), (152, 200, 240), (104, 160, 216)
    r.rect(0, 0, W - 1, H - 1, I2)
    for sx, sy in ((10, 50), (150, 70), (40, 130), (190, 150), (90, 200)):
        x, y = sx, sy
        for _ in range(40):
            r.set(x, y, I4); r.set(x + 1, y, I1); x += r.rnd.choice((1, 1, 2)); y += r.rnd.choice((-1, 0, 1))
    r.rect(0, 0, W - 1, 31, I3)
    for x in range(0, W, 7):
        h = 8 + (x * 11) % 22
        for y in range(0, h): 
            w = max(0, 3 - y * 3 // h)
            r.hl(x - w, x + w, y, I1 if y < h // 3 else I2)
        r.set(x, h, I4)
    r.hl(0, W - 1, 31, I4)
    for x, y in ((30, 80), (210, 70), (24, 180), (216, 176), (60, 140), (180, 128)):
        r.blob(x, y, 10, I1, I3, (255, 255, 255))
    def crystal(x, y, h):
        for k in range(h):
            w = (h - k) // 3 + 1
            r.hl(x - w, x + w, y - k, I3 if k % 2 else I2)
        r.vl(x - 1, y - h + 2, y, I1)
    for x, y, h in ((80, 100, 18), (160, 96, 22), (70, 180, 14), (172, 186, 16)): crystal(x, y, h)
    path(r, I1, I3, slabs=I2)
    dais(r, I1, I3, I4, (88, 176, 248), (232, 248, 255))
    mat(r, I4, I1)
    return r

def moltres():
    """A scorched peak at dusk: ember sky behind, cracked red rock, braziers of fire round the dais."""
    r = Room(146)
    S1, S2, S3 = (248, 168, 88), (232, 112, 72), (168, 64, 72)
    K1, K2, K3 = (168, 104, 88), (128, 72, 64), (88, 48, 48)
    F1, F2, F3 = (255, 240, 144), (248, 168, 48), (224, 72, 40)
    r.rect(0, 0, W - 1, H - 1, K2)
    for y in range(32, H, 10):
        for x in range((y * 7) % 30, W, 30): r.hl(x, x + 12, y, K3); r.hl(x + 1, x + 10, y - 1, K1)
    for y in range(0, 32): r.hl(0, W - 1, y, S1 if y < 10 else S2 if y < 22 else S3)
    for x in range(0, W, 16):                                    # distant peaks
        h = 6 + (x * 5) % 10
        for y in range(31 - h, 32): 
            w = (y - (31 - h)) // 1
            r.hl(x + 8 - w, x + 8 + w, y, K3)
    r.ell(186, 12, 8, 8, F1)
    r.hl(0, W - 1, 31, O)
    def brazier(x, y):
        r.rect(x - 6, y - 2, x + 6, y + 6, O); r.rect(x - 5, y - 1, x + 5, y + 5, K1); r.hl(x - 5, x + 5, y + 5, K3)
        for k in range(12):
            w = max(0, 5 - k // 2)
            r.hl(x - w, x + w, y - 2 - k, F3 if k < 4 else F2 if k < 8 else F1)
    for x, y in ((40, 90), (200, 90), (40, 160), (200, 160), (80, 60), (160, 60)): brazier(x, y)
    path(r, K1, K3, slabs=K2)
    dais(r, K1, K3, F2, F3, F1)
    for _ in range(40): r.set(r.rnd.randint(0, 239), r.rnd.randint(34, 207), F2)
    mat(r, K3, F2)
    return r

def mew():
    """Jungle ruins: grass floor, mossy stone blocks with vines, pink flowers and butterflies."""
    r = Room(151)
    G1, G2, G3 = (152, 216, 104), (104, 184, 80), (64, 136, 64)
    T1, T2, T3 = (216, 208, 176), (176, 168, 144), (128, 120, 104)
    P1, P2 = (255, 200, 232), (240, 136, 192)
    r.rect(0, 0, W - 1, H - 1, G2)
    for _ in range(500):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(32, 207)
        r.set(x, y, G1 if r.rnd.random() < .5 else G3)
    r.rect(0, 0, W - 1, 31, G3)
    for x in range(-6, W, 22): tree(r, x, 14, G1, G2, G3)
    r.hl(0, W - 1, 31, O)
    for x, y in ((30, 90), (206, 80), (48, 168), (196, 172)):
        r.rect(x - 14, y - 10, x + 14, y + 10, O); r.rect(x - 13, y - 9, x + 13, y + 9, T2); r.hl(x - 13, x + 13, y - 9, T1); r.hl(x - 13, x + 13, y + 9, T3)
        for k in range(-12, 13, 6): r.vl(x + k, y - 9, y - 3 + (k % 4), G3)
    for _ in range(26):
        x, y = r.rnd.randint(8, 232), r.rnd.randint(40, 200)
        if 96 < x < 144: continue
        r.set(x, y, P2); r.set(x + 1, y, P1); r.set(x, y + 1, P1); r.set(x + 1, y + 1, P2)
    for x, y in ((70, 120), (176, 132), (150, 48)):
        r.set(x, y, P2); r.set(x + 2, y, P2); r.set(x + 1, y + 1, O)
    path(r, T1, T3, slabs=T2)
    for y in range(84, 190, 9): r.hl(104, 108, y, G3); r.hl(131, 135, y + 4, G3)
    dais(r, T1, T3, G3, P2, P1)
    mat(r, T3, P2)
    return r

def raikou():
    """A stone circle on a stormy plain: dark grass, rain, a lightning-split menhir and yellow-lit runes."""
    r = Room(243)
    G1, G2, G3 = (104, 136, 104), (72, 104, 80), (48, 72, 64)
    S1, S2, S3 = (176, 176, 192), (128, 128, 152), (88, 88, 112)
    Y1, Y2 = (255, 240, 120), (248, 200, 48)
    r.rect(0, 0, W - 1, H - 1, G2)
    for _ in range(400): r.set(r.rnd.randint(0, 239), r.rnd.randint(32, 207), G3 if r.rnd.random() < .6 else G1)
    for y in range(0, 32): r.hl(0, W - 1, y, (56, 64, 96) if y < 16 else (72, 80, 112))
    for x in range(0, W, 30): r.blob(x + 10, 6, 14, (88, 96, 128), O, (112, 120, 152))
    x, y = 70, 0
    while y < 30: r.set(x, y, Y1); r.set(x + 1, y, (255, 255, 255)); x += r.rnd.choice((-1, 0, 1, 1)); y += 1
    r.hl(0, W - 1, 31, O)
    for k in range(10):                                           # the stone circle
        a = k * math.pi / 5 + 0.3
        x, y = LX + 96 * math.cos(a), 118 + 70 * math.sin(a)
        if 100 < x < 140 and y > 150: continue
        r.rect(int(x) - 5, int(y) - 16, int(x) + 5, int(y) + 2, O); r.rect(int(x) - 4, int(y) - 15, int(x) + 4, int(y) + 1, S2)
        r.vl(int(x) - 4, int(y) - 15, int(y) + 1, S1); r.rect(int(x) - 1, int(y) - 10, int(x) + 1, int(y) - 7, Y2)
    for _ in range(90):                                           # rain
        x, y = r.rnd.randint(0, 236), r.rnd.randint(0, 200)
        r.set(x, y, (168, 184, 216)); r.set(x + 1, y + 2, (168, 184, 216))
    path(r, S2, S3, slabs=S3)
    dais(r, S1, S3, S3, Y2, Y1)
    mat(r, S3, Y2)
    return r

def entei():
    """The burned tower: charred floorboards, fallen beams, embers, the open roof with smoke above."""
    r = Room(244)
    W1, W2, W3 = (128, 96, 80), (96, 68, 56), (64, 44, 40)
    A = (160, 152, 152)
    F1, F2, F3 = (255, 216, 112), (248, 136, 48), (200, 56, 40)
    r.rect(0, 0, W - 1, H - 1, W2)
    for y in range(32, H, 8):
        r.hl(0, W - 1, y, W3)
        for x in range((y // 8) * 29 % 40, W, 40): r.vl(x, y, y + 7, W3)
    for _ in range(14):                                          # burnt holes
        x, y = r.rnd.randint(10, 230), r.rnd.randint(40, 200)
        if 96 < x < 144: continue
        r.ell(x, y, 5, 3, (32, 24, 24)); r.set(x, y - 2, F3)
    r.rect(0, 0, W - 1, 31, (64, 64, 80))
    for x in range(0, W, 20): r.blob(x, 10, 10, (96, 96, 112), O, (128, 128, 144))
    for x in (0, 60, 160, 220): r.rect(x, 0, x + 12, 31, W3); r.vl(x + 1, 0, 31, W1)
    r.hl(0, W - 1, 31, O)
    for (x0, y0, x1, y1) in ((20, 70, 70, 100), (170, 150, 230, 120), (30, 170, 80, 186)):   # fallen beams
        for t in range(0, 60):
            x, y = x0 + (x1 - x0) * t / 60, y0 + (y1 - y0) * t / 60
            r.rect(int(x) - 3, int(y) - 3, int(x) + 3, int(y) + 3, O)
        for t in range(0, 60):
            x, y = x0 + (x1 - x0) * t / 60, y0 + (y1 - y0) * t / 60
            r.rect(int(x) - 2, int(y) - 2, int(x) + 2, int(y) + 2, W3); r.set(x, y - 2, W1)
    for _ in range(50):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(34, 207); r.set(x, y, r.rnd.choice((F1, F2, F3)))
    path(r, W1, W3, slabs=W2)
    dais(r, (88, 80, 80), W3, A, F3, F1)
    mat(r, W3, F2)
    return r

def suicune():
    """A clear northern lake: shallows over pale stones, lily pads, mist, and a crystal dais."""
    r = Room(245)
    L1, L2, L3 = (176, 232, 240), (128, 208, 232), (88, 168, 216)
    S1 = (232, 240, 240)
    M = (240, 248, 255)
    r.rect(0, 0, W - 1, H - 1, L2)
    for _ in range(40):
        x, y = r.rnd.randint(0, 236), r.rnd.randint(40, 206)
        r.ell(x, y, 4, 2, L1)
    for y in range(36, H, 9):
        for x in range((y * 11) % 34, W, 34): r.hl(x, x + 7, y, S1)
    r.rect(0, 0, W - 1, 31, (64, 112, 104))
    for x in range(-4, W, 18): tree(r, x, 12, (120, 184, 168), (72, 144, 136), (48, 104, 104), (96, 80, 72))
    r.hl(0, W - 1, 31, L3)
    for x, y in ((40, 90), (190, 110), (60, 160), (176, 176), (210, 60)):
        r.ell(x, y, 8, 4, O); r.ell(x, y, 7, 3, (96, 176, 104)); r.set(x + 2, y - 1, (248, 200, 232)); r.set(x, y, L2)
    for _ in range(8):                                        # mist
        x, y = r.rnd.randint(-10, 230), r.rnd.randint(40, 200)
        r.hl(x, x + 30, y, M); r.hl(x + 6, x + 22, y + 1, M)
    for k, y in enumerate(range(180, 84, -16)):
        x = 120
        r.ell(x, y + 2, 13, 6, O); r.ell(x, y + 2, 12, 5, (176, 184, 192)); r.ell(x, y, 12, 5, S1)
    dais(r, (224, 244, 252), L3, L1, (80, 200, 232), (240, 255, 255))
    mat(r, L3, L1)
    return r

def celebi():
    """A forest shrine: leaf-litter floor, tall trees, a small wooden shrine at the back, light shafts."""
    r = Room(251)
    G1, G2, G3 = (136, 200, 96), (88, 160, 72), (56, 112, 64)
    D1, D2 = (168, 136, 96), (128, 96, 72)
    r.rect(0, 0, W - 1, H - 1, G3)
    for _ in range(700):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(32, 207); r.set(x, y, r.rnd.choice((G2, G2, D2, G1)))
    r.rect(0, 0, W - 1, 31, (40, 80, 56))
    for x in range(-8, W, 16): tree(r, x, 18, G1, G2, G3, (96, 72, 56))
    # the little shrine behind the dais
    r.rect(104, 4, 135, 30, O); r.rect(105, 10, 134, 30, D1); r.vl(134, 10, 30, D2)
    for x in range(100, 140): r.set(x, 6 + abs(x - 120) // 6, (168, 56, 48))
    r.hl(98, 141, 10, (136, 40, 40)); r.rect(115, 18, 124, 30, D2)
    r.hl(0, W - 1, 31, O)
    for x in (30, 210):
        for y in (90, 170): tree(r, x, y, G1, G2, G3, (96, 72, 56))
    for x0 in (60, 170):                                     # shafts of light
        for y in range(34, 200):
            if (y // 2) % 3 == 0: r.set(x0 + (y - 34) // 4, y, (200, 232, 152))
    path(r, D1, D2, slabs=D2)
    dais(r, (176, 216, 136), G3, D2, (152, 248, 136), (240, 255, 216))
    mat(r, D2, G1)
    return r

def jirachi():
    """Under a sky of stars: a desert night, a comet overhead, a star-shaped dais and paper wish tags."""
    r = Room(385)
    N1, N2, N3 = (40, 48, 104), (28, 32, 80), (20, 24, 56)
    Sd1, Sd2, Sd3 = (232, 208, 152), (200, 176, 120), (160, 136, 96)
    Y1, Y2 = (255, 248, 168), (248, 216, 72)
    r.rect(0, 0, W - 1, 64, N2)
    for y in range(0, 64): r.hl(0, W - 1, y, N3 if y < 20 else N2 if y < 44 else N1)
    for _ in range(90): r.set(r.rnd.randint(0, 239), r.rnd.randint(0, 60), r.rnd.choice((Y1, (255, 255, 255), (184, 200, 255))))
    for t in range(60):                                       # comet
        r.set(150 + t, 10 + t // 3, Y1 if t < 6 else (184, 200, 255) if t % 2 else N1)
    r.ell(150, 10, 3, 3, Y1)
    for y in range(64, H):
        r.hl(0, W - 1, y, Sd2)
    for y in range(64, H, 12):
        for x in range((y * 5) % 40, W, 40): r.hl(x, x + 18, y, Sd1); r.hl(x + 4, x + 14, y + 1, Sd3)
    for x in range(0, W):                                     # dune line
        r.set(x, 64 + 3 * math.sin(x / 13), Sd1)
    for x, y in ((40, 100), (200, 110), (54, 170), (186, 172)):   # posts with wish tags
        r.rect(x - 1, y - 20, x + 1, y, O); r.vl(x, y - 20, y, (136, 96, 64))
        for k in range(3):
            r.rect(x + 2, y - 18 + k * 6, x + 5, y - 14 + k * 6, r.rnd.choice(((248, 136, 136), (136, 200, 248), (248, 232, 120))))
    path(r, Sd1, Sd3, slabs=Sd2)
    dais(r, (252, 244, 216), Sd3, Y2, Y2, Y1)
    for k in range(5):                                        # the star on the dais
        a = -math.pi / 2 + k * 2 * math.pi / 5
        for t in range(18): r.set(LX + t * math.cos(a), LY + t * 0.4 * math.sin(a), Y2)
    mat(r, Sd3, Y2)
    return r

ROOMS = dict(articuno=articuno, moltres=moltres, mew=mew, raikou=raikou, entei=entei, suicune=suicune, celebi=celebi, jirachi=jirachi)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber3_%s.png' % name))
