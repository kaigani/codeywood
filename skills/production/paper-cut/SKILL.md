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

## Writing Direction Narration

Direction narration fills silence gaps in the paper cut — the moments between dialogue where the image is static but the story continues. It is **not** a screenplay description or video prompt. It is a sparse, spoken layer that tells the audience what they would see and hear if the film were fully produced.

### What to Include

| Category | Example |
|----------|---------|
| **Sound effects** | "Coffee maker gurgles to life." |
| **Camera cues** | "Wide shot, static camera." |
| **Essential blocking** | "She sits on the floor next to Koda's station." |
| **Story-significant details** | "Her phone screen glows. Subject line: KODA-7 Firmware Recall." |
| **Emotional beats** | "The longest pause. The display cuts out completely." |

### What to Exclude

- Full scene descriptions (that's the video prompt's job)
- Character thoughts or inner monologue
- Dialogue paraphrasing ("she says something about...")
- Technical camera specs ("24mm lens, f/2.8")
- Anything the dialogue already communicates

### Word Count Targets

| Shot Type | Target | Rationale |
|-----------|--------|-----------|
| Detail/insert shot (3-5s) | 8-15 words | Just enough to name what we see |
| Medium shot with action (6-10s) | 15-25 words | One or two beats of blocking |
| Emotional hold (10-18s) | 25-40 words | Build atmosphere, describe the silence |
| No dialogue at all | Full gap | Narration is the only audio layer |
| Dialogue + trailing gap | Gap words only | Fill the silence after lines end |

### The Density Rule

**Sparse > thorough.** A paper cut with narration on every shot becomes an audiobook. Target narration on 40-60% of shots — specifically those with silence gaps > 2 seconds. Shots where dialogue fills the duration need no narration.

### The `direction` Field in shot_list.yaml

Write direction narration directly in the shot list's `direction` field. This is distinct from `video_prompt` (which instructs the video model) and `frame_prompt` (which instructs the image model):

```yaml
- id: 5
  duration: 10
  frame_prompt: "Medium shot of woman at kitchen table with coffee..."
  video_prompt: "Static camera, warm morning light, woman sips coffee..."
  direction: "She takes her mug — the ceramic one with the chipped handle — and sits at the kitchen table."
  sound: "Coffee cup set down on wood. Chair scrape."
```

The `direction` field is written for the narrator's voice. The `sound` field adds environmental cues. Both feed into the paper cut's direction narration layer.

---

## Pre-Generated Direction Audio

For better quality and faster iteration, pre-generate direction narration WAVs before building the paper cut.

### Workflow

1. **Write sparse narration cues** — a Python dict or YAML mapping `scene → shot_id → text`
2. **Batch-generate via TTS** — submit all cues to the ComfyUI `qwen3-tts-voiceclone` workflow with the narrator voice reference
3. **Save to `direction/` directory** — `PRODUCTION/{episode}/{scene}/direction/dir_{shot:02d}.wav`
4. **Paper cut auto-discovers** — the script checks `direction/` before attempting real-time TTS

### Naming Convention

```
PRODUCTION/EP01/sc01/direction/
├── dir_01.wav    ← shot 1 narration
├── dir_03.wav    ← shot 3 narration (shot 2 has dialogue, no narration needed)
├── dir_05.wav    ← shot 5 narration
└── ...
```

### Why Pre-Generate?

- **Quality control**: Listen to each narration before assembling. Re-generate any that sound wrong.
- **Speed**: Paper cut assembly takes ~25s when audio is pre-generated vs. minutes with real-time TTS.
- **No API dependency**: Paper cut builds offline once WAVs exist.
- **Iteration**: Can regenerate the paper cut dozens of times without re-hitting TTS.

---

## VO Sizing: Shot Duration vs. Dialogue

A shot must be long enough to hold all its dialogue with breathing room. If it isn't, lines get silently dropped and the paper cut is incomplete.

### The Rule

```
minimum_shot_duration = sum(all_vo_durations) + (num_lines × 0.3s gap) + 0.5s pre-offset + 1.0s buffer
```

### Practical Sizing

| Dialogue Lines | Typical VO Duration | Minimum Shot Duration |
|---------------|--------------------|-----------------------|
| 1-2 short lines | 2-4s | 5-6s |
| 2-4 exchanges | 6-12s | 10-15s |
| Long speech (1 character) | 8-12s | 12-15s |
| Dense back-and-forth (6+ lines) | 15-25s | 18-28s |

### When Shots Overflow

Symptoms: Paper cut output says "Mixing N audio track(s)" but some lines are missing when you listen. The `schedule_dialogue()` function breaks when `current_time + wav_dur > shot_duration`.

Fix: Extend the shot's `duration` in shot_list.yaml. Always check after generating voiceover — VO duration is unpredictable until the TTS actually generates the WAV.

### Post-VO Duration Audit

After generating voiceover, audit timing before building the paper cut:

```bash
# Check VO durations for a scene
for f in PRODUCTION/EP01/sc01/voiceover/*.wav; do
  dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f")
  echo "$(basename $f): ${dur}s"
done
```

Sum VO durations per shot and compare against shot duration. Extend any shot where total VO + gaps exceeds the allocated time.

---

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
