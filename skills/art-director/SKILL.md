---
skill: art-director
role: post-production
version: 1.0

description: |
  Art director cognitive skill. Teaches Claude to evaluate and maintain
  visual coherence across shots — color consistency, style DNA enforcement,
  continuity tracking, and quality arbitration.

inputs:
  required:
    - name: project_config
      type: file
      path: PROJECT_CONFIG.yaml
      description: Style DNA, locked visual language
  optional:
    - name: scene_clips
      type: directory
      description: Generated clips for review
    - name: identity_sheets
      type: directory
      path: REFERENCES/identity_sheets/
      description: Character identity references
    - name: location_refs
      type: directory
      path: REFERENCES/location_refs/
      description: Location reference images
    - name: color_palette_data
      type: file
      description: Pre-analyzed color palette JSON

outputs:
  - name: visual_review
    type: file
    description: Per-clip visual quality assessment with pass/fail
  - name: continuity_notes
    type: file
    description: Cross-clip continuity issues and corrections

tools:
  - scripts/analysis/analyze_clip.py
  - scripts/analysis/compare_clips.py
  - scripts/lib/video_analysis.py (analyze_color_palette, extract_filmstrip)
  - scripts/lib/ffmpeg.py (apply_color_grade)
---

# Art Director

## Purpose

Maintain visual coherence across an entire scene and episode. Individual shots may look great in isolation but clash when assembled. The art director catches inconsistencies before they reach the audience.

---

## Visual Coherence Checklist

### Principle: Visual Consistency > Visual Ambition

A simple, well-held shot with stable content beats an ambitious shot that morphs or breaks. When in doubt:
- Prefer locked camera over dynamic movement
- Prefer single subjects over crowded compositions
- Prefer mid-range framing over extreme wide or extreme close-up
- A beautiful 8s hold is worth more than a shaky 3s push-in

For every scene assembly, review these five dimensions:

### 1. Color Temperature Consistency

Adjacent clips should share the same color temperature unless a deliberate shift is scripted.

**Analysis tool**:
```bash
python3 scripts/analysis/analyze_clip.py ASSEMBLY --output analysis/
# Review color_palette.png — are all samples in the same temperature family?
```

**Common failures**:
- Outdoor scene where some clips are warm (golden hour) and others are neutral (overcast)
- Interior scene where some clips have blue cast (AI default) vs. warm (candlelight intent)
- Night scenes where some clips are pure blue vs. others are blue-green

**Fix**: Apply consistent color grade across the scene:
```python
from scripts.lib.ffmpeg import apply_color_grade
# Presets: warm_golden, cool_blue, high_contrast, bleach_bypass
apply_color_grade(clip, output, preset="warm_golden")
```

### 2. Exposure Consistency

Brightness levels should be consistent across clips in the same lighting setup.

**Common failures**:
- Character close-ups brighter than establishing shots (AI compensating for fill)
- Alternating between properly exposed and underexposed clips
- Sky/window areas blown out in some clips but not others

**Fix**: Re-generate with more specific lighting direction in the prompt, or apply color grade as a unifying pass.

### 3. Character Likeness

Characters should look like themselves across all shots.

**Key checks**:
- Skin tone: consistent across lighting setups
- Hair: color, style, volume consistent
- Wardrobe: colors, details, wear patterns consistent
- Age appearance: no shots where character looks significantly older/younger

**When to override quality for likeness**:
If a clip is beautifully composed but the character doesn't look like themselves, it must be flagged. Visual coherence > individual shot quality.

### 4. Environmental Continuity

The physical environment should be consistent across the scene.

**Key checks**:
- Background elements: same buildings, same trees, same furniture across shots
- Weather: if it's raining in the wide shot, close-ups should have wet surfaces
- Time of day: lighting angle and quality should be consistent
- Props: objects that appear in one shot should still be there in adjacent shots

### 5. Style DNA Fidelity

Every frame should feel like it belongs to the same show/film.

**Style DNA components** (from PROJECT_CONFIG.yaml):
1. **Medium/Era**: Does this look like the intended style?
2. **Line-work/Texture**: Consistent edge rendering across shots?
3. **Lighting/Rendering**: Same shadow quality, contrast level?
4. **Color Palette**: Within the defined palette boundaries?

---

## Review Protocol

### Per-Clip Visual Assessment

For each clip, score these dimensions (1-5):

| Dimension | 1 (Fail) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|-----------------|----------------|
| Color match | Wrong temperature | Slightly off | Perfect match |
| Likeness | Unrecognizable | Mostly right | Dead-on |
| Environment | Wrong location | Generic but ok | Specific and correct |
| Style DNA | Different show | Same universe | Same episode |
| Composition | Random framing | Functional | Intentional and beautiful |

**Pass threshold**: Average >= 3.0 AND no dimension at 1.
**Flag for redo**: Any dimension at 1, or average < 2.5.

### Cross-Clip Continuity Matrix

For each pair of adjacent clips, note:

```
Clip 1 → Clip 2:
  Color temperature:  [match / slight shift / mismatch]
  Exposure:           [match / slight shift / mismatch]
  Character likeness: [consistent / minor drift / different person]
  Environment:        [continuous / acceptable jump / discontinuous]
  Spatial logic:      [makes sense / ambiguous / impossible]
```

**Red flags**:
- Any "mismatch" or "different person" or "discontinuous" or "impossible"
- These must be resolved before assembly

---

## Override Rules

When visual coherence conflicts with individual shot quality:

### Coherence Wins When:
- Shot is technically excellent but color temperature clashes with neighbors
- Beautiful composition but character looks different from identity sheet
- Great motion/action but environment doesn't match the scene

**Action**: Flag for redo with specific correction notes.

### Quality Wins When:
- Minor color shift that can be corrected with color grade post-processing
- Slightly different wardrobe detail that audience won't notice at speed
- Background element differs but is out of focus / not prominent

**Action**: Accept with note, apply color grade if needed.

### Compromise:
- The clip is irreplaceable (unique action, perfect emotion, hard to regenerate)
- AND the coherence break is noticeable but not jarring

**Action**: Accept, document the compromise, consider sandwich technique (put a strong coherence-matched clip before and after to minimize the break).

---

## Color Correction Strategy

### When to Grade vs. When to Regenerate

| Issue | Grade | Regenerate |
|-------|-------|-----------|
| Slight warm/cool shift | Grade | - |
| Exposure off by <1 stop | Grade | - |
| Wrong time of day (day vs. night) | - | Regenerate |
| Wrong color palette entirely | - | Regenerate |
| Desaturated when should be vivid | Grade (boost sat) | - |
| AI-default blue cast | Grade (warm_golden) | - |

### Color Grade Presets

| Preset | Use For |
|--------|---------|
| `warm_golden` | Caribbean daylight, golden hour, warmth |
| `cool_blue` | Night scenes, underwater, cold tension |
| `high_contrast` | Dramatic moments, action sequences |
| `bleach_bypass` | Flashbacks, memories, desaturated drama |

---

## Scene Color Arc

**Design color arcs BEFORE shot lists.** Color is a free storytelling layer independent of generation quality. Warm→neutral→cool can encode safety→uncertainty→loss without any change to the visual generation pipeline. Apply as post-production grade.

A scene's color should evolve with its emotional arc:

```
Opening (warm neutral) → Tension (cooler, desaturated) → Climax (high contrast) → Resolution (warm return)
```

This arc should be INTENTIONAL and SUBTLE:
- No more than 200K color temperature shift within a scene
- Contrast changes should be gradual across 3-4 clips, not sudden
- Saturation changes should be nearly invisible per-cut but visible across the scene

Use `analyze_color_palette()` to verify the arc is smooth, not choppy.

### Deliberate Color Arcs for Deterioration

When a scene requires visible decline (character injury, environmental decay, system failure), use the color grade arc as the primary visual tool:
- Shift warm → desaturated across the EDL via `colorbalance`/`curves` ffmpeg filters applied per-clip in assembly
- This communicates physical/emotional deterioration without regenerating any clips — the source footage stays unchanged
- Combine with audio layering (worsening mechanical sounds, voice degradation) from the sound-designer skill for full sensory sell
