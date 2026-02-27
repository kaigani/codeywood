---
skill: paper-cut
role: production
version: 1.0

description: |
  Generate and review paper cuts — rough assemblies of static images with dialogue
  and direction narration. Paper cuts evaluate directorial decisions (shot selection,
  pacing, dialogue rhythm, story flow) before committing to video generation.

inputs:
  required:
    - name: shot_list
      type: file
      path: PRODUCTION/{episode}/{scene}/shot_list.yaml
      description: Shot list with frame_prompt, video_prompt, and dialogue
  optional:
    - name: frames
      type: directory
      path: PRODUCTION/{episode}/{scene}/frames/
      description: Klein-generated start frames for each shot
    - name: voiceover
      type: directory
      path: PRODUCTION/{episode}/{scene}/voiceover/
      description: Pre-generated TTS dialogue WAVs
    - name: narrator_voice_ref
      type: file
      path: REFERENCES/voice_refs/narrator_voice_ref.wav
      description: Narrator voice reference for direction narration

outputs:
  - name: paper_cut
    type: file
    path: PRODUCTION/{episode}/{scene}/paper_cut.mp4
    description: Assembled paper cut video with images + dialogue + direction
---

# Paper Cut Review

## What Is a Paper Cut?

A paper cut is a rough video assembly where:
- Each shot is a **static image** held for its target duration
- **Character dialogue** (TTS) plays at the correct timing
- **Direction narration** describes intended camera motion and mood in dialogue gaps

It exists to answer: **Are the directorial decisions right?** — before spending hours on video generation.

## When to Generate a Paper Cut

Generate a paper cut:
- After Directors Room completes a shot_list.yaml
- Before any video generation (T2V or I2V)
- When revising shot selection or pacing
- When adding/removing dialogue or changing delivery

## Generation Command

```bash
# Full paper cut with dialogue + direction narration
python3 scripts/production/generate_paper_cut.py \
  --scene PRODUCTION/EP01/sc01 \
  --narrator-voice REFERENCES/voice_refs/narrator_voice_ref.wav

# Dialogue only (no direction narration)
python3 scripts/production/generate_paper_cut.py \
  --scene PRODUCTION/EP01/sc01 --no-direction

# Direction only (skip dialogue — hear only visual intent)
python3 scripts/production/generate_paper_cut.py \
  --scene PRODUCTION/EP01/sc01 --direction-only

# Preflight (show plan without generating)
python3 scripts/production/generate_paper_cut.py \
  --scene PRODUCTION/EP01/sc01 --preflight
```

## Review Protocol

### Step 1: Watch and Listen

Watch the paper cut straight through without pausing. Note your gut reactions:
- Does the pacing feel right?
- Do any shots feel too long or too short?
- Does the dialogue flow naturally between characters?
- Are there awkward silences or overcrowded moments?
- Does the story build to its climax correctly?

### Step 2: Filmstrip Review

Generate a filmstrip of the paper cut:
```bash
python3 scripts/analysis/analyze_clip.py paper_cut.mp4 --quick
```

Check the filmstrip for:
- **Visual variety**: Are compositions varied enough shot-to-shot?
- **Character balance**: Does any character dominate the visual real estate?
- **Contrast at the reveal**: Is there enough visual difference between the setup and payoff?
- **Opening and closing frames**: Do they establish and resolve the visual story?

### Step 3: Shot-by-Shot Evaluation

For each shot, answer:

| Question | Pass / Fail |
|----------|------------|
| Does this shot earn its screen time? | |
| Is the dialogue timed to the visual beat? | |
| Does the direction narration describe achievable camera work? | |
| Is the emotional arc building correctly at this point? | |
| Could this shot be cut without losing story? | |

### Step 4: Sequence Evaluation

**Pacing arc**: Map the shot durations. The rhythm should serve the story:
- Slow → build → impact → resolve (for reveals)
- Quick → quick → hold (for tension release)
- Asymmetric durations — no two adjacent shots should have the same length class

**Dialogue density**: Count spoken seconds vs. silence per shot. Rules of thumb:
- Dialogue scenes: 60-70% spoken, 30-40% breathing room
- Tension scenes: Decrease dialogue as tension increases
- Reveal moments: Silence IS the dialogue

**Tonal coherence**: Do the direction notes describe a consistent visual world? Check for:
- Lighting consistency (same time of day, same mood)
- Camera language consistency (are we using the same framing vocabulary?)
- Sound design consistency (ambient bed, transition sounds)

### Step 5: Directorial Reasoning Check

These questions address the reasoning gap identified in the Gemini analysis comparison:

**Foreshadowing**: Are there subtle visual or audio cues planted in Act 1 that pay off in Act 3? If not, what could be added? Examples:
- A barely perceptible glitch in a character's video feed
- An audio loop that repeats one second too long
- A character briefly staring blankly before snapping back

**Thematic coherence**: Does every shot serve the central idea?
- What is the film ABOUT (not just what happens)?
- Does each shot reinforce or develop the theme?
- Are there shots that advance plot but not theme? Cut or redesign them.

**Intentional uncanniness**: If the AI-generated aesthetic has artifacts (slightly unnatural movement, TTS voice quality), can they serve the story?
- In the Mondays case, the stilted TTS voices foreshadow the reveal that these are not living people
- Lean into artifacts that serve the narrative; fix only those that distract from it

**The "why" behind each cut**: For every transition, articulate why we cut HERE and not 0.5s earlier or later. If you can't articulate it, the cut is wrong.

## Revision Workflow

After review, create revision notes per shot:

```
Shot 3:  KEEP — Barb's timing is perfect, 5s is right
Shot 4:  SHORTEN to 3s — small talk reactions don't need 5s
Shot 7:  REWRITE DIALOGUE — Monica's line is too direct, add hesitation
Shot 11: CUT — this shot doesn't advance story or theme
Shot 14: EXTEND to 12s — the reveal needs more breathing room
Shot 17: REWRITE DIRECTION — add foreshadowing glitch in Dick's video
```

Then update the shot_list.yaml and regenerate the paper cut. This loop should take minutes, not hours.

## Pipeline Position

```
Script → Directors Room → shot_list.yaml
                              ↓
                         PAPER CUT ← ← ← (iterate)
                              ↓
                     Approved? → Video Generation
```

The paper cut loop is fast and cheap:
- Klein frames: ~15s each
- TTS dialogue: ~5s per line
- Assembly: ~25s total
- Full paper cut: ~5 minutes

Video generation is slow and expensive:
- LTX-2 clips: ~90s each
- Kling clips: ~120s each + $0.34/s

Every iteration saved in the paper cut loop saves 10-20 minutes of video generation.
