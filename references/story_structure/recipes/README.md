# Story Recipe Library

Genre-specific story recipes derived using
`../story-recipe-methodology.md` (v2 — wired) and the skill at
`skills/writer/story-recipe/SKILL.md`.

Each recipe in this directory is a working AI prompt: slot, emotional
contract, FFAR+C cast (causally obligated), named tropes (including
anti-tropes), **wired beat spine** (every beat carries `Needs:` /
`Sets up:` causal edges plus an emotional target), conformity/variation
rules, and the fixed whole-output **Wiring tests** block.

## Use

- A project picks a recipe at `writers-room` Phase 0 (or earlier, via
  the `story-recipe` skill).
- The recipe is copied into `projects/{project}/STORY/RECIPE.md` and
  logged in `PROJECT_CONFIG.yaml` under `writers_room.recipe`.
- The recipe's Needs/Sets-up edges are the floor of the Story Lock's
  Episode Arc and seed the project's Causal Contract (writers-room
  v3.7). Edges fixed; edge-content free.
- Register (warm / brutal / pulpy / quiet / etc.) is a separate dial
  recorded alongside the slug.

## Provenance

Ported 2026-06-11 from the gemmawood sister project
(`260611 gemmawood/data/recipes/`), where all 54 passed a mechanical
wiring validator: emitter-named concrete-artifact tags, bidirectional
graph closure, front-half obligations, climax consuming ≥3 distinct
earlier beats, no template boilerplate. `ensemble_heist` is the
hand-wired gold example; `cyberpunk`, `urban_fantasy`, `tragedy`,
`hard_sf_systems` were hand-wired alongside it; the remaining 49 were
migrated via `_rewire-prompt.md` and validated per-recipe. Substance
spot-checks: slasher (full audit); comfort_rewatch_sitcom,
sports_underdog_montage, talent_show_stage (soft-stakes stress sample).

## Contributing

To add a recipe, follow the 8-step derivation procedure in
`../story-recipe-methodology.md`. Use
`skills/writer/story-recipe/RECIPE_TEMPLATE.md` as the format.
To migrate a v1 recipe, use `_rewire-prompt.md` (or run the skill's
Rewire mode).

**Acceptance bar:** every new or edited recipe must pass the Claude
wiring self-check in `skills/writer/story-recipe/SKILL.md` (tag
grammar, graph closure both directions, front-half obligations, climax
preconditions, verbatim Wiring-tests block) plus a derivation-notes
review. A recipe missing any of the seven mandatory elements degrades
into a description.

## Library (54 slots, all v2-wired)

- `body_horror_medical` — recoil + transformation + intimacy
- `buddy_road_movie` — friction + reluctant intimacy + grace
- `class_shame_upstairs_downstairs` — shame + transgression + consequence
- `comfort_rewatch_sitcom` — familiarity + low-stakes + belonging
- `coming_of_age_indie` — awakening + alienation + small breakthrough
- `competence_porn_workplace` — mastery + pressure + belonging
- `cosmic_horror` — dread + revelation + dissolution
- `cozy_mystery_village` — puzzle + community + restoration
- `cursed_gunslinger_western` — vengeance + dread + reckoning
- `cyberpunk` — alienation + rage + defiance
- `domestic_horror` — intimacy + violation + recognition
- `dystopian` — oppression + awakening + revolt
- `ensemble_heist` — cleverness + camaraderie + reversal *(gold example)*
- `epic_fantasy_quest` — destiny + sacrifice + transformation
- `erotic_tension_slow_approach` — prolongation + delay + consummation
- `family_saga_multigen` — legacy + grievance + return
- `folk_horror_ancestral` — inheritance + ritual + reckoning
- `forced_together_romance` — friction + proximity + dissolve
- `four_quadrant_animated_adventure` — wonder + risk + delight
- `gothic_romance` — desire + suspicion + revelation
- `hard_sf_systems` — physics + collaboration + revelation
- `haunted_house` — grief + dread + release
- `innocent_companion_hostile_system` — wonder + protection + ache
- `kitchen_sink_drama` — indignity + endurance + small mercy
- `legal_thriller` — outrage + pressure + vindication
- `locked_room_thriller` — confinement + pressure + revelation
- `lone_survival_wilderness` — endurance + ingenuity + ache
- `monster_horror_genre` — tension + chase + reveal
- `mythic_franchise_epic` — pantheon + war + apotheosis
- `noir_detective` — decay + compulsion + complicity
- `operatic_melodrama` — passion + tragedy + grand emotion
- `political_satire_bite` — recognition + complicity + futility
- `political_thriller` — conspiracy + escalation + crisis
- `post_apocalyptic` — loss + endurance + renewal
- `prestige_period_intrigue` — etiquette + concealment + power
- `procedural_pressure_realtime` — clock + room + improvisation
- `psychological_thriller` — doubt + paranoia + collapse
- `revenge_thriller_quiet` — patience + targeting + reckoning
- `romantasy` — desire + danger + transformation
- `shonen_anime_quest` — friendship + escalation + earned-power
- `slasher` — fear + pursuit + survival
- `slow_burn_prestige` — ambiguity + interiority + patient revelation
- `space_opera` — wonder + peril + exaltation
- `sports_underdog_montage` — training + setback + victory
- `talent_show_stage` — performance + stakes + reveal
- `teen_intimacy_confession` — vulnerability + becoming + risk
- `tragedy` — hope + flaw + ruin
- `transgressive_anthology` — transgressive desire + visceral consequence + spectacular ruin
- `transgressive_serial` — desire + mutation + systems horror + ecstatic collapse
- `urban_fantasy` — disorientation + enchantment + belonging
- `vampire` — desire + seduction + damnation
- `western` — loneliness + violence + reckoning
- `western_road_lone` — drift + accumulation + reckoning
- `ya_dystopian_romance` — sorted world + forbidden love + reluctant symbol

## Not in this library, by design

- **Innocent + impossible-tech companion vs hostile system (stray-signal
  variant)** — the generalized slot now exists above as
  `innocent_companion_hostile_system`; the original project-specific
  derivation lives inside the stray-signal project.
