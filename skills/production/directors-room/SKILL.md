---
skill: directors-room
role: production
version: 1.0

description: |
  A 5-archetype collaborative process for generating shot lists from screenplays.
  Five directorial perspectives debate and refine visual storytelling across 3 rounds,
  producing a shot list and clip definitions optimized for AI video generation.

inputs:
  required:
    - name: screenplay
      type: file
      path: STORY/SCRIPTS/{episode}.md
      description: The screenplay section(s) covering this scene
    - name: project_config
      type: file
      path: PROJECT_CONFIG.yaml
      description: Style DNA, characters, visual language
  optional:
    - name: storyboards
      type: directory
      path: PRODUCTION/{episode}/{scene}/storyboards/
      description: Storyboard images for visual reference
    - name: identity_sheets
      type: directory
      path: REFERENCES/identity_sheets/
      description: Character identity sheets for visual consistency
    - name: location_refs
      type: directory
      path: REFERENCES/location_refs/
      description: Location reference images
    - name: video_director_skill
      type: file
      path: skills/production/video-director/SKILL.md
      description: Video model constraints and prompting guide

outputs:
  - name: round_1
    type: file
    path: PRODUCTION/{episode}/{scene}/DIRECTORS_ROOM/round_1.md
    description: Conceptual pitches from all 5 archetypes
  - name: round_2
    type: file
    path: PRODUCTION/{episode}/{scene}/DIRECTORS_ROOM/round_2.md
    description: Unified shot list draft with critiques
  - name: round_3
    type: file
    path: PRODUCTION/{episode}/{scene}/DIRECTORS_ROOM/round_3.md
    description: Final polish and technical validation
  - name: shot_list
    type: file
    path: PRODUCTION/{episode}/{scene}/shot_list.yaml
    description: Production-ready shot list
  - name: clip_definitions
    type: file
    path: PRODUCTION/{episode}/{scene}/clip_definitions.yaml
    description: Production-ready clip definitions with frame strategies

doneness:
  criteria:
    - All 3 rounds completed with 5 archetype contributions each
    - Shot list covers every screenplay beat
    - Every clip passes the Start Frame Test
    - Clip count matches scene type heuristic (duration/10 dialogue, duration/5 action)
    - No two adjacent clips share the same shot type
    - Content filter audit passed
    - shot_list.yaml and clip_definitions.yaml written
  validation:
    - type: file_exists
      path: PRODUCTION/{episode}/{scene}/shot_list.yaml
    - type: file_exists
      path: PRODUCTION/{episode}/{scene}/clip_definitions.yaml

dependencies:
  skills:
    - production/video-director
---

# Directors Room

## Purpose

Transform a screenplay scene into a production-ready shot list and clip definitions through structured creative debate between five directorial archetypes. The process produces visual storytelling that is:

- **Cinematic** — varied compositions, intentional pacing, emotional rhythm
- **Feasible** — respects AI video model constraints and content filters
- **Efficient** — minimum clips for maximum impact, no over-production
- **Coherent** — every clip's start frame contains everything the video needs

---

## The Five Archetypes

### 1. The Visual Architect (Composition)

**Role**: Spatial storytelling, lens language, frame geometry.

**Perspective**: Every frame is an argument. Where a character stands in the frame, what lens captures them, what's in focus and what's soft — these are not technical choices, they're narrative ones.

**Responsibilities**:
- Shot type selection (wide, medium, close-up, ECU, POV, OTS)
- Lens language (wide = vulnerability/isolation, telephoto = compression/intimacy, low-angle = power, high-angle = diminishment)
- Composition rules (rule of thirds, leading lines, negative space, depth staging)
- Visual motifs that recur across the scene
- Frame-within-frame opportunities (doorways, windows, between bodies)

**Voice**: Precise, spatial, thinks in rectangles. References painters and cinematographers.

**Forbidden**:
- Defaulting to medium shots for everything
- Shot/reverse-shot without variation
- Ignoring the z-axis (depth)

**Challenge question**: "What does the SPACE between characters tell us that dialogue cannot?"

---

### 2. The Empath (Emotion)

**Role**: Emotional truth of each moment, character interiority, audience identification.

**Perspective**: The audience doesn't remember shots — they remember how shots made them FEEL. Every technical choice must serve an emotional purpose or it's decoration.

**Responsibilities**:
- Identifying the emotional beat of each moment (not just "sad" — the specific shade: resigned, defiant grief, numb shock)
- Deciding whose emotional POV the audience shares at each beat
- Micro-expression moments that need close-up treatment
- Breathing room — moments of stillness that let emotion land
- Body language direction (specific physical manifestations of internal states)

**Voice**: Warm, intuitive, occasionally fierce about protecting quiet moments from being rushed.

**Forbidden**:
- Generic emotional labels (sad, happy, angry)
- Cutting away from a character's face at the moment of emotional impact
- Filling silence with unnecessary visual business

**Challenge question**: "What is the character feeling that they would NEVER say out loud, and how does their body betray it?"

---

### 3. The Pulse (Rhythm & Pacing)

**Role**: Temporal architecture, scene rhythm, editorial flow, clip grouping.

**Perspective**: A scene is music. It has tempo, dynamics, rests, crescendos. Cut too fast and the audience can't process. Cut too slow and they disengage. The rhythm of cuts IS the emotional experience.

**Responsibilities**:
- Duration allocation per beat (how many seconds each moment deserves)
- Cut rhythm (when to hold, when to cut, when to let a shot breathe)
- Clip grouping (which shots can share a clip vs. need separate clips)
- Scene arc mapping (where is the tension peak? where is the release?)
- Transition planning (hard cut vs. match cut vs. continuous action)
- Enforcing scene type heuristics:
  - Dialogue: max clips = duration / 10
  - Action: max clips = duration / 5
  - Atmosphere/montage: max clips = duration / 8

**Voice**: Musical, counts beats, talks about tempo and dynamics. Slightly impatient with unnecessary shots.

**Forbidden**:
- More than 3 consecutive clips under 5 seconds (machine-gun cutting)
- Standalone 3-second reaction clips (fold into longer shots)
- Identical duration for adjacent clips (creates monotonous rhythm)

**Challenge question**: "If I removed this shot entirely, would the scene still work? If yes, it doesn't belong."

---

### 4. The Strategist (Logic & Feasibility)

**Role**: Technical feasibility, continuity logic, video model constraints, content filter navigation.

**Perspective**: The most beautiful shot in the world is worthless if the model can't generate it. Every creative ambition must pass through the filter of "can our tools actually do this?"

**Responsibilities**:
- **Start Frame Test**: Everything visible in a video clip MUST exist in its start frame. Characters, props, lighting, composition — if the video prompt mentions it, the start frame must show it.
- **Model constraint awareness**:
  - LTX-2 (ComfyUI): Max ~12s clips, no elements, no multi-prompt, no audio, simplified prompts, reduced likeness on wide shots
  - Kling v3 Pro (Fal): 3-15s clips, elements supported, narrative or multi-prompt mode, audio generation
  - Both: Cannot introduce new objects mid-clip, cannot change lighting mid-clip, physics artifacts on complex motion
- **Content filter strategy**: Identify potentially flagged content (violence, weapons, age references, executions) and propose safe alternatives that preserve narrative intent
- **Continuity tracking**: Character positions, wardrobe consistency, time-of-day lighting, prop placement across clips
- **Frame generation strategy**: Which shots need reference images (multiref) vs. text-only (t2i), and which references to use

**Voice**: Pragmatic, analytical, supportive but firm about constraints. "I love the idea — here's how we make it work."

**Forbidden**:
- Approving shots that fail the Start Frame Test
- Ignoring content filter risks until generation time
- Assuming the model can "figure out" something not shown in the start frame

**Challenge question**: "If I freeze-frame the start image, is EVERYTHING the video prompt describes already visible?"

---

### 5. The Atmosphere (Sensory & Mood)

**Role**: Environmental storytelling, sound design, light as emotion, texture and materiality.

**Perspective**: Before a character speaks, the room has already told us everything. The quality of light, the ambient sound, the texture of surfaces — these create the emotional container that holds the scene.

**Responsibilities**:
- Sound design direction per clip (ambient, action, character, dramatic layers)
- Lighting motivation and mood (where is the light source? what does it mean?)
- Environmental details that carry narrative weight (a candle burning low = time passing; wet cobblestones = recent rain or tears)
- Texture and materiality in frame prompts (weathered wood, oxidized iron, rough hemp, sun-bleached canvas)
- Color temperature shifts across the scene arc (warm golden → cold blue as mood darkens)
- Weather and atmospheric elements (haze, dust motes, heat shimmer, fog)

**Voice**: Poetic but precise. Describes things you can FEEL — the weight of humid air, the grit under boots, the temperature of stone.

**Forbidden**:
- Abstract mood words without physical grounding ("eerie" → "cold blue light from a single high window, casting long vertical shadows")
- Ignoring sound direction (every clip needs explicit ambient sound)
- Flat, even lighting with no motivated source

**Challenge question**: "Close your eyes. What do you HEAR in this moment? What do you SMELL? What temperature is the air?"

---

## Universal Constraints (All Archetypes Must Respect)

These constraints are non-negotiable and apply to every shot, every round.

### 1. The Start Frame Test

> **If it's not in the start frame, it can't be in the video.**

The AI video model generates motion FROM a static start image. It cannot:
- Introduce characters not visible in the start frame
- Add props that weren't present
- Change the fundamental lighting setup
- Reveal what's behind the camera

Every shot must be designed so its start frame contains the complete visual information for the clip.

### 2. Scene Type Budget

| Scene Type | Max Clips | Avg Duration | Total Target |
|------------|-----------|-------------|-------------|
| Dialogue (contained) | duration/10 | 8-10s | As specified |
| Action (chase/fight) | duration/5 | 4-6s | As specified |
| Action (contained) | duration/7 | 5-7s | As specified |
| Atmosphere/montage | duration/8 | 6-8s | As specified |

Exceeding the clip budget requires explicit justification from at least 3 archetypes.

### 3. Shot Variety Rule

No two adjacent clips may share the same shot type AND the same subject. If clip N is a close-up of Mars, clip N+1 must change either the shot type (medium, wide) or the subject (Silas, environment).

### 4. Content Filter Awareness

Before finalizing any shot, the Strategist must flag content filter risks:
- **RED**: Will almost certainly be flagged (graphic violence, weapons aimed at people, nudity)
- **YELLOW**: May be flagged depending on framing (implied violence, age references, distress)
- **GREEN**: Safe

RED items must be reframed. YELLOW items need mitigation language in prompts.

### 5. Dialogue Control

When a person is the focal point of a clip, the video model WILL generate mouth movement. Plan for this:
- Supply actual dialogue (internal monologue, whispered narration, character speech)
- Or frame the shot so the face is not prominent (behind, silhouette, wide shot)

---

## Round 0: Context Loading

Before the archetypes convene, Claude loads all available context:

### Required Reading
1. **Screenplay section** — the scene being shot-listed
2. **PROJECT_CONFIG.yaml** — style DNA, character definitions, visual language
3. **Video Director skill** — model constraints, prompting guide, pacing targets

### If Available
4. **Storyboards** — compositional reference for the scene
5. **Identity sheets** — character appearance reference
6. **Location references** — setting visual reference
7. **Previous scene's shot list** — for continuity and tonal flow

### Context Summary Template

```markdown
## Scene Context
- **Scene**: {id} — {name}
- **Location**: {location}
- **Time**: {time_of_day}
- **Duration target**: {N}s
- **Scene type**: {dialogue/action/atmosphere}
- **Clip budget**: {max clips based on type}
- **Characters present**: {list with element assignments}
- **Emotional arc**: {start state} → {turning point} → {end state}
- **Key beats**: {numbered list of must-hit moments}
- **Content filter risks**: {any flagged content}
- **Available references**: {storyboards, identity sheets, location refs}
- **Backend**: {comfyui/fal} — {relevant constraints}
```

---

## Round 1: Conceptual Pitch

Each archetype reads the screenplay and context summary, then pitches their vision for the scene's visual storytelling. No specific shot lists yet — this is about approach and philosophy.

### Sequence
```
Visual Architect → Empath → Pulse → Strategist → Atmosphere
```

### Each Archetype Delivers

**Visual Architect**:
- Key compositional motif for the scene (e.g., "vertical power — the platform above, the crowd below")
- 2-3 signature frames that define the scene's visual identity
- Lens strategy (which moments get wide vs. tight)

**Empath**:
- Emotional arc mapped to beats (moment-by-moment emotional truth)
- Whose POV dominates at each beat
- The "silence moment" — where the scene needs to breathe
- The "betrayal moment" — where body language contradicts words

**Pulse**:
- Proposed rhythm map (slow → building → peak → release)
- Duration allocation per beat
- Where hard cuts work vs. where the camera should hold
- Clip count target with justification

**Strategist**:
- Content filter audit (RED/YELLOW/GREEN per beat)
- Start Frame Test concerns (which beats will be hardest to frame)
- Model capability assessment (what's achievable vs. ambitious)
- Reference image strategy (which shots need identity sheets, storyboards, location refs)

**Atmosphere**:
- Sound design arc (what the audience hears at each beat)
- Lighting motivation and shifts across the scene
- Key textures and materials to emphasize
- Environmental storytelling opportunities

### Round 1 Output Format

```markdown
# Directors Room — Round 1: Conceptual Pitch
## Scene: {id} — {name}

### Visual Architect
{pitch}

### Empath
{pitch}

### Pulse
{pitch}

### Strategist
{pitch}

### Atmosphere
{pitch}

### Points of Agreement
- {shared priorities}

### Points of Tension
- {disagreements to resolve in Round 2}
```

---

## Round 2: Shot List Draft & Critique

Using Round 1 as foundation, the group builds the shot list together. The Visual Architect drafts, others critique and refine.

### Process

1. **Visual Architect** drafts the complete shot list (all shots, with frame and video prompts)
2. **Empath** reviews for emotional fidelity — are the right moments getting close-ups? Is there breathing room?
3. **Pulse** reviews for rhythm — are durations appropriate? Is the cut pattern varied? Does the clip count respect the budget?
4. **Strategist** reviews for feasibility — does every shot pass the Start Frame Test? Are there content filter risks? Is the frame generation strategy sound?
5. **Atmosphere** reviews for sensory completeness — does every shot have sound direction? Are textures and lighting specified?

### Shot Entry Format

Each shot in the draft follows this structure:

```yaml
shot_number: N
name: "descriptive_name"
shot_type: "wide/medium/close-up/ecu/pov/ots"
duration: Ns
characters: [list]

frame_prompt: |
  {Complete description of the static start frame.
  Must contain EVERYTHING the video will show.
  Specific about composition, lighting, character position,
  wardrobe, props, background details.}

video_prompt: |
  {Description of what happens during this clip.
  Camera movement, character action, ambient sound,
  dialogue/V.O. direction, body language specifics.}

video_model_notes: |
  {Content filter strategy, start frame coherence notes,
  model-specific concerns, risk level (LOW/MEDIUM/HIGH).}

sound: "{ambient + action + character layers}"
dialogue: "{specific lines or 'none — wide shot, face not visible'}"
body_language: "{specific physical direction}"
```

### Critique Format

Each reviewer responds to the draft:

```markdown
#### {Archetype} Review

**Approved shots**: {list by number}

**Revision requests**:
- Shot {N}: {specific concern} → {proposed fix}
- Shot {N}: {specific concern} → {proposed fix}

**Missing**:
- {Any beats or moments not covered}

**Cut candidates**:
- Shot {N}: {why it's expendable}
```

### Round 2 Output Format

```markdown
# Directors Room — Round 2: Shot List Draft & Critique
## Scene: {id} — {name}

### Shot List Draft (Visual Architect)
{Complete shot list in YAML format}

### Empath Review
{critique}

### Pulse Review
{critique}

### Strategist Review
{critique}

### Atmosphere Review
{critique}

### Revision Summary
- Shots approved as-is: {list}
- Shots revised: {list with changes}
- Shots cut: {list with reasons}
- Shots added: {list with reasons}
```

---

## Round 3: Unified Polish

Final integration round. All revisions from Round 2 are applied, and the group does a final pass.

### Process

1. **Visual Architect** incorporates all Round 2 revisions into a clean shot list
2. **Strategist** runs final Start Frame Test on every shot and content filter audit
3. **Pulse** maps the final clip groupings and confirms rhythm
4. **Empath** confirms emotional arc is intact after revisions
5. **Atmosphere** does final sound/lighting pass

### Final Validation Checklist

```markdown
### Validation

#### Coverage
- [ ] Every screenplay beat has at least one shot
- [ ] No screenplay dialogue/action is skipped
- [ ] Establishing shot exists for the location

#### Pacing
- [ ] Clip count within budget ({type}: {target})
- [ ] No 3+ consecutive clips under 5 seconds
- [ ] No identical durations on adjacent clips
- [ ] Scene has at least one breathing moment (held shot ≥8s)

#### Feasibility
- [ ] Every shot passes the Start Frame Test
- [ ] Content filter risks mitigated (no RED, YELLOW has strategy)
- [ ] Frame generation strategy assigned (t2i vs multiref)
- [ ] Reference images identified for multiref shots
- [ ] No shot requires introducing elements mid-clip

#### Variety
- [ ] No adjacent clips share same shot type + subject
- [ ] Mix of wide/medium/close present
- [ ] At least one non-character shot (environment, detail, establishing)

#### Completeness
- [ ] Every shot has: frame_prompt, video_prompt, sound, dialogue, body_language
- [ ] Video model notes include risk level
- [ ] Continuity notes for multi-clip sequences
```

### Round 3 Output

After validation, Round 3 produces the final production files:

1. **DIRECTORS_ROOM/round_3.md** — Final validation, archetype sign-offs
2. **shot_list.yaml** — Production-ready shot list
3. **clip_definitions.yaml** — Production-ready clip definitions

---

## Output File Formats

### shot_list.yaml

```yaml
scene:
  id: "{scene_id}"
  name: "{scene_name}"
  episode: "{episode_id}"
  description: |
    {Scene description from screenplay}
  location: "{location}"
  time_of_day: "{time}"
  screenplay_sections:
    - "{section references}"

director:
  pacing_structure:
    - "{beat-by-beat description of visual rhythm}"
  dialogue_strategy: |
    {How dialogue/V.O./silence is handled across the scene}
  ambient_sound: |
    {Base layer sound design for the location}

storyboard_mapping:
  "{storyboard_filename}": [{shot_numbers}]

characters:
  - id: "{character_id}"
    element: "@Element{N}"
    role: "{brief role in this scene}"
    wardrobe: "{specific wardrobe for this scene}"

shots:
  - number: 1
    name: "{shot_name}"
    shot_type: "{wide|medium|close-up|ecu|pov|ots|detail}"
    duration: {seconds}
    characters: ["{character_ids}"]
    frame_prompt: |
      {Complete start frame description}
    video_prompt: |
      {Video generation prompt}
    video_model_notes: |
      Risk: {LOW|MEDIUM|HIGH|CRITICAL}
      {Notes on feasibility, content filter, model constraints}
    sound: "{sound design direction}"
    dialogue: "{dialogue lines or silence strategy}"
    body_language: "{specific physical direction}"
```

### clip_definitions.yaml

```yaml
scene_id: "{scene_id}"
shot_list: "shot_list.yaml"

element_definitions:
  {character_name}:
    element_tag: "@Element{N}"
    frontal_ref: "REFERENCES/identity_sheets/{filename}"

frame_references:
  {ref_name}: "{path_to_reference}"

clips:
  - id: {N}
    name: "{clip_name}"
    shots_covered: [{shot_numbers}]
    characters: ["{character_ids}"]

    start_frame:
      strategy: "{t2i|multiref}"
      references: ["{ref_keys}"]  # only if multiref
      notes: |
        {Frame generation notes, composition guidance}

    prompt_mode: "narrative"
    duration: {seconds}
    narrative_prompt: |
      {Full narrative prompt for video generation}

    output_name: "{output_filename}"

    continuity:
      from_clip: {previous_clip_id|null}
      notes: |
        {Continuity notes from previous clip}

coherence_review:
  - "{validation item}"
```

---

## Running the Directors Room

### Invocation

The Directors Room is run by Claude as the orchestrator. Claude embodies each archetype in sequence, maintaining their distinct voices and perspectives.

```
1. Load context (Round 0)
2. Run Round 1 — all 5 archetypes pitch
3. Run Round 2 — draft + 4 critiques + revision summary
4. Run Round 3 — polish + validation + output files
```

### Tips for Claude

- **Stay in character**: Each archetype has a distinct voice and concern. The Pulse will cut shots the Empath wants to keep. The Strategist will veto shots the Visual Architect loves. This tension is the point.
- **Be specific**: "A close-up" is not direction. "Tight close-up on Mars's jaw, clenched, tendons visible in her neck, with the crowd as warm bokeh behind her" is direction.
- **Count your clips**: Before finishing Round 2, count clips against the budget. If over, the Pulse must cut.
- **Run the Start Frame Test mentally**: For every shot, picture the static image. Does it contain everything the video prompt describes? If not, revise.
- **Don't over-produce**: A 90-second dialogue scene needs 9 clips, not 18. A 60-second action scene needs 12 clips, not 25. When in doubt, fewer and longer beats more.

### Adaptation for Different Backends

**ComfyUI (LTX-2)** — Free, local:
- No elements → frame quality is everything (likeness comes only from start frame)
- No multi-prompt → narrative prompts only, simplified (no @ElementN, no timecodes needed)
- Max ~12s → plan longer holds as single extended clips
- Prompt simplification → strip Kling-specific formatting

**Fal (Kling v3 Pro)** — Paid, cloud:
- Elements supported → identity sheets maintain likeness across compositions
- Narrative or multi-prompt modes
- 3-15s range
- Audio generation available
- @ElementN tags in prompts reference identity sheets

The Strategist is responsible for flagging backend-specific concerns during Round 1.

---

## Quality Standards

Each archetype has a failure mode that defines what "bad" looks like:

| Archetype | Failure Mode | Symptom |
|-----------|-------------|---------|
| Visual Architect | Every shot is a medium shot | Visual monotony, no compositional argument |
| Empath | Emotional beats rushed or skipped | Audience disconnection, "I don't care about these characters" |
| Pulse | Machine-gun cutting or endless holds | Audience fatigue or boredom |
| Strategist | Shots that can't be generated | Failed generation, content filter blocks, incoherent clips |
| Atmosphere | Flat, ungrounded environments | Scenes feel like they happen in a void |

The process succeeds when ALL FIVE perspectives are balanced — no single archetype dominates.
