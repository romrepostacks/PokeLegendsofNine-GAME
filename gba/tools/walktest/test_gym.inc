#include "bn_assert.h"
#include "bn_sram.h"
#include "pr_mon.h"
#include "pr_world_data.h"
// Gym test (9.3.4, gymtest.py): SRAM 0x7E00 holds an area (+ 1); you start on the rug of its gym with its juniors
// beaten (unless 0x7E02 holds 1: then they fight), and the address of game_state goes to 0x7E20 (map, x, y, facing
// are its first fields), that of its `beaten` bits to 0x7E24, and the juniors' trainer ids to 0x7E28 (4 int16, -1 none).
// An assert writes "CRSH" at 0x7E10.
static void crash_mark()
{
    char tag[4] = { 'C', 'R', 'S', 'H' };
    bn::sram::write_offset(tag, 0x7E10);
}
static void test_setup()
{
    bn::assert::set_callback(crash_mark);
    int16_t req = 0, fight = 0;
    bn::sram::read_offset(req, 0x7E00);
    bn::sram::read_offset(fight, 0x7E02);
    pr::game_state& g = pr::state();
    pr::reset_state();
    g.name[0]='G'; g.name[1]='Y'; g.name[2]='M';
    g.story = pr::story::STARTER | pr::story::CALL1 | pr::story::CALL2 | pr::story::CALL3;
    g.run.skip_story = true;
    constexpr pr::species_id team[] = { pr::species_id::KORAIDON, pr::species_id::MIRAIDON, pr::species_id::SKELEDIRGE,
                                        pr::species_id::MEOWSCARADA, pr::species_id::QUAQUAVAL, pr::species_id::KINGAMBIT };
    for(int i = 0; i < 6; ++i) g.party[i] = pr::mon::make(team[i], 1000);
    g.party_count = 6;
    int room = -1;
    for(int i = 0; req > 0 && i < pr::world_data::maps_count; ++i)
    {
        const pr::map_def& m = pr::world_data::maps[i];
        if(m.room && m.room->puzzle && m.exit_map == pr::world_data::area_maps[req - 1]) room = i;
    }
    if(room >= 0)
    {
        const pr::map_def& m = pr::world_data::maps[room];
        g.map = int16_t(room); g.x = m.spawn_x; g.y = m.spawn_y; g.surfing = false; g.facing = pr::direction::UP;
        int16_t ids[4] = { -1, -1, -1, -1 };
        for(int i = 0, n = 0; i < m.trainers_count; ++i)
        {
            if(m.trainers[i].role != pr::trainer_role::JUNIOR) continue;
            if(fight != 1) g.beaten.set(m.trainers[i].id);
            if(n < 4) ids[n++] = int16_t(m.trainers[i].id);
        }
        bn::sram::write_offset(ids, 0x7E28);
    }
    uint32_t at = uint32_t(reinterpret_cast<uintptr_t>(&g));
    bn::sram::write_offset(at, 0x7E20);
    uint32_t bits = uint32_t(reinterpret_cast<uintptr_t>(&g.beaten));
    bn::sram::write_offset(bits, 0x7E24);
    pr::save_game();
}
