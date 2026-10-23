# SUMMONING CHAMBERS, round 7: Alola's last and Galar. python3 chambers7.py OUTDIR [names...]
# Same rules as round 6: nothing standing straight behind the dais (x 84..156, y 0..70), legendary placed by place.py.
import sys, os, math
from chambers import Room, W, H, O, LX, LY, mat, dais, path
from chambers3 import tree
from chambers4 import tomb, braille
from chambers5 import sky, speckle
from chambers6 import outdoor, cave, side_ok, stars, crystal, gear

def marshadow():
    """A shadowed grove at dusk: a ring of standing stones, the ground dark with tree shadow."""
    r = Room(802)
    outdoor(r, [(56, 48, 88), (96, 72, 112), (152, 104, 120)], ((152, 176, 128), (128, 152, 112), (104, 128, 96)), 600)
    for x, y in ((14, 40), (44, 32), (196, 32), (226, 40)): tree(r, x, y, (64, 104, 72), (40, 72, 56), (24, 48, 40))
    for k in range(10):                                             # standing stones around the room
        a = k * math.pi / 5 + 0.3
        x, y = int(120 + 96 * math.cos(a)), int(128 + 66 * math.sin(a))
        if not side_ok(x) and y < 110: continue
        r.rect(x - 5, y - 16, x + 5, y, O); r.rect(x - 4, y - 15, x + 4, y - 1, (112, 112, 128)); r.vl(x - 3, y - 14, y - 2, (144, 144, 160))
        r.hl(x - 7, x + 7, y + 1, (32, 40, 40))
    path(r, (96, 104, 96), (56, 64, 60), x0=110, x1=129, slabs=(80, 88, 80))
    dais(r, (216, 216, 208), (128, 128, 120), (72, 72, 96), (136, 120, 200), (232, 224, 255))
    mat(r, (56, 64, 60), (136, 120, 200))
    return r

def zeraora():
    """A storm-lit plateau of black rock with lightning rods crackling at the sides."""
    r = Room(807)
    outdoor(r, [(40, 40, 64), (64, 64, 96), (96, 96, 128)], ((88, 88, 96), (64, 64, 72), (48, 48, 56)), 500)
    for x, y in ((30, 90), (210, 90), (30, 170), (210, 170)):
        r.rect(x - 2, y - 36, x + 2, y, O); r.vl(x, y - 35, y - 1, (184, 184, 200)); r.ell(x, y - 38, 4, 4, O); r.ell(x, y - 38, 3, 3, (255, 232, 96))
        xx = x
        for k in range(16): r.set(xx, y - 40 - k, (255, 248, 160)); xx += (1, -1, 1, 0)[k % 4]
        r.ell(x, y + 2, 8, 3, (40, 40, 48))
    for _ in range(18):
        x, y = r.rnd.randint(2, 236), r.rnd.randint(50, 200)
        if side_ok(x): r.hl(x, x + 2, y, (248, 216, 72))
    path(r, (112, 112, 120), (64, 64, 72), x0=110, x1=129, slabs=(88, 88, 96))
    dais(r, (136, 136, 144), (72, 72, 80), (80, 144, 248), (248, 216, 72), (255, 255, 216))
    mat(r, (64, 64, 72), (248, 216, 72))
    return r

def metal_floor(r, P1, P2, P3, block=24):
    r.rect(0, 32, W - 1, H - 1, P2)
    for y in range(32, H, block):
        r.hl(0, W - 1, y, P3)
        for x in range(0, W, block):
            r.vl(x, y, y + block - 1, P3); r.hl(x + 1, x + block - 2, y + 1, P1)
            for dx, dy in ((3, 3), (block - 4, 3), (3, block - 4), (block - 4, block - 4)): r.set(x + dx, y + dy, P1)

def meltan():
    """A scrapyard at dawn: riveted steel plates, heaps of nuts and bolts at the sides."""
    r = Room(808)
    sky(r, [(232, 184, 152), (248, 216, 176), (248, 232, 208)])
    for x in range(0, W, 34):                                       # a far row of stacked crates
        if side_ok(x + 10): r.rect(x, 14, x + 22, 31, O); r.rect(x + 1, 15, x + 21, 31, (152, 152, 168)); r.hl(x + 1, x + 21, 22, (120, 120, 136))
    r.hl(0, W - 1, 31, O)
    metal_floor(r, (184, 184, 192), (152, 152, 160), (112, 112, 120))
    for x, y in ((40, 80), (200, 80), (36, 168), (204, 168)):
        r.blob(x, y, 14, (128, 128, 136), O, (176, 176, 184))
        for _ in range(10):
            xx, yy = x + r.rnd.randint(-12, 12), y + r.rnd.randint(-8, 6)
            r.ring(xx, yy, 2, 2, (232, 200, 72)); r.set(xx, yy, (96, 96, 104))
    path(r, (176, 176, 184), (112, 112, 120), slabs=(144, 144, 152))
    dais(r, (200, 200, 208), (120, 120, 128), (232, 184, 56), (248, 216, 96), (255, 248, 216))
    mat(r, (112, 112, 120), (232, 184, 56))
    return r

def melmetal():
    """A foundry: dark iron floor, channels of molten steel glowing at the sides."""
    r = Room(809)
    r.rect(0, 0, W - 1, 31, (56, 52, 56))
    for x in range(0, W, 24): r.vl(x, 0, 31, (40, 36, 40)); r.hl(x, x + 23, 10, (40, 36, 40))
    r.hl(0, W - 1, 31, O)
    metal_floor(r, (104, 100, 104), (80, 76, 80), (56, 52, 56))
    for x in (40, 200):                                             # molten channels
        r.rect(x - 9, 36, x + 9, H - 1, O); r.rect(x - 8, 36, x + 8, H - 1, (232, 104, 40))
        for y in range(38, H, 6): r.hl(x - 6, x + 2, y, (255, 184, 72)); r.set(x + 4, y + 3, (255, 232, 160))
    path(r, (104, 100, 104), (56, 52, 56), slabs=(88, 84, 88))
    dais(r, (136, 132, 136), (72, 68, 72), (232, 184, 56), (255, 144, 56), (255, 232, 176))
    mat(r, (56, 52, 56), (232, 184, 56))
    return r

def weald(r, seed, tint, glow, glow2, crest):
    """The Slumbering Weald: deep blue-green forest in fog, a stone circle and the hero's crest in the floor."""
    sky(r, [(136, 160, 184), (160, 184, 200), (184, 200, 208)], 48)
    G1, G2, G3 = (128, 168, 136), (104, 144, 120), (80, 120, 104)
    r.rect(0, 36, W - 1, H - 1, G2)
    for _ in range(600): r.set(r.rnd.randint(0, 239), r.rnd.randint(38, 207), r.rnd.choice((G1, G3)))
    for x, y in ((10, 38), (40, 30), (70, 40), (170, 40), (200, 30), (230, 38), (16, 120), (224, 120), (20, 196), (220, 196)):
        tree(r, x, y, (104, 152, 144), (56, 104, 104), (32, 72, 80), (80, 64, 56))
    for y in range(46, H, 20):
        for x in range((y * 17) % 80, W, 80):
            if side_ok(x) or y > 90: r.hl(x, x + 14, y, (176, 200, 184))
    for x, y in ((50, 150), (190, 150)): crest(r, x, y)
    path(r, (152, 160, 160), (96, 104, 112), slabs=(128, 136, 136))
    dais(r, (176, 184, 184), (104, 112, 120), tint, glow, glow2)

def sword(r, x, y, c=(96, 152, 232)):
    r.rect(x - 2, y - 14, x + 2, y + 6, O); r.vl(x, y - 13, y + 2, (232, 236, 248)); r.hl(x - 5, x + 5, y + 2, O); r.hl(x - 4, x + 4, y + 3, c); r.vl(x, y + 4, y + 6, (120, 88, 56))

def shield(r, x, y, c=(208, 72, 88)):
    r.ell(x, y, 8, 9, O); r.ell(x, y, 7, 8, c); r.ell(x - 2, y - 2, 3, 3, (248, 184, 120))

def zacian():
    r = Room(888); weald(r, 888, (72, 120, 216), (120, 184, 248), (232, 248, 255), sword); mat(r, (96, 104, 112), (72, 120, 216)); return r

def zamazenta():
    r = Room(889); weald(r, 889, (192, 64, 80), (248, 112, 112), (255, 232, 224), shield); mat(r, (96, 104, 112), (192, 64, 80)); return r

def eternatus():
    """The top of the Energy Tower: steel deck, a red-violet sky with the Darkest Day's clouds."""
    r = Room(890)
    sky(r, [(64, 16, 48), (120, 32, 72), (184, 48, 88), (216, 88, 104)], 44)
    for x in range(0, W, 26):
        if side_ok(x + 8): r.blob(x + 8, 14, 9, (88, 24, 56), O, (136, 40, 80))
    r.rect(0, 36, W - 1, 40, (96, 88, 104)); r.hl(0, W - 1, 36, O); r.hl(0, W - 1, 40, O)
    for x in range(0, W, 10): r.vl(x, 37, 39, (144, 136, 152))
    metal_floor(r, (128, 120, 136), (104, 96, 112), (72, 64, 80))
    r.rect(0, 32, W - 1, 35, (64, 16, 48))
    for x, y in ((36, 110), (204, 110), (40, 180), (200, 180)):    # dynamax pillars of light
        r.rect(x - 6, 44, x + 6, y, (232, 72, 120)); r.vl(x - 2, 44, y, (255, 168, 200)); r.ell(x, y, 10, 4, O); r.ell(x, y, 9, 3, (184, 40, 96))
    path(r, (128, 120, 136), (72, 64, 80), slabs=(104, 96, 112))
    dais(r, (152, 144, 160), (80, 72, 88), (184, 40, 96), (248, 88, 152), (255, 216, 232))
    mat(r, (72, 64, 80), (232, 72, 120))
    return r

def dojo(r, seed, wall, mat_c, accent, glow, glow2, scrolls):
    """A dojo hall: wood walls with hanging scrolls, a tatami floor."""
    Wd1, Wd2, Wd3 = wall
    r.rect(0, 0, W - 1, 31, Wd2)
    for x in range(0, W, 30): r.vl(x, 0, 31, Wd3); r.vl(x + 1, 0, 31, Wd1)
    for x in (30, 60, 180, 210):
        r.rect(x - 6, 3, x + 6, 27, O); r.rect(x - 5, 4, x + 5, 26, (240, 232, 208)); r.rect(x - 6, 3, x + 6, 4, Wd3)
        for k in range(3): r.hl(x - 2, x + 2, 9 + k * 5, scrolls)
    r.hl(0, W - 1, 31, O)
    T1, T2, T3 = mat_c
    r.rect(0, 32, W - 1, H - 1, T2)
    for j, y in enumerate(range(32, H, 32)):
        for i, x in enumerate(range(-((j % 2) * 24), W, 48)):
            r.rect(x, y, x + 47, y + 31, T3); r.rect(x + 1, y + 1, x + 46, y + 30, T2)
            for yy in range(y + 3, y + 30, 3): r.hl(x + 2, x + 45, yy, T1)
    path(r, Wd1, Wd3, x0=110, x1=129)
    dais(r, Wd1, Wd3, accent, glow, glow2)
    mat(r, Wd3, accent)

def kubfu():
    r = Room(891)
    dojo(r, 891, ((200, 160, 112), (168, 128, 88), (120, 88, 64)), ((200, 200, 136), (176, 176, 112), (136, 136, 88)), (200, 72, 56), (248, 168, 96), (255, 240, 216), (56, 48, 48))
    return r

def urshifu():
    """The top of the Tower of Two Fists: the two scrolls, Darkness and Water, hung either side."""
    r = Room(892)
    dojo(r, 892, ((152, 120, 96), (120, 92, 72), (80, 60, 52)), ((184, 184, 128), (160, 160, 104), (120, 120, 80)), (88, 80, 120), (120, 168, 232), (232, 240, 255), (56, 48, 48))
    for x, y, c in ((36, 110, (48, 40, 64)), (204, 110, (56, 120, 200))):   # the two great scrolls on stands
        r.rect(x - 12, y - 40, x + 12, y + 4, O); r.rect(x - 11, y - 39, x + 11, y + 3, (240, 232, 208)); r.rect(x - 12, y - 42, x + 12, y - 39, (96, 64, 48))
        r.ell(x, y - 18, 7, 7, c)
    return r

def zarude():
    """Deep jungle: thick leaves crowding every side, hanging vines, a mossy clearing."""
    r = Room(893)
    speckle(r, (72, 128, 64), [(56, 104, 56), (96, 152, 80)], 700, 0)
    for x in range(-10, W, 22):
        if side_ok(x) or True: r.blob(x, 10, 16, (48, 112, 56), O, (88, 160, 80))
    for x, y in ((14, 80), (226, 80), (10, 150), (230, 150), (20, 200), (220, 200), (52, 60), (188, 60)):
        r.blob(x, y, 15, (48, 112, 56), O, (88, 160, 80))
    for x in (60, 76, 164, 180):                                    # vines
        for y in range(16, 72): r.set(x + int(2 * math.sin(y / 5)), y, (64, 136, 56))
        r.ell(x, 72, 3, 2, (104, 176, 80))
    r.ell(120, 92, 70, 60, O); r.ell(120, 92, 69, 59, (184, 168, 120))    # a sunlit clearing of packed earth
    r.speck(52, 34, 188, 150, (160, 144, 96), 300, (184, 168, 120)); r.speck(52, 34, 188, 150, (128, 176, 88), 120, (184, 168, 120))
    path(r, (136, 112, 80), (96, 76, 56), x0=110, x1=129)
    dais(r, (232, 224, 192), (152, 136, 96), (56, 112, 56), (152, 216, 96), (232, 255, 200))
    mat(r, (96, 76, 56), (152, 216, 96))
    return r

def regieleki():
    r = Room(894)
    tomb(r, 894, (248, 232, 152), (224, 200, 112), (176, 152, 72), (240, 216, 128), (200, 176, 88), (152, 128, 56), (80, 184, 248), (232, 255, 255), block=20)
    for _ in range(14):
        x, y = r.rnd.randint(20, 220), r.rnd.randint(40, 196)
        if not side_ok(x): continue
        for k in range(8): r.set(x, y + k, (255, 255, 200)); x += (1, -1)[k % 2]
    mat(r, (152, 128, 56), (80, 184, 248))
    return r

def regidrago():
    r = Room(895)
    tomb(r, 895, (152, 184, 136), (120, 152, 112), (88, 112, 80), (136, 168, 120), (104, 136, 96), (72, 96, 64), (216, 64, 72), (255, 200, 200), block=20)
    for x, y in ((50, 110), (190, 110), (56, 176), (184, 176)):     # dragon-head carvings in the floor
        r.ell(x, y, 10, 6, O); r.ell(x, y, 9, 5, (88, 120, 80)); r.set(x - 4, y - 1, (216, 64, 72)); r.set(x + 4, y - 1, (216, 64, 72))
    mat(r, (72, 96, 64), (216, 64, 72))
    return r

def glastrier():
    """A frozen snowfield: blue-white drifts, ice spikes at the sides, a cold clear sky."""
    r = Room(896)
    outdoor(r, [(160, 192, 232), (192, 216, 240), (224, 236, 248)], ((248, 252, 255), (224, 236, 248), (192, 212, 236)), 400)
    for x, y in ((30, 80), (50, 72), (190, 72), (210, 80), (24, 160), (216, 160), (40, 200), (200, 200)):
        crystal(r, x, y, 20, (232, 248, 255), (152, 200, 240), (255, 255, 255))
    path(r, (208, 224, 240), (160, 184, 216), x0=110, x1=129, slabs=(184, 204, 228))
    dais(r, (232, 240, 248), (160, 184, 216), (88, 152, 216), (136, 208, 248), (240, 252, 255))
    mat(r, (160, 184, 216), (88, 152, 216))
    return r

def spectrier():
    """A graveyard on a moonless night: violet mist, old headstones, ghost lights."""
    r = Room(897)
    outdoor(r, [(24, 16, 40), (40, 32, 64), (64, 48, 88)], ((72, 64, 88), (56, 48, 72), (40, 36, 56)), 500)
    stars(r, 40, 0, 34, ((120, 112, 168), (200, 192, 232)))
    for x, y in ((24, 70), (54, 62), (186, 62), (216, 70), (30, 140), (210, 140), (40, 196), (200, 196), (64, 108), (176, 108)):
        r.rect(x - 6, y - 12, x + 6, y, O); r.ell(x, y - 12, 6, 4, O); r.rect(x - 5, y - 11, x + 5, y - 1, (128, 120, 144)); r.ell(x, y - 12, 5, 3, (128, 120, 144))
        r.hl(x - 2, x + 2, y - 8, (88, 80, 104)); r.vl(x, y - 10, y - 4, (88, 80, 104))
    for _ in range(14):
        x, y = r.rnd.randint(4, 232), r.rnd.randint(44, 196)
        if side_ok(x): r.ell(x, y, 2, 2, (184, 120, 232)); r.set(x, y, (240, 216, 255))
    for y in range(60, H, 24):
        for x in range((y * 7) % 60, W, 60):
            if side_ok(x) or y > 90: r.hl(x, x + 20, y, (104, 88, 136))
    path(r, (88, 80, 104), (48, 44, 64), x0=110, x1=129, slabs=(72, 64, 88))
    dais(r, (208, 200, 224), (120, 112, 144), (120, 72, 184), (184, 120, 232), (240, 224, 255))
    mat(r, (48, 44, 64), (184, 120, 232))
    return r

def calyrex():
    """The Crown Shrine grounds: snow on old stone, a field of Shaderoot carrots at the sides."""
    r = Room(898)
    outdoor(r, [(176, 200, 232), (208, 220, 240), (232, 236, 248)], ((248, 248, 252), (232, 232, 240), (208, 212, 228)), 300)
    for x0 in (16, 168):                                            # carrot rows, tops showing through the snow
        for y in range(70, 200, 16):
            for x in range(x0, x0 + 56, 12):
                r.ell(x, y + 2, 3, 2, (232, 120, 48)); r.set(x - 1, y - 1, (80, 152, 72)); r.set(x + 1, y - 2, (80, 152, 72)); r.set(x, y - 2, (112, 184, 88))
    for x in (60, 180):                                             # stone lanterns
        r.rect(x - 4, 44, x + 4, 66, O); r.rect(x - 3, 45, x + 3, 65, (176, 176, 192)); r.rect(x - 7, 42, x + 7, 46, O); r.rect(x - 2, 50, x + 2, 54, (248, 216, 120))
    path(r, (200, 200, 212), (152, 152, 168), x0=110, x1=129, slabs=(176, 176, 192))
    dais(r, (224, 224, 232), (152, 152, 168), (96, 168, 120), (176, 232, 168), (248, 255, 240))
    mat(r, (152, 152, 168), (96, 168, 120))
    return r

def enamorus():
    """A spring sky shrine above pink clouds, cherry petals drifting."""
    r = Room(905)
    sky(r, [(248, 200, 224), (248, 216, 232), (255, 232, 240)], H)
    for x, y in ((20, 60), (60, 40), (190, 44), (226, 64), (14, 140), (226, 140), (30, 196), (210, 196), (70, 110), (172, 110)):
        r.blob(x, y, 16, (255, 240, 248), (232, 184, 208), (255, 255, 255))
    for _ in range(60):
        x, y = r.rnd.randint(0, 236), r.rnd.randint(0, 205)
        if side_ok(x) or y > 80: r.set(x, y, (240, 128, 176)); r.set(x + 1, y, (255, 176, 208))
    path(r, (248, 224, 232), (216, 168, 192), x0=110, x1=129, slabs=(232, 200, 216))
    dais(r, (255, 244, 248), (216, 168, 192), (216, 96, 152), (248, 144, 192), (255, 232, 244))
    mat(r, (216, 168, 192), (216, 96, 152))
    return r

ROOMS = dict(marshadow=marshadow, zeraora=zeraora, meltan=meltan, melmetal=melmetal, zacian=zacian, zamazenta=zamazenta,
             eternatus=eternatus, kubfu=kubfu, urshifu=urshifu, zarude=zarude, regieleki=regieleki, regidrago=regidrago,
             glastrier=glastrier, spectrier=spectrier, calyrex=calyrex, enamorus=enamorus)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name in sys.argv[2:] or ROOMS:
        ROOMS[name]().save(os.path.join(out, 'chamber7_%s.png' % name))
