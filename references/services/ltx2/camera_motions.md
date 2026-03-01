# LTX-2 Camera Motion Reference

Extracted from official guide + RunDiffusion example prompts + sandbox testing (2026-02-27).
Sandbox tests used a consistent stone courtyard scene with 16 motion variations.

## Camera Motions (Confirmed Working)

### Horizontal Movement

| Motion | Prompt Language | Example | Notes |
|--------|----------------|---------|-------|
| **Pan right** | "camera pans right" | Sandbox test | Simple direction works. Do NOT use "from left to right" — ambiguous, produced wrong direction |
| **Pan left** | "camera pans left" | Sandbox test | Simple direction works |
| **Pan L→R (RunDiffusion)** | "camera pans slowly from left to right" | #1 Living room | WARNING: "from X to Y" phrasing may confuse LTX-2 — both directions produced pan left in testing |
| **Lateral track** | "lateral tracking shot", "drifting parallel to the façade" | #4 Alpine, #20 Neon alley | |
| **Track sideways** | "tracks sideways from window toward seating area" | #17 Penthouse | |
| **Tracking following** | "lateral tracking shot following a model" | #20 Neon alley | |

### Depth Movement (Toward/Away)

| Motion | Prompt Language | Example |
|--------|----------------|---------|
| **Dolly-in** | "dolly-in through", "gentle dolly-forward" | #2 Mid-century, #11 Boathouse |
| **Dolly-through** | "stable dolly-through", "tracking shot down a corridor" | #7 Desert, #9 Passive house |
| **Push-in** | "camera slowly pushes in" | #17 Penthouse |
| **Dolly-out** | "slow dolly-out from terrace to ocean horizon" | #16 Mediterranean |
| **Dolly-around** | "dolly-around inside a gilded ballroom" | #14 Ballroom |

### Vertical Movement

| Motion | Prompt Language | Example |
|--------|----------------|---------|
| **Crane-down** | "slow crane-down", "gentle vertical drift" | #10 Cloister |
| **Dolly-down** | "slow dolly-down from ribbed plaster vaults" | #5 Neo-Gothic |
| **Crane-up** | "slow crane-up inside a conservatory" | #15 Victorian |
| **Sweeping crane up** | "sweeping crane from pavers upward to arcades" | #13 Renaissance |
| **Lift + crane back** | "slowly lifts and cranes back to reveal" | #19 Hospitality lounge |
| **Downward dolly-in** | "downward dolly-in toward a product" | #6 Cyclorama |

### Rotation / Orbit

| Motion | Prompt Language | Example |
|--------|----------------|---------|
| **Macro orbit** | "extremely close macro orbit around" | #3 Product shot |
| **Orbit / circle** | "camera circles slowly around [subject], orbiting clockwise" | Sandbox test — WORKS, genuine perspective rotation |
| **Tilt up** | "tilts up to reveal" | #1 Living room (after pan) |
| **Tilt down** | "camera tilts slowly downward, revealing..." | Sandbox test — WORKS, smooth vertical rotation |

### Compound / Multi-Move

| Motion | Prompt Language | Example |
|--------|----------------|---------|
| **Pan + tilt** | "pans slowly left to right, then tilts up to reveal" | #1 Living room |
| **Push-in + track** | "pushes in and tracks sideways" | #17 Penthouse |
| **Crane + reveal** | "from rug-level close-up then slowly lifts and cranes back to reveal" | #19 Hospitality lounge |
| **Dolly-in through threshold** | "dolly-in through a sliding glass façade, passing zones" | #2 Mid-century |

### Special / Stylistic

| Motion | Prompt Language | Example | Notes |
|--------|----------------|---------|-------|
| **Whip pan** | "whip pans rapidly to the right, motion-blurring across the scene, and settles on [target]" | Sandbox test — WORKS | Clear motion blur + fast pan + settle |
| **Dutch angle** | "low angle dutch tilt shot... horizon tilted approximately 15 degrees" | Sandbox test — WORKS | Consistent canted frame held steady |
| **Aerial descend** | "bird's eye view looking straight down... camera slowly descends from high above" | Sandbox test — WORKS | True overhead angle maintained during descent |
| **Push-in + rack focus** | "camera slowly pushes in as focus racks from [foreground] to [background]" | Sandbox test — WORKS | Both motion AND focus shift present |
| **Zoom in (optical)** | "slowly zooms in optically... the perspective does not change, only the framing tightens" | Sandbox test — PARTIAL | Frame tightens but hard to distinguish from dolly |

### Static / Minimal

| Motion | Prompt Language | Example |
|--------|----------------|---------|
| **Static tripod** | "static tripod shot with controlled rotational movement from the model" | #8 Fashion |
| **Static frame** | "static frame" | Official guide |
| **Static locked-off** | "static locked-off wide shot... camera does not move at all" | Sandbox test — WORKS |

## Motion Qualifiers (How to Describe Speed/Feel)

From the examples, these qualifier patterns appear consistently:

| Qualifier | Prompt Language |
|-----------|----------------|
| **Speed** | "slowly", "gentle", "slow", "stable" |
| **Stabilization** | "smooth gimbal", "smooth motion blur", "low-vibration" |
| **Parallax** | "soft parallax against backdrop", "clean parallax", "parallax deepens through arches" |
| **Exposure** | "without exposure jumps", "stable exposure transitions", "no pumping or flicker" |
| **End state** | "ending on a medium shot of...", "to reveal...", "toward the staircase" |

## Anti-Patterns (What NOT to Say)

| Bad | Why | Use Instead |
|-----|-----|-------------|
| "camera holds steady on a tripod" | Renders tripod as scene object | "static tripod shot" or "locked-off frame" |
| "pushes forward on a dolly track" | May render dolly track | "slow dolly-in" or "pushes in" |
| "crane shot from a jib arm" | May render equipment | "slow crane-up" |
| "handheld shakycam" | Vague, may produce artifacts | "handheld movement" (official guide term) |
| "handheld camera movement walking" | Renders literal hand in frame | "handheld movement" or just describe the motion |
| "rapid cuts" | T2V generates continuous clips | Only useful if model supports multi-cut |
| "pans from left to right" | Ambiguous — LTX-2 may ignore or reverse direction | "camera pans right" (simple direction) |
| "pans from right to left" | Same ambiguity | "camera pans left" (simple direction) |

## Lens Specifications in Examples

The examples consistently specify focal length. Most common:

| Lens | Count | Typical Use |
|------|-------|-------------|
| 35mm | 11 | General interior/exterior, architecture, fashion |
| 28mm | 2 | Wide interiors, establishing shots |
| 40mm | 2 | Environmental portraits, mid-range detail |
| 50mm | 2 | Shallow DOF, product, architectural detail |
| 85mm macro | 1 | Extreme close-up product |

## Common Technical Directives

Phrases that appear repeatedly across multiple examples:

- "smooth motion blur"
- "no abrupt jumps"
- "no watermark"
- "no flicker"
- "no exposure pulsing"
- "controlled specular highlights"
- "natural falloff on shadows"
- "subtle lens bloom / flare"
- "clean parallax"

## Sandbox Test Results (2026-02-27)

16-shot camera motion grid test using identical stone courtyard scene. All clips 5s, 1280x720, 25fps.

### Documented Motions (All Confirmed Working)

| # | Motion | Seed | Verdict |
|---|--------|------|---------|
| 1 | Pan Right | 9101 | WORKS — simple "camera pans right" |
| 2 | Pan Left | 9102 | WORKS — simple "camera pans left" |
| 3 | Dolly-In | 9003 | WORKS — smooth forward movement |
| 4 | Dolly-Out | 9004 | WORKS — smooth pull-back to wide |
| 5 | Crane-Up | 9005 | WORKS — ground to overhead |
| 6 | Crane-Down | 9006 | WORKS — overhead to eye level |
| 7 | Lateral Track | 9007 | WORKS — parallax through arches |
| 8 | Static Frame | 9008 | WORKS — locked frame, environmental motion only |

### Undocumented Motions (New Discoveries)

| # | Motion | Seed | Verdict | Notes |
|---|--------|------|---------|-------|
| 9 | Tilt Down | 9009 | **WORKS** | True tilt (rotation), distinct from crane |
| 10 | Handheld Walk | 9010 | **PARTIAL** | Forward motion OK but no handheld shake; rendered literal hand |
| 11 | Orbit | 9011 | **WORKS** | Genuine 360° perspective shift around subject |
| 12 | Zoom In (Optical) | 9012 | **PARTIAL** | Frame tightens but hard to distinguish from slow dolly |
| 13 | Whip Pan | 9013 | **WORKS** | Correct hold → blur → settle timing |
| 14 | Dutch Angle | 9014 | **WORKS** | Consistent ~15° canted horizon |
| 15 | Aerial Descend | 9015 | **WORKS** | Bird's eye maintained during descent |
| 16 | Push-In + Rack Focus | 9016 | **WORKS** | Both motion and focus shift present |

**Score: 14/16 fully working, 2/16 partial.** LTX-2 has broader camera motion vocabulary than officially documented.
