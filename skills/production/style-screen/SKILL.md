---
skill: style-screen
role: production
version: 1.0

description: |
  Rapid style viability screening across generation backends. Tests whether
  a visual style can be rendered by a given model/pipeline by generating a
  standard set of compositions and scoring the results. The same styles are
  tested across T2V and T2I backends to build a cross-backend compatibility map.

inputs:
  required:
    - name: style_definitions
      type: file
      description: YAML defining style names and one-line physical materials summaries
  optional:
    - name: shot_list_t2v
      type: file
      description: T2V shot list (video prompts, durations, seeds)
    - name: shot_list_t2i
      type: file
      description: T2I shot list (image prompts, dimensions, seeds)
    - name: previous_scores
      type: file
      description: Previous scorecard results for comparison

outputs:
  - name: generated_media
    type: directory
    description: Generated clips (clips_t2v/) or images (images/) per style
  - name: scorecard
    type: file
    description: Per-style quality scores across QC dimensions
  - name: tier_classification
    type: file
    description: Styles sorted into Tier 1/2/3/Fail based on average scores

tools:
  - sandbox/ltx2_t2v_lab/run_experiment.py (LTX-2 T2V generation)
  - sandbox/z_image_t2i_lab/run_experiment_t2i.py (z-image T2I generation)

doneness:
  criteria:
    - All styles generated for the target backend (no errors)
    - Each style scored on all QC dimensions
    - Tier classification assigned
    - Cross-backend comparison documented (if both backends tested)
---

# Style Screen — Rapid Style Viability Testing

## Purpose

Determine whether a visual art style can be rendered by a given AI generation backend before committing it to production. A style that scores well on one backend may fail on another — this skill provides a structured way to test, score, and compare.

---

## The Physical Materials Principle

AI image and video generators render the real world. They have been trained on photographs and footage of physical things. When describing a style:

**DO**: Describe physical materials, real-world processes, and tangible objects.
- "Damaged VHS tape playing on a CRT television"
- "UV-reactive paint on skin under blacklight tubes"
- "Torn paper layers with visible paper fibers and rough scissor cuts"

**DON'T**: Describe digital rendering techniques or abstract visual concepts.
- ~~"Apply glitch effect with RGB channel offset"~~
- ~~"Render in solarized style with inverted tones"~~
- ~~"Use a cyanotype color palette"~~

If the style involves something that physically exists (damaged film, infrared film stock, a CRT screen, construction paper collage), describe those physical things. If it involves a rendering process that doesn't exist as a physical object, reframe it as one.

---

## Backend-Specific Language Rules

The same style needs different prompt language for different backends.

### T2V (Video) — Cinematic Language

Video models expect motion, temporal progression, and audio cues.

| Element | Use | Example |
|---------|-----|---------|
| Camera motion | Dolly, track, pan, handheld drift | "Camera dollies slowly forward" |
| Motion verbs | Walk, turn, fall, ripple, flicker | "The figure walks through the center" |
| Temporal connectors | Then, as, while, gradually | "Rain falls as bright streaks" |
| Audio descriptions | Hum, click, patter, whir | "The CRT hums and the audio warbles" |
| Scene headers | EXT./INT. location | "EXT. CITY ALLEY – NIGHT." |

**Avoid in T2V**: "photograph", "print", "frame", "still" — these suppress motion.

### T2I (Image) — Photographic Language

Image models expect static compositions, exposure settings, and print language.

| Element | Use | Example |
|---------|-----|---------|
| Composition framing | Centered, rule of thirds, overhead angle | "Centered perspective looking down the alley" |
| Photographic terms | Photograph, print, exposure, f-stop | "Photograph captured by FLIR thermal camera" |
| Material description | Same as T2V — physical materials first | "Prussian blue and cream-white tones only" |
| Static states | Stands, faces, fills the frame | "A figure stands in the center of the alley" |
| Print/capture medium | Cyanotype print, Polaroid, gelatin silver | "Cyanotype sun print on heavy watercolor paper" |

**Avoid in T2I**: Camera movement, temporal language, audio descriptions.

---

## Prompt Translation Rules

When converting a prompt between backends:

| T2V → T2I | Example |
|-----------|---------|
| "walks through" → "stands in" | Motion verb → static state |
| "Camera dollies forward" → "Centered perspective" | Camera motion → composition framing |
| "Rain falls as streaks" → "Rain visible as streaks" | Temporal → descriptive |
| "The face turns slowly" → "The face, turned slightly" | Action → pose |
| "Electronic hum and rain" → *(remove)* | Audio → nothing |
| "Footage from a FLIR camera" → "Image captured by a FLIR camera" | "Footage" → "Image/Photograph" |
| *(add nothing)* → "Photograph of..." / "Print of..." | Add photographic framing |

| T2I → T2V | Example |
|-----------|---------|
| "stands in" → "walks through" | Static state → motion verb |
| "Centered perspective" → "Camera dollies forward" | Framing → camera motion |
| "Photograph of" → *(remove or replace)* | Remove print language |
| *(add nothing)* → "The figure moves..." | Add motion |
| *(add nothing)* → "ambient hum", "rain patters" | Add audio cues |

### Special Cases: Styles Where Photographic Language Is Native

Some styles are inherently photographic processes. For these, "photograph" and "print" are **correct** T2I language and should be kept:

- **Wet Plate Collodion**: "A wet plate collodion photograph" — this IS what the style is
- **Hand-Tinted Silent Film**: "A hand-tinted photograph" — the tinting IS applied to prints
- **Xerox Art**: "A photocopy of a photograph" — the copier IS the medium
- **Cyanotype**: "A cyanotype sun print" — the print IS the process

For T2V, these same words suppress motion, so they must be reframed (e.g., "liquid silver" instead of "wet plate photograph", "light leak" instead of "hand-tinted frame").

---

## Test Format

### Two Dimensions of Testing

A complete backend screen tests **two independent dimensions**:

1. **Style Screen**: Can the backend render a given visual style? (Fixed shot types, vary styles)
2. **Shot Type Screen**: Can the backend interpret cinematographic vocabulary? (Fixed style, vary shot types)

These are separate test suites run independently. Together they form a complete capability map for a backend.

### Style Screen — Standard Scene
Use a common scene across all styles for fair comparison. The default test scene:
> **Figure in a rain-soaked city alley at night.**

This provides: a human figure (tests character rendering), environment (tests materials), weather (tests particle effects), lighting (tests contrast/color), and mood.

Two compositions per style:
1. **Wide shot**: Full environment + figure. Tests style's ability to render a complete scene.
2. **Close-up**: Face detail. Tests style's ability to render fine detail and texture.

### Shot Type Screen — Standard Style
Use a neutral photorealistic style (no art style layered on) so the shot type is the only variable. Same common scene. Test across 6 categories:

| Category | What It Tests | Example Shots |
|----------|--------------|---------------|
| Framing Scale | Distance control (EWS to ECU to macro) | Extreme wide, cowboy, extreme close-up, extreme macro |
| Subject Count | Multi-subject composition | OTS, two-shot, dirty single, POV |
| Depth of Field | Focus plane control | Split diopter, tilt-shift, rack focus |
| Camera Angles | Angular interpretation | Dutch angle, bird's-eye, ground-level, extreme low |
| Creative Perspectives | Conceptual framing | Voyeur, mirror POV, probe lens, reverse POV |
| Mechanisms | Implied motion/position | Crane, tight profile, ultra-wide environmental, upside-down |

### Deterministic Seeds
All generations use fixed seeds for reproducibility:
- T2V style test: seeds 9001–9024 (v1), 9101–9124 (v2)
- T2I style test: seeds 9501–9540
- T2I shot type test: seeds 9601–9624
- V2 iterations: add +100 to the base seed
- All images 1280×720 (16:9)

---

## Shot List Templates

### T2V Shot List (`shot_list_t2v.yaml`)

```yaml
scene:
  id: style_screen_name
  name: "Style Screen — Description"

t2v_metadata:
  negative_prompt: "text, watermark, deformed, extra limbs"
  notes: >
    Test description and methodology notes.

shots:
  - id: 1
    name: "01 Style Name — Wide"
    shot_type: wide           # wide | closeup
    duration: 5               # seconds (T2V only)
    seed: 9001
    video_prompt: >
      Full cinematic prompt with motion verbs, camera direction,
      temporal connectors, and audio cues. Physical materials first,
      then scene action, then camera, then audio.
```

### T2I Shot List (`shot_list_t2i.yaml`)

```yaml
scene:
  id: style_screen_name
  name: "Style Screen — Description"

t2i_metadata:
  negative_prompt: "text, watermark, deformed, extra limbs, blurry, low quality"
  steps: 25
  cfg: 4
  notes: >
    Test description and methodology notes.

shots:
  - id: 1
    name: "01 Style Name — Wide"
    shot_type: wide           # wide | closeup
    width: 1280               # wide = 1280x720
    height: 720               # closeup = 1024x1024
    seed: 9501
    image_prompt: >
      Static photographic prompt with composition framing, physical
      materials, and print/capture medium. No motion, no audio,
      no temporal language.
```

---

## Style Scorecard

### QC Dimensions (all backends)

| Dimension | 1 (Fail) | 2 (Weak) | 3 (Acceptable) | 4 (Good) | 5 (Excellent) |
|-----------|----------|----------|-----------------|----------|----------------|
| **Style Fidelity** | Wrong style entirely | Hints of style, mostly generic | Recognizable style | Strong style presence | Unmistakable, could not be anything else |
| **Material Rendering** | No physical materials visible | Vague texture | Some materials readable | Materials convincing | Materials feel tangible and real |
| **Composition Clarity** | Chaotic/unreadable | Muddled, subject unclear | Subject identifiable | Clean composition | Intentional, beautiful framing |
| **Color Palette** | Random/default colors | Vaguely in range | Correct palette family | Strong palette match | Exact palette, no strays |
| **Artifact Quality** | Distracting AI artifacts | Some artifacts, somewhat distracting | Minor artifacts | Negligible artifacts | Clean or artifacts serve the style |

### Video-Only Dimension

| Dimension | 1 (Fail) | 2 (Weak) | 3 (Acceptable) | 4 (Good) | 5 (Excellent) |
|-----------|----------|----------|-----------------|----------|----------------|
| **Motion Quality** | Frozen/static | Minimal motion | Some natural motion | Good motion, mostly natural | Fluid, purposeful, style-appropriate |

### Scoring Rules
- **T2I score**: Average of 5 dimensions (style, material, composition, color, artifact)
- **T2V score**: Average of 6 dimensions (add motion quality)
- Score the wide and close-up separately, then average for the style's overall score

---

## Tier Classification

| Tier | Score Range | Meaning | Action |
|------|-------------|---------|--------|
| **Tier 1** | >= 4.0 avg | Production ready | Use directly in projects |
| **Tier 2** | >= 3.0 avg | Promising, needs work | Iterate prompts (v2), rescore |
| **Tier 3** | >= 2.0 avg | Marginal, limited use | May work for specific shots only |
| **Fail** | < 2.0 avg | Not viable on this backend | Try different backend or abandon |

---

## Iteration Workflow

When a style scores Tier 2 or 3:

1. **Diagnose**: Which dimensions are weak? Material rendering? Motion? Color?
2. **Weaken the trigger**: Identify what prompt language is causing the model to miss.
   - "photograph" / "print" / "frame" → suppresses T2V motion
   - Abstract process descriptions → model doesn't understand
   - Too many competing style cues → model averages them into mush
3. **Fix**: Rewrite the weak dimension. Common fixes:
   - Process language → physical object language ("solarized darkroom" → "thin neon edge lights tracing every contour")
   - Static trigger words → cinematic reframes ("film frame" → "a scene where...")
   - Strengthen material specificity ("paper texture" → "cold-press watercolor grain, visible paper fibers")
4. **V2 seed offset**: Use seed + 100 from the original (e.g., 9001 → 9101, 9501 → 9601)
5. **Rescore**: Apply the same scorecard, compare against v1

---

## Cross-Backend Comparison

### LTX-2 T2V vs Z-Image T2I — 20 Styles (2026-02-28)

| # | Style | T2V Avg | T2V Tier | T2I Avg | T2I Tier | Notes |
|---|-------|---------|----------|---------|----------|-------|
| 01 | Punk Zine Collage | 4.2 | T1 | 4.6 | T1 | Both strong. T2I torn paper more defined |
| 02 | Glitch VHS | 4.3 | T1 | 4.8 | T1 | Both strong. CRT framing works on both |
| 03 | Infrared Aerochrome | 4.0 | T1 | 4.6 | T1 | Both strong. v2 removed "film stock" trigger for T2V |
| 04 | Damaged 8mm Film | 4.2 | T1 | 4.8 | T1 | Both strong. Chemical burns render well everywhere |
| 05 | Blacklight UV | 4.3 | T1 | 5.0 | T1 | Both strong. UV glow slightly richer in stills |
| 06 | Cyanotype | 3.2 | T2 | 4.8 | T1 | **T2I wins.** "Print" language natural for T2I, suppresses T2V motion |
| 07 | Thermal FLIR | 4.2 | T1 | 4.6 | T1 | Both strong. False-color works across backends |
| 08 | Solarized | 2.5 | T3 | 4.4 | T1 | **T2I wins.** Tone reversal too subtle in video; neon edge reframe needed |
| 09 | Wet Plate Collodion | 4.0 | T1 | 5.0 | T1 | T2V needed "liquid mercury" reframe; T2I uses native "photograph" |
| 10 | Hand-Tinted Silent | 4.0 | T1 | 4.8 | T1 | T2V needed "light leak" reframe; T2I uses native "photograph" |
| 11 | Xerox Art / Risograph | 4.0 | T1 | 4.0 | T1 | T2V uses risograph reframe; T2I uses native "photocopy" |
| 12 | Rear Projection | 2.8 | T3 | 4.4 | T1 | **T2I wins.** Lighting mismatch reads better as a still |
| 13 | Night Vision | 4.0 | T1 | 4.6 | T1 | Both strong. Green phosphor + halo bloom consistent |
| 14 | Projection Mapping | 3.2 | T2 | 4.6 | T1 | **T2I wins.** Surface warping more visible without motion blur |
| 15 | Hologram / Pepper's Ghost | 3.0 | T2 | 4.6 | T1 | **T2I wins.** Translucent glow clearer in stills |
| 16 | Surveillance Mosaic | 3.2 | T2 | 5.0 | T1 | **T2I wins.** CRT grid layout reads perfectly as image |
| 17 | Gothic Western | Fail | Fail | 5.0 | T1 | **T2I only.** LTX-2 photorealistic bias kills linework |
| 18 | Stop Motion (Laika) | Fail | Fail | 4.8 | T1 | **T2I only.** LTX-2 cannot render puppet aesthetic |
| 19 | Anime Cel (Ghibli) | Fail | Fail | 5.0 | T1 | **T2I only.** LTX-2 cannot render cel-shading |
| 20 | Painterly Illustration | Fail | Fail | 5.0 | T1 | **T2I only.** LTX-2 cannot render brushstrokes |

### Summary

| Metric | LTX-2 T2V | Z-Image T2I |
|--------|-----------|-------------|
| Styles tested | 20 | 20 |
| Tier 1 | 10 (50%) | 20 (100%) |
| Tier 2 | 4 (20%) | 0 |
| Tier 3 | 2 (10%) | 0 |
| Fail | 4 (20%) | 0 |
| Average (styles 01-16) | 3.69 | 4.68 |
| Average (all 20) | — | 4.72 |

### Conclusions

1. **T2I is broadly more capable for style rendering.** All 20 styles score Tier 1 on z-image; only 10 of 20 reach Tier 1 on LTX-2.
2. **Physical materials principle validated across both backends.** The same material-first descriptions work for both, though T2I tolerates photographic process language that suppresses T2V motion.
3. **Non-photorealistic styles are T2I-only (for now).** Gothic Western, Stop Motion, Anime Cel, and Painterly Illustration require a T2I backend. LTX-2's photorealistic training bias prevents rendering hand-drawn or sculptural aesthetics.
4. **"Photograph" trigger word is backend-specific.** Suppresses T2V motion but is native/beneficial for T2I. Styles 09-11 use different prompt versions per backend.
5. **T2V-weak styles that work in T2I**: Solarized, Rear Projection, Projection Mapping, Hologram, Surveillance Mosaic. These are all styles where the effect is more visible in a still frame than in motion.

---

## Style Registry

All 20 tested styles across experimental, illustration, animation, and stop-motion categories:

### Experimental / Physical Media (01–16)

| # | Style | Physical Materials | v2 Fix (if any) |
|---|-------|--------------------|------------------|
| 01 | Punk Zine Collage | Torn paper layers, marker pen, construction paper, 16mm film | — (baseline, proven) |
| 02 | Glitch VHS | Damaged VHS tape, CRT television, analog signal corruption | v2: CRT screen as physical object in frame |
| 03 | Infrared Aerochrome | Kodak Aerochrome IR film stock, infrared wavelength color shift | v2: Removed "film stock" trigger, added motion |
| 04 | Damaged 8mm Film | Deteriorated 8mm film print, projector gate, chemical burns | — |
| 05 | Blacklight UV | UV-reactive paint, fluorescent materials, blacklight tubes | — |
| 06 | Cyanotype | Prussian blue photographic process, watercolor paper | v2: Blue monochrome lighting condition instead of print |
| 07 | Thermal FLIR | FLIR camera, infrared heat detection, false-color display | — |
| 08 | Solarized | Sabattier darkroom effect, tone reversal, Mackie lines | v2: Neon edge light tracing contours instead of darkroom process |
| 09 | Wet Plate Collodion | 1860s glass plate, silver on black glass, hand-poured collodion | v2 (T2V): Liquid mercury / molten silver surfaces |
| 10 | Hand-Tinted Silent Film | B&W silver nitrate film, hand-painted color washes, iris mask | v2 (T2V): Light leaks from damaged camera body |
| 11 | Xerox Art | Photocopier artifacts, toner, paper bond, repeated degradation | v2 (T2V): Risograph misregistration, fluorescent ink plates |
| 12 | Rear Projection | Old Hollywood rear-projection screen, studio lighting mismatch | v2: More action, stronger composite seam |
| 13 | Night Vision | Gen 3 image intensifier tube, green phosphor monochrome, halo bloom | Extrapolated from solarized B&W + thermal false color |
| 14 | Projection Mapping | Video projector on brick building, surface warping, ambient bleed | Extrapolated from rear projection's dual-plane success |
| 15 | Hologram / Pepper's Ghost | Translucent projection in physical space, scan lines, blue glow | Extrapolated from blacklight UV glow + rear projection planes |
| 16 | Surveillance Mosaic | CRT monitor grid, multiple camera angles, security room | Extrapolated from thermal false-color + VHS CRT framing |

### Illustration, Animation & Stop-Motion (17–20)

These styles test capabilities that T2V (LTX-2) struggled with due to photorealistic bias. T2I backends may render them more faithfully.

| # | Style | Visual Language | T2V Limitation |
|---|-------|----------------|----------------|
| 17 | Gothic Western | Heavy ink outlines, cross-hatching, high-contrast graphic novel, Castlevania × Leone | LTX-2 rendered photorealistically, lost linework |
| 18 | Stop Motion (Laika) | Sculpted polymer clay, felt, wire armature, miniature practical sets, macro lens | LTX-2 photorealistic bias couldn't render puppet aesthetic |
| 19 | Anime Cel (Ghibli) | Clean ink outlines, flat color fills, watercolor backgrounds, saturated limited palette | LTX-2 "cannot render cel-shading or hand-drawn look" |
| 20 | Painterly Illustration | Oil paint brushstrokes, impasto highlights, canvas texture, Rembrandt lighting | LTX-2 "cannot render brushstrokes or oil paint" |
