#!/usr/bin/env python3
"""Chamber test (9.4.0): for every legendary, calls it at the TOWER SUMMIT's SUMMONING STONE in mGBA, checks you land
in its own SUMMONING CHAMBER, walks the path up to the dais (7, 5) and presses A to start the battle. The chamber on screen
is compared with the approved art (gba/data/chamber_<num>.png with the sprite placed as place.py placed it); OUT
gets c<num>.png (approved | game) and sheet.png, all of them.
    python3 tools/walktest/chambertest.py [OUT] [dex numbers...]
Needs what walktest.py needs."""
import os, shutil, struct, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walktest
from gymtest import Live, BOOT

GBA = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(GBA, 'data')
SPRITES = os.path.join(os.path.dirname(GBA), 'sprites', 'pokemon')

def room_png(num, shiny):
    return Image.open(os.path.join(DATA, 'chamber_%d%s.png' % (num, '_shiny' if shiny else ''))).convert('RGBA')

def approved(num, shiny):
    room = room_png(num, shiny)
    if num != 382:   # place.py
        sp = Image.open(os.path.join(SPRITES, ('shiny/' if shiny else '') + '%d.png' % num)).convert('RGBA').resize((64, 64), Image.NEAREST)
        x0, y0, x1, y1 = sp.getbbox()
        room.alpha_composite(sp.crop((x0, y0, x1, y1)), (120 - (x1 - x0) // 2, max(0, 66 - (y1 - y0))))
    return room.convert('RGB').crop((0, 8, 240, 168))    # the camera, with you at (7, 5)

def changed(a, b, x, y):
    return sum(abs(a[x, y][i] - b[x, y][i]) for i in range(3)) > 40

def differ(a, b, skip=(60, 0, 180, 80)):
    """The share of pixels that differ by more than GBA colour rounding, the player and (skip) the legendary left out."""
    pa, pb, n, bad = a.load(), b.load(), 0, 0
    for y in range(160):
        for x in range(240):
            if 110 <= x < 130 and 60 <= y < 96 or skip[0] <= x < skip[2] and skip[1] <= y < skip[3]: continue
            n += 1
            bad += changed(pa, pb, x, y)
    return bad / max(1, n)

def sprite_box(shot, clean):
    """Where the legendary is: what differs from the bare room above the dais's front, the player left out."""
    ps, pc, xs, ys = shot.load(), clean.load(), [], []
    for y in range(66):
        for x in range(60, 180):
            if not (110 <= x < 130 and y >= 56) and changed(ps, pc, x, y): xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None

def main():
    args = sys.argv[1:]
    out = os.path.abspath(args[0] if args else 'chambertest-out')
    only = [int(a) for a in args[1:]]
    os.makedirs(out, exist_ok=True)
    nums = only or sorted(int(f[8:-4]) for f in os.listdir(DATA) if f.startswith('chamber_') and f[8:-4].isdigit())
    cases = [(n, False) for n in nums] + ([(382, True)] if 382 in nums else [])
    work = tempfile.mkdtemp(prefix='chambertest-')
    rom, harness = walktest.build(work, 'test_chamber.inc')
    sav = os.path.join(out, 'addr.sav')
    open(sav, 'wb').write(b'\xff' * 0x8000)
    subprocess.run([harness, rom, sav], input='w 30\n', text=True, check=True)
    at = struct.unpack('<I', open(sav, 'rb').read()[0x7E20:0x7E24])[0]
    bad, shots = [], []
    for num, shiny in cases:
        sav = os.path.join(out, 'c%d.sav' % num)
        blank = bytearray(b'\xff' * 0x8000)
        blank[0x7E00:0x7E04] = struct.pack('<hh', num, 1 if shiny else 0)
        open(sav, 'wb').write(blank)
        live = Live(harness, rom, sav)
        live.send(*BOOT)
        pos = lambda: struct.unpack('<hhh', live.mem(at, 6))
        summit = pos()[0]
        for _ in range(30):                        # the stone's texts, then the warp
            live.send('k A 1', 'w 30')
            if pos()[0] != summit: break
        live.send('w 120')
        m, x, y = pos()
        why = None if m != summit and (x, y) == (7, 11) else 'never reached a chamber (map %d at %d,%d)' % (m, x, y)
        if not why:
            for _ in range(6): live.send('k U 1', 'w 24')
            live.send('w 30')
            m2, x, y = pos()
            if (x, y) != (7, 5): why = 'walked to %d,%d, not 7,5' % (x, y)
        tag = 'c%d%s' % (num, 's' if shiny else '')
        live.send('p %s' % os.path.join(out, tag + '_dais.ppm'))
        if not why:
            for _ in range(6): live.send('k A 1', 'w 40')
            live.send('w 120', 'p %s' % os.path.join(out, tag + '_battle.ppm'))
        live.send('w 1')
        live.close()
        if not why and open(sav, 'rb').read()[0x7E10:0x7E14] == b'CRSH': why = 'CRASH'
        score = '-'
        if os.path.exists(os.path.join(out, tag + '_dais.ppm')):
            game = Image.open(os.path.join(out, tag + '_dais.ppm')).convert('RGB')
            want = approved(num, shiny)
            d = differ(want, game, (0, 0, 0, 0) if num == 382 else (60, 0, 180, 80))
            score = '%.1f%%' % (d * 100)
            if not why and d > 0.03: why = 'the room looks %s off the approved art' % score
            if not why and num != 382:
                clean = room_png(num, shiny).convert('RGB').crop((0, 8, 240, 168))
                a, b = sprite_box(want, clean), sprite_box(game, clean)
                off = max(abs(a[i] - b[i]) for i in range(4)) if a and b else 99
                score += ', sprite within %d px' % off
                if off > 3: why = 'the legendary sits %d px off the approved art' % off
            if not why:
                fight = Image.open(os.path.join(out, tag + '_battle.ppm')).convert('RGB')
                if differ(game, fight, (0, 0, 0, 0)) < 0.3: why = 'no battle after A'
            pair = Image.new('RGB', (484, 160), (255, 255, 255))
            pair.paste(want, (0, 0)); pair.paste(game, (244, 0))
            pair.save(os.path.join(out, tag + '.png')); shots.append(pair)
        print('%5d%s %s  differs %s%s' % (num, 's' if shiny else ' ', 'FAIL' if why else 'ok', score, ': ' + why if why else ''), flush=True)
        if why: bad.append(tag)
        os.remove(sav)
    if shots:
        cols = 4
        sheet = Image.new('RGB', (cols * 488, ((len(shots) + cols - 1) // cols) * 164), (255, 255, 255))
        for i, s in enumerate(shots): sheet.paste(s, ((i % cols) * 488, (i // cols) * 164))
        sheet.save(os.path.join(out, 'sheet.png'))
    shutil.rmtree(work)
    print('failing:', bad or 'none')
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
