# Kyogre resting in the sea, seen side-on with the waterline across its middle (round 3, after Kyle's note):
# 88x40, transparent; the bottom row is the waterline. python3 kyogre_side.py OUT.png
import sys, math
from PIL import Image

W, H = 88, 40
O = (38, 38, 56)
B1, B2, B3, B4 = (112, 168, 240), (64, 120, 216), (40, 80, 168), (32, 56, 120)
R1, R2 = (248, 96, 96), (200, 40, 56)
G1, G2 = (208, 208, 224), (160, 160, 184)
Y = (248, 216, 72)
px = [[None] * W for _ in range(H)]
def s(x, y, c):
    if 0 <= x < W and 0 <= y < H: px[int(y)][int(x)] = c
WL = H - 1                                   # waterline

# body: a long low dome from the snout (left) to the root of the tail (right)
def top(x):            # the body's top edge at column x
    t = (x - 6) / 64
    if t < 0 or t > 1: return None
    return WL - (5 + 24 * math.sin(math.pi * min(1, t * 1.15) ** 0.7) ** 0.8 * (1 - 0.3 * t))
for x in range(W):
    t = top(x)
    if t is None: continue
    for y in range(int(t), WL):
        s(x, y, B2 if y > t + 3 else B1)
    for y in range(int(t) + (WL - int(t)) * 2 // 3, WL): s(x, y, B3)        # shade low on the flank
# dorsal ridge
for x in range(30, 52):
    t = top(x); s(x, t - 1, B2); s(x, t - 2, B1 if x % 3 else B2)
# grey spots on the back
for cx, cy in ((30, 19), (39, 17), (48, 19)):
    for dx in range(-2, 2):
        for dy in range(-1, 1): s(cx + dx, cy + dy, G1)
    s(cx + 1, cy, G2)
# the glowing red lines along the flank
for x in range(22, 66):
    y = WL - 7 - 4 * math.sin((x - 22) / 8)
    s(x, y, R1); s(x, y + 1, R2)
for a in range(0, 360, 6):                                   # the red loop on the shoulder
    x, y = 40 + 7 * math.cos(math.radians(a)), WL - 19 + 4 * math.sin(math.radians(a))
    s(x, y, R1)
# head: mouth line, cheek and the eye
for x in range(6, 24): s(x, WL - 6 + (x - 6) // 7, B4)
for x in range(8, 14): s(x, WL - 5, (232, 232, 240))
for x in range(13, 18): s(x, WL - 13, O)
s(13, WL - 12, R2); s(14, WL - 12, R1); s(15, WL - 12, Y); s(16, WL - 12, Y); s(17, WL - 12, O)
s(14, WL - 11, R2); s(15, WL - 11, R2); s(16, WL - 11, O)
# front fin breaking the surface, white claws
for k in range(10):
    for j in range(k // 2 + 1): s(24 + k, WL - 1 - j, B2 if j else B3)
for k, x in enumerate((26, 29, 32)): s(x, WL - 2 - k, (240, 240, 248)); s(x, WL - 3 - k, (240, 240, 248))
# the tail fin, raised, four points
for k, (bx, h) in enumerate(((70, 18), (75, 23), (80, 20), (85, 14))):
    for y in range(WL - h, WL - 2):
        w = 1 + (y - (WL - h)) // 4
        for dx in range(-w, w + 1): s(bx + dx - (y - (WL - h)) // 3, y, B2 if dx < 0 else B3)
    s(bx, WL - h, B1)
for x in range(64, 82):
    for y in range(WL - 6, WL): s(x, y, B2 if y < WL - 2 else B3)
# outline (water side left open: the body runs on under the surface)
add = [(x, y) for y in range(H) for x in range(W) if px[y][x] is None and any(
    0 <= x + dx < W and 0 <= y + dy < H and px[y + dy][x + dx] not in (None, O) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
for x, y in add:
    if y < WL: px[y][x] = O
im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for y in range(H):
    for x in range(W):
        if px[y][x]: im.putpixel((x, y), px[y][x] + (255,))
im.save(sys.argv[1] if len(sys.argv) > 1 else 'kyogre_side.png')
