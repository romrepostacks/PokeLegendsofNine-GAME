#!/usr/bin/env python3
"""Art cohesion lint for the game's own (non-Pokémon) art in gba/data: catches the things a swipe review is bad at
seeing, so the review only has to judge taste. Run it on new art before it goes up for review.
    python3 tools/art/artlint.py              new or changed findings against the approved baseline (exit 1 if any)
    python3 tools/art/artlint.py --all        every finding, approved art included
    python3 tools/art/artlint.py --approve    record the current findings as the baseline (after Kyle approves)

Checks, per PNG:
  alpha    a pixel neither fully clear nor fully solid (the GBA has no partial transparency: it's a smoothing leftover)
  colours  an 8x8 cell with more than 15 colours (one GBA palette bank: it would have to be merged, so colours drift)
  outline  a cut-out sprite whose edge is mostly not the #262638 outline (Kyle's rule for buildings, props, statues)
  stray    a colour on 1-3 pixels, a near miss of a colour the picture uses a lot (unsnapped generation, a paste)
The baseline (gba/data/artlint_baseline.json) holds each file's findings as approved, so old art doesn't fail."""
import collections, glob, json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '..', 'data')
BASELINE = os.path.join(DATA, 'artlint_baseline.json')
OUTLINE = (0x26, 0x26, 0x38)
MIN_OUTLINE = 0.6           # the approved trees sit at 0.65, everything else built by the art scripts near 1.0
NEAR, STRAY_PX, COMMON_PX = 24, 3, 20


def lint(path):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    px = im.load()
    out = {}
    semi = sum(1 for y in range(h) for x in range(w) if 0 < px[x, y][3] < 255)
    if semi:
        out['alpha'] = semi
    over = 0
    for ty in range(0, h - 7, 8):
        for tx in range(0, w - 7, 8):
            if len({px[x, y][:3] for y in range(ty, ty + 8) for x in range(tx, tx + 8) if px[x, y][3]}) > 15:
                over += 1
    if over:
        out['colours'] = over
    edge = lined = 0
    for y in range(h):
        for x in range(w):
            if px[x, y][3] and any(0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] == 0
                                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                edge += 1
                lined += px[x, y][:3] == OUTLINE
    # Soft-edged overlays (puddles, drifts, the title's sky) have no outline on purpose: only judge real outlines.
    if edge > 20 and lined and lined / edge < MIN_OUTLINE:
        out['outline'] = round(lined / edge, 2)
    count = collections.Counter(px[x, y][:3] for y in range(h) for x in range(w) if px[x, y][3])
    common = [c for c, n in count.items() if n >= COMMON_PX]
    stray = sum(1 for c, n in count.items() if n <= STRAY_PX and
                any(d != c and max(abs(a - b) for a, b in zip(c, d)) <= NEAR for d in common))
    if stray:
        out['stray'] = stray
    return out


def worse(now, then):
    """The findings in now that weren't in then, or got worse (a lower outline share is worse)."""
    bad = {}
    for k, v in now.items():
        t = then.get(k)
        if t is None or (v < t if k == 'outline' else v > t):
            bad[k] = v
    return bad


def main(args):
    files = sorted(glob.glob(os.path.join(DATA, '**', '*.png'), recursive=True))
    found = {os.path.relpath(f, DATA): lint(f) for f in files}
    found = {k: v for k, v in found.items() if v}
    if '--approve' in args:
        json.dump(found, open(BASELINE, 'w'), indent=0, sort_keys=True)
        print('baseline: %d files with findings, of %d' % (len(found), len(files)))
        return 0
    base = {} if '--all' in args else json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    report = {k: worse(v, base.get(k, {})) for k, v in found.items()}
    report = {k: v for k, v in report.items() if v}
    totals = collections.Counter(c for v in report.values() for c in v)
    for k, v in sorted(report.items()):
        print('%-48s %s' % (k, '  '.join('%s %s' % kv for kv in sorted(v.items()))))
    print('%d of %d files: %s' % (len(report), len(files), ', '.join('%s %d' % kv for kv in sorted(totals.items())) or 'clean'))
    return 1 if report else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
