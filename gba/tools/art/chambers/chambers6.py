# SUMMONING CHAMBERS, round 6: Kalos and Alola. python3 chambers6.py OUTDIR [names...]
# Lesson from round 5: keep the backdrop straight behind the dais (x 84..156, y 0..70) plain, no buildings or trees there.
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path
from chambers3 import tree
from chambers5 import sky, speckle

def lit(c, d=40): return tuple(max(0, min(255, k + d)) for k in c)

def outdoor(r, sky_cols, ground, n=500, horizon=40, wave=19):
    sky(r, sky_cols, horizon + 8)
    G1, G2, G3 = ground
    r.rect(0, horizon, W - 1, H - 1, G2)
    for x in range(W):
        h = horizon + int(4 * math.sin(x / wave)); r.vl(x, h, h + 4, G1)
    for _ in range(n): r.set(r.rnd.randint(0, 239), r.rnd.randint(horizon + 6, 207), r.rnd.choice((G1, G3)))

def cave(r, wall, floor, n=500):
    W1, W2, W3 = wall
    r.rect(0, 0, W - 1, 31, W2)
    for _ in range(40):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(0, 26); r.blob(x, y, r.rnd.randint(5, 9), W2, O, W1)
    r.hl(0, W - 1, 31, O)
    F1, F2, F3 = floor
    r.rect(0, 32, W - 1, H - 1, F2)
    for _ in range(n): r.set(r.rnd.randint(0, 239), r.rnd.randint(33, 207), r.rnd.choice((F1, F3)))

def side_ok(x): return not 84 < x < 156

def stars(r, n, y0=0, y1=40, cols=((255, 255, 255), (200, 216, 255))):
    for _ in range(n):
        x, y = r.rnd.randint(0, 239), r.rnd.randint(y0, y1); r.set(x, y, r.rnd.choice(cols))

def crystal(r, x, y, h, c1, c2, c3):
    # a pointed crystal, lit on the left face
    q = max(2, h // 4)                                              # widest a quarter of the way up
    ws = [round(4 * k / q) if k < q else round(4 * (h - k) / (h - q)) for k in range(h + 1)]
    for k, w in enumerate(ws): r.hl(x - w - 1, x + w + 1, y - k, O)
    for k, w in enumerate(ws):
        if w: r.hl(x - w, x, y - k, c1); r.hl(x + 1, x + w, y - k, c2)
    r.vl(x - 1, y - h + q, y - q // 2, c3)

def xerneas():
    """Kalos forest glade at sunrise: a pink-gold sky, the sun just up behind the hills, dew mist on the grass,
    long tree shadows and life sparkles in every colour."""
    r = Room(716)
    sky(r, [(104, 112, 184), (168, 136, 192), (232, 152, 168), (248, 184, 152), (255, 216, 160)], 48)
    outdoor_ground = ((192, 192, 112), (136, 160, 96), (104, 128, 80))
    G1, G2, G3 = outdoor_ground
    r.rect(0, 40, W - 1, H - 1, G2)
    for x in range(W):
        h = 40 + int(4 * math.sin(x / 19)); r.vl(x, h, h + 4, G1)
    for _ in range(500): r.set(r.rnd.randint(0, 239), r.rnd.randint(46, 207), r.rnd.choice((G1, G3)))
    # the sun just clearing the hills on the right, half of it still below them
    r.ell(200, 41, 15, 15, (255, 224, 160)); r.ell(200, 41, 12, 12, (255, 248, 208))
    for x in range(W):
        h = 40 + int(4 * math.sin(x / 19)); r.rect(x, h, x, H - 1, G2); r.vl(x, h, h + 4, G1 if abs(x - 200) > 40 else (232, 208, 128))
    for _ in range(500): r.set(r.rnd.randint(0, 239), r.rnd.randint(46, 207), r.rnd.choice((G1, G3)))
    trees = ((12, 40), (44, 30), (232, 40), (20, 120), (220, 120), (28, 190), (212, 190))
    for x, y in trees:                                              # long morning shadows, cast away from the sun
        for k in range(26): r.hl(x - 6 - k, x + 4 - k, y + 2 + k // 6, (88, 128, 88))
    for x, y in trees: tree(r, x, y, (200, 216, 136), (96, 160, 104), (56, 112, 80))
    for y in range(52, H, 22):                                      # dew mist lying low
        for x in range((y * 13) % 70, W, 70):
            if side_ok(x) or y > 90: r.hl(x, x + 14, y, (176, 184, 144))
    rainbow = ((248, 112, 112), (248, 200, 88), (120, 216, 120), (96, 168, 248), (184, 120, 232))
    for _ in range(70):
        x, y = r.rnd.randint(0, 236), r.rnd.randint(44, 200)
        if side_ok(x): c = r.rnd.choice(rainbow); r.set(x, y, c); r.set(x + 1, y, (255, 255, 255)); r.set(x, y - 1, c)
    path(r, (232, 208, 160), (184, 160, 112), x0=110, x1=129)
    dais(r, (248, 236, 224), (184, 160, 112), (96, 160, 104), (96, 168, 248), (232, 248, 255))
    mat(r, (184, 160, 112), (96, 168, 248))
    return r

def yveltal():
    """A withered waste under a crimson sky: grey dead earth, bare black trees, cracks."""
    r = Room(717)
    outdoor(r, [(120, 32, 48), (168, 48, 56), (208, 88, 72)], ((112, 104, 112), (88, 80, 88), (64, 56, 64)), 600)
    for _ in range(26):                                             # cracks
        x, y = r.rnd.randint(4, 230), r.rnd.randint(50, 200)
        if not side_ok(x): continue
        for k in range(10): r.set(x, y, (48, 40, 48)); x += r.rnd.choice((-1, 1, 1)); y += r.rnd.choice((0, 1))
    for x0, y0 in ((30, 44), (206, 44), (24, 140), (214, 150)):    # bare trees
        r.rect(x0 - 2, y0 - 20, x0 + 2, y0, O); r.vl(x0, y0 - 19, y0 - 1, (40, 32, 40))
        for d in (-1, 1):
            for k in range(8): r.set(x0 + d * k, y0 - 14 - k, O); r.set(x0 + d * k, y0 - 13 - k, (40, 32, 40))
    path(r, (136, 128, 136), (96, 88, 96), slabs=(112, 104, 112))
    dais(r, (152, 144, 152), (96, 88, 96), (168, 40, 56), (232, 64, 72), (255, 200, 200))
    mat(r, (96, 88, 96), (232, 64, 72))
    return r

def zygarde():
    """Terminus Cave: dark rock, a floor of green hexagon cells."""
    r = Room(718)
    cave(r, ((72, 88, 72), (48, 60, 52), (32, 40, 36)), ((152, 160, 136), (136, 144, 120), (120, 128, 104)), 300)
    for j, y in enumerate(range(38, H, 14)):
        for x in range(-8 + (j % 2) * 12, W, 24):
            pts = [(x + 8 * math.cos(a * math.pi / 3), y + 6 * math.sin(a * math.pi / 3)) for a in range(6)]
            for k in range(6):
                (ax, ay), (bx, by) = pts[k], pts[(k + 1) % 6]
                for t in range(9): r.set(ax + (bx - ax) * t / 8, ay + (by - ay) * t / 8, (72, 136, 80))
            if r.rnd.random() < 0.15 and side_ok(x): r.set(x, y, (152, 248, 120)); r.set(x + 1, y, (96, 216, 96))
    path(r, (168, 176, 152), (112, 120, 96), slabs=(136, 144, 120))
    dais(r, (184, 192, 168), (112, 120, 96), (48, 168, 88), (120, 240, 120), (224, 255, 208))
    mat(r, (112, 120, 96), (72, 136, 80))
    return r

def diancie():
    """A diamond mine: violet cave, pink and white crystals growing from the floor."""
    r = Room(719)
    cave(r, ((136, 104, 168), (104, 80, 136), (72, 56, 104)), ((96, 80, 120), (80, 64, 104), (64, 48, 88)))
    for x, y, h in ((24, 70, 22), (40, 66, 14), (204, 70, 22), (220, 64, 12), (30, 150, 18), (210, 150, 18), (60, 190, 12), (182, 192, 14), (66, 108, 10), (176, 110, 10)):
        crystal(r, x, y, h, (255, 200, 232), (232, 128, 184), (255, 255, 255))
    for _ in range(40):
        x, y = r.rnd.randint(0, 236), r.rnd.randint(36, 200)
        if side_ok(x): r.set(x, y, (255, 216, 240))
    path(r, (120, 104, 144), (80, 64, 104), slabs=(104, 88, 128))
    dais(r, (232, 224, 240), (128, 112, 152), (232, 128, 184), (255, 168, 216), (255, 255, 255))
    mat(r, (80, 64, 104), (255, 168, 216))
    return r

def hoopa():
    """A desert under a hot sky, golden rings hanging open in the air at the sides."""
    r = Room(720)
    outdoor(r, [(248, 216, 160), (248, 192, 136), (232, 168, 120)], ((240, 208, 144), (224, 184, 120), (200, 160, 96)), 400, 44, 27)
    for x, y in ((36, 70), (204, 70), (40, 160), (200, 160)):
        r.ring(x, y, 16, 20, O, 4); r.ring(x, y, 16, 20, (248, 200, 72), 2.2); r.ring(x - 1, y - 1, 15, 19, (255, 240, 160), 0.6)
        r.ell(x, y, 12, 16, (72, 40, 104)); r.speck(x - 10, y - 14, x + 10, y + 14, (184, 120, 232), 30, (72, 40, 104))
    path(r, (232, 200, 136), (200, 160, 96), x0=110, x1=129)
    dais(r, (248, 232, 200), (200, 160, 96), (152, 88, 184), (248, 200, 72), (255, 248, 200))
    mat(r, (200, 160, 96), (152, 88, 184))
    return r

def volcanion():
    """A steam vent mountain: dark rock, hot blue pools, white steam rising."""
    r = Room(721)
    cave(r, ((112, 88, 80), (80, 64, 60), (56, 44, 44)), ((96, 80, 72), (80, 64, 60), (64, 52, 48)))
    for x, y in ((40, 90), (200, 90), (44, 170), (196, 170)):
        r.ell(x, y, 22, 10, O); r.ell(x, y, 21, 9, (72, 152, 200)); r.ell(x - 4, y - 2, 10, 4, (136, 200, 232))
        for k in range(5):
            r.blob(x + r.rnd.randint(-10, 10), y - 14 - k * 8, 6, (232, 232, 240), (200, 200, 216), (255, 255, 255))
    path(r, (112, 96, 88), (72, 56, 52), slabs=(96, 80, 72))
    dais(r, (136, 120, 112), (80, 64, 60), (232, 104, 56), (120, 200, 248), (232, 248, 255))
    mat(r, (72, 56, 52), (232, 104, 56))
    return r

def tapu(r, sky_cols, ground, stone, accent, glow, glow2, extra):
    """Alola's island ruins: an open grassy ridge, old stone pillars with the tapu's totem marks at the sides."""
    outdoor(r, sky_cols, ground)
    S1, S2, S3 = stone
    for x, y in ((28, 96), (212, 96), (28, 176), (212, 176)):
        r.rect(x - 9, y - 34, x + 9, y + 4, O); r.rect(x - 8, y - 33, x + 8, y + 3, S2); r.vl(x - 7, y - 32, y + 2, S1); r.vl(x + 7, y - 32, y + 2, S3)
        r.rect(x - 4, y - 24, x + 4, y - 18, accent); r.hl(x - 4, x + 4, y - 12, accent); r.set(x, y - 8, accent)
    extra(r)
    path(r, S2, S3, x0=110, x1=129, slabs=S3)
    dais(r, S1, S3, accent, glow, glow2)
    mat(r, S3, accent)

def tapu_koko():
    r = Room(785)
    def e(r):
        for x0 in (60, 180):
            x, y = x0, 0
            while y < 40: r.set(x, y, (255, 248, 160)); r.set(x + 1, y, (255, 255, 255)); x += r.rnd.choice((-1, 1, 1, 0)); y += 1
    tapu(r, [(248, 168, 88), (248, 200, 112), (255, 232, 160)], ((152, 192, 96), (120, 160, 80), (88, 128, 64)), ((216, 208, 176), (184, 176, 144), (144, 136, 112)), (232, 168, 40), (255, 216, 64), (255, 255, 208), e)
    return r

def tapu_lele():
    r = Room(786)
    def e(r):
        for _ in range(260):
            x, y = r.rnd.randint(0, 236), r.rnd.randint(46, 205)
            if side_ok(x) and y < 190: continue
            c = r.rnd.choice(((248, 160, 200), (255, 216, 232), (232, 112, 168))); r.set(x, y, c); r.set(x + 1, y, c)
        for _ in range(40): x, y = r.rnd.randint(0, 236), r.rnd.randint(0, 200); r.set(x, y, (255, 200, 232))
    tapu(r, [(232, 200, 248), (248, 216, 240), (255, 232, 240)], ((152, 208, 136), (120, 184, 120), (96, 152, 104)), ((232, 224, 216), (200, 192, 184), (160, 152, 152)), (232, 112, 168), (248, 160, 216), (255, 232, 248), e)
    return r

def tapu_bulu():
    r = Room(787)
    def e(r):
        for x, y in ((64, 70), (176, 70), (60, 140), (180, 140), (70, 196), (170, 196)):
            r.rect(x - 3, y - 14, x + 3, y, O); r.rect(x - 2, y - 13, x + 2, y, (88, 152, 72)); r.vl(x - 1, y - 12, y - 1, (128, 192, 96))
            r.rect(x - 7, y - 9, x - 3, y - 7, O); r.rect(x - 7, y - 14, x - 5, y - 8, O); r.rect(x - 6, y - 13, x - 6, y - 8, (88, 152, 72))
    tapu(r, [(248, 200, 136), (240, 176, 112), (232, 152, 96)], ((216, 152, 96), (192, 128, 80), (160, 104, 64)), ((216, 192, 160), (184, 160, 128), (144, 120, 96)), (200, 72, 56), (152, 216, 88), (232, 255, 200), e)
    return r

def tapu_fini():
    r = Room(788)
    def e(r):
        for y in range(44, H, 18):                                  # drifting mist bands
            for x in range((y * 11) % 60, W, 60):
                if side_ok(x) or y > 80: r.rect(x, y, x + 22, y + 1, (216, 232, 240)); r.hl(x + 4, x + 16, y - 1, (240, 248, 252))
    tapu(r, [(176, 200, 216), (200, 216, 228), (216, 228, 236)], ((144, 192, 168), (120, 168, 152), (96, 144, 128)), ((208, 216, 224), (176, 184, 200), (136, 144, 168)), (88, 112, 200), (136, 200, 248), (232, 248, 255), e)
    return r

def altar(r, seed, sky_cols, floor, accent, emblem, glow, glow2, star_n=0, orb=None):
    """Altar of the Sunne / Moone: a marble terrace on a peak, open sky above, the emblem set in the floor."""
    sky(r, sky_cols, 48)
    if star_n: stars(r, star_n, 0, 44)
    if orb: orb(r)
    F1, F2, F3 = floor
    r.rect(0, 40, W - 1, H - 1, F2)
    for y in range(40, H, 16):
        r.hl(0, W - 1, y, F3)
        for x in range((8 if (y // 16) % 2 else 0), W, 16): r.vl(x, y, y + 15, F3); r.hl(x + 1, x + 14, y + 1, F1)
    for x in range(0, W, 12):                                       # balustrade at the cliff edge
        r.rect(x, 32, x + 6, 40, O); r.rect(x + 1, 33, x + 5, 40, F1)
    r.hl(0, W - 1, 31, O); r.rect(0, 30, W - 1, 31, F3)
    for cx, cy in ((40, 130), (200, 130)): emblem(r, cx, cy)
    path(r, F1, F3, slabs=F2)
    dais(r, F1, F3, accent, glow, glow2)
    mat(r, F3, accent)

def sun(r, cx, cy, c=(248, 176, 56)):
    r.ell(cx, cy, 10, 7, O); r.ell(cx, cy, 9, 6, c)
    for k in range(8):
        a = k * math.pi / 4
        for t in range(12, 18): r.set(cx + t * math.cos(a), cy + t * 0.7 * math.sin(a), c)

def moon(r, cx, cy, c=(176, 160, 248)):
    r.ell(cx, cy, 10, 7, O); r.ell(cx, cy, 9, 6, c); r.ell(cx + 5, cy - 2, 8, 6, (200, 192, 216))

def cosmog():
    """Altar on the peak at dusk, the first stars out: where Cosmog came through."""
    r = Room(789)
    altar(r, 789, [(40, 48, 112), (88, 72, 152), (200, 120, 168)], ((216, 216, 232), (184, 184, 208), (144, 144, 176)),
          (96, 120, 216), lambda r, x, y: (r.ring(x, y, 12, 8, (96, 120, 216), 2), stars(r, 6, y - 6, y + 6, ((96, 120, 216),))),
          (144, 176, 255), (232, 240, 255), 60)
    return r

def cosmoem():
    """Altar at full night: deep violet sky thick with stars, the cocoon's glow."""
    r = Room(790)
    altar(r, 790, [(16, 16, 48), (40, 32, 88), (72, 48, 120)], ((176, 176, 200), (144, 144, 176), (112, 112, 144)),
          (232, 200, 96), lambda r, x, y: (r.ring(x, y, 12, 8, (232, 200, 96), 2), r.ring(x, y, 6, 4, (96, 120, 216), 1.5)),
          (248, 216, 120), (255, 248, 216), 120)
    return r

def solgaleo():
    r = Room(791)
    altar(r, 791, [(248, 160, 64), (248, 200, 96), (255, 232, 176)], ((248, 240, 224), (224, 216, 192), (184, 176, 152)),
          (232, 136, 40), sun, (248, 184, 56), (255, 248, 208), 0, lambda r: sun(r, 206, 16, (255, 240, 160)))
    return r

def lunala():
    r = Room(792)
    altar(r, 792, [(24, 24, 72), (48, 48, 112), (80, 72, 152)], ((200, 200, 224), (168, 168, 200), (128, 128, 168)),
          (144, 112, 232), moon, (176, 144, 255), (240, 232, 255), 80, lambda r: moon(r, 206, 16, (248, 240, 200)))
    return r

def necrozma():
    """Ultra Space: black void, prism shards of broken light."""
    r = Room(800)
    sky(r, [(40, 24, 72), (64, 40, 112), (88, 56, 144)], H)
    stars(r, 120, 0, 207, ((80, 80, 120), (160, 160, 200)))
    prism = ((248, 96, 96), (248, 200, 72), (96, 216, 120), (72, 168, 248), (176, 96, 232))
    for k, (x, y) in enumerate(((30, 60), (210, 54), (26, 140), (214, 150), (60, 196), (180, 196))):
        crystal(r, x, y, 26, (80, 80, 104), (48, 48, 72), prism[k % 5])
        for t in range(30): r.set(x + 6 + t, y - 20 + t // 2, prism[(k + t // 6) % 5])
    path(r, (48, 48, 72), (24, 24, 40), slabs=(40, 40, 60))
    dais(r, (200, 192, 224), (112, 104, 144), (248, 200, 72), (255, 232, 120), (255, 255, 255))
    mat(r, (24, 24, 40), (248, 200, 72))
    return r

def gear(r, cx, cy, rr, c, light):
    for k in range(10):
        a = k * math.pi / 5
        r.rect(int(cx + (rr + 2) * math.cos(a)) - 2, int(cy + (rr + 2) * math.sin(a)) - 2, int(cx + (rr + 2) * math.cos(a)) + 2, int(cy + (rr + 2) * math.sin(a)) + 2, O)
    r.ell(cx, cy, rr + 1, rr + 1, O); r.ell(cx, cy, rr, rr, c); r.ring(cx - 1, cy - 1, rr - 2, rr - 2, light)
    for k in range(10):
        a = k * math.pi / 5
        r.rect(int(cx + (rr + 2) * math.cos(a)) - 1, int(cy + (rr + 2) * math.sin(a)) - 1, int(cx + (rr + 2) * math.cos(a)) + 1, int(cy + (rr + 2) * math.sin(a)) + 1, c)
    r.ell(cx, cy, rr // 3 + 1, rr // 3 + 1, O); r.ell(cx, cy, rr // 3, rr // 3, (64, 48, 40))

def magearna():
    """A clockmaker's hall: brass and wood, gears turning on the walls."""
    r = Room(801)
    B1, B2, B3 = (232, 192, 112), (200, 152, 80), (152, 112, 64)
    r.rect(0, 0, W - 1, 31, (112, 72, 56))
    for x in range(0, W, 20): r.vl(x, 0, 31, (88, 56, 44))
    for x, y, rr in ((20, 16, 11), (52, 10, 7), (188, 10, 7), (220, 16, 11)): gear(r, x, y, rr, B2, B1)
    r.hl(0, W - 1, 31, O)
    r.rect(0, 32, W - 1, H - 1, (160, 112, 72))
    for y in range(32, H, 8): r.hl(0, W - 1, y, (136, 92, 60))
    for y in range(32, H, 8):
        for x in range(((y // 8) % 2) * 24, W, 48): r.vl(x, y, y + 7, (136, 92, 60))
    for x, y, rr in ((36, 100, 14), (204, 100, 14), (40, 172, 10), (200, 172, 10)): gear(r, x, y, rr, B2, B1)
    path(r, B2, B3, slabs=B3)
    dais(r, B1, B3, (200, 64, 64), (248, 112, 112), (255, 224, 224))
    mat(r, B3, (200, 64, 64))
    return r

ROOMS = dict(xerneas=xerneas, yveltal=yveltal, zygarde=zygarde, diancie=diancie, hoopa=hoopa, volcanion=volcanion,
             tapu_koko=tapu_koko, tapu_lele=tapu_lele, tapu_bulu=tapu_bulu, tapu_fini=tapu_fini,
             cosmog=cosmog, cosmoem=cosmoem, solgaleo=solgaleo, lunala=lunala, necrozma=necrozma, magearna=magearna)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber6_%s.png' % name))
