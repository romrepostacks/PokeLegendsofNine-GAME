"""9.3.4: the CHALLENGE TOWER's front and one SUMMONING CHAMBER per legendary (all 92), as Kyle approved them in
the art review. Writes gba/data/tower_front.png (112x144, 7x9 tiles) and gba/data/chamber_<dex number>.png
(240x208, the 15x13 chamber); Kyogre's is drawn with it resting in its pool (chamber_382.png, and
chamber_382_shiny.png for a shiny one), every other legendary is its front sprite on the dais (place.py's rule,
which build_assets.py repeats for the game). Run by hand from gba/: python3 tools/art/chambers/build.py data"""
import sys, os, ast
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chambers, chambers2, chambers3, chambers4, chambers5, chambers6, chambers7, chambers8, towers

SPRITES = os.path.join(HERE, '..', '..', '..', '..', 'sprites', 'pokemon')

# The approved room of every legendary: (module, its room's name).
ROOMS = {
    144: (chambers3, 'articuno'), 145: (chambers2, 'zapdos'), 146: (chambers3, 'moltres'), 150: (chambers, 'mewtwo'),
    151: (chambers3, 'mew'), 243: (chambers3, 'raikou'), 244: (chambers3, 'entei'), 245: (chambers3, 'suicune'),
    249: (chambers2, 'lugia'), 250: (chambers, 'ho-oh'), 251: (chambers3, 'celebi'), 377: (chambers4, 'regirock'),
    378: (chambers4, 'regice'), 379: (chambers4, 'registeel'), 380: (chambers4, 'latias'), 381: (chambers4, 'latios'),
    382: (chambers2, 'kyogre'), 383: (chambers, 'groudon'), 384: (chambers2, 'rayquaza'), 385: (chambers3, 'jirachi'),
    386: (chambers4, 'deoxys'), 480: (chambers4, 'uxie'), 481: (chambers4, 'mesprit'), 482: (chambers4, 'azelf'),
    483: (chambers2, 'dialga'), 484: (chambers2, 'palkia'), 485: (chambers4, 'heatran'), 486: (chambers4, 'regigigas'),
    487: (chambers2, 'giratina'), 488: (chambers4, 'cresselia'), 489: (chambers5, 'phione'), 490: (chambers5, 'manaphy'),
    491: (chambers, 'darkrai'), 492: (chambers5, 'shaymin'), 493: (chambers2, 'arceus'), 494: (chambers5, 'victini'),
    638: (chambers5, 'cobalion'), 639: (chambers5, 'terrakion'), 640: (chambers5, 'virizion'), 641: (chambers5, 'tornadus'),
    642: (chambers5, 'thundurus'), 643: (chambers5, 'reshiram'), 644: (chambers5, 'zekrom'), 645: (chambers5, 'landorus'),
    646: (chambers5, 'kyurem'), 647: (chambers5, 'keldeo'), 648: (chambers5, 'meloetta'), 649: (chambers5, 'genesect'),
    716: (chambers6, 'xerneas'), 717: (chambers6, 'yveltal'), 718: (chambers6, 'zygarde'), 719: (chambers6, 'diancie'),
    720: (chambers6, 'hoopa'), 721: (chambers6, 'volcanion'), 785: (chambers6, 'tapu_koko'), 786: (chambers6, 'tapu_lele'),
    787: (chambers6, 'tapu_bulu'), 788: (chambers6, 'tapu_fini'), 789: (chambers6, 'cosmog'), 790: (chambers6, 'cosmoem'),
    791: (chambers6, 'solgaleo'), 792: (chambers6, 'lunala'), 800: (chambers6, 'necrozma'), 801: (chambers6, 'magearna'),
    802: (chambers7, 'marshadow'), 807: (chambers7, 'zeraora'), 808: (chambers7, 'meltan'), 809: (chambers7, 'melmetal'),
    888: (chambers7, 'zacian'), 889: (chambers7, 'zamazenta'), 890: (chambers7, 'eternatus'), 891: (chambers7, 'kubfu'),
    892: (chambers7, 'urshifu'), 893: (chambers7, 'zarude'), 894: (chambers7, 'regieleki'), 895: (chambers7, 'regidrago'),
    896: (chambers7, 'glastrier'), 897: (chambers7, 'spectrier'), 898: (chambers7, 'calyrex'), 905: (chambers7, 'enamorus'),
    1001: (chambers8, 'wo_chien'), 1002: (chambers8, 'chien_pao'), 1003: (chambers8, 'ting_lu'), 1004: (chambers8, 'chi_yu'),
    1007: (chambers8, 'koraidon'), 1008: (chambers8, 'miraidon'), 1014: (chambers8, 'okidogi'), 1015: (chambers8, 'munkidori'),
    1016: (chambers8, 'fezandipiti'), 1017: (chambers8, 'ogerpon'), 1024: (chambers8, 'terapagos'), 1025: (chambers8, 'pecharunt'),
}

def room_image(mod, name):
    r = mod.ROOMS[name]()
    im = Image.new('RGB', (chambers.W, chambers.H))
    im.putdata([c for row in r.px for c in row])
    return im

def shiny_map():
    """Kyogre's colours to its shiny ones: for each colour of the front sprite, the commonest shiny colour there."""
    a = Image.open(os.path.join(SPRITES, '382.png')).convert('RGBA')
    b = Image.open(os.path.join(SPRITES, 'shiny', '382.png')).convert('RGBA').resize(a.size, Image.NEAREST)
    votes = {}
    for y in range(a.height):
        for x in range(a.width):
            p, q = a.getpixel((x, y)), b.getpixel((x, y))
            if p[3] > 128 and q[3] > 128: votes.setdefault(p[:3], {}).setdefault(q[:3], 0); votes[p[:3]][q[:3]] += 1
    m = {c: max(v, key=v.get) for c, v in votes.items()}
    def to_shiny(c):
        near = min(m, key=lambda k: sum((k[i] - c[i]) ** 2 for i in range(3)))
        return m[near] if sum((near[i] - c[i]) ** 2 for i in range(3)) < 3000 else c
    return to_shiny

def kyogre(shiny):
    """The approved round-3 Kyogre: the side-on sprite resting at the waterline (y 66), ripples round it, the
    pool's front stones back in front of it."""
    sys.argv = ['kyogre_side.py', os.path.join('/tmp', 'kyogre_side.png')]
    exec(open(os.path.join(HERE, 'kyogre_side.py')).read(), {'__name__': 'kyogre_side'})
    ky = Image.open('/tmp/kyogre_side.png').convert('RGBA')
    if shiny:
        f = shiny_map()
        ky.putdata([f(p[:3]) + (p[3],) if p[3] else p for p in ky.getdata()])
    clean = room_image(chambers2, 'kyogre').convert('RGBA')
    room, wl = clean.copy(), 66
    room.alpha_composite(ky, (120 - 44, wl - ky.height + 1))
    d = ImageDraw.Draw(room)
    for x0, x1 in ((74, 166),):
        d.arc((x0 - 4, wl - 3, x1 + 4, wl + 5), 0, 180, fill=(232, 244, 255)); d.arc((x0 - 9, wl - 5, x1 + 9, wl + 8), 15, 165, fill=(120, 192, 248))
    for (a, b, c, e) in ast.literal_eval(open(os.path.join(HERE, 'chamber2_kyogre_front.txt')).read()):
        room.paste(clean.crop((a, b, c + 1, e + 1)), (a, b))
    return room.convert('RGB')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    towers.save(towers.b_beacon(), os.path.join(out, 'tower_front.png'))
    for num, (mod, name) in sorted(ROOMS.items()):
        im = kyogre(False) if num == 382 else room_image(mod, name)
        im.save(os.path.join(out, 'chamber_%d.png' % num))
    kyogre(True).save(os.path.join(out, 'chamber_382_shiny.png'))
    print('build.py: tower_front.png and %d chambers' % len(ROOMS))
