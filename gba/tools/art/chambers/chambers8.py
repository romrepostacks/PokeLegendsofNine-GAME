# SUMMONING CHAMBERS, round 8: Paldea and Kitakami, the last twelve. python3 chambers8.py OUTDIR [names...]
# Same rules: nothing standing straight behind the dais (x 84..156, y 0..70), legendary placed by place.py.
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path
from chambers3 import tree
from chambers5 import sky, speckle
from chambers6 import outdoor, cave, side_ok, stars, crystal

def shrine(r, seed, wall, floor, accent, glow, glow2, stakes, extra=None):
    """A Treasure of Ruin's sealed shrine: dark stone, the coloured stakes that hold the seal at the four corners."""
    W1, W2, W3 = wall
    r.rect(0, 0, W - 1, 31, W2)
    for y in range(0, 32, 8):
        r.hl(0, W - 1, y, W3)
        for x in range((8 if (y // 8) % 2 else 0), W, 16): r.vl(x, y, y + 7, W3)
    for x in (28, 212):                                             # sealed doors in the back wall
        r.rect(x - 12, 4, x + 12, 31, O); r.rect(x - 11, 5, x + 11, 31, W3); r.vl(x, 5, 31, O)
        for y in (12, 20): r.hl(x - 9, x + 9, y, stakes)
    r.hl(0, W - 1, 31, O)
    F1, F2, F3 = floor
    r.rect(0, 32, W - 1, H - 1, F2)
    for y in range(32, H, 16):
        r.hl(0, W - 1, y, F3)
        for x in range((8 if (y // 16) % 2 else 0), W, 16): r.vl(x, y, y + 15, F3); r.hl(x + 1, x + 14, y + 1, F1)
    for x, y in ((36, 96), (204, 96), (36, 176), (204, 176)):     # the stakes
        r.rect(x - 3, y - 26, x + 3, y, O); r.rect(x - 2, y - 25, x + 2, y - 1, stakes); r.vl(x - 1, y - 24, y - 2, tuple(min(255, c + 60) for c in stakes))
        for k in range(4): r.set(x - 5 + k, y - 28 - k, O); r.set(x + 5 - k, y - 28 - k, O)
        r.ell(x, y + 2, 6, 2, W3)
    if extra: extra(r)
    path(r, F1, F3, slabs=F2)
    dais(r, F1, F3, accent, glow, glow2)
    mat(r, F3, accent)

def wo_chien():
    r = Room(1001)
    def e(r):                                                       # withered vines over the floor
        for x0 in (60, 170):
            for y in range(40, 200, 2): r.set(x0 + int(8 * math.sin(y / 9)), y, (104, 96, 56))
        for _ in range(30):
            x, y = r.rnd.randint(4, 236), r.rnd.randint(40, 200)
            if side_ok(x): r.set(x, y, (136, 128, 72)); r.set(x + 1, y, (104, 96, 56))
    shrine(r, 1001, ((88, 96, 72), (64, 72, 56), (40, 48, 40)), ((200, 196, 168), (176, 172, 144), (144, 140, 116)), (88, 128, 56), (152, 200, 88), (232, 255, 200), (88, 152, 56), e)
    return r

def chien_pao():
    r = Room(1002)
    def e(r):
        for _ in range(60):
            x, y = r.rnd.randint(2, 236), r.rnd.randint(36, 205)
            if side_ok(x) or y > 80: r.hl(x, x + 3, y, (232, 240, 248))
    shrine(r, 1002, ((112, 120, 144), (88, 96, 120), (64, 72, 96)), ((176, 188, 208), (152, 164, 188), (120, 132, 160)), (72, 104, 176), (136, 200, 248), (240, 252, 255), (88, 120, 216), e)
    return r

def ting_lu():
    r = Room(1003)
    def e(r):
        for x, y in ((64, 120), (176, 120), (70, 190), (170, 190)): r.blob(x, y, 9, (136, 104, 72), O, (176, 144, 104))
    shrine(r, 1003, ((120, 96, 72), (96, 72, 56), (64, 48, 40)), ((176, 148, 112), (152, 124, 92), (120, 96, 72)), (136, 88, 56), (216, 160, 88), (255, 232, 192), (168, 112, 64), e)
    return r

def chi_yu():
    r = Room(1004)
    def e(r):
        for x, y in ((64, 110), (176, 110), (64, 186), (176, 186)):  # braziers
            r.rect(x - 6, y - 4, x + 6, y + 4, O); r.rect(x - 5, y - 3, x + 5, y + 3, (88, 72, 64))
            for k in range(10): w = max(0, 4 - k // 2); r.hl(x - w, x + w, y - 5 - k, (255, 200, 72) if k > 4 else (232, 88, 40))
    shrine(r, 1004, ((104, 72, 72), (80, 52, 52), (56, 36, 40)), ((152, 120, 112), (128, 96, 92), (96, 72, 72)), (184, 56, 48), (248, 128, 64), (255, 224, 176), (216, 72, 48), e)
    return r

def area_zero(r, seed, tint, glow, glow2, crystals):
    """Area Zero: the crater floor, terastal crystals glittering, the far crater wall under a hazy sky."""
    sky(r, [(176, 200, 216), (200, 216, 224), (216, 224, 224)], 40)
    for x in range(W):                                              # crater rim
        h = 18 + int(6 * math.sin(x / 23) + 3 * math.sin(x / 7))
        r.vl(x, h, 36, (136, 144, 136)); r.set(x, h, O)
    outdoor(r, [(176, 200, 216)], ((152, 192, 136), (128, 168, 120), (104, 144, 104)), 500, horizon=36)
    for x in range(W):
        h = 18 + int(6 * math.sin(x / 23) + 3 * math.sin(x / 7))
        r.vl(x, h, 35, (136, 144, 136)); r.set(x, h, O)
    sky_cols = [(176, 200, 216), (200, 216, 224)]
    for x in range(W):
        h = 18 + int(6 * math.sin(x / 23) + 3 * math.sin(x / 7))
        for y in range(0, h): r.set(x, y, sky_cols[0] if y < 9 else sky_cols[1])
    for k, (x, y, h) in enumerate(((24, 80, 20), (44, 70, 12), (200, 72, 14), (220, 82, 22), (30, 160, 16), (212, 160, 16), (50, 200, 12), (190, 200, 12))):
        c = crystals[k % len(crystals)]
        crystal(r, x, y, h, c[0], c[1], (255, 255, 255))
    path(r, (184, 192, 176), (128, 136, 120), x0=110, x1=129, slabs=(160, 168, 152))
    dais(r, (224, 228, 216), (136, 144, 128), tint, glow, glow2)
    mat(r, (128, 136, 120), tint)

TERA = (((248, 168, 200), (216, 96, 152)), ((168, 216, 255), (96, 152, 232)), ((255, 232, 160), (232, 176, 72)), ((200, 248, 200), (104, 200, 136)))

def koraidon():
    r = Room(1007); area_zero(r, 1007, (216, 64, 64), (248, 144, 88), (255, 232, 200), TERA); return r

def miraidon():
    r = Room(1008); area_zero(r, 1008, (88, 72, 200), (136, 200, 248), (232, 248, 255), TERA); return r

def kitakami(r, seed, accent, glow, glow2, sky_cols, extra=None):
    """Kitakami: rice terraces and red maple on the hills, a stone path to the dais."""
    outdoor(r, sky_cols, ((168, 192, 104), (136, 168, 88), (112, 144, 72)), 400)
    for y in range(60, H, 20):                                      # terrace edges
        for x in range(0, W):
            if side_ok(x) or y > 100: r.set(x, y + int(2 * math.sin(x / 11 + y)), (104, 128, 64))
    for x, y in ((16, 40), (46, 32), (194, 32), (224, 40), (20, 150), (220, 150)):
        tree(r, x, y, (248, 144, 88), (216, 80, 56), (152, 48, 48), (104, 72, 56))
    if extra: extra(r)
    path(r, (192, 184, 160), (144, 136, 112), x0=110, x1=129, slabs=(168, 160, 136))
    dais(r, (224, 216, 192), (144, 136, 112), accent, glow, glow2)
    mat(r, (144, 136, 112), accent)

def okidogi():
    r = Room(1014)
    def e(r):
        for x, y in ((60, 120), (180, 120)): r.rect(x - 5, y - 22, x + 5, y, O); r.rect(x - 4, y - 21, x + 4, y - 1, (160, 160, 168)); r.hl(x - 4, x + 4, y - 15, (88, 168, 72))
    kitakami(r, 1014, (72, 136, 56), (136, 216, 96), (232, 255, 216), [(200, 216, 232), (216, 228, 236), (232, 236, 236)], e)
    return r

def munkidori():
    r = Room(1015)
    def e(r):
        for x, y in ((60, 120), (180, 120)): r.rect(x - 5, y - 22, x + 5, y, O); r.rect(x - 4, y - 21, x + 4, y - 1, (160, 160, 168)); r.hl(x - 4, x + 4, y - 15, (176, 88, 200))
    kitakami(r, 1015, (136, 72, 168), (200, 136, 232), (248, 232, 255), [(200, 216, 232), (216, 228, 236), (232, 236, 236)], e)
    return r

def fezandipiti():
    r = Room(1016)
    def e(r):
        for x, y in ((60, 120), (180, 120)): r.rect(x - 5, y - 22, x + 5, y, O); r.rect(x - 4, y - 21, x + 4, y - 1, (160, 160, 168)); r.hl(x - 4, x + 4, y - 15, (232, 112, 168))
    kitakami(r, 1016, (184, 72, 128), (248, 144, 192), (255, 232, 244), [(200, 216, 232), (216, 228, 236), (232, 236, 236)], e)
    return r

def ogerpon():
    """Kitakami at the autumn festival: paper lanterns strung along the sides, the masked one's mountain."""
    r = Room(1017)
    def e(r):
        for y0 in (50, 130):
            for x0, x1 in ((0, 80), (160, 240)):
                for x in range(x0, x1): r.set(x, y0 + int(4 * math.sin((x - x0) / 80 * math.pi)), O)
                for x in range(x0 + 8, x1, 16):
                    yy = y0 + int(4 * math.sin((x - x0) / 80 * math.pi))
                    r.ell(x, yy + 6, 4, 5, O); r.ell(x, yy + 6, 3, 4, (248, 120, 72)); r.set(x - 1, yy + 4, (255, 216, 160))
    kitakami(r, 1017, (64, 136, 72), (136, 216, 120), (232, 255, 224), [(232, 176, 136), (248, 208, 160), (248, 232, 200)], e)
    return r

def terapagos():
    """The Terarium's heart below Area Zero: a crystal cavern, every wall faceted in tera colours."""
    r = Room(1024)
    cave(r, ((88, 104, 136), (64, 80, 112), (40, 52, 80)), ((112, 128, 160), (96, 112, 144), (80, 96, 128)), 300)
    for k, (x, y, h) in enumerate(((16, 30, 24), (40, 28, 18), (68, 26, 12), (172, 26, 12), (200, 28, 18), (224, 30, 24),
                                    (24, 100, 20), (216, 100, 20), (30, 170, 18), (210, 170, 18), (60, 204, 14), (180, 204, 14))):
        c = TERA[k % 4]; crystal(r, x, y, h, c[0], c[1], (255, 255, 255))
    for _ in range(50):
        x, y = r.rnd.randint(2, 236), r.rnd.randint(36, 205)
        if side_ok(x): r.set(x, y, TERA[r.rnd.randint(0, 3)][0])
    path(r, (136, 152, 184), (88, 104, 136), slabs=(112, 128, 160))
    dais(r, (200, 216, 240), (112, 128, 160), (96, 152, 232), (168, 216, 255), (255, 255, 255))
    mat(r, (88, 104, 136), (96, 152, 232))
    return r

def pecharunt():
    """Paradise Barrens' Chonky Mochi grotto: a purple poisoned glade, peach-coloured mochi lanterns."""
    r = Room(1025)
    outdoor(r, [(64, 40, 88), (104, 64, 120), (152, 96, 152)], ((120, 96, 136), (96, 72, 112), (72, 52, 88)), 500)
    for x, y in ((16, 40), (46, 32), (194, 32), (224, 40)): tree(r, x, y, (136, 104, 152), (96, 64, 120), (64, 40, 88), (88, 64, 72))
    for x, y in ((40, 110), (200, 110), (44, 186), (196, 186)):
        r.ell(x, y, 12, 8, O); r.ell(x, y, 11, 7, (152, 64, 168)); r.ell(x - 3, y - 2, 4, 2, (200, 120, 216))   # poison pools
        r.ring(x + 6, y - 4, 2, 2, (216, 152, 232))
    for x, y in ((72, 70), (168, 70), (76, 150), (164, 150)):     # mochi
        r.ell(x, y, 6, 5, O); r.ell(x, y, 5, 4, (248, 192, 200)); r.set(x - 2, y - 2, (255, 240, 240))
    path(r, (160, 136, 168), (104, 80, 120), x0=110, x1=129, slabs=(136, 112, 152))
    dais(r, (224, 208, 228), (128, 104, 144), (136, 56, 160), (216, 120, 232), (255, 232, 248))
    mat(r, (104, 80, 120), (216, 120, 232))
    return r

ROOMS = {'wo_chien': wo_chien, 'chien_pao': chien_pao, 'ting_lu': ting_lu, 'chi_yu': chi_yu, 'koraidon': koraidon, 'miraidon': miraidon,
         'okidogi': okidogi, 'munkidori': munkidori, 'fezandipiti': fezandipiti, 'ogerpon': ogerpon, 'terapagos': terapagos, 'pecharunt': pecharunt}

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber8_%s.png' % name))
