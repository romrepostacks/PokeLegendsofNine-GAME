# SUMMONING CHAMBERS, round 5: sixteen more legendaries (Sinnoh's last and Unova's). python3 chambers5.py OUTDIR [names...]
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path
from chambers3 import tree

def sky(r, cols, y1=32):
    n = len(cols)
    for y in range(0, y1): r.hl(0, W - 1, y, cols[min(n - 1, y * n // y1)])

def speckle(r, base, cols, n, y0=32):
    r.rect(0, y0, W - 1, H - 1, base)
    for _ in range(n): r.set(r.rnd.randint(0, 239), r.rnd.randint(y0, 207), r.rnd.choice(cols))

def bubbles(r, n, c=(216, 240, 255)):
    for _ in range(n):
        x, y = r.rnd.randint(4, 235), r.rnd.randint(36, 200); r.ring(x, y, 2, 2, c)

def phione():
    """A shallow reef garden: sunlit sand under clear water, coral heads, sea grass, bubbles."""
    r = Room(489)
    speckle(r, (40, 104, 160), [(56, 128, 184), (32, 88, 144)], 500, 0)
    for y in range(0, H, 11):
        for x in range((y * 13) % 40, W, 40): r.hl(x, x + 10, y, (88, 160, 208))
    for x, y, c in ((30, 70, (240, 112, 128)), (200, 60, (248, 176, 88)), (40, 170, (192, 120, 216)), (204, 172, (240, 112, 128)), (70, 120, (248, 176, 88)), (176, 118, (192, 120, 216))):
        r.blob(x, y, 9, c, O, tuple(min(255, k + 50) for k in c))
    for x in (90, 150, 20, 220):
        for y in range(150, 196): r.set(x + 2 * math.sin(y / 4 + x), y, (72, 168, 112))
    bubbles(r, 30)
    path(r, (240, 232, 192), (208, 192, 152), x0=110, x1=129, y0=80)
    dais(r, (248, 240, 216), (200, 184, 144), (32, 88, 144), (88, 200, 248), (232, 255, 255))
    mat(r, (208, 192, 152), (88, 200, 248))
    return r

def manaphy():
    """The Sea Temple: deep-blue stone halls underwater, gold trim, glowing runes, bubbles rising."""
    r = Room(490)
    B1, B2, B3 = (72, 112, 184), (48, 80, 152), (32, 52, 112)
    G1, G2 = (248, 216, 96), (200, 160, 48)
    r.rect(0, 0, W - 1, H - 1, B2)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, B3)
        for x in range(0, W, 16): r.vl(x, y, y + 15, B3); r.hl(x + 1, x + 14, y + 1, B1)
    r.rect(0, 0, W - 1, 31, B3)
    for x in range(6, W, 26):
        r.rect(x, 0, x + 12, 31, B2); r.rect(x - 2, 0, x + 14, 3, G2); r.rect(x - 2, 28, x + 14, 31, G2); r.vl(x, 4, 27, B1)
    for x in (60, 180): r.ell(x, 14, 8, 8, O); r.ell(x, 14, 7, 7, (120, 232, 248)); r.ell(x - 2, 12, 2, 2, (255, 255, 255))
    r.hl(0, W - 1, 31, O)
    for x, y in ((40, 100), (200, 100), (40, 170), (200, 170)):
        r.rect(x - 8, y - 28, x + 8, y + 6, O); r.rect(x - 7, y - 27, x + 7, y + 5, B1); r.rect(x - 9, y - 30, x + 9, y - 26, G1)
        r.rect(x - 2, y - 18, x + 2, y - 12, (120, 232, 248))
    bubbles(r, 26, (168, 216, 248))
    path(r, B1, B3, slabs=B2)
    for y in range(86, 190, 10): r.set(104, y, G1); r.set(135, y, G1)
    dais(r, B1, B3, G1, (120, 232, 248), (232, 255, 255))
    mat(r, B3, G2)
    return r

def shaymin():
    """Flower Paradise: a sunny meadow packed with pink and white blossoms, open sky."""
    r = Room(492)
    sky(r, [(176, 224, 255), (152, 208, 248), (200, 232, 200)])
    speckle(r, (112, 192, 96), [(88, 168, 80), (144, 216, 112)], 400)
    for _ in range(420):
        x, y = r.rnd.randint(0, 238), r.rnd.randint(34, 205)
        if 100 < x < 140 and y > 70: continue
        c = r.rnd.choice(((248, 160, 200), (255, 255, 255), (248, 200, 224)))
        r.set(x, y, c); r.set(x + 1, y, c); r.set(x, y + 1, (232, 112, 160) if c != (255, 255, 255) else (248, 232, 120))
    for x in [x for x in range(-6, W, 28) if not 66 < x < 156]: tree(r, x, 26, (152, 216, 112), (104, 184, 80), (64, 136, 64))
    path(r, (232, 216, 168), (192, 176, 128), x0=110, x1=129)
    dais(r, (248, 240, 224), (192, 176, 128), (104, 184, 80), (248, 128, 176), (255, 232, 240))
    mat(r, (192, 176, 128), (248, 128, 176))
    return r

def victini():
    """Liberty Garden: a lawn at the foot of the old lighthouse, red brick, bunting, a V on the dais."""
    r = Room(494)
    sky(r, [(168, 216, 255), (144, 200, 248)])
    speckle(r, (104, 176, 88), [(80, 152, 72), (136, 200, 104)], 500)
    r.rect(96, 0, 143, 31, O); r.rect(97, 0, 142, 31, (224, 216, 208))
    for y in range(0, 32, 6): r.hl(97, 142, y, (200, 72, 64))
    r.rect(112, 8, 127, 31, (88, 72, 64))
    for k in range(30):                                       # bunting
        x = 4 + k * 8
        y = int(36 + 4 * math.sin(k / 2))
        r.set(x, y, O); r.rect(x + 1, y + 1, x + 4, y + 3, ((232, 72, 56), (248, 216, 72))[k % 2])
    for x, y in ((40, 110), (200, 110), (50, 180), (190, 180)):
        r.rect(x - 12, y - 6, x + 12, y + 6, O); r.rect(x - 11, y - 5, x + 11, y + 5, (200, 96, 72)); r.hl(x - 11, x + 11, y - 5, (232, 136, 104))
        r.blob(x, y - 10, 9, (88, 168, 80), O, (136, 208, 104))
    path(r, (208, 104, 80), (160, 64, 56), slabs=(176, 80, 64))
    dais(r, (248, 232, 200), (176, 80, 64), (248, 216, 72), (240, 96, 56), (255, 224, 160))
    for t in range(12): r.set(LX - 8 + t * 0.7, LY - 4 + t * 0.7, (232, 72, 56)); r.set(LX + 8 - t * 0.7, LY - 4 + t * 0.7, (232, 72, 56))
    mat(r, (160, 64, 56), (248, 216, 72))
    return r

def justice(r, rock, accent, glow, glow2, plants=None, trees=None):
    R1, R2, R3 = rock
    speckle(r, R2, [R1, R3], 600, 0)
    r.rect(0, 0, W - 1, 31, R3)
    for x in range(0, W, 12): r.blob(x, 12 + (x * 5) % 10, 9, R2, O, R1)
    r.hl(0, W - 1, 31, O)
    if trees:
        for x, y in trees: tree(r, x, y, *plants)
    for x, y in ((52, 110), (188, 104), (40, 176), (200, 182)):
        r.rect(x - 2, y - 26, x + 2, y + 2, O); r.rect(x - 1, y - 25, x + 1, y + 1, (216, 216, 232))   # a sword planted in stone
        r.hl(x - 6, x + 6, y - 18, O); r.hl(x - 5, x + 5, y - 18, accent)
        r.blob(x, y + 4, 7, R2, O, R1)
    path(r, R1, R3, slabs=R2)
    dais(r, R1, R3, accent, glow, glow2)

def cobalion():
    r = Room(638); justice(r, ((152, 168, 192), (112, 128, 160), (72, 84, 112)), (88, 144, 232), (88, 160, 248), (216, 232, 255))
    mat(r, (72, 84, 112), (88, 160, 248)); return r
def terrakion():
    r = Room(639); justice(r, ((200, 168, 128), (160, 128, 96), (112, 88, 72)), (200, 112, 56), (232, 136, 64), (255, 216, 160))
    mat(r, (112, 88, 72), (232, 136, 64)); return r
def virizion():
    r = Room(640); justice(r, ((136, 192, 112), (96, 160, 88), (64, 112, 72)), (232, 96, 136), (120, 232, 120), (232, 255, 216),
                           ((152, 216, 112), (104, 184, 80), (64, 136, 64)), ((24, 70), (216, 66), (90, 150), (150, 170)))
    mat(r, (64, 112, 72), (232, 96, 136)); return r

def forces(r, sky_cols, ground, accent, glow, glow2, extra):
    sky(r, sky_cols, 48)
    G1, G2, G3 = ground
    r.rect(0, 40, W - 1, H - 1, G2)
    for x in range(W): r.vl(x, 40 + int(4 * math.sin(x / 19)), 44 + int(4 * math.sin(x / 19)), G1)
    for _ in range(500): r.set(r.rnd.randint(0, 239), r.rnd.randint(46, 207), r.rnd.choice((G1, G3)))
    extra(r)
    path(r, (208, 192, 160), (160, 144, 112), x0=110, x1=129, slabs=(176, 160, 128))
    dais(r, (232, 224, 200), (160, 144, 112), accent, glow, glow2)

def tornadus():
    def e(r):
        for cx, cy in ((40, 90), (196, 120), (70, 180)):
            for t in range(220): a = t / 18.0; rr = 24 * t / 220; r.set(cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.6, (200, 240, 216))
    r = Room(641); forces(r, [(152, 216, 200), (120, 192, 184), (168, 224, 208)], ((136, 192, 120), (104, 160, 96), (72, 120, 80)), (72, 168, 104), (104, 216, 152), (224, 255, 232), e)
    mat(r, (160, 144, 112), (72, 168, 104)); return r
def thundurus():
    def e(r):
        for x0 in (40, 190):
            x, y = x0, 0
            while y < 46: r.set(x, y, (255, 248, 160)); r.set(x + 1, y, (255, 255, 255)); x += r.rnd.choice((-1, 0, 1, 1)); y += 1
        for _ in range(80): x, y = r.rnd.randint(0, 236), r.rnd.randint(0, 200); r.set(x, y, (152, 168, 208))
    r = Room(642); forces(r, [(64, 72, 104), (80, 88, 128), (104, 112, 152)], ((112, 128, 104), (80, 96, 80), (56, 68, 64)), (96, 104, 200), (248, 224, 96), (255, 255, 216), e)
    mat(r, (160, 144, 112), (96, 104, 200)); return r
def landorus():
    def e(r):
        for _ in range(500):
            x, y = r.rnd.randint(0, 236), r.rnd.randint(50, 205)
            if 96 < x < 144: continue
            r.vl(x, y, y + 3, (232, 192, 88)); r.set(x, y - 1, (248, 224, 128))
    r = Room(645); forces(r, [(176, 216, 248), (200, 224, 240), (240, 224, 184)], ((200, 184, 104), (168, 152, 80), (128, 112, 64)), (184, 120, 56), (232, 168, 64), (255, 232, 168), e)
    mat(r, (160, 144, 112), (184, 120, 56)); return r

def dragon_ruins(r, stone, fire, glow, glow2, bolts=False):
    S1, S2, S3 = stone
    r.rect(0, 0, W - 1, H - 1, S2)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, S3)
        for x in range((8 if (y // 16) % 2 else 0), W, 16): r.vl(x, y, y + 15, S3); r.hl(x + 1, x + 14, y + 1, S1)
    for _ in range(12):                                           # broken flags
        x, y = r.rnd.randint(4, 220), r.rnd.randint(40, 200)
        if 90 < x < 150: continue
        r.rect(x, y, x + 7, y + 4, S3)
    sky(r, [(40, 40, 72), (56, 56, 96)] if bolts else [(232, 232, 248), (208, 216, 240)])
    for x in range(0, W, 30): r.rect(x + 6, 4 + (x * 3) % 10, x + 18, 31, S2); r.vl(x + 6, 4 + (x * 3) % 10, 31, S1); r.vl(x + 18, 4 + (x * 3) % 10, 31, S3)
    r.hl(0, W - 1, 31, O)
    for x, y in ((40, 100), (200, 100), (40, 172), (200, 172)):
        r.rect(x - 7, y - 4, x + 7, y + 6, O); r.rect(x - 6, y - 3, x + 6, y + 5, S1); r.hl(x - 6, x + 6, y + 5, S3)
        if bolts:
            xx, yy = x, y - 4
            for k in range(14): r.set(xx, yy - k, fire[k % 2]); xx += (1, -1)[k % 2]
        else:
            for k in range(12): w = max(0, 5 - k // 2); r.hl(x - w, x + w, y - 4 - k, fire[0] if k > 6 else fire[1])
    path(r, S1, S3, slabs=S2)
    dais(r, S1, S3, S3, glow, glow2)

def reshiram():
    r = Room(643); dragon_ruins(r, ((240, 240, 248), (208, 208, 224), (160, 160, 184)), ((255, 255, 255), (136, 200, 255)), (248, 160, 72), (255, 240, 200))
    mat(r, (160, 160, 184), (248, 160, 72)); return r
def zekrom():
    r = Room(644); dragon_ruins(r, ((96, 96, 112), (64, 64, 80), (40, 40, 56)), ((136, 232, 255), (255, 255, 255)), (72, 168, 248), (200, 240, 255), bolts=True)
    mat(r, (40, 40, 56), (72, 168, 248)); return r

def kyurem():
    """Giant Chasm's heart: a snow-crusted crater of black rock, frost on everything, ice spikes."""
    r = Room(646)
    speckle(r, (200, 216, 232), [(232, 240, 248), (160, 176, 200)], 500, 0)
    r.rect(0, 0, W - 1, 31, (56, 64, 80))
    for x in range(0, W, 10):
        h = 8 + (x * 7) % 16; r.rect(x, 0, x + 9, h, (88, 96, 112)); r.hl(x, x + 9, h, (232, 240, 248))
    r.hl(0, W - 1, 31, O)
    for x, y in ((40, 90), (200, 96), (60, 170), (180, 176), (24, 140), (216, 150)): r.blob(x, y, 10, (72, 80, 96), O, (112, 120, 136))
    for x, y, h in ((80, 120, 20), (160, 112, 24), (100, 190, 12), (146, 188, 14)):
        for k in range(h): w = (h - k) // 4 + 1; r.hl(x - w, x + w, y - k, (168, 216, 248) if k % 2 else (224, 244, 255))
    path(r, (232, 240, 248), (152, 168, 192), slabs=(200, 216, 232))
    dais(r, (88, 96, 112), (56, 64, 80), (168, 216, 248), (120, 200, 248), (240, 255, 255))
    mat(r, (152, 168, 192), (120, 200, 248))
    return r

def keldeo():
    """A shallow moor: still water over grass, reeds, stepping tussocks, mist."""
    r = Room(647)
    speckle(r, (112, 168, 168), [(136, 192, 184), (88, 144, 152)], 400, 0)
    sky(r, [(176, 200, 216), (160, 184, 200)])
    for _ in range(40):
        x, y = r.rnd.randint(4, 230), r.rnd.randint(36, 200)
        if 96 < x < 144: continue
        for k in range(3): r.vl(x + k * 2, y - 6 - k, y, (136, 168, 88)); r.set(x + k * 2, y - 7 - k, (168, 128, 72))
    for _ in range(6): x, y = r.rnd.randint(-10, 220), r.rnd.randint(40, 200); r.hl(x, x + 30, y, (224, 236, 240))
    for k, y in enumerate(range(180, 80, -16)):
        r.ell(120, y + 2, 12, 5, O); r.ell(120, y + 2, 11, 4, (72, 112, 64)); r.ell(120, y, 11, 4, (104, 160, 80))
    dais(r, (192, 208, 208), (112, 136, 136), (248, 216, 96), (96, 200, 232), (232, 252, 255))
    mat(r, (72, 112, 64), (96, 200, 232))
    return r

def meloetta():
    """A concert stage: wooden boards, red curtains, footlights, music notes in the air."""
    r = Room(648)
    W1, W2, W3 = (216, 168, 112), (184, 136, 88), (136, 96, 64)
    C1, C2, C3 = (232, 72, 72), (192, 40, 56), (136, 32, 48)
    r.rect(0, 0, W - 1, H - 1, W2)
    for y in range(32, H, 8): r.hl(0, W - 1, y, W3); r.hl(0, W - 1, y + 1, W1)
    r.rect(0, 0, W - 1, 31, C2)
    for x in range(0, W, 8): r.vl(x, 0, 31, C3); r.vl(x + 3, 0, 31, C1)
    for side in (0, 1):
        x0 = 0 if side == 0 else W - 30
        r.rect(x0, 0, x0 + 29, H - 1, C2)
        for x in range(x0, x0 + 30, 6): r.vl(x, 0, H - 1, C3); r.vl(x + 2, 0, H - 1, C1)
    r.hl(0, W - 1, 0, (248, 216, 96)); r.hl(0, W - 1, 3, (248, 216, 96))
    for x in range(40, 200, 16): r.ell(x, 200, 4, 3, O); r.ell(x, 200, 3, 2, (255, 240, 160))
    for x, y in ((60, 80), (180, 70), (70, 150), (170, 140)):
        r.ell(x, y, 3, 2, O); r.vl(x + 3, y - 9, y, O); r.hl(x + 3, x + 6, y - 9, O)
    dais(r, (248, 232, 200), W3, (248, 216, 96), (120, 232, 168), (232, 255, 240))
    mat(r, C3, (248, 216, 96))
    return r

def genesect():
    """A ship's lab: red and grey steel, a fossil in a case, cannons racked on the walls."""
    r = Room(649)
    M1, M2, M3, M4 = (184, 184, 200), (144, 144, 168), (104, 104, 128), (64, 64, 88)
    R1, R2 = (232, 80, 88), (168, 40, 56)
    r.rect(0, 0, W - 1, H - 1, M2)
    for y in range(32, H, 12):
        r.hl(0, W - 1, y, M3)
        for x in range(0, W, 24): r.vl(x, y, y + 11, M3); r.set(x + 3, y + 3, M1)
    r.rect(0, 0, W - 1, 31, M4)
    for x in range(4, W, 36):
        r.rect(x, 4, x + 28, 27, O); r.rect(x + 1, 5, x + 27, 26, M3); r.hl(x + 1, x + 27, 5, R1)
        r.rect(x + 6, 12, x + 22, 16, M1); r.rect(x + 22, 13, x + 26, 15, R2)
    r.hl(0, W - 1, 31, O)
    r.rect(24, 120, 60, 160, O); r.rect(25, 121, 59, 159, (168, 208, 216)); r.blob(42, 142, 9, (200, 176, 136), O, (232, 208, 168))
    for x0 in (88, 140):
        for y in range(80, 192, 2): r.hl(x0, x0 + 11, y, R2 if (y // 4) % 2 else M4)
    for x, y in ((200, 110), (200, 170)):
        r.rect(x - 14, y - 10, x + 14, y + 8, O); r.rect(x - 13, y - 9, x + 13, y + 7, M3); r.rect(x - 11, y - 7, x + 11, y - 1, (40, 56, 64))
        r.hl(x - 9, x + 3, y - 5, R1)
    path(r, M1, M4, x0=104, x1=135, slabs=M3)
    dais(r, M1, M3, R2, R1, (255, 200, 200))
    mat(r, M4, R1)
    return r

ROOMS = dict(phione=phione, manaphy=manaphy, shaymin=shaymin, victini=victini, cobalion=cobalion, terrakion=terrakion, virizion=virizion,
             tornadus=tornadus, thundurus=thundurus, landorus=landorus, reshiram=reshiram, zekrom=zekrom, kyurem=kyurem, keldeo=keldeo,
             meloetta=meloetta, genesect=genesect)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber5_%s.png' % name))
