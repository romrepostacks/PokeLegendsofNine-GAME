"""Draws the title screen art once into gba/data/ (9.4.1): ARCEUS over the nine lands at dawn (title_sky.png), the
logo with a gem for each land (title_logo.png), a twinkle (title_spark.png, 4 frames of 16x16) and HO-OH's
silhouette (title_hooh.png). Hand pixelled: flat colours, 4-px dawn bands, the world's #262638 outline.
Run by hand when the art changes (it needs the Caladea font); build_assets.py only reads the PNGs.
The lands, left to right: TEMPESTA's storm, VELLORIN's hills, CALDERRA's volcano, the SUNDERED ISLES, ORIGIN's
temple under ARCEUS, GENOVA's towers, the SKYREACH pillar, AETERNA's clock tower, the HOLLOW LANDS upside down."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'data')
FONT = '/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf'
W, H = 240, 160            # the screen; the 256x256 backgrounds hold it at (8, 48)
O = (38, 38, 56)           # the shared outline
NIGHT = (30, 20, 46)
# One gem per land, in the logo, left to right (VELLORIN ... ORIGIN); ORIGIN's is the logo's own white and gold.
GEMS = [(88, 200, 96), (232, 72, 48), (56, 128, 232), (48, 200, 160), (240, 120, 200), (128, 112, 240),
        (120, 76, 144), (168, 224, 248), None]
GEM_Y = 45                 # the gems' centre row on the screen
GEM_X = [120 + (i - 4) * 18 for i in range(9)]

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def ramp(stops, t):
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return lerp(c0, c1, (t - t0) / (t1 - t0))
    return stops[-1][1]

def on_bg(img):
    bg = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    bg.alpha_composite(img, (8, 48))
    return bg

def silhouette(num, size, col):
    im = Image.open(os.path.join(ROOT, 'sprites', 'pokemon', '%d.png' % num)).convert('RGBA')
    im = im.crop(im.getbbox())
    s = size / max(im.size)
    im = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.NEAREST)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    a, o = im.load(), out.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            if a[x, y][3] > 128:
                o[x, y] = col + (255,)
    return out

def sky():
    img = Image.new('RGBA', (W, H))
    px = img.load()
    d = ImageDraw.Draw(img)
    rect = lambda x0, y0, x1, y1, c: d.rectangle((x0, y0, x1, y1), fill=c)
    # Dawn in 4-px bands: night overhead, violet, rose, a pale gold horizon behind the temple.
    stops = [(0, (22, 18, 58)), (0.3, (70, 40, 112)), (0.55, (168, 80, 136)), (0.75, (240, 144, 128)),
             (0.9, (255, 196, 136)), (1, (255, 228, 168))]
    for y in range(H):
        c = ramp(stops, min(1.0, (y // 4 * 4) / 120.0)) + (255,)
        for x in range(W):
            px[x, y] = c
    rnd = random.Random(9)
    for _ in range(46):
        x, y = rnd.randrange(W), rnd.randrange(40)
        px[x, y] = (208, 196, 255, 255) if rnd.random() < 0.5 else (140, 124, 204, 255)
    # ARCEUS's glow: banded rings behind it.
    for r, c in ((54, (250, 168, 128)), (44, (255, 192, 140)), (35, (255, 214, 160)), (27, (255, 234, 192)),
                 (20, (255, 246, 222))):
        d.ellipse((120 - r, 84 - r, 120 + r, 84 + r), fill=c)

    FAR, MID, NEAR = (196, 120, 150), (142, 78, 132), (92, 48, 104)
    LIT = (255, 206, 150)           # dawn light on the tops

    # TEMPESTA (top left): a storm cloud with a bolt down to the sea.
    for cx, cy, r in ((12, 62, 9), (24, 57, 11), (38, 60, 9), (48, 64, 6), (4, 66, 6)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r // 2 + 2), fill=(96, 78, 122))
    for cx, cy, r in ((22, 54, 7), (34, 56, 6)):
        d.ellipse((cx - r, cy - r, cx + r, cy), fill=(138, 112, 160))
    rect(0, 66, 54, 69, (78, 62, 104))
    bolt = [(26, 70), (24, 76), (28, 77), (25, 84), (29, 85), (27, 92)]
    for (x0, y0), (x1, y1) in zip(bolt, bolt[1:]):
        d.line((x0, y0, x1, y1), fill=(255, 240, 120))
    for x, y in ((14, 72), (12, 78), (40, 73), (42, 80)):     # rain
        d.line((x, y, x - 1, y + 3), fill=(150, 130, 180))

    # The HOLLOW LANDS (top right): an island hanging upside down, its tree pointing at the ground.
    isle = [(206, 66), (238, 66), (232, 60), (226, 52), (220, 46), (214, 54)]     # rock on top, point up
    d.polygon(isle, fill=(88, 64, 112))
    rect(206, 66, 238, 68, (120, 92, 140))                     # its grass, underneath
    d.line((206, 68, 238, 68), fill=(150, 120, 168))
    rect(221, 69, 223, 73, (70, 48, 92))                       # the tree hangs down from it
    d.ellipse((215, 73, 229, 84), fill=(104, 74, 132))
    d.ellipse((217, 78, 223, 83), fill=(132, 100, 160))
    for x, y in ((211, 62), (230, 63), (220, 50)):
        px[x, y] = (200, 160, 240, 255)                        # faint violet glints

    # CALDERRA: the volcano, far off, smoking and glowing.
    d.polygon([(22, 116), (44, 92), (52, 92), (78, 116)], fill=FAR)
    d.polygon([(44, 92), (52, 92), (56, 97), (40, 97)], fill=(212, 104, 104))
    rect(45, 91, 51, 92, (255, 150, 72)); rect(47, 90, 49, 90, (255, 224, 120))
    for i, (x, y, r) in enumerate(((48, 84, 3), (51, 78, 4), (47, 71, 4), (52, 64, 3))):
        d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 108, 140) if i % 2 else (166, 120, 150))

    # The SKYREACH: the SKY PILLAR through the clouds, far right of ARCEUS.
    rect(188, 54, 197, 118, FAR)
    for y in (64, 78, 92, 106):
        rect(186, y, 199, y + 2, (210, 140, 160))              # tier ledges
    rect(190, 48, 195, 53, FAR); rect(191, 45, 194, 47, (210, 140, 160))
    rect(188, 54, 188, 118, (216, 150, 164))                   # lit left edge
    for cx, cy, w in ((192, 72, 16), (192, 98, 20)):
        d.ellipse((cx - w, cy - 3, cx + w, cy + 3), fill=(244, 196, 196))
        d.ellipse((cx - w + 6, cy - 5, cx + w - 8, cy + 1), fill=(255, 220, 210))

    # The sea of the SUNDERED ISLES, with dawn streaks.
    rect(0, 116, 104, 131, (232, 150, 150))
    for y, x0, x1 in ((119, 10, 40), (122, 56, 96), (125, 4, 30), (127, 70, 100), (121, 84, 102)):
        d.line((x0, y, x1, y), fill=(255, 210, 180))
    for x0, x1, top in ((60, 74, 112), (78, 88, 114), (92, 98, 116)):
        d.ellipse((x0, top, x1, top + 8), fill=MID)
        d.line((x0 + 2, top, x1 - 2, top), fill=(196, 120, 150))
    # A palm on the big isle.
    d.line((67, 112, 68, 104), fill=MID)
    for dx, dy in ((-4, 2), (-2, -1), (3, -1), (4, 2)):
        d.line((68, 104, 68 + dx, 104 + dy), fill=MID)

    # VELLORIN: green hills with a little town, nearest on the left.
    d.ellipse((-30, 104, 44, 150), fill=(76, 120, 96))
    d.ellipse((22, 118, 58, 150), fill=(66, 104, 92))
    d.arc((-30, 104, 44, 150), 200, 320, fill=(140, 176, 120))
    for hx, hy in ((8, 108), (18, 106), (30, 110)):            # houses: wall, roof, window
        rect(hx, hy, hx + 6, hy + 4, (224, 206, 196))
        d.polygon([(hx - 1, hy), (hx + 3, hy - 4), (hx + 7, hy)], fill=(206, 84, 72))
        px[hx + 2, hy + 2] = (255, 236, 150, 255)

    # ORIGIN: the white and gold temple under ARCEUS.
    rect(96, 118, 144, 131, (238, 222, 196))
    rect(92, 128, 148, 131, (210, 186, 150))
    rect(100, 116, 140, 117, (255, 214, 96))
    for x in range(100, 141, 8):
        rect(x, 118, x + 2, 127, (255, 246, 228)); px[x + 2, 118] = (210, 186, 150, 255)
    d.polygon([(96, 116), (120, 106), (144, 116)], fill=(255, 214, 96))
    d.polygon([(102, 115), (120, 108), (138, 115)], fill=(255, 238, 168))

    # GENOVA: glass towers, the windows already lit.
    for x0, top, w in ((150, 100, 8), (160, 88, 9), (171, 96, 7), (179, 104, 6)):
        rect(x0, top, x0 + w, 131, MID)
        rect(x0, top, x0, 131, (176, 104, 150))
        for y in range(top + 3, 128, 4):
            for x in range(x0 + 2, x0 + w - 1, 3):
                if (x * 7 + y) % 5:
                    px[x, y] = (150, 216, 232, 255)
    rect(164, 84, 164, 87, MID); px[164, 83] = (255, 96, 96, 255)    # the beacon

    # AETERNA: the clock tower, its two faces telling different times.
    rect(206, 92, 218, 131, MID)
    d.polygon([(204, 92), (212, 82), (220, 92)], fill=NEAR)
    d.ellipse((208, 96, 216, 104), fill=(250, 232, 200))
    d.line((212, 100, 212, 97), fill=O); d.line((212, 100, 214, 101), fill=O)
    rect(206, 92, 206, 131, (176, 104, 150))

    # The right lands' ground, then the near ridge the text sits on.
    pts = [(146, 160), (146, 128)] + [(x, 128 - int(3 * math.sin(x / 9.0))) for x in range(146, W + 1, 2)] + [(W, 160)]
    d.polygon(pts, fill=NEAR)
    ridge = [(0, H)]
    for x in range(0, W + 1, 2):
        y = 136 - 4 * math.sin(x / 23.0 + 1) - 2 * math.sin(x / 7.0) + (0 if 80 < x < 160 else 2)
        ridge.append((x, int(y)))
    ridge.append((W, H))
    d.polygon(ridge, fill=NIGHT)
    for (x0, y0), (x1, y1) in zip(ridge[1:-1], ridge[2:-1]):
        d.line((x0, y0 - 1, x1, y1 - 1), fill=(66, 40, 84))      # rim of dawn light on the ridge
    for x in range(4, W, 11):                                    # grass tufts on the ridge
        y = ridge[1 + x // 2][1]
        px[x, y - 2] = (66, 40, 84, 255); px[x + 1, y - 3] = (66, 40, 84, 255); px[x + 2, y - 2] = (66, 40, 84, 255)

    # ARCEUS, floating over its temple.
    arc = Image.open(os.path.join(ROOT, 'sprites', 'pokemon', '493.png')).convert('RGBA')
    img.alpha_composite(arc, (120 - 48, 39))
    return on_bg(img)

def logo():
    big, small = ImageFont.truetype(FONT, 32), ImageFont.truetype(FONT, 14)
    mask = Image.new('L', (W, 48))
    d = ImageDraw.Draw(mask)
    d.fontmode = '1'      # no anti-aliasing: crisp pixels
    for text, font, y in (('POKé LEGENDS', small, -1), ('LANDS OF NINE', big, 9)):
        d.text(((W - d.textlength(text, font=font)) // 2, y), text, font=font, fill=255)
    m = mask.load()
    on = lambda x, y: 0 <= x < W and 0 <= y < 48 and m[x, y]
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    p = img.load()
    gold = [(0, (255, 248, 200)), (0.4, (255, 216, 96)), (0.7, (232, 152, 40)), (1, (176, 80, 24))]
    TOP = 2
    for y in range(48):
        for x in range(W):
            if on(x, y):
                t = y / 11.0 if y < 12 else (y - 14) / 24.0
                c = ramp(gold, max(0.0, min(1.0, t)))
                p[x, y + TOP] = min(((255, 248, 200), (255, 216, 96), (232, 152, 40), (176, 80, 24)),
                                    key=lambda g: sum((g[i] - c[i]) ** 2 for i in range(3))) + (255,)
            elif any(on(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                p[x, y + TOP] = O + (255,)
            elif on(x - 1, y - 2) or on(x - 2, y - 2) or on(x - 2, y - 1):
                p[x, y + TOP] = NIGHT + (255,)
    # The gold rule under the name, a gem for each land set in it.
    d = ImageDraw.Draw(img)
    x0, x1 = GEM_X[0] - 10, GEM_X[-1] + 10
    d.rectangle((x0, GEM_Y - 2, x1, GEM_Y + 2), fill=O)
    d.line((x0 + 1, GEM_Y - 1, x1 - 1, GEM_Y - 1), fill=(255, 216, 96))
    d.line((x0 + 1, GEM_Y, x1 - 1, GEM_Y), fill=(232, 152, 40))
    d.line((x0 + 1, GEM_Y + 1, x1 - 1, GEM_Y + 1), fill=(176, 80, 24))
    for gx, c in zip(GEM_X, GEMS):
        d.polygon([(gx, GEM_Y - 5), (gx + 5, GEM_Y), (gx, GEM_Y + 5), (gx - 5, GEM_Y)], fill=O)
        d.polygon([(gx, GEM_Y - 4), (gx + 4, GEM_Y), (gx, GEM_Y + 4), (gx - 4, GEM_Y)], fill=c or (255, 216, 96))
        if c is None:
            d.polygon([(gx, GEM_Y - 2), (gx + 2, GEM_Y), (gx, GEM_Y + 2), (gx - 2, GEM_Y)], fill=(255, 248, 200))
        p[gx - 1, GEM_Y - 2] = (255, 255, 255, 255); p[gx - 2, GEM_Y - 1] = (255, 255, 255, 255)
    return on_bg(img)

def spark():
    # A four-point twinkle growing and fading: 4 frames, 16x16 each, stacked.
    sheet = Image.new('RGBA', (16, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for f, r in enumerate((2, 4, 7, 4)):
        cx, cy = 8, f * 16 + 8
        d.line((cx - r, cy, cx + r, cy), fill=(255, 240, 160, 255))
        d.line((cx, cy - r, cx, cy + r), fill=(255, 240, 160, 255))
        if r > 3:
            d.line((cx - 1, cy - 1, cx + 1, cy + 1), fill=(255, 255, 255, 255))
            d.line((cx - 1, cy + 1, cx + 1, cy - 1), fill=(255, 255, 255, 255))
        sheet.putpixel((cx, cy), (255, 255, 255, 255))
    return sheet

def hooh():
    out = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    s = silhouette(250, 56, (56, 20, 48))
    out.alpha_composite(s, ((64 - s.size[0]) // 2, (64 - s.size[1]) // 2))
    return out

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    sky().save(os.path.join(OUT, 'title_sky.png'))
    logo().save(os.path.join(OUT, 'title_logo.png'))
    spark().save(os.path.join(OUT, 'title_spark.png'))
    hooh().save(os.path.join(OUT, 'title_hooh.png'))
    # A preview of the screen as it settles (no text), for review.
    if len(sys.argv) > 1:
        a = Image.open(os.path.join(OUT, 'title_sky.png')).crop((8, 48, 248, 208))
        a.alpha_composite(Image.open(os.path.join(OUT, 'title_logo.png')).crop((8, 48, 248, 208)))
        a.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(OUT, 'title_preview.png'))
