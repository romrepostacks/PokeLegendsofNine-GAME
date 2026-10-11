#include "bn_assert.h"
#include "bn_sram.h"
#include "pr_mon.h"
#include "pr_world_data.h"
// pilot.py: an assert writes "CRSH" at SRAM 0x7E10; every boot writes where the game state lives at 0x7E40
// ("PILT", its address, then offsets) so the pilot can read it.
static void crash_mark()
{
    char tag[4] = { 'C', 'R', 'S', 'H' };
    bn::sram::write_offset(tag, 0x7E10);
}
static void test_setup()
{
    using namespace pr;
    bn::assert::set_callback(crash_mark);
    game_state& g = state();
    const char* b = reinterpret_cast<const char*>(&g);
    auto o = [b](const void* p) { return uint16_t(reinterpret_cast<const char*>(p) - b); };
    const mon& m = g.party[0];
    const char* mb = reinterpret_cast<const char*>(&m);
    auto mo = [mb](const void* p) { return uint16_t(reinterpret_cast<const char*>(p) - mb); };
    struct table
    {
        char tag[4];
        uint32_t addr;
        uint16_t v[40];
    } t = { { 'P', 'I', 'L', 'T' }, uint32_t(reinterpret_cast<uintptr_t>(&g)), {
        uint16_t(sizeof(game_state)), uint16_t(sizeof(mon)),
        o(&g.map), o(&g.x), o(&g.y), o(&g.facing), o(&g.party_count), o(&g.surfing), o(&g.story), o(&g.money),
        o(&g.play_frames), o(&g.items), o(&g.party), o(&g.beaten), o(&g.picked), o(&g.owned), o(&g.visited),
        o(&g.region), o(&g.flags), o(&g.run), o(&g.opt), o(&g.last_heal),
        mo(&m.species_index), mo(&m.level), mo(&m.hp), mo(&m.max_hp), mo(&m.moves), mo(&m.pp_used), mo(&m.move_count),
        mo(&m.xp), mo(&m.st), o(&g.seen), o(&g.walk_off), o(&g.box) } };
    bn::sram::write_offset(t, 0x7E40);
    // A region start (SRAM 0x7E02 = 1000 + region): every region before it beaten, its legends caught, and you
    // at the region's first town with the party pilot.py wrote at 0x7F00 (count, level, species...), as if you'd
    // just arrived. 0x7E03's high bit: SKIP STORY TEXT. Only when there's no save yet.
    int16_t scen = 0;
    bn::sram::read_offset(scen, 0x7E02);
    if(scen < 1000 || save_exists())
    {
        return;
    }
    namespace wd = pr::world_data;
    const int region = scen - 1000;
    struct party_req
    {
        uint16_t count, level, skip, money;
        uint16_t species[10];
    } req;
    bn::sram::read_offset(req, 0x7F00);
    reset_state();
    g.name[0]='P'; g.name[1]='I'; g.name[2]='L'; g.name[3]='O'; g.name[4]='T';
    g.story = story::STARTER | story::CALL1 | story::CALL2 | story::CALL3 | story::SCENE_TEMPEST_RUN |
              story::SCENE_PORTMERE | story::SCENE_HIDEOUT | story::SCENE_SHRINE | story::STORM_ENDED | story::CHAMPION |
              story::LEGEND_CAUGHT;
    g.run.skip_story = req.skip;
    g.run.adventure = true;
    for(int i = 0; i < req.count && i < 10; ++i)
    {
        g.party[i] = mon::make(species_id(req.species[i]), req.level);
    }
    g.party_count = uint8_t(req.count);
    g.money = uint32_t(req.money) * 10;
    g.add_item(item_id::ULTRABALL, 30);
    g.add_item(item_id::HYPERPOTION, 10);
    g.add_item(item_id::REVIVE, 5);
    g.add_item(item_id::HM03, 1);
    g.add_item(item_id::HM08, 1);
    for(int i = 0; i < wd::maps_count; ++i)
    {
        if(map_region(i) >= region) continue;
        const map_def& m = wd::maps[i];
        for(int k = 0; k < m.trainers_count; ++k) g.beaten.set(m.trainers[k].id);
        g.visited.set(i);
        for(int k = 0; k < m.items_count; ++k) g.picked.set(m.items[k].id);
    }
    constexpr int legends[] = { 0, 1, 2, 3, flag::CALDERRA_STARTER, flag::GROUDON, flag::KYOGRE, flag::RAYQUAZA, flag::DEOXYS };
    constexpr int legends_region[] = { 2, 2, 2, 2, 2, 3, 3, 4, 4 };
    for(int k = 0; k < 9; ++k) if(legends_region[k] < region) g.flags.set(legends[k]);
    for(int r = 2; r < region; ++r) g.flags.set(champion_flag(r));
    if(region > 5) { g.flags.set(flag::MEWTWO); g.flags.set(flag::MEW); }
    if(region > 6) { g.flags.set(flag::DIALGA); g.flags.set(flag::PALKIA); }
    if(region > 7) g.flags.set(flag::GIRATINA);
    if(region > 8) { g.flags.set(flag::ARTICUNO); g.flags.set(flag::ZAPDOS); g.flags.set(flag::MOLTRES); g.flags.set(flag::LUGIA); }
    g.region = uint8_t(region - 1);
    for(int i : wd::area_maps)
    {
        if(map_region(i) == region)
        {
            g.map = int16_t(i); g.x = wd::maps[i].spawn_x; g.y = wd::maps[i].spawn_y;
            g.visited.set(i);
            g.last_heal = int16_t(i);
            break;
        }
    }
    save_game();
}
