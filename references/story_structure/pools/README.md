# Lore Entropy Pools

Curated option pools injected into writers-room **Phase 3.5 (Lore Forge)
Step 0** to break the model's default lore attractors. Ported 2026-06-11
from the gemmawood sister project (byte-identical to the divergence-test
originals, where they were validated across 20-run batches).

**cultures.json** — 1,585-entry curated cultural/historical option set
(name, country, period: current / historical / pre-historical). 32
entries sampled per project; faction and population parallels in
SEASON_LORE.md must come from the sampled set. Breaks the default
attractor toward a narrow band of Western/East-Asian parallels
(divergence finding: Byzantine Empire appeared in 11/20 unconditioned
runs, Mongol 9/20).

**history_shapes.json** — 32 lore trajectory templates (e.g. Cyclical
Dynasties, Migration & Founding, Suspended Apocalypse, Ascendant
Underclass). One sampled per project with instruction to harmonize.
Breaks the "founding rupture then five-act decline" template that
emerged across unconditioned runs.

**country_culture_reference.xlsx** — provenance spreadsheet for the
1,585 cultures.json entries.

**sampling_state.json** — machine-managed no-repeat ledger (created on
first draw, committed to git). Cultures are excluded once drawn by any
project until the pool exhausts (~49 projects at 32/draw), then the
ledger auto-resets with a notice. History shapes use a sliding window
(last 8 draws excluded). Do not edit by hand; `--reset` clears it.

## Use

```bash
# Standard draw for a project (writes projects/{name}/STORY/WRITERS_ROOM/LORE_SEEDS.md)
python3 scripts/writer/sample_pools.py --project {name}

# Deterministic re-roll / preview
python3 scripts/writer/sample_pools.py --project {name} --seed 7
python3 scripts/writer/sample_pools.py --project {name} --dry-run
```

User-brief overrides win over the sample (a brief that demands a
specific culture or history shape is honored); document overrides in
LORE_SEEDS.md.
