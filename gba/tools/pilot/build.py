#!/usr/bin/env python3
"""Builds the pilot's test ROM into WORK: a copy of gba/ whose main() runs test_pilot.inc's test_setup() and
whose battles pick for you when SRAM 0x7E04 says so (battle_patch.inc).
    python3 tools/pilot/build.py WORK"""
import os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
GBA = os.path.dirname(os.path.dirname(HERE))

def build(work):
    gba = os.path.join(work, 'gba')
    if os.path.exists(gba):
        shutil.rmtree(gba)
    shutil.copytree(GBA, gba, symlinks=True, ignore=shutil.ignore_patterns('build', 'roms', 'butano', '*.gba', '*.elf'))
    os.symlink(os.path.join(GBA, 'butano'), os.path.join(gba, 'butano'))
    for d in ('js', 'sprites'):
        if not os.path.exists(os.path.join(work, d)):
            os.symlink(os.path.join(os.path.dirname(GBA), d), os.path.join(work, d))
    main = os.path.join(gba, 'src', 'main.cpp')
    s = open(main).read()
    s = s.replace('int main()', '#include "%s"\nint main()' % os.path.join(HERE, 'test_pilot.inc'), 1)
    s = s.replace('pr::ui::set_faded(true);', 'pr::ui::set_faded(true);\n    test_setup();', 1)
    open(main, 'w').write(s)
    bat = os.path.join(gba, 'src', 'pr_battle.cpp')
    s = open(bat).read()
    anchor = '        ui& u = gui();\n        int queue[max_own];'
    assert s.count(anchor) == 1
    s = s.replace(anchor, open(os.path.join(HERE, 'battle_patch.inc')).read() + anchor, 1)
    s = '#include "bn_sram.h"\n' + s
    open(bat, 'w').write(s)
    # A fresh -j4 build sometimes races on generated sprite headers; a second make picks up where it stopped.
    if subprocess.run(['make', '-j4'], cwd=gba, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        subprocess.run(['make', '-j4'], cwd=gba, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['gcc', '-O2', os.path.join(HERE, 'pilot_harness.c'), '-o', os.path.join(work, 'harness'), '-lmgba'], check=True)
    return os.path.join(gba, 'party-royale.gba'), os.path.join(work, 'harness')

if __name__ == '__main__':
    print(build(os.path.abspath(sys.argv[1])))
