# Video Director Skill

## Purpose
Direct AI video generation with cinematic pacing, explicit scene direction, and sound design guidance. This skill ensures video clips feel intentional rather than rushed, with proper establishing moments and breathing room.

## Trigger
When planning video clip sequences, writing multi-prompt video prompts, or reviewing pacing of assembled scenes.

## Production Pipeline Tiers

Choose the right pipeline tier based on production phase:

| Tier | Pipeline | Time (11 clips) | Cost | When to Use |
|------|----------|-----------------|------|-------------|
| 1 — First Draft | LTX-2 T2V (text only) | ~18 min | $0.00 | Testing shot lists, prompt quality, pacing |
| 2 — Revision | Klein frames + LTX-2 i2v | ~28 min | $0.00 | Character anchoring, composition control |
| 3 — Final | Dev frames + Kling v3 Pro | $$$ | varies | Final production, highest quality |

**Default workflow**: Start at Tier 1 for every scene. Only escalate to Tier 2/3 for shots that need it.

---

## Core Principles

### 1. PACING: Let Scenes Breathe

**Problem**: AI-generated sequences often feel rushed because we pack too much action into short clips.

**Solution**: Build in "breathing room" moments:
- Establishing shots that set location/mood before action
- Reaction beats after significant moments
- Transitional pauses between locations
- Lingering on meaningful details

**Pacing Structure for a Scene**:
```
1. ESTABLISH (2-4s) - Wide shot, location, mood
2. APPROACH (3-4s) - Character enters/moves through space
3. DETAIL (2-3s) - Close-up on significant element
4. ACTION (3-5s) - The key beat of the scene
5. REACTION (2-3s) - Character processes what happened
6. TRANSITION (2-3s) - Movement to next beat
```

**Example - Rushed vs. Directed**:

| Rushed (BAD) | Directed (GOOD) |
|--------------|-----------------|
| "She enters the room and finds the book" (5s) | Shot 1: "Wide shot of empty cell, dust in moonlight" (3s) |
| | Shot 2: "She steps through doorway, pauses, scans the room" (4s) |
| | Shot 3: "Close-up on her hands tracing the wall" (3s) |
| | Shot 4: "She discovers a loose stone, begins prying" (4s) |

### 2. EXPLICIT DIRECTION: More is Better

**Problem**: AI video models WILL invent content to fill gaps. Vague prompts lead to unwanted invention.

**Solution**: Be maximally explicit about:
- What the character IS doing
- What the character is NOT doing (especially dialogue)
- Environmental sounds
- Camera behavior
- Lighting continuity

**Explicit Direction Template**:
```
[SHOT TYPE], [CHARACTER ACTION with specific body language],
[ENVIRONMENTAL DETAIL], [LIGHTING NOTE],
[SOUND DIRECTION], [CAMERA MOVEMENT]
```

**Example**:
```
Medium shot, @Element1 crouches at the wall and pries at loose mortar with a blade,
her jaw clenched with effort, knuckles white on the handle,
dust particles drift in wrong-blue moonlight from the barred window,
practical lantern light flickers on her face,
No talking, characters are silent, only the scrape of metal on stone and her labored breathing,
slow push-in on her hands
```

### 3. DIALOGUE CONTROL: Supply or Suppress

**CRITICAL**: Kling and similar models WILL invent dialogue when a person is the focal point of a shot, regardless of silence directives. The degree of invention depends on the shot:

**When silence directives work**:
- Wide shots where the character is small in frame
- Action shots with strong physical movement (running, climbing, fighting)
- Detail shots focused on objects, not faces
- Shots where the character's mouth is not visible

**When the model will insert dialogue anyway**:
- Close-ups on a character's face
- Medium shots with minimal action (standing, waiting, thinking)
- Two-shots where characters face each other
- Any shot where a character is clearly the emotional focal point

**Strategy: Supply dialogue rather than fight the model**:
- Internal monologue: `@Element1 whispers to herself "Almost there..."`
- Character-to-character: `@Element1 says "I won't let you take it"`
- Breathing/effort: `@Element1 gasps for breath between words`
- When silence IS achievable (wide/action shots): `No talking, characters are silent`

**Fallback for close shots where you want silence**: Describe non-verbal mouth actions explicitly — "jaw clenched shut", "bites her lip", "presses lips together" — to give the model something to do with the mouth besides invent speech.

**Note**: "no spoken dialogue" is less effective than "No talking, characters are silent", but even the latter fails on character close-ups. Supply dialogue or internal monologue instead.

**Sound Direction Options**:

| Type | Prompt Language |
|------|-----------------|
| Silent character | "No talking, characters are silent" |
| Effort sounds | "wordless grunts of effort, no talking" |
| Breathing | "her breathing quickens, no talking" |
| Reaction sounds | "sharp intake of breath, characters are silent" |
| Environmental only | "only ambient sounds, no talking" |
| Scripted dialogue | "she whispers 'It's here'" |

### 4. ENVIRONMENTAL SOUND DIRECTION

Even without custom voice, describe the soundscape:

**Sound Categories**:
- **Ambient**: "distant waves", "dripping water", "wind through bars"
- **Action**: "scrape of metal", "creak of hinges", "soft footsteps on stone"
- **Character**: "steady breathing", "grunt of effort", "sharp exhale"
- **Dramatic**: "ominous low hum", "rising tension", "sudden silence"

**Example Sound Direction**:
```
ambient dripping water echoes in the corridor,
her soft footsteps on wet stone,
the creak of an iron door hinge,
No talking, characters are silent
```

### 5. ESTABLISHING SHOTS: Set the Stage

Every new location needs establishment before action:

**Establishing Shot Checklist**:
- [ ] Wide/medium-wide framing
- [ ] No character or character small in frame
- [ ] Key environmental details visible
- [ ] Lighting/time of day clear
- [ ] Mood-setting elements present
- [ ] Duration: 2-4 seconds minimum

**Establishing Shot Prompts**:
```
Wide establishing shot, [LOCATION] at [TIME],
[KEY ENVIRONMENTAL DETAILS], [MOOD ELEMENTS],
[LIGHTING QUALITY], static camera, no characters visible
```

### 6. DETAIL SHOTS: Linger on Significance

Insert close-ups on meaningful objects/moments:

**When to Use Detail Shots**:
- Before a key object is used
- During moments of discovery
- To show character emotion through hands/eyes
- To create tension through slow reveal

**Detail Shot Structure**:
```
Extreme close-up, [SPECIFIC DETAIL],
[TEXTURE/QUALITY DESCRIPTION],
[LIGHTING ON THE DETAIL],
[SUBTLE MOVEMENT if any],
duration 2-3 seconds
```

### 7. MULTI-PROMPT PACING

When using multi-prompt (multiple cuts in one generation):

**Rules**:
1. Each cut needs full explicit direction
2. Include transition language ("Cut to:")
3. Vary shot types (wide → medium → close)
4. Don't pack too much action into one cut
5. Include at least one "breathing" moment per sequence

**Multi-Prompt Template**:
```python
multi_prompt = [
    {
        "prompt": "Cut to: [ESTABLISHING/TRANSITION], [ENVIRONMENT], "
                  "[MOOD], static camera, no dialogue",
        "duration": "3"
    },
    {
        "prompt": "Cut to: [CHARACTER ACTION], [SPECIFIC BODY LANGUAGE], "
                  "[SOUND DIRECTION], [CAMERA MOVEMENT]",
        "duration": "4"
    },
    {
        "prompt": "Cut to: [DETAIL/REACTION], [CLOSE FRAMING], "
                  "[EMOTIONAL BEAT], [SOUND], slow movement",
        "duration": "3"
    }
]
```

## Scene Planning Workflow

### Step 1: Beat Sheet
List the emotional/narrative beats of the scene:
1. What must happen?
2. What emotion should the audience feel?
3. What information is conveyed?

### Step 2: Shot List with Pacing
For each beat, plan:
- Shot type (establish, action, detail, reaction)
- Duration needed
- Sound requirements
- Dialogue status

### Step 3: Breathing Room Check
Review shot list and ask:
- Is there an establishing shot before action?
- Are there detail moments to slow pace?
- Do transitions have time to land?
- Is there variety in shot rhythm?

### Step 4: Explicit Direction Pass
For each shot, ensure:
- Character action is specific (body language, movement)
- Sound is explicitly directed
- Dialogue status is clear
- Camera behavior is noted

## Common Pacing Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Rushed feeling | Too much action per clip | Add establishing/detail shots |
| Invented dialogue | Character appears to speak nonsense | Add "No talking, characters are silent" |
| Confusing action | Character does unexpected things | More explicit body direction |
| Flat audio | Generic ambient sounds | Specific environmental sound direction |
| Jarring cuts | Transitions feel abrupt | Add transition/breathing shots |
| Lost geography | Viewer confused about location | More establishing shots |
| Over-produced dialogue | Too many clips/compositions for enclosed scene | Use Scene Type Production Guide; fewer clips, longer durations, restricted shot repertoire |

## Example: SC02 Revision Notes

Original issue: Scene felt rushed, needed more establishing and breathing room.

**Revision approach**:
1. Add exterior establishing shot of compound at dusk (3s)
2. Add detail shot of hands on wall before climbing (2s)
3. Add corridor atmosphere shot before Mars enters frame (3s)
4. Add close-up on her face as she scans the cell (2s)
5. Add detail shot on the blade working the mortar (3s)
6. All prompts include "No talking, characters are silent" or specific sounds

**Sound direction added**:
- "her steady breathing, no words"
- "scrape of metal on stone"
- "soft footsteps on wet floor"
- "sharp exhale of relief"
- "grunt of effort as she pries"

## Quality Checklist

Before generating video clips:
- [ ] Establishing shot exists for each new location
- [ ] Pacing includes breathing moments (not all action)
- [ ] Shot variety exists (wide/medium/close mix)
- [ ] Every prompt has explicit dialogue control
- [ ] Sound direction is specific for each clip
- [ ] Character actions include body language details
- [ ] Transitions are planned, not assumed
- [ ] Total duration feels appropriate (not rushed)
- [ ] Clip count matches scene type target (see Scene Type Production Guide)
- [ ] Dialogue scenes use restricted shot repertoire (OTS, two-shot, singles)
- [ ] Frame reuse strategy identified (4-6 base compositions, not unique per shot)

## Frame Validation Gate (CRITICAL)

**WORKFLOW: Frames must be validated BEFORE clip generation**

```
Generate Frames → Claude Reviews Frames → Validation Pass? → Generate Clips
                         ↓ (fail)
                   Fix prompts, regenerate
```

**Frame Acceptance Criteria** (invoke `shot-quality-validator`):
1. **Single moment** - Clean frame, no composite/multi-state images
2. **Character consistency** - Matches identity sheet
3. **Technical quality** - No artifacts, correct resolution
4. **Composition** - Matches shot type specification

**CRITICAL CHECK: No Composite Images**

Frame prompts must NOT contain transitional language:
- BAD: "Her expression shifts from determination to horror"
- GOOD: "Her expression is focused determination"

Transitional language causes models to render multiple states in one image.
Keep transitions in VIDEO prompts only.

**Review Process**:
1. After `generate_frames.py`, Claude reads each generated frame
2. For each frame, verify against acceptance criteria
3. If ANY frame fails → identify issue, fix prompt, regenerate
4. Only proceed to clips when ALL frames pass

## Agentic Clip Generation Loop (CRITICAL)

**Video generation is NON-DETERMINISTIC. Clips must be generated ONE AT A TIME with Claude review after each.**

This is NOT a batch process. The workflow is an adaptive loop where each clip's output
informs the next clip's approach.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENTIC CLIP GENERATION LOOP                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. GENERATE Clip N                                                 │
│          ↓                                                          │
│  2. EXTRACT last frame from Clip N                                  │
│          ↓                                                          │
│  3. CLAUDE REVIEWS last frame:                                      │
│     - What is character's actual position/state/expression?         │
│     - Does this match what we expected?                             │
│     - What action would naturally CONTINUE from this frame?         │
│          ↓                                                          │
│  4. ASSESS next clip's planned start frame and prompts:             │
│     - Does the planned start frame match the ending state?          │
│     - Do the prompts describe actions that continue naturally?      │
│          ↓                                                          │
│  5. DECISION:                                                       │
│     ├─ PROCEED: Ending aligns with next clip → generate Clip N+1    │
│     ├─ ADJUST: Modify next clip's prompts to match actual ending    │
│     ├─ BRIDGE: Insert bridge clip to smooth transition              │
│     └─ USE LAST FRAME: Set next clip to start from extracted frame  │
│          ↓                                                          │
│  6. LOOP back to step 1 for next clip                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Why This Matters:**
- Video models are non-deterministic - character may end in unexpected position
- Pre-planned prompts may contradict the actual generated ending
- Real-time adjustment prevents continuity breaks
- Each clip's output is a constraint on the next clip's input

**Claude's Review Questions After Each Clip:**
1. Where is the character physically positioned in the last frame?
2. What is their body language/expression?
3. What direction are they facing/moving?
4. Does this match what the next clip expects as its starting state?
5. Do I need to adjust the next clip's prompts or start frame strategy?

**Adjustment Options:**
| Situation | Action |
|-----------|--------|
| Ending matches plan | Proceed with next clip as planned |
| Minor position difference | Adjust next clip's first prompt to match |
| Significant gap | Use `last_frame` strategy instead of `shot` |
| Major discontinuity | Generate bridge clip from last frame |
| Unexpected ending | May need to regenerate current clip |

**Generating Frames from Last Frame** (for exceptional continuity):
When a bridge clip needs a custom start frame derived from the previous clip's ending:
```
1. Extract last frame from Clip N
2. Use Nano Banana Pro /edit endpoint with last frame as reference
3. Generate new frame showing next logical state
4. Use new frame as start for bridge clip
```

## Start Frame Awareness (CRITICAL)

**Prompts must describe actions that CONTINUE from the actual start frame state.**

The model SEES the start frame. If the prompt describes a state that contradicts
what's visible in the start frame, the model will:
- Try to reconcile the contradiction (creating awkward transitions)
- Invent intermediate actions (moving to a "new" doorway)
- Produce discontinuous motion

### Multi-Prompt Alignment Rule

**The FIRST prompt of a multi-prompt clip MUST describe what is visible in the start frame.**

```
START FRAME IMAGE = What the model SEES at frame 0
FIRST PROMPT = MUST describe action continuing FROM the start frame
ELEMENT REFERENCE IMAGES = Supplemental refs for consistency (NOT what first prompt describes)
```

**Common Mistake:**
- Start frame: shot06 (ledger discovery)
- First prompt: "prying at mortar..." (describes shot05)
- Result: Model sees ledger but prompt says hands-at-wall = CONTRADICTION

**Correct Approach:**
- Start frame: shot05 (hands at mortar)
- First prompt: "prying at mortar, stone loosens..."
- Element refs: can include shot06 for character consistency in later cuts

**Element reference images serve these purposes:**
1. Character consistency across cuts (identity/costume)
2. Future state preview (where the action is heading)
3. Environmental consistency

**Element reference images do NOT replace the start frame.** The start frame is what
the model renders FROM. Element refs are supplemental context.

**Before writing clip prompts, Claude MUST:**
1. View/understand the start frame (either the generated shot frame OR extracted last frame)
2. Describe the character's current position/state in the start frame
3. Write prompts that continue FROM that state, not TO that state
4. Verify FIRST PROMPT aligns with START FRAME (not with element refs)

**Example - BAD vs GOOD**:

Start frame shows: Mars standing IN the doorway, silhouetted

| BAD (contradicts start frame) | GOOD (continues from start frame) |
|-------------------------------|-----------------------------------|
| "She reaches for the door handle, pushes door open" | "She steps forward through the doorway into the dark cell" |
| (implies she's OUTSIDE the door) | (continues from her IN-doorway position) |

## Shot-Specific Reference Images

**Each shot in a multi-prompt should have a supporting reference image for the main character.**

For each cut in a multi-prompt clip:
1. Identify the main action/pose required
2. Include a reference image showing the character in a similar context
3. This can be: the generated frame for that shot, a frame from a previous clip, or a custom reference

**Reference image priority for elements**:
1. Generated frame for the specific shot (if available)
2. Last frame from previous clip (for continuity)
3. Hero shot (for general character reference)
4. Identity sheet (fallback)

This ensures the model has visual context for what the character should look like
in each specific moment, not just a general reference.

## Start Frame Strategy (CRITICAL)

**Use a generated Nano Banana Pro frame when available. Fall back to `last_frame` when not.**

```yaml
# Strategy decision tree:
# 1. Do we have a generated frame for this shot? → Use it (strategy: shot)
# 2. No generated frame? → Use last_frame from previous clip (strategy: last_frame)
```

**When to use each strategy:**

| Strategy | When to Use |
|----------|-------------|
| `shot` | Generated frame exists for the shot's start state |
| `last_frame` | No generated frame, OR bridge clip continuing from previous action |
| `custom` | Special case: manually prepared frame |

**Example:**
```yaml
clips:
  - id: 1
    start_frame:
      strategy: shot       # Has generated frame
      shot_id: 1

  - id: 2
    start_frame:
      strategy: shot       # Has generated frame (new location)
      shot_id: 3

  - id: 3  # Bridge clip
    start_frame:
      strategy: last_frame  # No generated frame, continues from clip 2
      clip_id: 2

  - id: 4
    start_frame:
      strategy: shot       # Has generated frame for new shot type
      shot_id: 6
```

**Key principle:** The start frame must accurately represent the character's state
at the beginning of the clip. Whether that comes from a generated frame or
extracted last frame, the prompts must describe actions that CONTINUE from
that visible state.

---

## Multi-Shot vs Single-Shot Strategy

### Decision Rule

| Condition | Strategy | Start Frame |
|-----------|----------|-------------|
| **Same location, continuous action** | Multi-shot + extend from last frame | First clip only |
| **Location change** | New clip (single or multi-shot) | Fresh start frame |
| **Time jump** | New clip | Fresh start frame |

**Same-location scenes**: All clips after the first extend from the last frame of the
previous clip. Elements provide character and location consistency. Shot frames serve as
**element references** (pose/composition guides), NOT as start frames.

### Asset Requirements by Scene Type

| Scene Type | Elements | Start Frame | Shot Frames Used As |
|------------|----------|-------------|---------------------|
| Single-location dialogue | Chars + Location | First clip only, then extend | Element `reference_image_urls` |
| Single-location action | Chars + Location | First clip only, then extend | Element `reference_image_urls` |
| Multi-location travel | Chars (location changes per segment) | Per location change | Start frames + element refs |
| Montage / quick cuts | Chars only | Per clip | Start frames |

### Element Structure for Multi-Shot

Each Kling element has two parts:
- `frontal_image_url`: Identity sheet (characters) or establishing shot (location) — **stays constant across all clips**
- `reference_image_urls`: Pose-specific shot frames — **changes per clip**

For a given clip, each character's references should include the shot frames showing
the poses/compositions that character will inhabit in that clip's multi-prompt cuts.

**Example — 3 elements for a single-location dialogue scene:**

```
Element 1 (Character A):
  frontal: character_a_identity_sheet.png     # constant
  refs:    [shot05_opens_book.png,             # pose in cut 1
            shot06_recoils.png]                # pose in cut 2

Element 2 (Character B):
  frontal: character_b_identity_sheet.png     # constant
  refs:    [shot08_emerges.png]               # pose in this clip

Element 3 (Location):
  frontal: shot01_establish.png               # constant (room overview)
  refs:    [shot15_window_detail.png]          # key architectural feature
```

### Multi-Shot Clip Design

When grouping shots into multi-prompt clips for same-location scenes:
1. **Max duration**: 10s per clip (Kling v3 Pro limit)
2. **Group by dramatic beat**: Shots that share characters and flow naturally
3. **First prompt must match start frame**: The start frame is either a generated shot frame (clip 1) or the last frame of the previous clip (clips 2+)
4. **Subsequent prompts use CUT to: prefix**: Signals the model to shift framing/composition
5. **Element refs guide each cut**: Include shot frames for poses in each prompt

### Location Element

For same-location scenes, define a location element to provide environmental consistency:
- **Frontal**: Wide establishing shot showing the full space
- **References**: Key architectural details, different angles, important features (window, door, etc.)

This is especially important when the camera moves to different areas of the same room
or when specific set details (like a window or doorway) are critical to the action.

---

## Scene Type Production Guide

**SC03 Debrief Lesson**: A 86s single-set dialogue scene was produced with 25 shots / 18 clips (avg 4.8s/clip). This is action-scene pacing applied to a dialogue scene. The video model struggled with the volume of varied compositions in an enclosed space. Dialogue scenes need fewer, longer clips with a restricted shot repertoire.

### Pacing Targets by Scene Type

| Scene Type | Clip Count | Avg Clip Duration | Shots per 10s | Shot Types |
|------------|-----------|-------------------|---------------|------------|
| Dialogue (single-set) | 6-8 | 8-10s | 0.7-1.0 | OTS, two-shot, singles, establish |
| Dialogue (multi-set) | 8-12 | 6-8s | 1.0-1.5 | Same + location establishes |
| Action (chase/fight) | 10-15 | 3-5s | 2.0-3.0 | Wide, medium, ECU, detail, POV |
| Action (contained) | 6-10 | 4-6s | 1.5-2.0 | Medium, close, detail |
| Montage / transition | 4-8 | 3-4s | 2.0-3.0 | Varied, poetic |
| Establish / atmosphere | 2-4 | 5-8s | 0.5-1.0 | Wide, detail |

**Clip count heuristic:**
- Dialogue: max clips = scene_duration / 10
- Action: max clips = scene_duration / 5
- Max unique compositions = clips / 2 + 1

### Dialogue Scene Production Rules

For single-set dialogue scenes (the most common and hardest to get right):

1. **Fewer, longer clips**: Push toward maximum clip duration (10s for Kling v3 Pro). A 90s dialogue scene = 6-8 clips, not 15-18.

2. **Restricted shot repertoire** (max 6-7 base compositions):
   - Establishing wide (1 clip, opening)
   - Two-shot medium (the workhorse — majority of clips)
   - Over-the-shoulder A (A's face, B's shoulder foreground)
   - Over-the-shoulder B (B's face, A's shoulder foreground)
   - Single close-up A (1-2 key emotional beats only)
   - Single close-up B (1-2 key emotional beats only)
   - Closing wide (optional bookend)

3. **Frame reuse strategy**: Generate 4-6 base composition frames, then reuse or adjust with Nano Banana Pro (`image_urls` reference mode) for slight variations (expression, gaze, hand position). Do NOT generate a unique frame for every shot.

4. **Multi-prompt for shot/reverse-shot**: Within a single clip, use multi-prompt to cut between OTS-A and OTS-B. One 10s clip with two 5s prompts covers more ground than two separate 3s clips.

5. **Minimize hard cuts**: Reserve for:
   - The establishing shot (clip 1)
   - 1-2 key emotional turning points
   - The closing shot
   - Everything else extends from previous clip's last frame

6. **No standalone ECU/detail clips**: In dialogue, avoid dedicated close-up clips for objects or body details. These fragment the scene. Handle ECU moments as cuts within multi-prompt clips instead.

### SC03 Before/After Example

```
SC03 ACTUAL (over-produced):
  25 shots → 18 clips → 86s
  9 different shot types, 25 unique compositions
  Avg clip: 4.8s | Hard cuts: 8 | Pacing: ~3 shots/10s

  Shot types used: establish, entrance, ECU-book, opens-book, recoils,
  spins, reveal, blade, confrontation, truth-CU, throat-CU, gut-punch,
  silence-two-shot, window-detail, studies-window, calculation, decision,
  climbs, half-through, apology, drop, left-behind, dust-detail, closing

SC03 REVISED (dialogue-appropriate):
  8 shots → 7 clips → ~75s
  6 base compositions, 4 reused with adjustments
  Avg clip: 10.7s | Hard cuts: 2 | Pacing: ~1 shot/10s

  Clip 1: Establish + Entrance (10s) — wide room, Mars enters [shot frame]
  Clip 2: Mars alone with book (10s) — medium single, discovers book [extend]
  Clip 3: Jonah reveal + confrontation (10s) — two-shot, he emerges [hard cut]
  Clip 4: Truth exchange (10s) — OTS Mars→Jonah, the "Yes" moment [extend]
  Clip 5: The weight lands (8s) — OTS Jonah→Mars, silence [extend]
  Clip 6: Window + calculation (10s) — two-shot, she decides [hard cut]
  Clip 7: Escape + aftermath (10s) — she climbs, he's alone [extend]

  Shot repertoire: establish, medium-single, two-shot, OTS-A, OTS-B, wide-closing
  Frame reuse: two-shot frame reused for clips 3-5 with Nano Banana adjustments
```

### Frame Reuse with Nano Banana Pro

Instead of generating 25 unique frames, generate 4-6 base composition frames and create variations:

1. Generate base frames: one per shot type (establish, two-shot, OTS-A, OTS-B, close-A, close-B)
2. For clips sharing the same composition, reuse the base frame directly OR use Nano Banana Pro with `image_urls` to create slight variations (shifted expression, adjusted gaze, different hand position)
3. Two-shot and OTS frames can serve multiple clips with only prompt changes
4. Benefits: visual consistency, reduced cost, less model confusion from varied compositions

---

## Agentic Workflow Implementation

**How Claude executes the agentic clip generation loop:**

### Step-by-Step Execution Pattern

```bash
# For each clip in sequence:

# 1. Generate single clip
python3 scripts/production/generate_clips.py --scene PRODUCTION/EP01/sc02 --clip 1

# 2. Extract last frame for review
ffmpeg -sseof -0.1 -i clips/sc02_clip01.mp4 -frames:v 1 clips/clip01_last_frame.png

# 3. Claude reads and reviews the last frame
# (Use Read tool on the extracted frame)

# 4. Claude assesses alignment with next clip
# - Read next clip's planned start frame
# - Compare to actual ending state
# - Decide: proceed / adjust / bridge / use last_frame

# 5. If adjustments needed, update clip definition
# (Use Edit tool on PRODUCTION/EP01/sc02/clip_definitions.yaml)

# 6. Proceed to next clip
python3 scripts/production/generate_clips.py --scene PRODUCTION/EP01/sc02 --clip 2
```

### Claude's Review Protocol

After each clip is generated, Claude MUST:
1. **Read** the extracted last frame image
2. **Describe** in plain language what the frame shows:
   - Character position (standing, sitting, crouching)
   - Body orientation (facing camera, profile, back to camera)
   - Expression/emotional state
   - Environment context
3. **Compare** to next clip's expected start state
4. **Decide** on action before proceeding

### Example Review Output

```
CLIP 2 LAST FRAME REVIEW:
- Mars is standing IN the doorway, facing into the cell
- Her body is silhouetted against teal corridor light
- Right hand rests on door frame, left at her side
- Expression: cautious, alert

NEXT CLIP (2B) EXPECTS:
- Start: last_frame from clip 2 ✓
- First prompt: "steps forward from doorway into cell"

ASSESSMENT: Aligned ✓
- Last frame shows Mars IN doorway
- Prompt describes stepping forward FROM doorway
- Proceed with clip 2B as planned
```

---

## Integration with Other Skills

- **Prompt Engineer**: Provides technical prompt structure; Director provides pacing/intent
- **Shot List Generator**: Creates shot list; Director reviews for pacing
- **Storyboard**: Visual reference; Director interprets for video timing

---

## LTX-2 / ComfyUI Backend Prompting Guide

When using the ComfyUI backend (LTX-2 19B via `ltx2-i2v`), prompting requires a different approach than Kling. LTX-2 has no element system, no multi-prompt, and no audio generation — but it's free and runs on local GPU.

### T2V Prompt Best Practices

When using T2V (no start frame), the model has no visual anchor. Every detail must be in the prompt:

1. **Setting anchors required**: Include specific location markers in EVERY wide/medium shot. Without them, the model defaults to generic environments
2. **Period costume required**: Explicitly describe clothing era. Without this, defaults to modern
3. **Character physical specificity**: Full physical description every time — skin tone, hair, distinguishing features. No shortcuts
4. **Literal and descriptive**: Describe what the camera SEES, not emotional/abstract language
5. **Include dialogue as quoted text**: Actual spoken words in the prompt, not "she whispers something"
6. **Extra detail where ambiguous**: More is better for T2V — no start frame to anchor interpretation
7. **Negative prompt**: Add era-specific exclusions ("modern clothing, contemporary architecture" for period pieces)

**What T2V excels at**: Texture/detail shots, close-ups with action direction, abstract/architectural, lighting mood, movement direction.

**What needs most help**: Wide shots with specific architecture, period-accurate costumes, character consistency across shots.

### The "Complete Story" Approach

LTX-2 requires a **narrative approach** — not a list of elements but a cohesive mini-screenplay.

**Single Paragraph Structure**: Write one continuous, present-tense paragraph that describes the scene from beginning to end. Think of it as a mini screenplay compressed into a single paragraph.

**Six-Part Structure**:
1. **Scene**: Setting, location, lighting, atmosphere
2. **Subject/Action**: Who is doing what, with specific physical movements
3. **Camera/Lens**: Camera behavior, angle, focal length
4. **Style**: Visual quality, film stock reference, color grading
5. **Motion/Time**: Temporal flow, speed changes, duration markers
6. **Guardrails**: What NOT to do (negative prompt handles most of this)

### Show, Don't Tell

Describe **physical movements** instead of emotional labels.

| Bad (emotional label) | Good (physical movement) |
|----------------------|--------------------------|
| "She is nervous" | "Her fingers drum against the book cover, knuckles whitening" |
| "He looks suspicious" | "His eyes narrow, chin drops, shoulders angle toward the door" |
| "The scene is tense" | "Both figures freeze mid-step, the only motion is dust drifting through lamplight" |

### Temporal Flow and Connectors

Use words like **"then," "as," "slowly," "suddenly," "meanwhile"** to connect actions into a smooth continuous flow. Without these, LTX-2 may render all described actions simultaneously rather than sequentially.

**Bad**: "A woman runs. Birds fly. The flag waves."
**Good**: "A woman breaks into a sprint along the wall, then as she reaches the corner, a flock of birds bursts upward from the palm tree while the flag above snaps hard in a sudden gust."

### Camera and Lens Language

Use specific cinematography terms to control camera behavior:

| Term | Effect |
|------|--------|
| `slow pan left` | Horizontal camera sweep |
| `dolly in` / `push in` | Camera physically moves closer |
| `low angle` | Camera below subject looking up |
| `tracking shot` | Camera follows subject movement |
| `static camera` | Locked-off, no camera movement |
| `85mm` / `35mm` | Focal length (tighter vs wider) |
| `shallow depth of field` | Background blur |
| `rack focus` | Shift focus between foreground/background |

### Audio-Video Sync

Describe audio events alongside visual actions to improve temporal coherence:
- "Steam bursts from the pipe as she ducks beneath it"
- "The door slams shut and she flinches at the sound"
- "Waves crash against stone in rhythm with her footsteps"

### Composition and Realism Tips

1. **Start with close-ups, move outward**: Beginning a scene on a tight framing enhances character/material consistency. Wider shots can reduce likeness fidelity.

2. **Avoid complex physics**: Don't ask for non-linear or chaotic movements (juggling, swirling liquids, complex particle effects). These create artifacts. Stick to natural, linear motion paths.

3. **Environmental detail matters**: Describe lighting, textures, and atmospheric effects explicitly — "soft rim light catches the edge of her jaw," "mist clings to the stone floor," "golden hour warmth on weathered wood."

4. **Limit scene complexity**: Fewer characters and objects = better results. One or two subjects maximum. Background crowds will degrade.

### Element Auto-Remapping (Kling)

`@ElementN` in prompts references the Nth element in the `elements` array (1-indexed). When only a subset of elements is sent for a particular clip, the indexing must be remapped. For example, if only `@Element2` character appears in a clip, it must be referenced as `@Element1` in the prompt since it's the 1st (and only) element sent.

`fal_api.py` handles this remapping automatically — but be aware of it when debugging prompt/element mismatches.

### Metadata Discipline

**Always save full prompts in JSON metadata — never truncate.** The `prompt[:200]` truncation bug has been caught twice in production. Full prompts are essential for:
- Debugging generation failures
- Reproducing specific results
- Comparing prompt variations

### LTX-2 vs Kling Prompt Translation

When the Generator simplifies a Kling prompt for LTX-2, it:
- Strips `@ElementN` tags (no element system)
- Removes `CUT to:` prefixes (no multi-prompt cuts)
- Strips timecode markers `[0:00-0:03]` (harmless but noisy)
- Concatenates multi-prompt entries with ". " separator

**But automatic simplification isn't enough for best results.** When specifically targeting LTX-2, rewrite prompts to follow the narrative paragraph structure above rather than relying on auto-simplified Kling prompts.

### LTX-2 Known Limitations

| Limitation | Workaround |
|-----------|------------|
| No character identity sheets | Rely on start frame for character appearance |
| No multi-prompt (cut within clip) | Write single continuous paragraph with temporal connectors |
| No audio generation | Post-production audio or accept silent clips |
| Max ~10s (257 frames) | Keep clips under 10s; split longer sequences |
| Reduced likeness on wide shots | Start tight, pull out; or accept lower consistency |
| Complex physics = artifacts | Simplify motion, avoid chaotic movements |
| ALL CAPS words mispronounced | Never use ALL CAPS in dialogue — LTX-2 tokenizes them differently and produces garbled speech (e.g. "MAP" → "May-Ape"). Use lowercase or title case only |

---

## Version History

- **2026-02-05**: Dialogue control phrasing update
  - Changed from "no spoken dialogue" to "No talking, characters are silent"
  - More effective at preventing Kling from inventing nonsense dialogue

- **2026-02-05**: Agentic Clip Generation Loop (non-deterministic workflow)
  - Clips generated ONE AT A TIME with Claude review after each
  - Last frame extraction and review before proceeding to next clip
  - Real-time prompt adjustment based on actual generated output
  - Workflow is adaptive loop, NOT batch process

- **2026-02-05**: Multi-Prompt Alignment Rule added (SC02 clip03 issue)
  - First prompt MUST align with start frame image
  - Element reference images are for supplemental consistency, NOT first prompt content
  - Documented common mistake: start frame shows X, first prompt describes Y

- **2026-02-05**: Major update based on SC02 production test iterations
  - Added Frame Validation Gate (Claude reviews frames before clips)
  - Added End-of-Clip Continuity Review workflow
  - Added Start Frame Awareness section (prompts must continue from visible state)
  - Added Shot-Specific Reference Images guidance
  - Added Start Frame Strategy (shot vs last_frame decision tree)
  - Documented single moment rule (no transitional language in frame prompts)

- **2026-02-05**: Initial version based on SC02 production learnings
  - Pacing principles
  - Dialogue control (prevent invented speech)
  - Sound direction guidance
  - Explicit direction templates

- **2026-02-09**: LTX-2 / ComfyUI Backend Prompting Guide
  - Added "Complete Story" narrative prompting approach for LTX-2
  - Six-part prompt structure: Scene, Subject/Action, Camera/Lens, Style, Motion/Time, Guardrails
  - Show Don't Tell: physical movements over emotional labels
  - Temporal connectors for sequential action flow
  - Camera/lens language reference table
  - Composition tips: start tight, avoid complex physics, limit scene complexity
  - Known limitations and workarounds

- **2026-02-06**: Scene Type Production Guide (SC03 debrief)
  - Added dialogue scene production rules: fewer clips, longer durations, restricted shot repertoire
  - Added clip count and duration targets per scene type
  - Added frame reuse strategy with Nano Banana Pro
  - SC03 retrospective: 25 shots / 18 clips was over-produced for dialogue; target is 6-8 clips
  - Added clip count heuristic: dialogue = duration/10, action = duration/5
