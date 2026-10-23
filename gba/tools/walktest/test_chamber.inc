#include "bn_assert.h"
#include "bn_sram.h"
#include "pr_mon.h"
#include "pr_game_data.h"
#include "pr_world_data.h"
// Chamber test (9.3.4, chambertest.py): SRAM 0x7E00 holds a dex number, 0x7E02 1 for a shiny. You start on the TOWER
// SUMMIT facing its SUMMONING STONE, on a challenge, with that legendary already called. The address of game_state
// goes to 0x7E20 (map, x, y are its first fields). An assert writes "CRSH" at 0x7E10.
static void crash_mark()
{
    char tag[4] = { 'C', 'R', 'S', 'H' };
    bn::sram::write_offset(tag, 0x7E10);
}
static void test_setup()
{
    bn::assert::set_callback(crash_mark);
    int16_t num = 0, shiny = 0;
    bn::sram::read_offset(num, 0x7E00);
    bn::sram::read_offset(shiny, 0x7E02);
    pr::game_state& g = pr::state();
    pr::reset_state();
    g.name[0]='T'; g.name[1]='W'; g.name[2]='R';
    g.story = pr::story::STARTER | pr::story::CALL1 | pr::story::CALL2 | pr::story::CALL3;
    g.run.skip_story = true;
    constexpr pr::species_id team[] = { pr::species_id::KORAIDON, pr::species_id::MIRAIDON, pr::species_id::SKELEDIRGE,
                                        pr::species_id::MEOWSCARADA, pr::species_id::QUAQUAVAL, pr::species_id::KINGAMBIT };
    for(int i = 0; i < 6; ++i) g.party[i] = pr::mon::make(team[i], 1000);
    g.party_count = 6;
    for(int i = 0; num > 0 && i < pr::species_count; ++i)
    {
        if(pr::game_data::species_list[i].dex_number == num) { g.tower.legend = int16_t(i); break; }
    }
    g.tower.active = true;
    g.tower.legend_shiny = shiny == 1;
    for(int i = 0; i < pr::world_data::maps_count; ++i)
    {
        const pr::map_def& m = pr::world_data::maps[i];
        if(m.room && m.room->kind == pr::room_kind::SUMMIT)
        {
            g.map = int16_t(i); g.x = 7; g.y = 6; g.surfing = false; g.facing = pr::direction::UP;
        }
    }
    uint32_t at = uint32_t(reinterpret_cast<uintptr_t>(&g));
    bn::sram::write_offset(at, 0x7E20);
    pr::save_game();
}
