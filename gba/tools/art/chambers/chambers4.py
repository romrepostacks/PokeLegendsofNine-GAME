# SUMMONING CHAMBERS, round 4: twelve more legendaries. python3 chambers4.py OUTDIR [names...]
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path
from chambers3 import tree

def braille(r, x0, y0, n, c, d):
    # rows of raised dots, as on the old tombs' walls
    for k in range(n):
        x = x0 + k * 7
        for i in range(2):
            for j in range(3):
                if (k * 7 + i * 3 + j) % 4: r.set(x + i * 3, y0 + j * 3, c); r.set(x + i * 3 + 1, y0 + j * 3 + 1, d)

def tomb(r, seed, F1, F2, F3, Wl1, Wl2, Wl3, glow, glow2, block=16):
    r.rect(0, 0, W - 1, H - 1, F2)
    for y in range(32, H, block):
        r.hl(0, W - 1, y, F3)
        for x in range((block // 2 if (y // block) % 2 else 0), W, block): r.vl(x, y, y + block - 1, F3); r.hl(x + 1, x + block - 2, y + 1, F1)
    r.rect(0, 0, W - 1, 31, Wl2)
    for y in range(0, 32, 8):
        r.hl(0, W - 1, y, Wl3)
        for x in range((8 if (y // 8) % 2 else 0), W, 16): r.vl(x, y, y + 7, Wl3)
    r.hl(0, W - 1, 31, O)
    braille(r, 30, 10, 8, Wl1, Wl3); braille(r, 156, 10, 8, Wl1, Wl3)
    for x in (16, 224):                                        # wall columns with braille panels
        for y in (70, 150):
            r.rect(x - 9, y - 24, x + 9, y + 10, O); r.rect(x - 8, y - 23, x + 8, y + 9, Wl2); r.vl(x + 8, y - 23, y + 9, Wl3)
            braille(r, x - 5, y - 18, 2, Wl1, Wl3)
    path(r, F1, F3, slabs=F2)
    dais(r, F1, F3, Wl3, glow, glow2)

def regirock():
    """A sandstone tomb: sand-dusted flagstones, braille along the walls, a rock dais lit orange."""
    r = Room(377)
    tomb(r, 377, (232, 200, 144), (208, 168, 112), (168, 128, 88), (232, 192, 136), (192, 148, 96), (144, 104, 72), (232, 120, 56), (255, 200, 120))
    for _ in range(200):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(34, 207)
        r.set(x, y, (240, 216, 168))
    for x, y in ((50, 110), (190, 120), (64, 184), (180, 180)): r.blob(x, y, 8, (176, 136, 96), O, (208, 176, 128))
    mat(r, (144, 104, 72), (232, 120, 56))
    return r

def regice():
    """An ice tomb: walls of cut ice blocks with braille, a glassy floor, a pale blue dais."""
    r = Room(378)
    tomb(r, 378, (216, 240, 255), (176, 216, 248), (128, 176, 224), (224, 244, 255), (168, 208, 240), (112, 160, 216), (88, 200, 248), (232, 255, 255), block=24)
    for _ in range(30):
        x, y = r.rnd.randint(0, 236), r.rnd.randint(40, 200)
        r.hl(x, x + 3, y, (248, 252, 255))
    mat(r, (112, 160, 216), (232, 255, 255))
    return r

def registeel():
    """An iron tomb: riveted steel plates, braille in raised studs, a dais ringed with violet light."""
    r = Room(379)
    tomb(r, 379, (184, 184, 200), (144, 144, 168), (104, 104, 128), (176, 176, 196), (136, 136, 160), (88, 88, 112), (168, 104, 232), (232, 208, 255), block=20)
    for y in range(36, H, 20):
        for x in range(4, W, 20): r.set(x, y, (232, 232, 240)); r.set(x + 12, y + 12, (232, 232, 240))
    mat(r, (88, 88, 112), (168, 104, 232))
    return r

def regigigas():
    """The giant's temple: a grand stone hall, the three small titans as statues on plinths round the dais."""
    r = Room(486)
    S1, S2, S3 = (216, 216, 208), (176, 176, 168), (128, 128, 128)
    G1, G2 = (248, 232, 160), (216, 184, 88)
    r.rect(0, 0, W - 1, H - 1, S2)
    for y in range(32, H, 24):
        r.hl(0, W - 1, y, S3)
        for x in range(0, W, 24): r.vl(x, y, y + 23, S3); r.hl(x + 1, x + 22, y + 1, S1)
    r.rect(0, 0, W - 1, 31, S3)
    for x in range(10, W, 36): r.rect(x, 0, x + 14, 31, S2); r.vl(x, 0, 31, S1); r.rect(x - 2, 0, x + 16, 4, S1); r.rect(x - 2, 27, x + 16, 31, S1)
    braille(r, 90, 12, 9, S1, S3)
    r.hl(0, W - 1, 31, O)
    def statue(x, y, body, eye):
        r.rect(x - 15, y + 2, x + 15, y + 12, O); r.rect(x - 14, y + 3, x + 14, y + 11, S1); r.hl(x - 14, x + 14, y + 11, S3)
        r.rect(x - 9, y - 22, x + 9, y + 2, O); r.rect(x - 8, y - 21, x + 8, y + 1, body)          # body
        r.rect(x - 14, y - 18, x - 9, y - 4, O); r.rect(x - 13, y - 17, x - 10, y - 5, body)      # arms
        r.rect(x + 9, y - 18, x + 14, y - 4, O); r.rect(x + 10, y - 17, x + 13, y - 5, body)
        r.vl(x - 8, y - 21, y + 1, tuple(min(255, c + 40) for c in body))
        for k in (-4, 0, 4): r.rect(x + k - 1, y - 16, x + k, y - 15, eye)
    statue(44, 92, (176, 128, 96), (248, 200, 72)); statue(196, 92, (160, 208, 240), (255, 255, 255)); statue(44, 166, (152, 152, 176), (248, 80, 80))
    statue(196, 166, (200, 200, 192), (248, 232, 120))
    path(r, S1, S3, slabs=S2)
    dais(r, S1, S3, G2, (120, 216, 120), G1)
    mat(r, S3, G2)
    return r

def island(r, seed, tint, flower, glow, glow2, dusk=False):
    """Southern Island: a ring of beach in the sea, palms, a grassy middle."""
    Sk = [(248, 176, 136), (232, 136, 128), (176, 112, 152)] if dusk else [(168, 216, 255), (144, 200, 248), (120, 184, 240)]
    for y in range(0, 32): r.hl(0, W - 1, y, Sk[0] if y < 10 else Sk[1] if y < 20 else Sk[2])
    sea = (64, 136, 216) if not dusk else (88, 96, 176)
    r.rect(0, 32, W - 1, H - 1, sea)
    for y in range(34, H, 6):
        for x in range((y * 7) % 24, W, 24): r.hl(x, x + 6, y, tuple(min(255, c + 40) for c in sea))
    if dusk: r.ell(200, 30, 14, 10, (255, 216, 144)); r.hl(0, W - 1, 31, (255, 216, 144))
    r.ell(120, 118, 112, 86, O); r.ell(120, 118, 111, 85, (240, 224, 168)); r.ell(120, 116, 96, 72, (104, 184, 96))
    for _ in range(300):
        x, y = r.rnd.randint(30, 210), r.rnd.randint(50, 186)
        if ((x - 120) / 96) ** 2 + ((y - 116) / 72) ** 2 < 0.95: r.set(x, y, r.rnd.choice(((80, 160, 80), (136, 208, 112))))
    for x, y in ((40, 100), (200, 104), (60, 170), (182, 170)): tree(r, x, y, (136, 208, 112), (72, 160, 80), (48, 112, 64), (144, 104, 72))
    for _ in range(20):
        x, y = r.rnd.randint(50, 190), r.rnd.randint(70, 180)
        if 100 < x < 140: continue
        r.set(x, y, flower); r.set(x + 1, y, (255, 255, 255))
    path(r, (240, 224, 168), (200, 184, 128), x0=110, x1=129)
    dais(r, (248, 240, 216), (200, 184, 128), tint, glow, glow2)

def latias():
    r = Room(380); island(r, 380, (232, 96, 112), (248, 136, 168), (232, 80, 96), (255, 208, 216))
    mat(r, (200, 184, 128), (232, 96, 112)); return r

def latios():
    r = Room(381); island(r, 381, (88, 120, 216), (136, 176, 248), (64, 112, 224), (208, 224, 255), dusk=True)
    mat(r, (200, 184, 128), (88, 120, 216)); return r

def deoxys():
    """Birth Island: black rock under open space, a meteor overhead, a triangle laid out in the floor."""
    r = Room(386)
    R1, R2, R3 = (136, 128, 144), (104, 96, 112), (72, 68, 84)
    for y in range(H): r.hl(0, W - 1, y, (16, 16, 40))
    for _ in range(140): r.set(r.rnd.randint(0, 239), r.rnd.randint(0, 207), r.rnd.choice(((255, 255, 255), (184, 200, 255), (255, 200, 160))))
    for t in range(40): r.set(30 + t, 6 + t // 4, (255, 176, 96) if t > 34 else (136, 96, 168))
    r.ell(70, 16, 4, 4, (255, 200, 120))
    # the island
    r.ell(120, 120, 108, 84, O); r.ell(120, 120, 107, 83, R2)
    for _ in range(500):
        x, y = r.rnd.randint(14, 226), r.rnd.randint(38, 202)
        if ((x - 120) / 106) ** 2 + ((y - 120) / 82) ** 2 < 0.97: r.set(x, y, r.rnd.choice((R1, R3)))
    tri = [(LX, 92), (LX - 70, 190), (LX + 70, 190)]
    for a, b in ((0, 1), (1, 2), (2, 0)):
        (x0, y0), (x1, y1) = tri[a], tri[b]
        for t in range(120):
            x, y = x0 + (x1 - x0) * t / 120, y0 + (y1 - y0) * t / 120
            r.set(x, y, (232, 88, 64)); r.set(x, y + 1, (152, 48, 48))
    for x, y in tri: r.rect(x - 4, y - 4, x + 4, y + 2, O); r.rect(x - 3, y - 3, x + 3, y + 1, (248, 200, 72))
    path(r, R1, R3, x0=112, x1=127, y0=96, slabs=R2)
    dais(r, R1, R3, (152, 48, 48), (232, 88, 64), (255, 216, 168))
    mat(r, R3, (232, 88, 64))
    return r

def lake_cave(r, seed, rock, water, crystal, glow, glow2, motif):
    R1, R2, R3 = rock
    r.rect(0, 0, W - 1, H - 1, R2)
    for _ in range(600): r.set(r.rnd.randint(0, 239), r.rnd.randint(32, 207), r.rnd.choice((R1, R3)))
    r.rect(0, 0, W - 1, 31, R3)
    for x in range(0, W, 9):
        h = 6 + (x * 13) % 18
        for y in range(0, h): w = max(0, 3 - y * 3 // h); r.hl(x - w, x + w, y, R2)
    r.hl(0, W - 1, 31, O)
    r.ell(LX, LY + 10, 78, 40, O); r.ell(LX, LY + 10, 77, 39, water[1])
    for k in range(0, 360, 20):
        a = math.radians(k); r.hl(int(LX + 60 * math.cos(a)) - 3, int(LX + 60 * math.cos(a)) + 3, int(LY + 10 + 28 * math.sin(a)), water[0])
    def cr(x, y, h):
        for k in range(h): w = (h - k) // 3 + 1; r.hl(x - w, x + w, y - k, crystal[1] if k % 2 else crystal[0])
        r.vl(x - 1, y - h + 2, y, (255, 255, 255))
    for x, y, h in ((30, 110, 18), (210, 112, 22), (44, 180, 14), (196, 184, 16), (22, 60, 12), (218, 56, 14)): cr(x, y, h)
    path(r, R1, R3, x0=110, x1=129, y0=70, slabs=R2)
    dais(r, R1, R3, crystal[1], glow, glow2)
    motif(r)

def uxie():
    """Lake Acuity's cavern: a still underground lake, yellow crystals, open-book sigils in the floor."""
    r = Room(480)
    def m(r):
        for x, y in ((70, 150), (170, 150)):
            r.rect(x - 8, y - 5, x - 1, y + 4, (248, 232, 120)); r.rect(x + 1, y - 5, x + 8, y + 4, (248, 232, 120)); r.vl(x, y - 5, y + 4, O)
            for k in range(-3, 4, 2): r.hl(x - 7, x - 2, y + k, (200, 176, 72)); r.hl(x + 2, x + 7, y + k, (200, 176, 72))
    lake_cave(r, 480, ((152, 144, 128), (112, 104, 96), (72, 68, 64)), ((168, 208, 232), (88, 144, 192)), ((255, 240, 136), (232, 200, 72)), (248, 216, 72), (255, 255, 200), m)
    mat(r, (72, 68, 64), (248, 216, 72)); return r

def mesprit():
    """Lake Verity's cavern: warm rock, pink crystals, hearts set in the floor."""
    r = Room(481)
    def m(r):
        for x, y in ((70, 150), (170, 150)):
            r.ell(x - 3, y - 2, 4, 4, (240, 120, 168)); r.ell(x + 3, y - 2, 4, 4, (240, 120, 168))
            for k in range(7): r.hl(x - 7 + k, x + 7 - k, y + 1 + k, (240, 120, 168))
    lake_cave(r, 481, ((168, 144, 144), (128, 104, 112), (88, 68, 80)), ((200, 200, 240), (128, 136, 208)), ((255, 192, 224), (232, 120, 176)), (240, 104, 168), (255, 224, 240), m)
    mat(r, (88, 68, 80), (240, 104, 168)); return r

def azelf():
    """Lake Valor's cavern: cool rock, blue crystals, flame-shaped sigils for willpower."""
    r = Room(482)
    def m(r):
        for x, y in ((70, 156), (170, 156)):
            for k in range(14): w = max(0, 5 - abs(k - 9) // 1 if k > 6 else k // 2); r.hl(x - w, x + w, y - k, (96, 160, 240) if k < 8 else (168, 208, 255))
    lake_cave(r, 482, ((136, 144, 168), (96, 104, 136), (64, 68, 96)), ((168, 216, 240), (72, 136, 208)), ((176, 216, 255), (88, 144, 240)), (72, 136, 248), (216, 240, 255), m)
    mat(r, (64, 68, 96), (72, 136, 248)); return r

def heatran():
    """Inside a volcano's heart: iron-veined rock, a moat of magma round the dais, steel stalagmites."""
    r = Room(485)
    R1, R2, R3 = (120, 96, 88), (88, 68, 64), (60, 44, 44)
    I1, I2 = (192, 184, 192), (128, 120, 136)
    L1, L2, L3 = (255, 232, 120), (248, 144, 48), (208, 64, 40)
    r.rect(0, 0, W - 1, H - 1, R2)
    for _ in range(500): r.set(r.rnd.randint(0, 239), r.rnd.randint(32, 207), r.rnd.choice((R1, R3)))
    for sx, sy in ((20, 80), (180, 60), (40, 170), (200, 150)):
        x, y = sx, sy
        for _ in range(26): r.set(x, y, I1); r.set(x, y + 1, I2); x += 1; y += r.rnd.choice((-1, 0, 1))
    r.rect(0, 0, W - 1, 31, R3)
    for x in range(0, W, 11):
        h = 8 + (x * 7) % 16
        for y in range(0, h): w = max(0, 3 - y * 3 // h); r.hl(x - w, x + w, y, R1)
    r.hl(0, W - 1, 31, O)
    r.ell(LX, LY + 8, 66, 30, L3); r.ell(LX, LY + 8, 62, 27, L2)
    for k in range(0, 360, 24):
        a = math.radians(k); r.hl(int(LX + 54 * math.cos(a)) - 2, int(LX + 54 * math.cos(a)) + 2, int(LY + 8 + 22 * math.sin(a)), L1)
    for x, y, h in ((30, 120, 22), (210, 118, 26), (52, 190, 16), (188, 192, 18)):
        for k in range(h): w = (h - k) // 4 + 1; r.hl(x - w, x + w, y - k, I2 if k % 3 else I1)
    path(r, R1, R3, x0=110, x1=129, y0=80, slabs=R3)
    dais(r, (96, 88, 96), R3, I1, L3, L1)
    mat(r, R3, L2)
    return r

def cresselia():
    """Fullmoon Island: a moonlit clearing, silver grass, crescent feathers on the ground, a full moon."""
    r = Room(488)
    N1, N2 = (40, 48, 96), (28, 32, 72)
    G1, G2, G3 = (120, 152, 176), (88, 112, 144), (60, 76, 108)
    for y in range(0, 40): r.hl(0, W - 1, y, N2 if y < 20 else N1)
    for _ in range(40): r.set(r.rnd.randint(0, 239), r.rnd.randint(0, 36), (232, 232, 255))
    r.ell(186, 16, 12, 12, (252, 248, 216)); r.ell(182, 13, 4, 3, (232, 224, 192))
    r.rect(0, 34, W - 1, H - 1, G2)
    for _ in range(600): r.set(r.rnd.randint(0, 239), r.rnd.randint(36, 207), r.rnd.choice((G1, G3)))
    for x in range(-8, W, 18): tree(r, x, 30, (88, 120, 160), (56, 80, 120), (36, 52, 84), (72, 64, 80))
    for x in (24, 216):
        for y in (100, 176): tree(r, x, y, (88, 120, 160), (56, 80, 120), (36, 52, 84), (72, 64, 80))
    for _ in range(14):
        x, y = r.rnd.randint(50, 190), r.rnd.randint(80, 196)
        if 100 < x < 140: continue
        for t in range(8): r.set(x + t, y + int(2 * math.sin(t / 2.5)), (248, 216, 232)); r.set(x + t, y + 1 + int(2 * math.sin(t / 2.5)), (216, 168, 224))
    path(r, G1, G3, x0=110, x1=129, slabs=G2)
    dais(r, (216, 216, 240), G3, (248, 232, 160), (216, 160, 232), (255, 240, 255))
    mat(r, G3, (216, 160, 232))
    return r

ROOMS = dict(regirock=regirock, regice=regice, registeel=registeel, regigigas=regigigas, latias=latias, latios=latios, deoxys=deoxys,
             uxie=uxie, mesprit=mesprit, azelf=azelf, heatran=heatran, cresselia=cresselia)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber4_%s.png' % name))
