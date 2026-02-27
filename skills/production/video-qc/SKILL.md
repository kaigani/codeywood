---
skill: video-qc
role: production
version: 1.0

description: |
  Video quality control skill using joint reasoning between Claude and Qwen 2.5 VL.
  Claude orchestrates the pipeline, Qwen VL observes frame content, Claude reasons
  over observations against the production brief. Catches hallucinated content,
  object duplication, count drift, property instability, and rendering artifacts
  that neither system reliably detects alone.

inputs:
  required:
    - name: generated_clip
      type: file
      description: The generated video clip to review (.mp4)
    - name: production_brief
      type: string
      description: What SHOULD be in the clip — expected objects, actions, colors, counts, camera motion
  optional:
    - name: start_frame
      type: file
      description: The start frame image used to generate this clip (for composition match)
    - name: video_prompt
      type: string
      description: The exact prompt sent to the video model
    - name: narration_text
      type: string
      description: Dialogue or narration expected during this clip
    - name: shot_list_entry
      type: string
      description: The shot list YAML entry for this clip (frame_prompt, video_prompt, video_model_notes)

outputs:
  - name: qc_report
    type: file
    description: Structured pass/fail table per assessment dimension with specific defect descriptions and timecodes
  - name: defect_list
    type: list
    description: Itemized list of all detected defects with severity, timecode, and detection method
  - name: escalation_recommendation
    type: string
    description: Recommended action — pass, trim, re-prompt, regenerate, escalate model

tools:
  - Read (for viewing frames and start images)
  - scripts/analysis/analyze_clip.py (filmstrip, metadata, color, motion, audio analysis)
  - scripts/lib/video_analysis.py (programmatic frame extraction)
  - ComfyUI qwen25-vl workflow (vision-language observation)
---

# Video QC

## Purpose

Catch defects in AI-generated video clips before they enter the assembly pipeline. Video generation models (LTX-2, Kling, etc.) produce clips with defects that are invisible to programmatic checks and difficult for any single system to reliably detect: hallucinated duplicate subjects during camera moves, object count drift across frames, shape morphing, color order changes, and rendering artifacts.

This skill uses **joint reasoning** between Claude and Qwen 2.5 VL as a combined system:

- **Claude** orchestrates the pipeline, extracts technical data, and performs reasoning over observations
- **Qwen 2.5 VL** observes frame content through structured prompts — zone inventories, per-second tracking, targeted verification
- **The fundamental rule**: Never let a single system both observe AND evaluate in the same pass

This separation exists because:
1. Claude alone misidentifies structural errors (e.g., calling a hallucinated duplicate head "mouth distortion")
2. Qwen VL alone has strong positive/confirmation bias and cannot independently discover defects
3. Together, with observation separated from reasoning, they reliably catch critical defects

---

## The Honesty Rule

**NEVER summarize positively if defects exist.** This is the foundational principle inherited from image QC.

- Say "Hallucinated second head at 8.5s" not "Generally good clip with minor artifacts"
- The user trusts this assessment to decide pass/fail — false positives waste regeneration time and money
- When in doubt, flag it. The user can override if they think it's acceptable
- Every review MUST produce a structured report with per-dimension verdicts

---

## The Five-Step Pipeline

Every video QC review follows these five steps in order. Do not skip steps. Do not combine observation and evaluation.

### Step 1: EXTRACT (Local Tools)

**Actor**: Claude using local analysis tools
**Purpose**: Gather all technical and visual data before any evaluation begins

**Actions**:
1. Run `analyze_clip.py` on the clip:
   ```bash
   python3 scripts/analysis/analyze_clip.py CLIP_PATH
   ```
   This produces: filmstrip (20 frames in 4x5 grid), metadata (resolution, fps, duration, codec), color palette JSON, motion energy chart, silence regions.

2. Read the analysis outputs:
   - `summary.json` — full analysis results
   - `metadata.json` — technical specs
   - `color_palette.json` — dominant colors at 8 sample points
   - `motion.json` — motion energy at 0.5s intervals
   - `silence.json` — silence regions

3. View the filmstrip image — this gives Claude a 20-frame overview of the entire clip

4. If a start frame was provided, read it for composition comparison

5. Extract per-second frames for detailed inspection:
   ```bash
   # Use ffmpeg to extract one frame per second
   ffmpeg -i CLIP_PATH -vf "fps=1" -q:v 2 OUTPUT_DIR/sec_%02d.png
   ```

**Output**: Technical metadata, filmstrip, per-second frames, color data, motion data — all available for later reasoning steps.

### Step 2: SCAN (Qwen VL — Zone Inventory)

**Actor**: Qwen 2.5 VL via ComfyUI `qwen25-vl` workflow
**Purpose**: Structured spatial inventory of what exists in the clip. Observation ONLY — no evaluation, no quality judgment.

**Prompt template**:
```
Divide this video into 4 equal vertical zones (A=top quarter, B=upper-middle, C=lower-middle, D=bottom quarter).

For each zone, list every distinct object or feature you can see at ANY point during the video.

Format your answer EXACTLY as:
ZONE A (top quarter): [list objects]
ZONE B (upper-middle): [list objects]
ZONE C (lower-middle): [list objects]
ZONE D (bottom quarter): [list objects]

Be literal. Report shapes and colors, not interpretations. If you see something that looks like a face, say "face-like shape" not "person".
```

**Parameters**: `max_new_tokens=512`, `seed=42`

**Why this works**: Zone inventory forces structured spatial observation without interpretation. If the same object (e.g., a face) appears in multiple non-adjacent zones, that's data for the REASON step — but Qwen VL doesn't need to judge it here.

**What to capture**: Save the raw zone inventory text for use in Steps 4 and 5.

### Step 3: TRACK (Qwen VL — Per-Second Description)

**Actor**: Qwen 2.5 VL via ComfyUI `qwen25-vl` workflow
**Purpose**: Temporal tracking of what's visible at each second. Forces unique per-second observation to catch count drift, property changes, and appearing/disappearing objects.

**Prompt template**:
```
Describe what is at the CENTER of the frame at each second of this video. You MUST give a DIFFERENT, UNIQUE description for each second — no repeating yourself.

Format:
0s: [what is at center of frame]
1s: [what is at center of frame]
2s: [what is at center of frame]
...continue for each second...

Focus on: colors, shapes, textures, objects. Be specific. If the camera is moving, describe what new content enters the frame.
```

**Parameters**: `max_new_tokens=1024`, `seed=42`

**Why this works**: Forcing unique descriptions per second prevents Qwen VL's tendency toward lazy repetition ("caps, caps, caps") and surfaces temporal changes that matter — objects appearing, disappearing, or changing properties.

**What to capture**: Save the raw per-second tracking text for use in Steps 4 and 5.

### Step 4: REASON (Claude — Cross-Reference Against Brief)

**Actor**: Claude
**Purpose**: This is where evaluation happens. Cross-reference the SCAN and TRACK observations against the production brief. Claude was NOT the observer — it's reasoning over Qwen VL's observations with fresh eyes.

**Reasoning checklist**:

1. **Expected vs Actual Inventory**:
   - List every object/feature mentioned in the production brief
   - For each, check: is it present in the zone scan? At the expected position?
   - List every object/feature in the zone scan NOT mentioned in the brief
   - Flag: MISSING (in brief, not observed) or HALLUCINATED (observed, not in brief)

2. **Object Continuity**:
   - Does any object appear in zones where it shouldn't? (e.g., a face in both zone A and zone C = possible duplicate)
   - Does the per-second tracking show objects appearing or disappearing?
   - Count drift: does the number of a specific object change across seconds?

3. **Property Stability**:
   - Do colors reported in tracking match what's expected?
   - Cross-reference with `color_palette.json` — do dominant colors shift unexpectedly?
   - Do shapes or sizes described change across seconds?

4. **Motion Analysis**:
   - Does `motion.json` show flat energy (freeze) or repetitive energy (loop)?
   - Does the motion pattern match expected camera movement?

5. **Physical Plausibility**:
   - Can the observations from zone scan and tracking be physically possible?
   - A face appearing below a stack of hats AND above them = physically impossible = hallucinated duplicate
   - Objects changing count without entering/exiting frame = generation error

6. **Composition Match** (if start frame provided):
   - Does the first filmstrip frame match the start frame composition?
   - Are the same objects present? Same positions? Same colors?

7. **Technical Check**:
   - Resolution, fps, duration match expectations?
   - Any codec or format anomalies?

**Output**: A list of suspected defects, each with: what was observed, why it's suspicious, suggested severity, and approximate timecode.

### Step 5: VERIFY (Qwen VL — Targeted Confirmation)

**Actor**: Qwen 2.5 VL via ComfyUI `qwen25-vl` workflow
**Purpose**: Feed suspected defects back to Qwen VL for targeted verification. This chains Qwen's own observations into physical plausibility checks.

**Prompt template** (one per suspected defect):
```
This video has KNOWN DEFECTS that we are investigating.

In your earlier observation, you reported:
- Zone A (top): [paste zone A observation]
- Zone C (lower-middle): [paste zone C observation]

You reported [specific observation, e.g., "a face-like shape in both zone A and zone C"].

Question: Is it physically possible for [the subject] to have [the observed pattern]? Could this be a video generation error where [specific defect hypothesis]?

Answer with YES (this is physically possible) or NO (this appears to be a generation error), and explain your reasoning.
```

**Parameters**: `max_new_tokens=512`, `seed=42`

**Why this works**:
- "KNOWN DEFECTS" framing bypasses Qwen VL's positive bias — it's not asked to find defects (which triggers denial), it's told defects exist and asked to evaluate a specific one
- Chaining its own observations prevents it from re-observing and rationalizing — it must reason about what it already reported
- Binary YES/NO format forces a clear answer

**Output**: Confirmed or rejected defects. Update the defect list from Step 4.

---

## Qwen VL Prompting Rules

These rules are critical. Violating them produces unreliable results.

### Rule 1: NEVER Include the Production Brief in Observation Prompts

When Qwen VL receives the "correct answer" alongside the observation request, it confirms the answer regardless of reality. This is confirmation bias and it is the #1 failure mode.

- **WRONG**: "The caps should be grey, brown, blue, red from bottom to top. What order are the caps?"
- **RIGHT**: "List the colors of the caps from bottom to top."

The production brief is for Claude's REASON step only. Qwen VL sees only neutral observation prompts.

### Rule 2: Separate Observation from Evaluation

Never ask Qwen VL to find defects in a single pass. It will report "no defects found" due to positive bias.

- **WRONG**: "Find all errors in this video"
- **RIGHT**: Step 1 = "List what you see in each zone" → Step 2 = "You reported X, is this physically possible?"

### Rule 3: Zone Scan for Spatial Inventory

Divide the frame into named zones and ask what's in each. This forces structured observation that surfaces spatial anomalies (same object in multiple zones = potential duplicate).

### Rule 4: Per-Second Tracking for Temporal Analysis

Force unique descriptions per second. This surfaces temporal anomalies (objects appearing, disappearing, changing). Without the "DIFFERENT, UNIQUE" instruction, Qwen VL produces lazy repetitive output.

### Rule 5: Chain Observations Back for Inference

The verify step must reference Qwen VL's own earlier observations. "You reported X" → "Is X physically possible?" This prevents re-observation and forces reasoning over captured data.

### Rule 6: Adversarial Framing for Targeted Checks

"This has KNOWN DEFECTS" unlocks honest reporting. Without this framing, Qwen VL defaults to "everything looks good" positive bias.

### Rule 7: Control Output Length

- `max_new_tokens=512` for zone scans and verification queries
- `max_new_tokens=1024` for per-second tracking
- **NEVER use 2048+** — causes degenerate repetition loops ("caps, face, caps, face..." infinitely)

### Rule 8: Keep Prompts Clean

Avoid special characters, excessive formatting, or very long prompts in ComfyUI form fields. Overly complex prompts cause 400 Bad Request errors. Keep prompts under ~500 words.

---

## Assessment Dimensions

Every clip is evaluated on these eight dimensions:

| Dimension | What to Check | Primary Detection Method |
|-----------|--------------|------------------------|
| **Technical** | Resolution, codec, fps, duration match specs | `metadata.json` from EXTRACT |
| **Expected vs Actual** | Objects in clip match production brief — nothing extra, nothing missing | SCAN zones vs brief (REASON step) |
| **Object Continuity** | No hallucinated duplicates, no disappearances mid-clip | SCAN zones for spatial duplication + TRACK for temporal |
| **Property Stability** | Colors, shapes, sizes consistent across clip duration | TRACK per-second + `color_palette.json` |
| **Prompt Adherence** | Every specific video prompt detail reflected in output | TRACK observations vs video prompt |
| **Composition Match** | First frame matches provided start frame | Filmstrip frame 0 vs start frame (Claude visual) |
| **Motion Quality** | No loops, no freezes, appropriate energy for the shot | `motion.json` energy curve |
| **Rendering Artifacts** | No face/mouth/hand distortions, no morphing | SCAN + VERIFY with adversarial framing |

---

## Common Video Defect Catalog

| Defect Class | Description | Detection Method | Typical Severity |
|-------------|-------------|-----------------|-----------------|
| **Hallucinated duplicate** | Same subject appears twice (e.g., two heads on one puppet) | Zone scan: subject reported in non-adjacent zones | CRITICAL |
| **Hallucinated content** | Object present in clip but NOT in production brief | Zone scan vs brief: unexpected object | CRITICAL |
| **Missing expected content** | Object in production brief but NOT present in clip | Zone scan vs brief: expected object absent | MAJOR |
| **Object count drift** | Number of objects changes during clip (e.g., 4 caps become 5) | Per-second tracking: count changes without enter/exit | MAJOR |
| **Shape morphing** | Object changes shape during clip (flat cap becomes beret) | Adversarial Qwen query + per-second tracking | MAJOR |
| **Color/property drift** | Object changes color or material during clip | Per-second tracking + `color_palette.json` shift | MODERATE |
| **Rendering artifact** | Face/mouth/hand distortion, teeth artifacts, melted features | Frame inspection (Claude) + adversarial Qwen verify | MAJOR |
| **Motion freeze** | Clip contains static frames (no motion for 1s+) | `motion.json`: energy drops to near-zero | MODERATE |
| **Motion loop** | Clip repeats the same motion cycle | `motion.json`: periodic energy pattern | MODERATE |
| **Composition mismatch** | First frame doesn't match the provided start frame | Visual comparison of filmstrip frame 0 vs start frame | MAJOR |
| **Technical fault** | Wrong resolution, fps, codec, or truncated duration | `metadata.json` vs expected specs | MAJOR |

---

## QC Report Format

Every video clip review MUST produce this structured report.

```
### [Clip Name] QC Review

**Clip**: [filename]
**Duration**: [X.Xs] | **Resolution**: [WxH] | **FPS**: [N]
**Production Brief**: [1-2 sentence summary of what should be in the clip]

#### Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| Technical | PASS/FAIL | [specific issue or "--"] |
| Expected vs Actual | PASS/FAIL | [what's extra or missing] |
| Object Continuity | PASS/FAIL | [duplication or disappearance] |
| Property Stability | PASS/FAIL | [what changed] |
| Prompt Adherence | PASS/FAIL | [what prompt detail is wrong] |
| Composition Match | PASS/FAIL/N/A | [mismatch description] |
| Motion Quality | PASS/FAIL | [freeze, loop, or energy issue] |
| Rendering Artifacts | PASS/FAIL | [specific artifact] |

#### Defects

| # | Severity | Timecode | Defect | Detection Method |
|---|----------|----------|--------|-----------------|
| 1 | CRITICAL | 7.0-9.5s | Hallucinated second puppet head below cap stack | Zone scan: face in zones B+D |
| 2 | MAJOR | 0-10s | Cap order wrong: should be grey→brown→blue→red, observed brown→grey→blue→red | TRACK vs brief |
| 3 | MODERATE | 4-6s | Cap count drifts from 12 to 14 | Per-second tracking |

#### Verdict

**FAIL** — [N] defects ([N] CRITICAL, [N] MAJOR, [N] MODERATE, [N] MINOR)

#### Recommendation

[Specific action: pass, trim to Xs-Ys, re-prompt with fix, regenerate with different seed, escalate to higher model]
```

---

## Escalation Rules

### Decision Tree

```
Defect found?
├── NO → PASS — clip enters assembly pipeline
├── YES, MINOR only → PASS WITH NOTE — clip usable, log for awareness
├── YES, MODERATE → Can defect be trimmed out?
│   ├── YES → TRIM — specify trim points, clip enters assembly
│   └── NO → REGENERATE — fix prompt, new seed
├── YES, MAJOR → REGENERATE with prompt fix
│   └── Same defect on 2nd attempt? → ESCALATE
└── YES, CRITICAL → REGENERATE immediately
    └── Same defect on 2nd attempt? → ESCALATE
```

### Escalation Actions

| Trigger | Action |
|---------|--------|
| Same defect, 2 consecutive seeds | Change prompt approach (not just seed) |
| Same defect, 2 consecutive prompt approaches | Escalate to different video model |
| Hallucinated duplicate on camera move | Add first+last frame constraint (i2v with both endpoints) |
| Persistent rendering artifacts on faces | Reduce clip duration, use tighter framing |
| Count drift on stacked/grouped objects | Simplify scene, reduce object count in prompt |
| Motion freeze or loop | Adjust motion description in prompt, try different seed |

### Severity Definitions

| Severity | Definition | Impact |
|----------|-----------|--------|
| **CRITICAL** | Content that was never in the brief (hallucinated heads, extra limbs, wrong subjects) | Clip unusable — immediate regeneration |
| **MAJOR** | Expected content wrong (wrong order, wrong color, missing object, composition mismatch) | Clip misleading — needs regeneration or significant trim |
| **MODERATE** | Temporal instability (count drift, minor color shift, brief morphing) | Clip marginal — may be trimmable or acceptable depending on context |
| **MINOR** | Subtle artifacts visible only on close inspection (slight texture wobble, minor shadow flicker) | Clip usable — log for awareness |

---

## Integration with Production Pipeline

### When to Run Video QC

1. **After every clip generation** — before the clip is considered for assembly
2. **After trim/edit operations** — verify the edit didn't introduce issues
3. **Before final assembly** — spot-check assembled sequence for transition artifacts

### QC Gates

| Stage | Pass Requirement | Escalation Threshold |
|-------|-----------------|---------------------|
| First draft (t2v) | No CRITICAL defects, MAJOR defects logged | 2 failed seeds on same defect |
| Revision (i2v) | No CRITICAL or MAJOR defects | 2 failed prompt approaches |
| Final production | All dimensions PASS | Escalate to higher model or manual fix |

### Pipeline Integration Pattern

```
generate_clip → video_qc → decision
                              ├── PASS → assembly
                              ├── TRIM → trim_clip → assembly
                              ├── REGENERATE → fix_prompt → generate_clip → video_qc (loop)
                              └── ESCALATE → change_model/approach → generate_clip → video_qc
```

### Batch QC

When reviewing multiple clips for a scene assembly:
1. QC each clip individually using the five-step pipeline
2. After individual QC, do a cross-clip consistency check:
   - Same character looks consistent across clips?
   - Color temperature and lighting consistent?
   - No continuity breaks between consecutive clips?

---

## ComfyUI Qwen 2.5 VL API Reference

**Endpoint**: `http://192.168.1.181:8100/workflows/qwen25-vl`
**Method**: POST (multipart form)

**Parameters**:
| Field | Type | Description |
|-------|------|-------------|
| `video` | file | The video file to analyze |
| `prompt` | string | The observation/verification prompt |
| `max_new_tokens` | integer | Max output tokens (use 512-1024, never 2048+) |
| `seed` | integer | Random seed (use 42 for reproducibility) |

**Response**: JSON with `description` field containing the model's text response.

**Example call** (from Claude via bash):
```bash
curl -s -X POST http://192.168.1.181:8100/workflows/qwen25-vl \
  -F "video=@/path/to/clip.mp4" \
  -F "prompt=Divide this video into 4 equal vertical zones..." \
  -F "max_new_tokens=512" \
  -F "seed=42"
```
