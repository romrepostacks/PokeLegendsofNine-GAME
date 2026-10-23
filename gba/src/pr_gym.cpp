// 9.3.4: every gym its own challenge, played the way tools/gym/solver.py plays it (that file is the spec, and
// tests every gym): ice, fences and their switches, boulders and pits, fans and currents, pads, bogs, wrong notes,
// vines, flame jets, gas and its valves, high ground and ledges, cracked floor, tesla coils, magnets, dive spots,
// and rooms that change state (era, tide, season, the clock).
#include "bn_bitset.h"
#include "bn_memory.h"

#include "pr_audio.h"
#include "pr_overworld_impl.h"
#include "pr_ui.h"

namespace pr
{

namespace
{
    constexpr int max_tiles = 640;
    constexpr int no_link = 0x3fff;
    constexpr const char* solid_letters = "#xuLgjPESQTrnWKX{}!`";

    // Where the challenge is up to. It lives outside the scene (made anew after every battle) and starts over
    // whenever you come in, or load a game saved inside.
    struct puzzle_run
    {
        int map_plus_1;             // the gym it's for, + 1 (0: none)
        int sw;                     // the switch last stepped on (1-3), or the coils' step count
        int var;                    // the room's state
        uint32_t act;               // bit 0 the gate's open, 1 + i valve i turned, 20 + i pearl i lit
        bn::bitset<max_tiles> holes;    // open pits (and broken floor)
        bn::bitset<max_tiles> rocks;    // boulders
    };
    BN_DATA_EWRAM puzzle_run pzr;

    bool has(const char* set, char c)
    {
        for(; *set; ++set)
        {
            if(*set == c)
            {
                return true;
            }
        }
        return false;
    }

    bool arrow(char c)
    {
        return c == '^' || c == 'v' || c == '<' || c == '>';
    }

    direction arrow_way(char c)
    {
        return c == '^' ? direction::UP : c == 'v' ? direction::DOWN : c == '<' ? direction::LEFT : direction::RIGHT;
    }

    int tile_index(const map_def& m, int tx, int ty)
    {
        return tx < 0 || ty < 0 || tx >= m.w || ty >= m.h ? -1 : ty * m.w + tx;
    }

    int link_of(const gym_puzzle& pz, int i)
    {
        return pz.aux[i] & no_link;
    }

    // Junior j is the room's trainer j + 1 (the leader comes first).
    bool junior_beaten(const map_def& m, int j)
    {
        return j + 1 < m.trainers_count && state().beaten.test(m.trainers[j + 1].id);
    }

    bool gate_open(const map_def& m, const gym_puzzle& pz)
    {
        if(pz.flags & puzzle_flag::GATE_JUNIORS)
        {
            for(int j = 0; j + 1 < m.trainers_count; ++j)
            {
                if(! junior_beaten(m, j))
                {
                    return false;
                }
            }
            return true;
        }
        return pzr.act & 1;
    }

    bool fence_up(const map_def& m, const gym_puzzle& pz, char c)
    {
        if(c == 'F' && (pz.flags & (puzzle_flag::GATE_PLATES | puzzle_flag::GATE_PEARLS | puzzle_flag::GATE_JUNIORS)))
        {
            return ! gate_open(m, pz);
        }
        if(pz.pulse)
        {
            return c != (pzr.sw < pz.pulse ? 'F' : 'f');    // tesla coils: F and f take turns
        }
        return (c == 'F' ? 1 : c == 'f' ? 2 : 3) != pzr.sw;
    }

    bool arrow_on(const gym_puzzle& pz, int i)
    {
        int lane = link_of(pz, i);
        if(lane != no_link)
        {
            return lane == pzr.sw;
        }
        return pz.fans < 0 || pzr.sw == pz.fans;
    }

    int level_of(const gym_puzzle& pz, int i, char c)
    {
        if(c == 'p' || c == 'O')
        {
            return (pz.aux[i] & 0x4000) ? 1 : 0;   // a pit or boulder up on high ground
        }
        return c == 'H' || c == 'l' ? 1 : c == 's' ? 2 : 0;
    }

    // The n-th tile with this letter, in reading order, in the room's first state (pedestals and pearls).
    int nth_of(const gym_puzzle& pz, int i, char c)
    {
        int n = 0;
        for(int k = 0; k < i; ++k)
        {
            n += pz.cells[k] == c;
        }
        return pz.cells[i] == c ? n : -1;
    }

    void reset_floor(const map_def& m, const gym_puzzle& pz)
    {
        pzr.holes.reset();
        pzr.rocks.reset();
        for(int i = 0; i < m.w * m.h; ++i)
        {
            pzr.holes.set(i, pz.cells[i] == 'p');
            pzr.rocks.set(i, pz.cells[i] == 'O');
        }
    }
}

const gym_puzzle* overworld::puzzle() const
{
    return _map->room ? _map->room->puzzle : nullptr;
}

char overworld::puzzle_cell(int tx, int ty) const
{
    int i = tile_index(*_map, tx, ty);
    return i < 0 ? '#' : puzzle()->cells[pzr.var * _map->w * _map->h + i];
}

bool overworld::puzzle_water(int tx, int ty) const
{
    char c = puzzle_cell(tx, ty);
    return c == '~' || c == 'D' || (arrow(c) && puzzle()->over == '~' && ! (puzzle()->flags & puzzle_flag::RAFT));   // a raft: you stand on it
}

bool overworld::puzzle_solid(int tx, int ty) const
{
    const gym_puzzle& pz = *puzzle();
    const map_def& m = *_map;
    int i = tile_index(m, tx, ty);
    if(i < 0 || pzr.rocks.test(i))
    {
        return true;
    }
    char c = puzzle_cell(tx, ty);
    if(c == 'O')
    {
        c = '_';
    }
    if(c == 'p' || (arrow(c) && pz.over == 'p' && ! arrow_on(pz, i)))
    {
        return pzr.holes.test(i) || arrow(c);
    }
    if(pz.flags & puzzle_flag::STEP_ASIDE)
    {
        for(int t = 1; t < m.trainers_count; ++t)
        {
            if(m.trainers[t].x == tx && m.trainers[t].y == ty)
            {
                return ! state().beaten.test(m.trainers[t].id);     // a gate junior steps aside once beaten
            }
        }
    }
    if(c == 'M')
    {
        return false;
    }
    if(has(solid_letters, c))
    {
        return true;
    }
    switch(c)
    {
    case 'F':
    case 'f':
    case 'G':
        return fence_up(m, pz, c);
    case '~':
    case 'D':
        return ! (pz.flags & puzzle_flag::SURF);
    case 'R':
        return pz.flags & puzzle_flag::R_SOLID;
    case 'J':
        return ! (pz.flags & puzzle_flag::J_STEP);
    case 'V':
    case 'Y':
    {
        if(c == 'Y' && ! (pz.flags & puzzle_flag::Y_JET))
        {
            return true;
        }
        int j = link_of(pz, i);
        return j == no_link || ! junior_beaten(m, j);
    }
    case 'z':
    {
        int v = link_of(pz, i);
        return v == no_link || ! ((pzr.act >> (v + 1)) & 1);
    }
    default:
        break;
    }
    return arrow(c) && pz.over == '~' && ! (pz.flags & (puzzle_flag::SURF | puzzle_flag::RAFT));
}

int overworld::puzzle_metatile(int tx, int ty) const
{
    const gym_puzzle& pz = *puzzle();
    const map_def& m = *_map;
    int n = m.w * m.h;
    int i = tile_index(m, tx, ty);
    const uint16_t* metas = pz.metas + pzr.var * 3 * n;
    if(pzr.rocks.test(i))
    {
        return metas[2 * n + i];
    }
    char c = puzzle_cell(tx, ty);
    bool alt = false;
    switch(c)
    {
    case 'F':
    case 'f':
    case 'G':
        alt = ! fence_up(m, pz, c);
        break;
    case 'p':
        alt = ! pzr.holes.test(i);
        break;
    case 'k':
        alt = pzr.holes.test(i);
        break;
    case 'z':
    case 'V':
    case 'Y':
        alt = ! puzzle_solid(tx, ty);
        break;
    default:
        alt = arrow(c) && pz.over == 'p' && ! arrow_on(pz, i);
        break;
    }
    return metas[(alt ? n : 0) + i];
}

void overworld::puzzle_enter()
{
    const gym_puzzle* pz = puzzle();
    if(! pz)
    {
        pzr.map_plus_1 = 0;
        return;
    }
    if(pzr.map_plus_1 == _map_index + 1)
    {
        return;
    }
    // In through the door (or a game loaded inside): the challenge starts over, from the rug.
    game_state& g = state();
    pzr.map_plus_1 = _map_index + 1;
    pzr.sw = 0;
    pzr.var = 0;
    pzr.act = 0;
    reset_floor(*_map, *pz);
    g.x = int16_t(_map->spawn_x);
    g.y = int16_t(_map->spawn_y);
    g.surfing = false;
}

void overworld::puzzle_redraw()
{
    draw_cells(true);
}

void overworld::puzzle_bump()
{
    game_state& g = state();
    audio::play(audio::sfx::BUMP);
    for(int f = 0; f < walk_frames; ++f)
    {
        set_player_frame(g.surfing ? 0 : f < walk_frames / 2 ? 1 + _step_parity : 0);
        tick();
    }
    _step_parity ^= 1;
}

// One tile on: walked, hopped down a ledge, or carried (sliding on ice, blown by a fan, swept by a current).
void overworld::puzzle_glide(direction d, int frames, bool jump, bool carried)
{
    game_state& g = state();
    int start_px = _px, start_py = _py;
    _from_x = g.x;
    _from_y = g.y;
    g.x = int16_t(g.x + dx_of(d));
    g.y = int16_t(g.y + dy_of(d));
    g.surfing = puzzle_water(g.x, g.y) && puzzle_water(_from_x, _from_y);
    for(int f = 1; f <= frames; ++f)
    {
        _px = start_px + dx_of(d) * 16 * f / frames;
        _py = start_py + dy_of(d) * 16 * f / frames;
        _cam_x = _px - view_x;
        _cam_y = _py - view_y;
        if(jump)
        {
            _lift = (f * (frames - f) * 8) / (frames * frames / 4);
        }
        set_player_frame(carried || g.surfing ? 0 : f <= frames / 2 ? 1 + _step_parity : 0);
        tick();
    }
    _lift = 0;
    _step_parity ^= 1;
    _from_x = _from_y = -1000;
    _grass_x = g.x;
    _grass_y = g.y;
    g.surfing = puzzle_water(g.x, g.y);
    set_player_frame(0);
}

// Gone to another spot of the room in a blink (a pad, a dive spot, or back to the rug).
void overworld::puzzle_warp(int tx, int ty)
{
    game_state& g = state();
    ui::fade_out(12);
    g.x = int16_t(tx);
    g.y = int16_t(ty);
    g.surfing = puzzle_water(tx, ty);
    _px = g.x * 16;
    _py = g.y * 16;
    _cam_x = _px - view_x;
    _cam_y = _py - view_y;
    _grass_x = g.x;
    _grass_y = g.y;
    set_player_frame(0);
    refresh(true);
    ui::fade_in(12);
}

void overworld::puzzle_step(direction d)
{
    game_state& g = state();
    const gym_puzzle& pz = *puzzle();
    const map_def& m = *_map;
    int tx = g.x + dx_of(d), ty = g.y + dy_of(d);
    int gi = tile_index(m, g.x, g.y), ti = tile_index(m, tx, ty);
    if(ti < 0 || actor_at(tx, ty) >= 0)
    {
        puzzle_bump();
        return;
    }
    char a = puzzle_cell(g.x, g.y), b = puzzle_cell(tx, ty);
    if(pzr.rocks.test(ti))
    {
        // A boulder: it goes one tile on, into a pit (filling it), never onto water, ice, a mat or a current.
        int bx = tx + dx_of(d), by = ty + dy_of(d), bi = tile_index(m, bx, by);
        char c2 = puzzle_cell(bx, by);
        if(bi < 0 || (level_of(pz, ti, b) != level_of(pz, bi, c2) && c2 != 's') || actor_at(bx, by) >= 0 ||
           (bx == g.x && by == g.y))
        {
            puzzle_bump();
            return;
        }
        pzr.rocks.reset(ti);
        if(pzr.holes.test(bi))
        {
            pzr.holes.reset(bi);
        }
        else if(puzzle_solid(bx, by) || has("~DZNi=", c2) || arrow(c2))
        {
            pzr.rocks.set(ti);
            puzzle_bump();
            return;
        }
        else
        {
            pzr.rocks.set(bi);
        }
        audio::play(audio::sfx::HIT);
        if(pz.flags & puzzle_flag::GATE_PLATES)
        {
            bool all = true;
            for(int i = 0; i < m.w * m.h; ++i)
            {
                all &= pz.cells[i] != 'q' || pzr.rocks.test(i);
            }
            if(all)
            {
                pzr.act |= 1;
            }
        }
        puzzle_redraw();
    }
    else if(puzzle_solid(tx, ty))
    {
        puzzle_bump();
        return;
    }
    // High ground: change level on stairs, or drop south off a ledge.
    int la = level_of(pz, gi, a), lb = level_of(pz, ti, b);
    bool drop = a == 'l' && d == direction::DOWN && lb == 0;
    if(la != 2 && lb != 2 && la != lb && ! drop)
    {
        puzzle_bump();
        return;
    }
    bool falls = b == 'k' && pzr.holes.test(ti);
    if(drop && la != lb)
    {
        audio::play(audio::sfx::JUMP);
    }
    puzzle_glide(d, drop && la != lb ? jump_frames / 2 : walk_frames, drop && la != lb, false);
    if(a == 'k')
    {
        pzr.holes.set(gi);      // cracked floor gives way behind you
        puzzle_redraw();
    }
    if(falls)
    {
        say("The cracked floor gave way!");
        reset_floor(m, pz);
        puzzle_warp(m.spawn_x, m.spawn_y);
        return;
    }
    if(puzzle_sight())
    {
        return;
    }
    // Carried on: ice and magnets slide you until something stops you, fans and currents blow you along.
    bool mag = pz.flags & puzzle_flag::E_MAG;
    for(int k = 0; k < 80; ++k)
    {
        char c = puzzle_cell(g.x, g.y);
        int i = tile_index(m, g.x, g.y);
        if(c == 'i' || (c == 'e' && mag))
        {
            int nx = g.x + dx_of(d), ny = g.y + dy_of(d);
            char cn = puzzle_cell(nx, ny);
            int ni = tile_index(m, nx, ny);
            if(ni < 0 || puzzle_solid(nx, ny) || actor_at(nx, ny) >= 0 || has("r~D", cn) || arrow(cn) ||
               (level_of(pz, ni, cn) != level_of(pz, i, c) && cn != 's' && c != 's'))
            {
                break;
            }
            puzzle_glide(d, run_frames, false, true);
            if(puzzle_sight())
            {
                return;
            }
            if((has("de", cn) && ! mag) || cn == 'd')
            {
                break;
            }
            continue;
        }
        if(arrow(c) && (pz.over != 'p' || arrow_on(pz, i)))
        {
            d = arrow_way(c);
            int nx = g.x + dx_of(d), ny = g.y + dy_of(d);
            if(puzzle_solid(nx, ny) || actor_at(nx, ny) >= 0)
            {
                break;
            }
            puzzle_glide(d, run_frames, false, true);
            if(puzzle_sight())
            {
                return;
            }
            continue;
        }
        break;
    }
    if(pz.pulse)
    {
        pzr.sw = (pzr.sw + 1) % (2 * pz.pulse);
        puzzle_redraw();
    }
    char c = puzzle_cell(g.x, g.y);
    int i = tile_index(m, g.x, g.y);
    if(c == 'Z' || c == 'N' || (c == 'p' && pzr.holes.test(i)))
    {
        say(c == 'Z' ? "You sank into the bog and had to crawl back to the entrance." :
            c == 'N' ? "A sour note! The floor bounced you back to the entrance." : "You fell! You climbed back out at the entrance.");
        puzzle_warp(m.spawn_x, m.spawn_y);
        return;
    }
    if(c == 'a' || c == 'b' || c == 'c')
    {
        int to = link_of(pz, i);
        if(to != no_link)
        {
            audio::play(audio::sfx::POP);
            puzzle_warp(to % m.w, to / m.w);
        }
    }
    if(c == '1' || c == '2' || c == '3')
    {
        if((pz.flags & puzzle_flag::ERA_SWITCH) && pz.states > 1)
        {
            pzr.var = (pzr.var + 1) % pz.states;
            audio::play(audio::sfx::PC_ON);
            puzzle_redraw();
        }
        else if(pzr.sw != c - '0')
        {
            pzr.sw = c - '0';
            audio::play(audio::sfx::PC_ON);
            puzzle_redraw();
        }
    }
    arrive();
}

bool overworld::puzzle_interact()
{
    game_state& g = state();
    const gym_puzzle& pz = *puzzle();
    const map_def& m = *_map;
    int here = tile_index(m, g.x, g.y);
    if(puzzle_cell(g.x, g.y) == 'D' && (pz.flags & puzzle_flag::DIVE) && link_of(pz, here) != no_link)
    {
        int to = link_of(pz, here);
        say("You dove down and swam through to another pool!");
        puzzle_warp(to % m.w, to / m.w);
        return true;
    }
    int fx = g.x + dx_of(g.facing), fy = g.y + dy_of(g.facing);
    int fi = tile_index(m, fx, fy);
    char c = puzzle_cell(fx, fy);
    if(c == 'S')
    {
        audio::play(audio::sfx::PC_ON);
        if(pz.states > 1 && ! (pz.flags & puzzle_flag::ERA_SWITCH))
        {
            pzr.var = (pzr.var + 1) % pz.states;
            puzzle_redraw();
            say("You turned the pedestal's dial. The whole room changed!");
        }
        else if(pz.flags & puzzle_flag::S_FANS)
        {
            pzr.sw = pzr.sw == pz.fans ? 0 : pz.fans;
            puzzle_redraw();
            say(pzr.sw == pz.fans ? "The fans whirred to life!" : "The fans wound down.");
        }
        else
        {
            pzr.act |= 1u << (nth_of(pz, fi, 'S') + 1);
            puzzle_redraw();
            say("You turned the valve. Somewhere, the gas cleared.");
        }
        return true;
    }
    if(c == 'Q')
    {
        int k = nth_of(pz, fi, 'Q');
        pzr.act |= 1u << (20 + k);
        bool all = true;
        for(int i = 0; i < m.w * m.h; ++i)
        {
            all &= pz.cells[i] != 'Q' || ((pzr.act >> (20 + nth_of(pz, i, 'Q'))) & 1);
        }
        if(all && (pz.flags & puzzle_flag::GATE_PEARLS))
        {
            pzr.act |= 1;
        }
        audio::play(audio::sfx::HEAL);
        puzzle_redraw();
        say(all ? "The pearl lit up, and the gate swung open!" : "The pearl lit up with a soft glow.");
        return true;
    }
    return false;
}

// Juniors see 5 tiles the way they face, over floor, grass, water and ice (the room's first state, as the solver).
bool overworld::puzzle_sight()
{
    game_state& g = state();
    const gym_puzzle& pz = *puzzle();
    const map_def& m = *_map;
    for(int i = 0; i < _actors.size(); ++i)
    {
        actor& a = _actors[i];
        if(! a.active_trainer() || a.tr->role != trainer_role::JUNIOR)
        {
            continue;
        }
        for(int s = 1; s <= sight; ++s)
        {
            int tx = a.x + dx_of(a.facing) * s, ty = a.y + dy_of(a.facing) * s;
            int ti = tile_index(m, tx, ty);
            char c = ti < 0 ? '#' : pz.cells[ti];
            if(has(solid_letters, c) || has("OFfGVYzlsp<>^v", c))
            {
                break;
            }
            if(tx == g.x && ty == g.y)
            {
                trainer_approach(i);
                return true;
            }
        }
    }
    return false;
}

bool overworld::puzzle_skips(const trainer& t) const
{
    const gym_puzzle* pz = puzzle();
    return pz && (pz->flags & puzzle_flag::STEP_ASIDE) && t.role == trainer_role::JUNIOR && state().beaten.test(t.id);
}

}
