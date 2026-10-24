#include "bn_assert.h"
#include "bn_sram.h"
#include "pr_mon.h"
#include "pr_game_data.h"
#include "pr_people_sprites.h"
#include "pr_world_data.h"
// Statue test (9.4.1, statuetest.py): SRAM 0x7E00 holds n; you start beside the nth landmark (a 32x32 statue_<look>
// person) on the tile below its right half, facing it. 0x7E20 gets the address of game_state (map, x, y first),
// 0x7E24 the landmark's map, x, y and kind, 0x7E2C the number of landmarks. An assert writes "CRSH" at 0x7E10.
static void crash_mark()
{
    char tag[4] = { 'C', 'R', 'S', 'H' };
    bn::sram::write_offset(tag, 0x7E10);
}
static void test_setup()
{
    namespace wd = pr::world_data;
    bn::assert::set_callback(crash_mark);
    int16_t n = 0;
    bn::sram::read_offset(n, 0x7E00);
    pr::game_state& g = pr::state();
    pr::reset_state();
    g.name[0]='T'; g.name[1]='S'; g.name[2]='T';
    g.story = pr::story::STARTER | pr::story::CALL1 | pr::story::CALL2 | pr::story::CALL3;
    g.run.skip_story = true;
    g.flags.set(pr::flag::ANCIENT_SEED);          // the tree is up in the present
    g.party[0] = pr::mon::make(pr::species_id::ARCEUS, 100);
    g.party_count = 1;
    int16_t found[4] = { -1, 0, 0, 0 }, count = 0;
    for(int i = 0; i < wd::maps_count; ++i)
    {
        const pr::map_def& m = wd::maps[i];
        for(int k = 0; k < m.people_count; ++k)
        {
            const pr::person& p = m.people[k];
            if(pr::person_sprites[int(p.kind)]->shape_size().width() != 32) continue;
            if(++count == n)
            {
                found[0] = int16_t(i); found[1] = int16_t(p.x); found[2] = int16_t(p.y); found[3] = int16_t(p.kind);
                g.map = int16_t(i); g.x = int16_t(p.x + 1); g.y = int16_t(p.y + 1); g.facing = pr::direction::UP;
                g.region = uint8_t(pr::map_region(i));
            }
        }
    }
    uint32_t at = uint32_t(reinterpret_cast<uintptr_t>(&g));
    bn::sram::write_offset(at, 0x7E20);
    bn::sram::write_offset(found, 0x7E24);
    bn::sram::write_offset(count, 0x7E2C);
    pr::save_game();
}
