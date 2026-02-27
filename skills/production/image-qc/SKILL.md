---
skill: image-qc
role: production
version: 1.0

description: |
  Image quality control skill. Teaches Claude to systematically evaluate
  generated images — identity sheets, scene frames, storyboards — for
  anatomical correctness, prompt adherence, style consistency, and
  composition integrity. Enforces honesty-first reporting with structured
  pass/fail verdicts per panel or area.

inputs:
  required:
    - name: generated_images
      type: file
      description: The generated image(s) to review (identity sheets, scene frames, storyboards)
    - name: prompt_used
      type: string
      description: The exact prompt that produced the image, for adherence checking
  optional:
    - name: project_config
      type: file
      path: PROJECT_CONFIG.yaml
      description: Style DNA and visual language definitions for style match verification
    - name: identity_sheets
      type: directory
      path: REFERENCES/identity_sheets/
      description: Character identity references for cross-image likeness comparison
    - name: location_refs
      type: directory
      path: REFERENCES/location_refs/
      description: Location reference images for environment consistency checks

outputs:
  - name: qc_report
    type: file
    description: Structured pass/fail table per panel or image area with specific defect descriptions
  - name: defect_list
    type: list
    description: Itemized list of all detected issues with panel/area references
  - name: escalation_recommendation
    type: string
    description: Recommended action — pass, re-generate with corrections, or escalate to higher-quality model

tools:
  - Read (for viewing generated images)
  - scripts/production/compose_frames.py
  - scripts/production/generate_refs_v2.py
---

# Image QC

## Purpose

Catch defects in AI-generated images before they enter the production pipeline. Every generated image — identity sheets, scene frames, storyboards — must pass structured quality control. False positives waste seeds, time, and money. The image QC skill enforces rigorous, honest evaluation so the user can make informed pass/fail decisions.

---

## The Honesty Rule

**NEVER summarize positively if defects exist.** This is the foundational principle of image QC.

- Say "Panel X has [defect]" not "Great identity sheet!"
- The user trusts this assessment to decide pass/fail — false positives waste seeds and time
- When in doubt, flag it. The user can override if they think it's acceptable
- Every review MUST include a structured table with per-panel or per-area verdicts

---

## Identity Sheet / Multi-Panel QC

Identity sheets and multi-panel composites are the most complex images to evaluate. Check every dimension below for each panel.

### 1. Panel Containment

Do all sub-images fit cleanly within their panel borders?

**Check for**:
- Content overflowing into adjacent panels
- Cropping that cuts off important features (tops of heads, hands)
- Bleeding or smearing across panel dividers
- Panels that are empty or contain only partial content

**Fail condition**: Any panel has content crossing its borders or is visibly cropped.

### 2. Face Integrity

Are all faces structurally sound?

**Check for**:
- Distorted or asymmetric eyes beyond natural variation
- Misaligned facial features (nose off-center, mouth shifted)
- Extra or missing features (three eyes, no nose, double mouth)
- Melted or blurred regions around the face
- Uncanny valley appearance — technically correct but deeply wrong

**Fail condition**: Any face with structural distortion or missing/extra features.

### 3. Eye Quality

Eyes are the #1 tell for AI generation artifacts. Dedicate specific attention here.

**Check for**:
- Mismatched pupil sizes or shapes between eyes
- Melted or blurred iris detail
- Extra eyes (anywhere on the face or body)
- Wrong gaze direction relative to the described pose
- Uncanny valley stare — both eyes locked forward with no natural variation
- Different eye colors when they should match
- Pupil/iris shape inconsistency (one round, one elongated)

**Fail condition**: Any eye anomaly that would be visible at normal viewing distance.

### 4. Hand and Limb Check

Hands remain a persistent weakness in image generation models.

**Check for**:
- Finger count: each hand should have exactly 5 fingers
- Fused digits (two fingers merged into one)
- Extra digits (6+ fingers, or thumb on wrong side)
- Unnatural joint angles (fingers bending backward, wrists at impossible angles)
- Limb count: correct number of arms and legs
- Proportional consistency (one arm significantly longer than the other)

**Fail condition**: Wrong digit count, fused fingers, or impossible joint angles.

### 5. Panel Completeness

Does each panel contain what was requested in the prompt?

**Check for**:
- Missing panels entirely (empty or black spaces where content should be)
- Panels that show a different subject than requested
- Panels that show the right subject but wrong pose/angle/expression
- Panels merged together (two requested views collapsed into one)

**Fail condition**: Any panel missing or showing incorrect content.

### 6. Style Consistency Across Panels

The same character should look like the same character across all panels.

**Check for**:
- Skin tone variation across panels
- Hair color, length, or style changing between panels
- Wardrobe details inconsistent (different colors, missing accessories)
- Age appearance shifting between panels
- Body type or proportions changing

**Fail condition**: Character not recognizable as the same person across panels.

### 7. Grid Clarity

The layout itself must be readable and organized.

**Check for**:
- Dividing lines that are inconsistent, wavy, or missing
- Uneven panel sizes when uniform was expected
- Layout that's difficult to parse — unclear where one panel ends and another begins
- Background color bleeding into or obscuring dividers

**Fail condition**: Layout is unreadable or panels cannot be distinguished.

---

## Single Image / Scene Frame QC

For individual frames, storyboards, and production shots.

### 1. Anatomical Correctness

**Check for**:
- Body proportions (head size relative to body, arm length, torso length)
- Limb count and positioning
- Face structure (eyes, nose, mouth in correct positions and proportions)
- Joint angles that defy human anatomy

### 2. Prompt Adherence

The most common failure mode. Check EVERY specific detail in the prompt against the output.

**Check for**:
- **Species/subject consistency**: If the prompt says "monkey", is it actually a monkey? Watch for species drift — monkey-to-human is a common failure mode. Check ALL panels, not just the most prominent one
- **Color specificity**: If the prompt specifies "RED cap, BLUE cap, BROWN cap" — verify those exact colors are present. Not "some colored caps" or "vaguely tinted caps"
- **Spatial placement**: If the prompt says "sitting in tree branches" — are subjects actually positioned in the tree? Not standing on the ground near a tree
- **Object count**: If the prompt says "three monkeys" — count them. Not two, not four
- **Action accuracy**: If the prompt describes a specific action, is that action depicted?
- **Setting details**: Verify background and environment match prompt description

**Fail condition**: Any specific prompt detail that is missing, wrong, or ambiguous.

### 3. Artifact Check

**Check for**:
- Watermarks or text artifacts embedded in the image
- Blending seams (visible boundaries where image regions were stitched)
- Resolution drops in specific areas (sharp foreground, blurry background when both should be sharp)
- Banding in gradients (especially skies)
- Repeated texture patterns (copy-paste artifacts)

### 4. Style Match

Does the image match the project's established visual style?

**Check against PROJECT_CONFIG.yaml style DNA**:
- Medium/Era: correct animation style or photographic approach
- Line-work/Texture: consistent edge rendering and surface detail
- Lighting/Rendering: correct shadow quality and contrast level
- Color Palette: within the defined palette boundaries

### 5. Aspect Ratio

**Check for**:
- Output matches the expected aspect ratio
- Flag if square (1:1) when 16:9 was expected, or vice versa
- Flag if the image has been stretched or squeezed to fit a different ratio

---

## Composition Prompt QC (Pre-Generation)

Review prompts BEFORE they are sent to the model. Catching prompt issues is cheaper than catching image issues.

### 1. Describe What the Camera Sees

The prompt should describe visible, physical reality — not narrative context.

- **Good**: "mouth wide open, eyebrows raised high, eyes widened"
- **Bad**: "shocked expression" (the model interprets "shocked" differently than you expect)
- **Good**: "thick dark curly hair falling past shoulders, sun-darkened olive skin"
- **Bad**: "she looks like a Caribbean sailor's daughter" (narrative reference the model has no context for)

### 2. No Narrative References the Model Cannot Know

The model only sees the prompt text and any image inputs. It has no story context.

- **Good**: "the puppet character from image 1"
- **Bad**: "the peddler" or "following the peddler's example"
- **Good**: "a tall man in a red coat holding a wooden staff"
- **Bad**: "the villain" or "Mars's father"

### 3. Physical Expression Vocabulary

Describe facial features physically, not emotionally.

| Instead of... | Write... |
|---------------|----------|
| sad | brow furrowed, mouth corners pulled down, eyes glistening |
| angry | jaw clenched, nostrils flared, brow compressed, eyes narrowed |
| surprised | eyebrows raised high, mouth open in O shape, eyes wide |
| scared | eyes wide, pupils dilated, mouth slightly open, shoulders raised |
| happy | cheeks raised, crow's feet at eyes, mouth open showing teeth |
| determined | jaw set, lips pressed together, brow slightly lowered, direct gaze |

### 4. Every Specific Visual Detail Must Be Named

Do not rely on the model to infer details from general descriptions.

- **Good**: "wearing a RED wool cap, a BLUE cotton cap stacked on top, and a BROWN leather cap on the very top"
- **Bad**: "wearing different colored caps"
- **Good**: "sitting on a thick oak branch, legs dangling, back against the trunk"
- **Bad**: "in the tree area"

### 5. Do Not Economize on Details

More specific detail equals better adherence. A prompt that's too sparse leaves the model guessing, and models guess wrong frequently.

- Specify materials: "worn leather boots" not "boots"
- Specify lighting: "warm afternoon sunlight from the left" not "daytime"
- Specify camera: "medium close-up, eye level" not just the subject

### 6. Body Pose Precision

**Good**: "right hand raised to shoulder height, index finger extended, pointing upward, other fingers curled into palm"
**Bad**: "shaking finger" (ambiguous — which hand? which direction? what gesture exactly?)

### 7. Spatial Anchoring

Always state WHERE subjects are in the frame.

- "positioned in the left third of the frame"
- "filling the center of the frame from waist up"
- "small figure in the bottom right corner, vast sky above"
- NOT just the subject floating in unspecified space

---

## Escalation Rules

When the primary model fails, escalate rather than re-rolling the same model endlessly.

| Failure Type | First Action | Escalation |
|--------------|-------------|------------|
| Species drift (monkey becomes human) | Re-prompt with exhaustive physical description | Escalate to Flux Dev (`--dev` flag) |
| Style inconsistency across panels | Check prompt for style anchors, re-generate | Escalate to Flux Dev with multi-image reference |
| Prompt adherence failure (missing details) | Add missing details explicitly to prompt, re-generate | Escalate to Flux Dev |
| Strong model bias it cannot overcome (e.g., beret bias on monkeys) | Fix downstream in qwen-image-edit or Flux Dev using multi-image reference | Accept the bias and work around it in composition |
| Wrong aspect ratio | Apply post-processing padding (`pad_to_16x9`) | Re-generate with correct aspect ratio parameter |
| Persistent face/hand artifacts | Re-generate with different seed | Escalate to higher-quality model or use inpainting |

**General rule**: Two consecutive failures on the same defect with the same model = escalate. Do not burn more than 2 seeds on the same issue.

---

## QC Report Format

Every generated image review MUST produce a structured report. No exceptions.

### Identity Sheet / Multi-Panel Format

```
### [Image Name] QC Review (workflow, seed N)

| Panel/Area | Expected Content | Status | Issues |
|------------|-----------------|--------|--------|
| Top-left   | Eye close-up    | PASS   | --     |
| Top-center | Profile view    | PASS   | --     |
| Top-right  | Hand reference  | FAIL   | 6 fingers on left hand |
| Center     | Full body front | PASS   | --     |
| Bottom-left| Vulnerable port.| FAIL   | Eyes mismatched, left iris melted |
| Bottom-mid | Action pose     | PASS   | --     |
| Bottom-right| Quiet moment   | PASS   | --     |

**Defects**:
1. Top-right panel: left hand has 6 fingers (extra pinky)
2. Bottom-left panel: left iris is melted/blurred, pupil shape inconsistent with right eye

**Verdict**: FAIL (2 defects in 7 panels)

**Recommendation**: Re-generate with different seed. If hand issues persist, escalate to Flux Dev.
```

### Single Image / Scene Frame Format

```
### [Image Name] QC Review (workflow, seed N)

| Check | Status | Notes |
|-------|--------|-------|
| Anatomical correctness | PASS | -- |
| Prompt adherence | FAIL | Prompt says "red cap" — cap is orange |
| Artifact check | PASS | -- |
| Style match | PASS | Matches Caribbean fantasy DNA |
| Aspect ratio | PASS | 16:9 as expected |

**Defects**:
1. Cap color is orange, not red as specified in prompt

**Verdict**: FAIL (1 prompt adherence issue)

**Recommendation**: Add "bright saturated red, not orange" to prompt and re-generate.
```

### Prompt QC Format (Pre-Generation)

```
### Prompt QC: [shot/panel name]

| Check | Status | Issue |
|-------|--------|-------|
| Physical descriptions only | FAIL | "angry expression" — replace with physical features |
| No narrative references | PASS | -- |
| Color specificity | FAIL | "colored caps" — specify exact colors |
| Spatial anchoring | PASS | -- |
| Detail sufficiency | FAIL | No material, lighting, or camera specs |

**Required fixes before generation**:
1. Replace "angry expression" with "jaw clenched, nostrils flared, brow compressed"
2. Replace "colored caps" with "RED wool cap, BLUE cotton cap, BROWN leather cap"
3. Add lighting direction and camera angle
```

---

## Common Failure Patterns by Model

Knowledge of model-specific weaknesses helps focus the QC eye.

### Nano Banana Pro
- Strongest at technical refs and identity sheets
- Watch for: multi-panel triptych generation when single frame expected (action prompts)
- Watch for: content filter triggers on age references or violence

### Klein (Flux 2)
- Fast drafts, bolder contrast
- Watch for: simplified details in complex scenes (cfg too low)
- Watch for: model biases on unusual subjects (berets on monkeys, humanization of animals)
- Watch for: output inheriting input resolution in i2i mode

### Dev (Flux 2)
- Higher quality but slower
- Watch for: over-smoothing at high step counts (diminishing returns past step 20)
- Watch for: AI-default blue cast in interior scenes

### Z-Image Base
- Watch for: model bias on headwear (berets on monkeys, wrong hat types) — fix downstream with qwen-image-edit or Flux Dev multiref rather than re-rolling endlessly
- Watch for: no cross-frame consistency (every generation is independent)

### qwen-image-edit
- Watch for: species drift (animal subjects becoming human) — especially in expression/portrait panels
- Watch for: style inconsistency when reference images have mixed styles
- Watch for: square output when wide was expected — post-process with `pad_to_16x9()`
- Watch for: field name confusion (`image`/`image2`/`image3` for qwen vs `image1`/`image2` for Dev multiref)

---

## Integration with Production Pipeline

### When to Run Image QC

1. **After every identity sheet generation** — before the sheet enters the reference library
2. **After every scene frame generation** — before the frame is used as a video start frame
3. **After every storyboard generation** — before boards are used for shot planning
4. **Before prompt submission** (prompt QC) — before spending API credits

### QC Gates

| Image Type | Pass Requirement | Escalation Threshold |
|------------|-----------------|---------------------|
| Identity sheet | All panels PASS, style consistent | 2 failed seeds on same defect |
| Scene frame | All checks PASS, prompt fully adhered | 2 failed seeds on same defect |
| Storyboard | Composition readable, no anatomical horrors | 3 failed seeds (lower bar for sketches) |
| Prompt | All checks PASS | N/A (fix before generation) |
