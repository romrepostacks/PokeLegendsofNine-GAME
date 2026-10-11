        // pilot.py: SRAM 0x7E04 picks for you (1 smart, 2 always the first move, 3 smart and catch everything new;
        // +0x80 runs from wild battles: with 3, only those it has nothing new in). Test builds only.
        {
            uint8_t pol = 0;
            bn::sram::read_offset(pol, 0x7E04);
            if(pol)
            {
                const bool wild = ! _s.opponent && ! _s.free;
                bool all_owned = true;
                for(int k = 0; k < _foe_count; ++k) all_owned &= state().owned.test(_foes[k].m->species_index);
                if(wild && (pol & 0x80) && ! _s.legendary && ((pol & 0x7f) != 3 || all_owned))
                {
                    gui().say("Got away safely!");
                    ran = true;
                    _active = -1;
                    return false;
                }
                const int style = pol & 0x7f;
                bool any_hit = false;
                for(int i = 0; i < _own_count; ++i)
                {
                    if(_own[i].out()) continue;
                    const mon& m = *_own[i].m;
                    int ft = -1;
                    for(int k = 0; k < _foe_count; ++k) if(! _foes[k].out()) { ft = k; break; }
                    if(ft < 0) ft = 0;
                    if(m.out_of_pp()) { choices[i] = { choice_kind::MOVE, -1, ft, item_id::POTION }; continue; }
                    if(style == 2)
                    {
                        int mv = 0;
                        while(mv < m.move_count - 1 && ! m.pp(mv)) ++mv;
                        choices[i] = { choice_kind::MOVE, mv, ft, item_id::POTION };
                        continue;
                    }
                    // Catch: a wild legend, or (style 3) anything not owned yet, once it's worn down.
                    const mon& fm = *_foes[ft].m;
                    bool want = wild && (_s.legendary || (style == 3 && ! state().owned.test(fm.species_index) && state().party_count < 8 && (! state().run.nuzlocke() || (_s.nuzlocke_catch && ! _nuz_caught))));
                    if(want)
                    {
                        constexpr item_id balls[] = { item_id::MASTERBALL, item_id::ULTRABALL, item_id::GREATBALL, item_id::POKEBALL };
                        item_id ball = item_id::POTION;
                        for(item_id b : balls)
                        {
                            if(b == item_id::MASTERBALL && ! _s.legendary) continue;
                            if(state().item_count(b)) { ball = b; break; }
                        }
                        bool low = fm.hp * 3 <= fm.max_hp || ball == item_id::MASTERBALL || fm.level + 5 < m.level;
                        if(ball != item_id::POTION && low && i == 0)
                        {
                            choices[i] = { choice_kind::BALL, 0, ft, ball }; any_hit = true;
                            continue;
                        }
                    }
                    if(m.hp * 4 < m.max_hp)
                    {
                        constexpr item_id meds[] = { item_id::FULLRESTORE, item_id::MAXPOTION, item_id::HYPERPOTION, item_id::SUPERPOTION, item_id::POTION };
                        bool used = false;
                        for(item_id it : meds)
                        {
                            if(state().item_count(it)) { choices[i] = { choice_kind::ITEM, 0, 0, it }; used = true; any_hit = true; break; }
                        }
                        if(used) continue;
                    }
                    int best = -1, best_t = ft, best_score = -1;
                    bool gentle = false;    // ponytail: gentle hits stalled 600+ presses on 9-vs-3 wilds; balls go at 1/3 HP anyway
                    for(int mv = 0; mv < m.move_count; ++mv)
                    {
                        if(! m.pp(mv)) continue;
                        const move& md = move_data(m.move(mv));
                        for(int k = 0; k < _foe_count; ++k)
                        {
                            if(_foes[k].out()) continue;
                            int score = 1;
                            if(md.category != move_category::STATUS)
                            {
                                int eff = move_effectiveness_x4(m, md, *_foes[k].m);
                                score = md.power * eff * (m.has_type(md.type) ? 3 : 2) / 2 * md.accuracy / 100 + 2;
                                if(eff == 0) score = 0;
                                if(gentle && score > 0) score = 100000 - score;
                            }
                            if(score > best_score) { best_score = score; best = mv; best_t = k; }
                        }
                    }
                    choices[i] = { choice_kind::MOVE, best < 0 ? 0 : best, best_t, item_id::POTION };
                    any_hit |= best_score > 1 || style == 2;
                }
                if(wild && ! any_hit && ! _s.legendary)
                {
                    // Nothing left that can hurt it (a Ghost against Normal and Ground moves): run, as a player would.
                    gui().say("Got away safely!");
                    ran = true;
                    _active = -1;
                    return false;
                }
                _active = -1;
                return true;
            }
        }
