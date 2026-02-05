# Video Director Skill

## Purpose
Direct AI video generation with cinematic pacing, explicit scene direction, and sound design guidance. This skill ensures video clips feel intentional rather than rushed, with proper establishing moments and breathing room.

## Trigger
When planning video clip sequences, writing multi-prompt video prompts, or reviewing pacing of assembled scenes.

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
no spoken dialogue, only the scrape of metal on stone and her labored breathing,
slow push-in on her hands
```

### 3. DIALOGUE CONTROL: Prevent Invented Speech

**CRITICAL**: Kling and similar models tend to invent nonsense dialogue if not explicitly told otherwise.

**Always include one of**:
- `no spoken dialogue` - Complete silence from character
- `wordless vocalizations only` - Grunts, sighs, gasps allowed
- `[CHARACTER] says '[EXACT DIALOGUE]'` - Specific scripted speech

**Sound Direction Options**:

| Type | Prompt Language |
|------|-----------------|
| Silent character | "no spoken dialogue, silent" |
| Effort sounds | "wordless grunts of effort as she digs" |
| Breathing | "her breathing quickens, no words" |
| Reaction sounds | "sharp intake of breath, no dialogue" |
| Environmental only | "only ambient sounds, no character speech" |
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
no spoken dialogue
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
| Invented dialogue | Character appears to speak nonsense | Add "no spoken dialogue" |
| Confusing action | Character does unexpected things | More explicit body direction |
| Flat audio | Generic ambient sounds | Specific environmental sound direction |
| Jarring cuts | Transitions feel abrupt | Add transition/breathing shots |
| Lost geography | Viewer confused about location | More establishing shots |

## Example: SC02 Revision Notes

Original issue: Scene felt rushed, needed more establishing and breathing room.

**Revision approach**:
1. Add exterior establishing shot of compound at dusk (3s)
2. Add detail shot of hands on wall before climbing (2s)
3. Add corridor atmosphere shot before Mars enters frame (3s)
4. Add close-up on her face as she scans the cell (2s)
5. Add detail shot on the blade working the mortar (3s)
6. All prompts include "no spoken dialogue" or specific sounds

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

## Agentic Workflow Implementation

**How Claude executes the agentic clip generation loop:**

### Step-by-Step Execution Pattern

```bash
# For each clip in sequence:

# 1. Generate single clip
python3 scripts/production/generate_clips.py --clip-def sc02_clips.yaml --clip 1

# 2. Extract last frame for review
ffmpeg -sseof -0.1 -i clips/sc02_clip01.mp4 -frames:v 1 clips/clip01_last_frame.png

# 3. Claude reads and reviews the last frame
# (Use Read tool on the extracted frame)

# 4. Claude assesses alignment with next clip
# - Read next clip's planned start frame
# - Compare to actual ending state
# - Decide: proceed / adjust / bridge / use last_frame

# 5. If adjustments needed, update clip definition
# (Use Edit tool on sc02_clips.yaml)

# 6. Proceed to next clip
python3 scripts/production/generate_clips.py --clip-def sc02_clips.yaml --clip 2
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

## Version History

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
