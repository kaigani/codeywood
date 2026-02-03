# Experimentation Findings

**Project**: Hellmouth Cowboy
**Date Started**: 2026-01-29
**Goal**: Establish locked style DNA and validate hero shot approach

---

## Style DNA Tests

### Test 1: gothic_western - Lone Figure
**Status**: ✓ Complete
**Winner**: SeeDream v4.5
**File**: `style_dna_1_seedream_20260129_180658.png`

**Observations**:
- [x] Matches target aesthetic (dark western + gothic horror) - PERFECT
- [x] High contrast working? - Excellent, dramatic sky vs. dark silhouette
- [x] Color palette accurate? - Deep blacks, blood-red crimson sky, desaturated tones
- [x] Silhouettes strong? - Gunslinger reads instantly, powerful presence
- [x] Would work as style reference? - YES, locked as master reference

**Notes**: Rich painterly cel-shaded rendering. Atmospheric dust and volumetric lighting work beautifully. Captures ominous biblical plague energy.


---

### Test 2: samurai_jack_minimal - Town Aftermath
**Status**: ✓ Complete
**Winner**: Nano Banana Pro (10/10 graphic minimal)
**File**: `style_dna_2_nano_banana_20260129_182924.png`

**Observations**:
- [x] Too minimal? - No, perfect for specific graphic needs
- [x] Graphic shapes working? - Excellent flat vector shapes, pure geometry
- [x] Negative space effective? - Massive blue sky, stark symmetry achieved
- [x] Loses needed detail? - Intentional, works for posters not primary production

**Notes**: Nano Banana Pro nailed this. Use this DNA for promotional/poster work, not primary production pipeline. Too minimal for character emotion work.


---

### Test 3: base - Gunfight Aftermath
**Status**: ✓ Complete
**Winner**: SeeDream v4.5
**File**: `style_dna_3_seedream_20260129_181007.png`

**Observations**:
- [x] Balance of detail vs style? - Good cel-shaded detail, maintains animation aesthetic
- [x] Color treatment? - Proper desaturated earth tones with blood-red accents
- [x] Texture quality? - Clean vector lines with weight variation visible
- [x] Atmospheric? - Yes, smoke and shallow depth work well

**Notes**: Solid baseline, but Gothic Western DNA is stronger for Hellmouth Cowboy's horror-western fusion aesthetic.


---

## Style DNA Evaluation

**Winner**: **SeeDream v4.5 + Gothic Western DNA**

**Rationale**:
- SeeDream v4.5 consistently interpreted animation style prompts correctly across all DNA templates
- Gothic Western DNA provides atmospheric, dramatic, horror-western fusion core to Hellmouth Cowboy
- Painterly cel-shaded aesthetic balances stylization with emotional depth
- Rich atmospheric rendering supports biblical plague/corruption themes
- All 3 tests maintained strong silhouettes, proper line work, and style consistency

**Secondary Model**: Nano Banana Pro for technical reference sheets (Phase 3 identity sheets)

**Refinements to make**:
- Gothic Western DNA is production-ready as-is
- Will tune reference weights during hero shot phase (0.85-0.90 for style lock)

**Locked Style DNA**:
```
Medium/Era: Dark animated style inspired by Castlevania gothic horror meets Sergio Leone spaghetti western cinematography
Line-work/Texture: Heavy ink outlines with weight variation, crisp silhouettes, slight paper grain texture
Lighting/Rendering: Dramatic rim lighting, deep cel-shaded shadows, volumetric dust and atmosphere, high contrast
Color Palette: Desaturated dusty palette with deep blacks and blood-red punctuation
```

**Extracted Hex Palette** (from Test 1 winner):
```
["#1a0d0f", "#2d1419", "#4a1e23", "#6b2d32", "#8b4449", "#a85c5c", "#c47a6f", "#d89881", "#8b6f5e", "#5e4a3d"]
```

---

## Hero Shot Tests (Nameless)

### Test 1: The Entrance
**Status**: ✓ Complete - **LOCKED AS PRIMARY**
**File**: `hero_nameless_entrance_seedream_20260129_202132.png`

**Observations**:
- [x] Captures character essence? - PERFECT - "walking plague, death on two legs"
- [x] Would work as key art? - YES - instantly iconic, poster-worthy
- [x] Style consistent with locked DNA? - 10/10 - Gothic Western DNA perfectly executed
- [x] Silhouette strong? - Perfect - reads at any scale, dominates despite low angle
- [x] Informs what to emphasize in identity sheet? - YES - skeleton motif, heavy outlines, atmospheric dust

**Notes**: Brilliant artistic choice showing skeleton beneath weathered skin. Blood-red petals/embers floating. Volumetric dust and heat shimmer. This IS Nameless.


---

### Test 2: The Signature Action (Gun Draw)
**Status**: ✓ Complete - **LOCKED AS PRIMARY**
**File**: `hero_nameless_draw_seedream_20260129_202202.png`

**Observations**:
- [x] Motion readable? - 10/10 - Draw motion perfect, dual revolvers with muzzle flash
- [x] Character consistent? - YES - Face matches entrance shot styling
- [x] Captures cold efficiency? - PERFECT - "No anger, no satisfaction. Just work that never ends"
- [x] Hands working? - Excellent - motion lines, dramatic perspective

**Notes**: Weathered face utterly calm. Heavy ink outlines on face and hands. Blood-red particles. Defines signature action perfectly.


---

### Test 3: The Quiet Moment
**Status**: ✓ Complete - **LOCKED AS PRIMARY**
**File**: `hero_nameless_quiet_seedream_20260129_202220.png`

**Observations**:
- [x] Vulnerability showing? - 10/10 - Slumped shoulders, exhaustion visible, "tired beyond measure"
- [x] Firelight working? - Exceptional - campfire from below, upward shadows, haunting mood
- [x] Isolation conveyed? - YES - Empty space around him, alone with dead embers
- [x] Different from action shots? - Perfect counterpoint - "who he is when no one is dying"

**Notes**: Gray hair revealed without hat. Massive dark silhouette behind him = weight of curse. Vulnerability beneath the legend.


---

## Hero Shot Evaluation (Nameless)

**Winner**: **ALL THREE LOCKED** - Each serves distinct narrative purpose

**What makes it work**:
- **Entrance**: Establishes visual presence and threat - "death walking"
- **Draw**: Defines signature action and cold efficiency
- **Quiet**: Reveals vulnerability and weight of curse

Gothic Western DNA perfectly executed across all shots. Style consistency excellent. Character reads clearly in action, stillness, and vulnerability.

**Details to emphasize in identity sheet**:
1. **Skeleton motif** - visible beneath weathered skin (entrance innovation)
2. **Heavy ink outlines** - especially face, hands, coat edges
3. **Gray hair** - longer than expected when hat off
4. **Dead eyes** - centuries of killing visible
5. **Weathered leather face** - stretched over sharp bones
6. **Twin revolvers** - worn grips, clear silhouettes
7. **Long duster coat** - nearly black with trail dust, dramatic flow
8. **Wide-brimmed hat** - pulled low, creates dramatic shadow


**Character-specific palette notes**:
```
Coat/Hat: ["#0d0d0d", "#1a1a1a", "#2d2d2d"] (near-black with dust)
Skin/Bone: ["#8b6f5e", "#6b5a4d", "#e8d4c0"] (weathered leather + bone white)
Blood-red accents: ["#8b1a1a", "#a82020", "#c42428"]
Atmosphere: ["#4a3d32", "#6b5a4d", "#8b7a6a"] (desaturated dusty tones)
```


---

## Technical Findings

### What Works
- **SeeDream v4.5**: Excellent animation style comprehension, "cel-shaded" and "ink outlines" interpreted correctly
- **Style DNA template approach**: Subject + Medium/Era + Line-work + Lighting + Composition + Mood + Color consistently produces coherent results
- **Guidance scale 4.0**: Good balance of creativity vs. prompt adherence
- **35 inference steps**: Sufficient quality without over-processing
- **Nano Banana Pro composite layouts**: Explicit panel descriptions (TOP ROW: ... | LEFT SIDE: ...) work for technical refs
- **Negative prompts**: Preventing photorealism and multiple characters works well

### What Doesn't Work
- **Hunyuan Image 3.0**: Defaults to photorealism despite "animated style" prompts - not suitable for animation projects
- **Grok Imagine**: Variable consistency, better for one-off posters than sequential frames
- **Generic "turnaround" prompts**: Inconsistent, need explicit composite layout descriptions instead

### Reference Weight Tuning
- Style reference: 0.85-0.95 for style lock-in (hero shots, identity sheets)
- Style reference: 0.50-0.70 for exploration (initial style tests)
- Character reference: TBD during hero shot phase

### Prompt Patterns That Work
- Deconstructed style DNA (medium + line + lighting + color) instead of IP references
- Explicit composition directions (wide shot, low angle, dutch angle)
- Mood descriptors (ominous arrival, biblical plague energy, cold efficiency)
- Specific color palette language (desaturated dusty, blood-red punctuation)
- Negative space emphasis (massive negative space in sky)

### Prompt Patterns That Fail
- Generic turnaround requests without explicit panel layout
- IP name-dropping without style deconstruction
- Vague style references ("dark", "moody" without specifics)


---

## Next Steps

- [x] Run all style DNA tests
- [x] Evaluate and select winning style DNA
- [x] Refine winning template (production-ready as-is)
- [x] Extract color palette
- [ ] Run hero shots with locked style (NEXT: Nameless - The Entrance, The Draw, The Quiet Moment)
- [ ] Select winning hero shot
- [ ] Document locked prompts in project STYLE_PROMPTS.md
- [ ] Update WORKFLOW.md with learnings
- [ ] Begin identity sheet generation

---

## Locked Artifacts

### Style Master Reference
**File**: `style_dna_1_seedream_20260129_180658.png`
**Model**: SeeDream v4.5
**Template**: Gothic Western DNA (locked)
**Palette**: `["#1a0d0f", "#2d1419", "#4a1e23", "#6b2d32", "#8b4449", "#a85c5c", "#c47a6f", "#d89881", "#8b6f5e", "#5e4a3d"]`

### Nameless Hero Shots (ALL THREE LOCKED)
**Entrance**: `hero_nameless_entrance_seedream_20260129_202132.png`
**Draw**: `hero_nameless_draw_seedream_20260129_202202.png`
**Quiet**: `hero_nameless_quiet_seedream_20260129_202220.png`
**Model**: SeeDream v4.5
**Settings**: 1024×1536, 35 steps, guidance 4.0
