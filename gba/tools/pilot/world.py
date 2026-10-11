"""The world as the ROM has it, parsed from generated/include/pr_world_data.h (maps, behaviours, doors, people,
trainers, items, links, areas), for pilot.py."""
import os, re, pickle

WALK, SOLID, GRASS, WATER, LEDGE_D, LEDGE_R, LEDGE_L, SIGN, DOOR, ITEM, COUNTER, PC, MAT, STATUE, WU, WD, WL, WR = range(18)

def split_top(s):
    """Splits 'a, {b, c}, "d, e"' at top-level commas."""
    out, depth, cur, q = [], 0, [], False
    i = 0
    while i < len(s):
        c = s[i]
        if q:
            cur.append(c)
            if c == '\\':
                cur.append(s[i + 1]); i += 1
            elif c == '"':
                q = False
        elif c == '"':
            q = True; cur.append(c)
        elif c == '{':
            depth += 1; cur.append(c)
        elif c == '}':
            depth -= 1; cur.append(c)
        elif c == ',' and depth == 0:
            out.append(''.join(cur).strip()); cur = []
        else:
            cur.append(c)
        i += 1
    if ''.join(cur).strip():
        out.append(''.join(cur).strip())
    return out

def val(t):
    t = t.strip()
    if t.startswith('"'):
        return bytes(t[1:-1], 'utf8').decode('unicode_escape').encode('latin1').decode('utf8', 'replace')
    if t in ('true', 'false'):
        return t == 'true'
    if t == 'nullptr':
        return None
    if 'area_flag::' in t or ('|' in t and '::' in t):
        F = dict(CENTER=1, LEAGUE=2, CHAMPION=4, BOSS=8, OWN_POOL=16, TOWER_TOWN=32, SAFARI=64, TRADE_TOWN=128, SHRINE=256, MIRROR=512)
        return sum(F.get(p.strip().split('::')[-1], 0) for p in t.split('|'))
    if '::' in t:
        return t.split('::')[-1]
    if t.startswith('&'):
        return t[1:]
    try:
        return int(t, 0)
    except ValueError:
        return t

def rows(body):
    body = body.strip()
    if not body:
        return []
    items = split_top(body)
    return [[val(x) for x in split_top(it[1:-1])] if it.startswith('{') else val(it) for it in items]

DECL = re.compile(r'(?:inline )?constexpr ([\w:]+(?:\s*\*)?(?: const\*)?) (\w+)(\[\])? = \{')

def parse(path):
    text = open(path, encoding='utf8').read()
    arrays = {}
    for m in DECL.finditer(text):
        name = m.group(2)
        if not (((name.startswith('map') or name.startswith('room')) and '_' in name) or name == 'maps'):
            continue
        i, depth = m.end(), 1
        q = False
        j = i
        while depth:
            c = text[j]
            if q:
                if c == '\\': j += 1
                elif c == '"': q = False
            elif c == '"': q = True
            elif c == '{': depth += 1
            elif c == '}': depth -= 1
            j += 1
        arrays[name] = text[i:j - 1]
    return arrays

class World:
    def __init__(self, header):
        a = parse(header)
        self.maps = []
        for mi, r in enumerate(rows(a['maps'])):
            p = r[5][:-len('behaviour')]
            m = dict(index=mi, name=r[0], w=r[2], h=r[3], spawn=(r[22], r[23]), level_cap=r[24], exit_map=r[25],
                     exit=(r[26], r[27]), leader_id=r[28], gate=r[29], leader_name=r[31], desc=r[35])
            m['room'] = m['exit_map'] >= 0
            # League gates (pr_overworld.cpp gate_open): a wall row that opens once that Elite Four member is beaten.
            ri = a.get(p + 'room')
            n = rows(ri)[3] if ri else 0
            m['gates'] = [dict(y=d[0], x0=d[1], x1=d[2], elite=d[3]) for d in rows(a.get(p + 'gates', ''))][:n] if n else []
            m['beh'] = rows(a[p + 'behaviour'])
            m['doors'] = [dict(x=d[0], y=d[1], kind=d[2], room=d[3]) for d in rows(a.get(p + 'doors', ''))][:r[9]]
            m['people'] = [dict(x=d[0], y=d[1], kind=d[2], facing=d[3], role=d[4], wander=d[5]) for d in rows(a.get(p + 'people', ''))][:r[11]]
            m['trainers'] = [dict(x=d[0], y=d[1], kind=d[2], facing=d[3], role=d[4], title=d[5], team_n=d[7], vanish=d[14],
                                  id=d[15], elite=d[16], area=d[17], scene=d[18]) for d in rows(a.get(p + 'trainers', ''))][:r[13]]
            m['items'] = [dict(x=d[0], y=d[1], item=d[2], id=d[3]) for d in rows(a.get(p + 'items', ''))][:r[15]] if r[15] else []
            m['links'] = [dict(to=d[0], ox=d[1], oy=d[2], w=d[3], h=d[4], name=d[5], gate=d[6], badges=d[7], need=d[8])
                          for d in rows(a.get(p + 'links', ''))][:r[19]] if r[19] else []
            ar = a.get(r[32]) if r[32] else None
            if ar is not None and not m['room']:
                v = rows(ar)
                m.update(kind=v[0], theme=v[1], weather=v[2], flags=v[3], tier=v[4], region=v[5], at=(v[6], v[7]),
                         dive=v[8], surface=v[9], scene=v[10], legend=v[15], legend_xy=(v[16], v[17]), twin=v[21])
            self.maps.append(m)
        for m in self.maps:
            if m['room']:
                m['region'] = self.maps[m['exit_map']]['region']
                m['flags'] = 0

    def beh(self, m, x, y):
        mp = self.maps[m]
        if 0 <= x < mp['w'] and 0 <= y < mp['h']:
            return mp['beh'][y * mp['w'] + x]
        return None

def load(gba_dir):
    header = os.path.join(gba_dir, 'generated', 'include', 'pr_world_data.h')
    cache = header + '.pilot.pickle'
    w = World.__new__(World)
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(header):
        w.maps = pickle.load(open(cache, 'rb'))
        if 'gates' in w.maps[0]:        # an older cache lacks the league gates
            return w
    w = World(header)
    pickle.dump(w.maps, open(cache, 'wb'))
    return w

if __name__ == '__main__':
    import sys
    w = load(sys.argv[1])
    print(len(w.maps), 'maps')
    for m in w.maps[:3] + w.maps[-2:]:
        print(m['index'], m['name'], m['w'], m['h'], m['room'], m.get('region'), len(m['doors']), len(m['people']), len(m['trainers']), len(m['links']), m['leader_id'], m['gate'])
