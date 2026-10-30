"""Box art for emulator libraries (Delta, etc.), approved 2026-10-30: the title screen's dawn seen through a gold ring set
with a gem for each land, the logo curved over it. 192x192, saved at 6x nearest (1152x1152) so the pixels stay sharp.
Run: python3 tools/art/cover_art.py [OUT_DIR]  (default gba/data/) -> cover.png, cover_1152.png. Needs the Caladea font."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import title_art as T

S = 192
O, GOLD = T.O, [(255, 248, 200), (255, 216, 96), (232, 152, 40), (176, 80, 24)]

def night():
    img = Image.new('RGBA', (240, S), (22, 18, 58, 255))     # stars thrown over 240 wide, as approved
    px, rnd = img.load(), random.Random(11)
    for _ in range(S * 240 // 260):
        x, y = rnd.randrange(240), rnd.randrange(S)
        px[x, y] = (208, 196, 255, 255) if rnd.random() < 0.5 else (140, 124, 204, 255)
    return img.crop((0, 0, S, S))

def gem(d, gx, gy, c, r=6):
    d.polygon([(gx, gy - r - 1), (gx + r + 1, gy), (gx, gy + r + 1), (gx - r - 1, gy)], fill=O)
    d.polygon([(gx, gy - r), (gx + r, gy), (gx, gy + r), (gx - r, gy)], fill=c or (255, 216, 96))
    if c is None:
        d.polygon([(gx, gy - 3), (gx + 3, gy), (gx, gy + 3), (gx - 3, gy)], fill=(255, 248, 200))
    d.point([(gx - 2, gy - 3), (gx - 3, gy - 2), (gx - 1, gy - 3)], fill=(255, 255, 255))

def ring(img, cx, cy, R, inner=None):
    d = ImageDraw.Draw(img)
    for r, c in ((R + 3, O), (R + 2, GOLD[3]), (R + 1, GOLD[2]), (R - 1, GOLD[1]), (R - 2, O)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=1 if r != R - 1 else 2)
    for i, c in enumerate(T.GEMS):
        t = -math.pi / 2 + (i - 8) * 2 * math.pi / 9
        gem(d, round(cx + R * math.cos(t)), round(cy + R * math.sin(t)), c)

def disc(img, cx, cy, R, fill):
    m = Image.new('L', img.size); ImageDraw.Draw(m).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    img.paste(fill, (0, 0), m)

def arc_text(img, text, size, cx, cy, r_top):
    """Bends a line of the logo round (cx, cy): its top on radius r_top, arc length kept at mid height."""
    font = ImageFont.truetype(T.FONT, size)
    w = int(ImageDraw.Draw(Image.new('L', (1, 1))).textlength(text, font=font)) + 4
    h = size + 4
    mask = Image.new('L', (w, h)); d = ImageDraw.Draw(mask); d.fontmode = '1'
    d.text((2, 0), text, font=font, fill=255)
    top = mask.getbbox()[1]; m = mask.load()
    rmid = r_top - h / 2
    on, sy = {}, {}
    for y in range(S):
        for x in range(S):
            dx, dy = x + .5 - cx, y + .5 - cy
            r, th = math.hypot(dx, dy), math.atan2(dx, -dy)
            u, v = int(w / 2 + th * rmid), int(r_top - r) + top
            if 0 <= u < w and 0 <= v < h and m[u, v]:
                on[x, y] = True; sy[x, y] = v - top
    p = img.load(); fh = max(sy.values()) if sy else 1
    for (x, y) in on:          # shadow then outline, under the letters
        for ex, ey in ((1, 2), (2, 2), (2, 1)):
            if (x + ex, y + ey) not in on and 0 <= x + ex < S and 0 <= y + ey < S:
                p[x + ex, y + ey] = T.NIGHT + (255,)
    for (x, y) in on:
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if (x + ex, y + ey) not in on and 0 <= x + ex < S and 0 <= y + ey < S:
                    p[x + ex, y + ey] = O + (255,)
    for (x, y) in on:
        c = T.ramp(list(zip((0, .4, .7, 1), GOLD)), sy[x, y] / fh)
        p[x, y] = min(GOLD, key=lambda g: sum((g[i] - c[i]) ** 2 for i in range(3))) + (255,)

def cover():
    # The nine lands' gems in a gold ring, a window onto the title screen's dawn, the logo bent round it.
    img = night(); cx, cy, R = 96, 122, 60
    sky = T.sky().crop((8, 48, 248, 208))
    win = Image.new('RGBA', (S, S)); win.alpha_composite(sky, (cx - 120, cy - 88))
    disc(img, cx, cy, R - 2, win)
    ring(img, cx, cy, R)
    arc_text(img, 'LANDS OF NINE', 24, cx, cy, R + 34)
    arc_text(img, 'POKé LEGENDS', 15, cx, cy, R + 52)
    return img

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T.HERE, '..', '..', 'data')
    im = cover()
    im.save(os.path.join(out, 'cover.png'))
    im.convert('RGB').resize((S * 6, S * 6), Image.NEAREST).save(os.path.join(out, 'cover_1152.png'))
