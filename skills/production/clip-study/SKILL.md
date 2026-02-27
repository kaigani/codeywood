---
skill: clip-study
role: production
version: 1.0

description: |
  The feedback loop skill. Drop a reference clip, analyze it, attempt to
  replicate it, compare results, and record learnings. This is how the
  system learns post-production craft from real examples.

inputs:
  required:
    - name: reference_clip
      type: file
      description: A video clip to study (can be a final cut, a single shot, or a sequence)
  optional:
    - name: source_clips
      type: directory
      description: Original source clips (if studying an edit, these are the raw clips before editing)
    - name: previous_learnings
      type: directory
      path: sandbox/clip_study/learnings/
      description: Previous study learnings for building on past insights

outputs:
  - name: analysis
    type: directory
    description: Full analysis artifacts (filmstrip, color, motion, audio, cuts)
  - name: study_document
    type: file
    description: Structured analysis of what makes the reference work
  - name: attempt
    type: directory
    description: Replication attempt with comparison
  - name: learnings
    type: file
    description: Recorded findings for persistent memory

tools:
  - scripts/analysis/analyze_clip.py
  - scripts/analysis/compare_clips.py
  - scripts/lib/video_analysis.py
  - scripts/lib/audio_analysis.py
  - scripts/lib/scene_detect.py (detect_cuts, shot_breakdown)
  - scripts/editing/smart_assemble.py
  - scripts/editing/trim_clip.py

doneness:
  criteria:
    - Reference fully analyzed (filmstrip, metadata, cuts, color, motion, audio)
    - Study document written with structured observations
    - At least one replication attempt made
    - Comparison run between reference and attempt
    - Learnings document written and saved to persistent memory
---

# Clip Study — The Feedback Loop

## Purpose

Learn post-production craft by studying reference clips. This is deliberate practice for editorial skills — observe, understand, attempt, compare, record.

---

## The 5-Step Protocol

### Step 1: OBSERVE

Run full analysis on the reference clip.

```bash
# Full analysis — filmstrip, color, motion, audio, silence
python3 scripts/analysis/analyze_clip.py REFERENCE

# If the reference is an edited sequence, also detect cuts
python3 -c "
from scripts.lib.scene_detect import shot_breakdown
shot_breakdown('REFERENCE', 'analysis/reference/shots/')
"
```

**Collect**:
- `filmstrip.png` — the visual summary
- `metadata.json` — technical specs (resolution, fps, duration, codecs)
- `color_palette.png` + `color_palette.json` — color language
- `motion_chart.png` + `motion.json` — energy timeline
- `waveform.png` — audio shape
- `silence.json` — dialogue windows and pauses
- `breakdown.json` — shot list with timecodes (if multi-shot)

### Step 2: UNDERSTAND

Write a structured analysis document. Read the filmstrip and all artifacts, then answer:

```markdown
# Study: {name}

## Technical Profile
- Duration: {Xs}
- Resolution: {WxH} @ {fps}fps
- Shots: {N} (from cut detection)
- Avg shot duration: {X}s
- Audio: {description}

## Shot Breakdown
For each detected shot:
| # | Timecode | Duration | Type | Subject | Motion | Notes |
|---|----------|----------|------|---------|--------|-------|
| 1 | 00:00.0  | 3.2s     | Wide | Office  | Static | Establishing shot |
| 2 | 00:03.2  | 2.8s     | CU   | Person A| Slight | Reaction |

## Visual Language
- Color palette: {warm/cool/neutral, dominant colors}
- Lighting: {direction, quality, mood}
- Composition patterns: {rule of thirds, centered, dynamic}
- Texture: {film grain, clean, stylized}

## Editorial Decisions
- Pacing: {rhythm description — fast/slow/varied}
- Cut types: {hard cuts, crossfades, L-cuts}
- Longest hold: {X}s — why does it work?
- Fastest sequence: {X}s avg — what creates the energy?
- Transitions: {what transitions are used and why}

## Audio Design
- Ambient bed: {description}
- Dialogue: {present/absent, style}
- Music: {present/absent, role}
- Dynamic range: {quiet→loud moments}

## What Makes It Work
1. {Key insight about why this edit is effective}
2. {Key insight}
3. {Key insight}

## What Could Be Replicated
- {Achievable with current tools}
- {Achievable with current tools}

## What's Beyond Current Tools
- {Would need X capability}
- {Would need X capability}
```

### Step 3: ATTEMPT

Using the analysis, attempt to replicate the editorial approach.

**If source clips are available** (e.g., studying our own final cut vs. rough cut):
1. Use the shot breakdown to determine where to cut
2. Write an EDL YAML matching the detected cut points
3. Apply trim amounts based on the reference's timing
4. Execute with `smart_assemble.py`

**If only the reference exists** (studying external footage):
1. Design a shot list inspired by the reference's structure
2. Generate clips using T2V/I2V with prompts derived from the filmstrip
3. Trim and assemble to match the reference's rhythm

### Step 4: COMPARE

Run side-by-side comparison:

```bash
python3 scripts/analysis/compare_clips.py REFERENCE ATTEMPT --output comparison/
```

**Review**:
- `dual_filmstrip.png` — visual comparison (reference top, attempt bottom)
- `color_comparison.png` — color palette match
- `motion_overlay.png` — energy curves overlaid
- `diff_report.json` — structured comparison data

**Key questions**:
- Does the attempt capture the same rhythm? (Compare motion charts)
- Does the color palette match? (Compare color analysis)
- Does the duration ratio feel right? (Compare timing)
- What's the biggest gap between reference and attempt?

### Step 5: RECORD

Write a learnings document and save to persistent memory.

```markdown
# Learnings: {study_name}
Date: {YYYY-MM-DD}
Reference: {file path or description}

## What Worked
- {Technique that successfully replicated}
- {Tool that performed well}

## What Failed
- {Approach that didn't work and why}
- {Limitation discovered}

## Prompt Techniques Discovered
- {New prompting approach learned from studying the reference}

## Editing Techniques Discovered
- {New trim/transition pattern that works}
- {Pacing insight}

## Updated Heuristics
- {Revised rule-of-thumb based on this study}
- {e.g., "Trim AI clip tails by 0.8s, not 0.5s, for 12s+ clips"}

## Tools Needed
- {Any capability gaps identified}
```

Save to `sandbox/clip_study/learnings/{study_name}.md` and persist key findings to memory with `[CODEYWOOD-clip-study]` tag.

---

## Workspace Structure

```
sandbox/clip_study/
  reference/                    # Drop reference clips here
  analysis/{study_name}/        # Analysis artifacts
  attempts/{study_name}/        # Replication attempts
    attempt_01/
      edl.yaml                  # Edit decision list
      clips/                    # Trimmed/generated clips
      assembly.mp4              # Assembled attempt
      comparison/               # vs. reference comparison
    attempt_02/                 # Iterate
      ...
  learnings/{study_name}.md     # Recorded findings
```

---

## Study Types

### Type A: Edit Study (have source + final)
The ideal case — we have both the raw clips AND a human-edited final cut.

**Goal**: Understand what the human editor chose to do.
**Method**: Analyze the final cut to detect cuts. Map those cuts back to the source clips. See what was trimmed, what was reordered, what was dropped entirely.
**Output**: An EDL that approximates the human's edit, plus insights about editorial craft.

### Type B: Style Study (reference only)
We have a finished clip/film but not the sources.

**Goal**: Understand the visual language and pacing.
**Method**: Analyze the reference for shot structure, color, motion, audio. Attempt to replicate the style with AI-generated clips.
**Output**: Prompt techniques and editing patterns that produce similar results.

### Type C: Technique Study (focused element)
Studying a specific technique: a transition, a color grade, a pacing pattern.

**Goal**: Isolate and replicate one specific editorial technique.
**Method**: Find examples in reference material. Analyze the technique. Practice it with test clips.
**Output**: A reusable technique pattern documented in the learnings.

---

## Memory Integration

After each study, key findings should be saved to persistent memory:

```
Tag: [CODEYWOOD-clip-study]
Content: Structured learnings from the study
```

Before starting a new study, search for previous learnings:
```
Search: [CODEYWOOD-clip-study] {relevant topic}
```

This creates a growing knowledge base of editorial craft that improves with each study cycle.
