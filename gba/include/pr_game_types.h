// Species and move data types; the data itself is generated into pr_game_data.h by tools/build_assets.py.
#ifndef PR_GAME_TYPES_H
#define PR_GAME_TYPES_H

#include <cstdint>
#include "bn_sprite_item.h"
#include "pr_ids.h"

namespace pr
{

enum class move_category : uint8_t
{
    PHYSICAL,
    SPECIAL,
    STATUS
};

enum class status : uint8_t
{
    NONE,
    POISON,
    BURN,
    PARALYSIS,
    SLEEP,
    FREEZE
};

// Who a move hits: the chosen foe, every foe (Earthquake, Growl), the user (Swords Dance) or no one (weather).
enum class move_target : uint8_t
{
    ONE,
    FOES,
    SELF,
    FIELD
};

enum class battle_weather : uint8_t
{
    NONE,
    SUN,
    RAIN,
    SAND,
    HAIL,
    WIND            // 4.0.0: strong winds (the SKYREACH's clouds): Flying types lose their weaknesses; it never stops
};

// The battle stats a move can raise or lower.
namespace battle_stat
{
    enum : int8_t { ATK, DEF, SPA, SPD, SPE, ACC, EVA, COUNT };
}

struct stat_change
{
    int8_t stat;
    int8_t delta;
};

// 9.6.0: what kind of move it is, for the abilities that care.
namespace move_flag
{
    constexpr uint8_t SOUND = 1;      // Soundproof, Punk Rock
    constexpr uint8_t BITE = 2;       // Strong Jaw
    constexpr uint8_t PULSE = 4;      // Mega Launcher
    constexpr uint8_t BALL = 8;       // Bulletproof (ball and bomb moves)
    constexpr uint8_t DANCE = 16;     // Dancer
    constexpr uint8_t WIND = 32;      // Wind Rider, Wind Power
    constexpr uint8_t POWDER = 64;    // Overcoat
    constexpr uint8_t EXPLODE = 128;  // Damp
}

struct move
{
    const char* name;
    int8_t type;
    uint8_t power;
    move_category category;
    uint8_t accuracy;
    status inflicts;          // status moves
    status secondary;         // damaging moves' side effect
    uint8_t secondary_chance;
    bool punch;               // Iron Fist boosts it
    uint8_t pp;
    move_target target;
    int8_t drain;             // % of the damage dealt: + heals the user, - is recoil
    uint8_t heal;             // % of the user's max HP it restores
    stat_change stats[3];     // stage changes (to the target, or the user if stat_self)
    uint8_t stat_count;
    uint8_t stat_chance;      // % (damaging moves' side effect; status moves always)
    bool stat_self;
    battle_weather weather;
    uint8_t flags;            // 9.6.0: move_flag bits, for the abilities that care (Soundproof, Strong Jaw...)
};

struct learn_entry
{
    uint8_t level;
    uint16_t move;
};

struct base_stats
{
    uint8_t hp;
    uint8_t atk;
    uint8_t def;
    uint8_t spa;
    uint8_t spd;
    uint8_t spe;
};

// What an ability does in battle (damage()): the rest are flavour.
enum class ability_kind : uint8_t
{
    FLAVOR,
    BOOST,          // its type's moves x1.5 at 1/3 HP or less (Blaze, Torrent...)
    IMMUNE,         // takes no damage from one type (Levitate, Flash Fire...)
    PUNCH,          // punching moves x1.2 (Iron Fist)
    MERCILESS,      // x1.5 against a poisoned target
    CORROSION,      // Poison moves hit Steel and Poison types
    DISGUISE,       // the first hit does nothing
    // 9.5.0: the common abilities. `type` holds their one setting where they have one (a weather, status or stat).
    WEATHER_SPEED,  // SPEED x2 in its weather (Swift Swim, Chlorophyll, Sand Rush)
    WEATHER_START,  // starts its weather when the battle does (Drizzle, Drought, Sand Stream, Snow Warning)
    INTIMIDATE,     // the foes' ATTACK -1 when the battle starts
    STURDY,         // holds on with 1 HP from full
    THICK_FAT,      // Fire and Ice moves do half to it
    FLUFFY,         // physical moves do half to it, Fire twice as much
    GUTS,           // ATTACK x1.5 with a status, and a burn doesn't halve it
    HUSTLE,         // ATTACK x1.5, its physical moves 80% as accurate
    HUGE_POWER,     // ATTACK x2 (Huge Power, Pure Power)
    TECHNICIAN,     // moves of 60 power or less x1.5
    RECKLESS,       // recoil moves x1.2
    SHEER_FORCE,    // moves with a side effect x1.3, without it
    TOUGH_CLAWS,    // physical moves x1.3
    ADAPTABILITY,   // STAB x2
    TYPE_POWER,     // its type's moves x1.5 (Steelworker, Transistor, Dragon's Maw)
    FILTER,         // super effective hits do 3/4 (Filter, Solid Rock, Prism Armor)
    MULTISCALE,     // half damage at full HP (Multiscale, Shadow Shield)
    MARVEL_SCALE,   // DEFENSE x1.5 with a status
    FUR_COAT,       // DEFENSE x2
    UNAWARE,        // ignores the other side's stat stages
    NO_GUARD,       // its moves and the moves against it always hit
    COMPOUND_EYES,  // its moves x1.3 as accurate
    WEATHER_EVADE,  // moves against it 80% as accurate in its weather (Sand Veil, Snow Cloak)
    ROCK_HEAD,      // no recoil
    WONDER_GUARD,   // only super effective moves hurt it
    NO_STATUS,      // can't get its status (Insomnia, Limber, Water Veil...), or any (status NONE: Purifying Salt)
    CONTACT_STATUS, // a physical hit on it may give the attacker its status, 30% (Static, Flame Body, Poison Point)
    ROUGH_SKIN,     // a physical hit on it costs the attacker 1/8 of its HP (Rough Skin, Iron Barbs)
    SHED_SKIN,      // a 1 in 3 chance to cure its status each turn
    SPEED_BOOST,    // SPEED +1 each turn
    HYDRATION,      // cures its status at the end of a rainy turn
    ICE_BODY,       // heals 1/16 at the end of a hail turn, and hail doesn't hurt it
    MOXIE,          // its best stat +1 when it knocks a foe out (Beast Boost, Moxie)
    DEFIANT,        // ATTACK +2 when a foe lowers its stats
    JUSTIFIED,      // ATTACK +1 when a Dark move hits it
    WEAK_ARMOR,     // a physical hit: DEFENSE -1, SPEED +2
    STAMINA,        // DEFENSE +1 when it's hit
    RATTLED,        // SPEED +1 when a Bug, Dark or Ghost move hits it
    CLEAR_BODY,     // foes can't lower its stats (or one stat: Hyper Cutter, Big Pecks, Keen Eye)
    PROTOSYNTHESIS, // its best stat x1.3 in harsh sunlight
    PRESSURE,       // moves aimed at it use 2 PP
    SYNCHRONIZE,    // a foe that gives it a status gets it too
    MOLD_BREAKER,   // its moves ignore the target's ability
    LIQUID_OOZE,    // draining it hurts instead
    AFTERMATH,      // knocked out by a physical move: the attacker loses 1/4 of its HP
    RIPEN,          // its SITRUS BERRY heals twice as much
    // 9.6.0: the rest. `type` holds the setting as above, or a move_flag, a terrain (1 electric, 2 grassy,
    // 3 misty, 4 psychic) or a stat.
    TRUANT,         // loafs around every second turn
    SLOW_START,     // ATTACK and SPEED halved for its first five turns
    QUARK_DRIVE,    // its best stat x1.3 (SPEED x1.5) in Electric Terrain, and its first five turns (Booster Energy)
    PICKUP,         // may find an item after a battle it won
    HONEY_GATHER,   // may gather HONEY after a battle it won (sold on the spot)
    ILLUMINATE,     // leading the party: twice as many wild POKéMON
    STENCH,         // its hits may make the target flinch, 10%; leading the party: half as many wild POKéMON
    NATURAL_CURE,   // its status is cured when the battle ends
    CUTE_CHARM,     // a physical hit on it may infatuate the attacker, 30%
    FOCUS,          // INTIMIDATE doesn't work on it; nor flinching (0), confusion (1) or infatuation (2); 3: Scrappy
    SHIELD_DUST,    // the moves that hit it have no side effects
    PRANKSTER,      // its status moves go first
    MYCELIUM_MIGHT, // its status moves go last, and ignore the target's ability
    DAZZLING,       // the foes' status moves that would go first fail against its side
    FLAG_IMMUNE,    // the moves with one move_flag do nothing to it (Soundproof, Bulletproof, Overcoat)
    FLAG_POWER,     // its moves with one move_flag x1.5 (Strong Jaw, Mega Launcher)
    PUNK_ROCK,      // its sound moves x1.3, sound moves against it x0.5
    LEAF_GUARD,     // no status in harsh sunlight
    HEALER,         // each ally with a status may be cured at the end of a turn, 30%
    STEADFAST,      // SPEED +1 when it flinches
    EARLY_BIRD,     // wakes up twice as fast
    FRISK,          // sees the foes' held items when the battle starts
    OVERCOAT,       // no harm from sandstorms and hail, and powder moves do nothing to it
    DAMP,           // no one can SELF-DESTRUCT, and AFTERMATH doesn't work
    TRAP,           // wild POKéMON: you can't run (0 all; else only your POKéMON of that type), but GHOST types and RUN AWAY can
    SERENE_GRACE,   // its moves' side effects twice as likely
    PLUS_MINUS,     // SP. ATK x1.5 when an ally has PLUS or MINUS
    ANTICIPATION,   // shudders when a foe has a super effective move
    FOREWARN,       // learns the foes' strongest move when the battle starts
    FLOWER_VEIL,    // its side's GRASS types' stats can't be lowered by foes
    CONTRARY,       // stat changes on it go the other way
    SIMPLE,         // stat changes on it count double
    TRACE,          // copies a foe's ability when the battle starts
    CHEEK_POUCH,    // eating a berry also heals 1/3 of its HP
    GLUTTONY,       // (the SITRUS BERRY is eaten at half HP for everyone here)
    STEAM_ENGINE,   // SPEED +6 when a Fire or Water move hits it
    WATER_COMPACTION, // DEFENSE +2 when a Water move hits it
    TOXIC_CHAIN,    // its hits may badly poison, 30%
    MUMMY,          // a physical hit on it gives the attacker its ability (Mummy, Lingering Aroma)
    WANDERING_SPIRIT, // a physical hit on it swaps abilities with the attacker
    DEFEATIST,      // ATTACK and SP. ATK halved at half HP or less
    ILLUSION,       // looks like the last POKéMON of its side until it's hit
    REFRIGERATE,    // its Normal moves are of `type` and x1.2
    STAKEOUT,       // its moves x2 on the first turn, as the foes come in
    COTTON_DOWN,    // when hit: everyone else's SPEED -1
    SAND_SPIT,      // when hit: a sandstorm
    SEED_SOWER,     // when hit: Grassy Terrain
    CHARGE_UP,      // when hit (by a wind move, 1: Wind Power): its next Electric move x2
    UNBURDEN,       // SPEED x2 once its held item is gone
    WIND_RIDER,     // wind moves do nothing to it and raise its ATTACK
    GOOEY,          // a physical hit on it: the attacker's SPEED -1
    TOXIC_DEBRIS,   // a physical hit on it poisons the attacker
    SUPERSWEET_SYRUP, // the foes' evasiveness -1 when the battle starts
    HOSPITALITY,    // heals its most hurt ally 1/4 when the battle starts
    CURSED_BODY,    // may disable the move that hit it, 30%
    FORECAST,       // its type follows the weather
    COLOR_CHANGE,   // its type becomes the type of the move that hit it
    AIR_LOCK,       // the weather has no effects while it's in battle
    FLOWER_GIFT,    // its side's ATTACK and SP. DEF x1.5 in harsh sunlight
    BAD_DREAMS,     // sleeping foes lose 1/8 of their HP each turn
    VICTORY_STAR,   // its side's moves x1.1 as accurate
    WONDER_SKIN,    // status moves against it hit half the time at most
    SAND_FORCE,     // Rock, Ground and Steel moves x1.3 in a sandstorm, and the sandstorm doesn't hurt it
    DOWNLOAD,       // ATTACK or SP. ATK +1 when the battle starts, against the foes' weaker defense
    STANCE_CHANGE,  // Blade Forme to attack (ATTACK/DEFENSE and SP. ATK/SP. DEF swap), Shield Forme for status moves
    AURA,           // moves of its `type` x1.33 for everyone (Fairy Aura, Dark Aura)
    AURA_BREAK,     // the auras weaken their moves instead (x0.75)
    MAGICIAN,       // its hits take the target's held item when it holds none (given back after the battle)
    STICKY_HOLD,    // its held item can't be taken
    BATTERY,        // its allies' special moves x1.3
    POWER_SPOT,     // its allies' moves x1.3
    FRIEND_GUARD,   // its allies take 3/4 damage
    DANCER,         // dances along to every dance move another POKéMON uses
    SCHOOLING,      // from level 20, a mighty school above 1/4 HP
    RECEIVER,       // takes the ability of an ally that faints
    WIMP_OUT,       // wild ones flee below half HP
    INNARDS_OUT,    // knocked out: the attacker takes the HP it had left
    SHIELDS_DOWN,   // no status above half HP
    BERSERK,        // SP. ATK +1 when a hit takes it below half HP
    ANGER_SHELL,    // a hit takes it below half HP: ATTACK, SP. ATK, SPEED +1, DEFENSE, SP. DEF -1
    TERRAIN_START,  // starts its terrain when the battle does
    SOUL_HEART,     // SP. ATK +1 each time a POKéMON faints
    BALL_FETCH,     // brings back the first POKé BALL that fails, holding nothing
    GULP_MISSILE,   // after SURF or DIVE, the next attacker is hit back
    ICE_FACE,       // the first physical hit does nothing (again when hail starts)
    ENTRY_STAT,     // its `type` stat +1 when the battle starts (Intrepid Sword, Dauntless Shield)
    UNNERVE,        // the foes can't eat berries
    AROMA_VEIL,     // its side can't be infatuated or disabled
    OPPORTUNIST,    // copies the foes' stat rises
    COMMANDER,      // with a DONDOZO on its side, DONDOZO's stats +2 when the battle starts
    CUD_CHEW,       // eats its SITRUS BERRY again at the end of the next turn
    GOOD_AS_GOLD,   // the foes' status moves do nothing to it
    RUIN,           // everyone else's `type` stat x0.75 (Tablets, Sword, Vessel, Beads of Ruin)
    ORICHALCUM_PULSE, // harsh sunlight when the battle starts; ATTACK x1.33 in it
    HADRON_ENGINE,  // Electric Terrain when the battle starts; SP. ATK x1.33 in it
    POISON_PUPPETEER, // the POKéMON it poisons are confused too
    TANGLED_FEET,   // moves against it half as accurate while it's confused
    FORM_TYPE,      // JUDGMENT and MULTI-ATTACK take its type (Multitype, RKS System)
    HUNGER_SWITCH,  // AURA WHEEL turns Dark every second turn
    FORM_CHANGE,    // another form's stats (`type` 0 Zero to Hero after its first turn, 1 Tera Shift from the start)
    RUN_AWAY,       // can always run, even from a POKéMON that traps
    RIVALRY         // its moves x1.25 against a POKéMON that shares a type with it (this game has no genders)
};

struct ability
{
    const char* name;
    const char* desc;
    ability_kind kind;
    int8_t type;              // BOOST / IMMUNE: the type, else -1
};

// ITEM_INFO: pocket 0 ITEMS, 1 POKé BALLS, 2 TMs & HMs, 3 BERRIES, 4 KEY ITEMS.
struct item_info
{
    const char* name;
    uint8_t pocket;
    const char* desc;
    uint32_t price;           // 9.3.0: wide enough for the EVOLVE CANDY's $1,000,000
    uint16_t heal;            // HP restored
    status cure;              // status cured
    bool revive;              // revives a fainted Pokémon to half HP
    bool full;                // full HP and status
};

// Held items (ITEMS, FREE BATTLE's draft and the trainers' Leftovers).
enum class held_item : uint8_t
{
    NONE,
    LEFTOVERS,
    LIFE_ORB,
    CHOICE_SCARF,
    FOCUS_SASH,
    SITRUS_BERRY
};

struct held_item_info
{
    const char* name;
    const char* desc;
};

// GBA 1.8: an item that evolves one species into another when it's used on it (stones, the LINKING CORD).
struct evo_item
{
    uint16_t from;
    uint16_t to;
    item_id item;
};

// GBA 1.8: a TM (it can be used again and again): the move it teaches, its item, and the badges the MART
// wants to see before it sells it.
struct tm_info
{
    uint16_t move;
    item_id item;
    uint8_t badges;
};

struct species
{
    const char* name;
    int16_t dex_number;
    int8_t type1;
    int8_t type2;             // -1: single type
    base_stats base;
    const learn_entry* learnset;
    int16_t learnset_count;
    const uint16_t* fixed_moves;    // hand-made entries without a learnset know these
    int8_t fixed_count;
    int16_t evolves_to;       // index into species_list, -1 if none
    uint8_t evolve_level;
    uint8_t capture_rate;     // Emerald's catch rate (PokeAPI), 3-255
    const ability& abil;
    uint16_t height;          // decimetres (DEXINFO)
    uint16_t weight;          // hectograms
    const char* genus;        // "Seed"
    const bn::sprite_item& front;
    const bn::sprite_item& back;
    const bn::sprite_item& icon;    // 32x32, the party screen and the PC
};

}

#endif
