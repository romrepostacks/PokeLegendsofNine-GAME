# Overworld art (9.4.0)

The overworld overhaul's art, approved round by round in the art review. It was drawn by the scripts in the project
folder's `plans/9.3.5-overworld/<round>/` (ground1, trees1, water1, props1, caves1, weather1, buildings1, interiors1,
battle1). Each folder here is one layer. `gba/tools/export.js` (`lookOf`) picks an area's layers, and the first layer
that has a tile wins:

| Folder | What |
|---|---|
| `ground_A/B/C` | meadow, deep green (forests), golden (Calderra, the Sundered Isles, ash); `ground_map.json` recolours old pieces |
| `trees_<ground>_oak/pine` | trees and bushes per ground |
| `props_<ground>`, `props_<ground>_moss` | fences, signs, rocks, tablets, ledges; mossy fence/rock/tablet in forests |
| `water_C` | tropical shallows with sand (golden ground); other areas keep the original water |
| `caves_A/B/U` | warm rock (regions 2-4), cool stone, under the sea |
| `weather_oak/pine/ash` | puddles, snow drifts, snow and ash on the trees, the ashen lawn |
| `buildings_A/B/C`, `interiors_A/B/C` | MART and house fronts and rooms, in the style of the town's CENTER |
| `battle_bg_A/B/C.png` | the battle backdrop per ground (`build_assets.py`) |
