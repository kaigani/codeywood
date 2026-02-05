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

---

## Integration with Other Skills

- **Prompt Engineer**: Provides technical prompt structure; Director provides pacing/intent
- **Shot List Generator**: Creates shot list; Director reviews for pacing
- **Storyboard**: Visual reference; Director interprets for video timing

## Version History

- **2026-02-05**: Initial version based on SC02 production learnings
  - Pacing principles
  - Dialogue control (prevent invented speech)
  - Sound direction guidance
  - Explicit direction templates
