"""Drives pilot_harness (mGBA) and reads the game state through test_pilot.inc's table."""
import os, struct, subprocess
from PIL import Image

SRAM = 0x0E000000
NAMES = ['gs_size', 'mon_size', 'map', 'x', 'y', 'facing', 'party_count', 'surfing', 'story', 'money', 'play_frames',
         'items', 'party', 'beaten', 'picked', 'owned', 'visited', 'region', 'flags', 'run', 'opt', 'last_heal',
         'm_species', 'm_level', 'm_hp', 'm_max_hp', 'm_moves', 'm_pp_used', 'm_move_count', 'm_xp', 'm_st', 'seen',
         'walk_off', 'box']

class Emu:
    def __init__(self, harness, rom, sav):
        self.p = subprocess.Popen([harness, rom, sav], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.frames = 0
        self.t = None

    def cmd(self, line, reply=False):
        self.p.stdin.write(line + '\n')
        if reply:
            self.p.stdin.flush()
            return self.p.stdout.readline().strip()

    def wait(self, n):
        self.cmd('w %d' % n); self.frames += n

    def press(self, keys, n=4):
        self.cmd('k %s %d' % (keys, n)); self.frames += n + 4

    def hold(self, keys, n):
        self.cmd('H %s %d' % (keys, n)); self.frames += n

    def hold_until(self, keys, mx, addr, ln):
        f = int(self.cmd('G %s %d %x %d' % (keys, mx, addr, ln), True)); self.frames += f
        return f

    def read(self, addr, n):
        return bytes.fromhex(self.cmd('m %x %d' % (addr, n), True))

    def write(self, addr, data):
        # In pieces: the harness takes at most 511 hex digits a line, and a longer write (a party, a box) was cut short.
        for i in range(0, len(data), 200):
            self.cmd("M %x %s" % (addr + i, data[i:i + 200].hex()))

    def shot(self, path):
        ppm = path[:-4] + '.ppm'
        self.cmd('p %s' % ppm, True)
        Image.open(ppm).resize((480, 320), Image.NEAREST).save(path)
        os.remove(ppm)

    def color(self, x, y):
        return tuple(int(v) for v in self.cmd('c %d %d' % (x, y), True).split())

    def save_state(self, path):
        return self.cmd('S %s' % path, True) == '1'

    def load_state(self, path):
        return self.cmd('L %s' % path, True) == '1'

    def close(self):
        self.p.stdin.close(); self.p.wait()

    # ----- the game state -----
    def table(self):
        raw = self.read(SRAM + 0x7E40, 8 + 80)
        if raw[:4] != b'PILT':
            return None
        addr = struct.unpack('<I', raw[4:8])[0]
        v = struct.unpack('<40H', raw[8:88])
        self.t = dict(zip(NAMES, v)); self.t['addr'] = addr
        return self.t

    def crashed(self):
        return self.read(SRAM + 0x7E10, 4) == b'CRSH'

    def g(self, field, n=2, signed=True):
        b = self.read(self.t['addr'] + self.t[field], n)
        return int.from_bytes(b, 'little', signed=signed)

    def pos(self):
        b = self.read(self.t['addr'] + self.t['map'], 6)
        return struct.unpack('<hhh', b)

    def party(self):
        t = self.t
        n = self.g('party_count', 1, False)
        raw = self.read(t['addr'] + t['party'], t['mon_size'] * max(n, 1))
        out = []
        for i in range(n):
            r = raw[i * t['mon_size']:(i + 1) * t['mon_size']]
            u16 = lambda o: struct.unpack_from('<H', r, o)[0]
            out.append(dict(species=u16(t['m_species']), level=u16(t['m_level']), hp=u16(t['m_hp']), max_hp=u16(t['m_max_hp']),
                            moves=[u16(t['m_moves'] + 2 * k) for k in range(r[t['m_move_count']])],
                            pp_used=list(r[t['m_pp_used']:t['m_pp_used'] + 4]), st=r[t['m_st']]))
        return out

    def bits(self, field, nbytes):
        return self.read(self.t['addr'] + self.t[field], nbytes)

    def bit(self, field, i):
        b = self.read(self.t['addr'] + self.t[field] + (i >> 3), 1)[0]
        return (b >> (i & 7)) & 1

    def items(self, n=256):
        return self.read(self.t['addr'] + self.t['items'], n)

    def set_policy(self, pol):
        self.write(SRAM + 0x7E04, bytes([pol]))
