---
skill: editor
role: post-production
version: 1.0

description: |
  Film editor cognitive skill. Teaches Claude to think like an editor —
  when to cut, what to trim, how to build rhythm, and how to review
  assembled footage using filmstrip analysis.

inputs:
  required:
    - name: clips
      type: directory
      description: Directory containing video clips to review/edit
  optional:
    - name: filmstrip
      type: file
      description: Pre-generated filmstrip PNG for faster review
    - name: reference_cut
      type: file
      description: Reference edit to compare against
    - name: shot_list
      type: file
      path: PRODUCTION/{episode}/{scene}/shot_list.yaml
      description: Original shot list for intent reference

outputs:
  - name: edl
    type: file
    description: Edit Decision List YAML for smart_assemble.py
  - name: review_notes
    type: file
    description: Per-clip review notes with trim/keep/redo decisions

tools:
  - scripts/analysis/analyze_clip.py
  - scripts/analysis/compare_clips.py
  - scripts/editing/trim_clip.py
  - scripts/editing/smart_assemble.py
  - scripts/editing/transition.py
  - scripts/lib/ffmpeg.py (trim_clip, crossfade_transition, l_cut, j_cut, speed_ramp)
  - scripts/lib/video_analysis.py (extract_filmstrip, probe_metadata)
---

# Film Editor

## Purpose

Transform raw AI-generated clips into a cohesive, well-paced sequence through editorial decisions: what to keep, what to trim, what to re-order, what transitions to use, and when to request a re-generation.

---

## Core Principle: See Before You Cut

**Never make editing decisions without first generating a filmstrip.**

```
analyze_clip.py CLIP --quick    → filmstrip + metadata for one clip
analyze_clip.py ASSEMBLY        → filmstrip of current assembly
compare_clips.py REF ASSEMBLY   → side-by-side with reference
```

The filmstrip is your editing bay. Read it frame by frame. Identify:
- Where the "good stuff" starts (usually 0.3-0.5s in)
- Where degradation begins (usually last 0.5-1.0s)
- Whether the shot composition matches the shot list intent
- Whether motion is present where expected

---

## The Three Cuts

Every edit point is one of these three:

### 1. Too Early
The cut happens before the action/emotion has landed. The audience feels jerked away.

**Symptoms**: Shot feels rushed, character expression not fully formed, action incomplete.
**Fix**: Extend the trim_out (let it breathe).

### 2. Too Late
The cut happens after the energy has drained. The audience has already moved on mentally.

**Symptoms**: Lingering on a static frame, repeated motion loops, AI degradation artifacts visible.
**Fix**: Trim more from the tail. AI clips almost always need 0.5-1.0s trimmed from tail.

### 3. Just Right
The cut happens at the peak of energy or at a natural pause point.

**Where to cut**:
- On action: Mid-gesture (hand reaching, head turning, body rising) — the audience's brain completes the motion
- On stillness: After a beat of held emotion (a look, a breath, a moment of recognition)
- On dialogue: At the end of a phrase, not mid-word
- On music: On the beat or on the downbeat

---

## AI Clip Trim Heuristics

AI-generated clips have consistent patterns that differ from live-action footage:

### Head Trim (first 0.3-0.5s)
- Model "settling in" — slight jitter or morphing as generation stabilizes
- Character may be slightly off-model before identity locks in
- Camera position may drift before stabilizing
- **Default head trim: 0.3s** (increase to 0.5s if visible settling)

### Tail Trim (last 0.5-1.5s)
- Progressive quality degradation (loss of detail, color shift)
- Motion becoming repetitive or looping
- Unintended camera drift
- Character features softening or distorting
- **Default tail trim: 0.5s** (increase to 1.0-1.5s for longer clips >10s)

### When to Trim vs. Regenerate

| Symptom | Action |
|---------|--------|
| Good composition, minor head/tail artifacts | **Trim** |
| Correct action but slightly wrong framing | **Trim + speed ramp** |
| Wrong character appearance | **Regenerate** (identity issue) |
| Wrong action/motion direction | **Regenerate** (prompt issue) |
| AI artifacts throughout (not just edges) | **Regenerate** (model limitation) |
| Good first 60%, degraded last 40% | **Trim aggressively** — keep the good part |
| Perfect 3s inside an 8s clip | **Trim** to the perfect 3s, adjust EDL |

---

## Rhythm and Pacing

### Production Pacing Targets

These targets produce confident, breathing pacing — not the anxious rapid-cutting that hides AI artifacts:

| Metric | Target | Anti-Pattern |
|--------|--------|-------------|
| Shots per minute | 6-8 | 14+ (anxiety cutting) |
| Median shot duration | 8-10s | 3s (nothing breathes) |
| Face close-up ratio | <30% of shots | 65%+ (concentrates artifacts in worst zone) |
| Minimum shot duration | 4s | Sub-2s cuts (except deliberate rhythmic effect) |
| Dramatic silences | 4-6 per 5 min | 0 (missing free storytelling beats) |

Longer holds signal confidence. Short cuts signal "don't look closely."

### The Rhythm Grid

Map out your intended rhythm before assembling:

```
[SLOW — 8s] [FAST — 3s] [FAST — 4s] [SLOW — 10s] [MED — 6s]
  establish    action      action      emotional     resolve
```

### Scene Type Rhythms

**Dialogue Scene**:
- Establish (wide, 8-10s) → Shot/reverse-shot (6-8s each) → Close-up reaction (5-6s) → Return to wide (6-8s)
- Use L-cuts for natural conversation flow (audio leads video by 0.5-1.0s)
- Total clips: scene_duration / 10

**Action Scene**:
- Build (medium, 5-6s) → Accelerate (3-4s clips) → Peak (2-3s) → Impact (held 6-8s) → Aftermath (8s)
- Hard cuts throughout, speed ramps on impacts
- Total clips: scene_duration / 5

**Atmosphere/Montage**:
- Long holds (8-12s) with crossfades (1.0-1.5s)
- Minimal cuts — let the mood build
- Total clips: scene_duration / 8

### Syncopation
Break rhythmic expectations intentionally:
- Three fast cuts followed by one long hold = tension release
- Two long holds followed by a sudden fast cut = surprise
- Alternating short/long = heartbeat rhythm

---

## Transition Guide

| Transition | Effect | Best For |
|-----------|--------|----------|
| **Hard cut** | Sharp, immediate | Action, dialogue, time jumps |
| **Crossfade** (0.5-1.5s) | Gradual blend | Time passage, mood shifts, montage |
| **L-cut** | Audio leads video | Dialogue (hear next speaker before seeing them) |
| **J-cut** | Video leads audio | Reveals (see location before hearing narration) |
| **Speed ramp** | Time manipulation | Impacts, establishing shots, transitions |

### When NOT to use transitions:
- Crossfade between two dialogue close-ups (disorienting)
- L/J-cut when there's no meaningful audio difference
- Speed ramp on a static shot (nothing to ramp)

---

## Assembly Best Practices

### Single-Pass Concat

**Never use pairwise concatenation** (`concat(A, concat(B, concat(C, ...)))`) for more than a few clips. Iterating pairwise across 17+ clips produces progressive quality degradation and unreadable output.

**Always use single-pass concat with a file list**: trim all clips, re-encode to uniform H.264/AAC, then concatenate in one ffmpeg pass.

### trim_and_reencode()

Combined trim + re-encode in one ffmpeg pass avoids intermediate format issues. Default behavior: keep audio (`-c:a aac`), retry with `-an` on failure.

### Stream Count Consistency

The concat demuxer maps streams from the first file. If file 1 has no audio track, ALL subsequent audio is silently dropped.

**Rule**: Ensure uniform stream layout before concat. Use `add_silent_audio()` for any clips that lack an audio track.

### Audio Track Requirement

ALL clips need audio tracks for concat — even silent ones. Use `add_silent_audio()` to add a silent AAC track to clips with no dialogue or ambient sound. This prevents the concat demuxer from dropping audio from all subsequent clips.

---

## Review Protocol

### Per-Clip Review

For each clip, evaluate:

1. **Intent match**: Does this deliver what the shot list requested?
2. **Composition**: Is the framing effective? Subject placement?
3. **Motion quality**: Is movement natural? Any loops/artifacts?
4. **Identity**: Do characters look correct? Consistent with refs?
5. **Technical**: Resolution, color, exposure acceptable?

Rating: **KEEP** / **TRIM** (specify head/tail amounts) / **REDO** (specify what's wrong)

### Sequence Continuity Check

After individual review, check across the sequence:

1. **Eye-line match**: Do characters look in consistent directions between cuts?
2. **Position continuity**: Does a character's screen position make spatial sense across cuts?
3. **Color consistency**: Major shifts in color temperature between adjacent clips?
4. **Scale jumps**: Avoid cutting from ECU to wide — step through medium
5. **Motion continuity**: If action carries across a cut, does direction match?

### EDL Drafting

After review, produce the EDL YAML:

```yaml
output: assembly_v2.mp4
clips:
  - path: clip_001.mp4
    trim_in_s: 0.3        # Default head trim
    trim_out_s: 0.5        # Default tail trim
    transition_out: hard_cut
    # Review: KEEP — good establishing shot, trim settling

  - path: clip_002.mp4
    trim_in_s: 0.0
    trim_out_s: 1.0        # Heavy tail trim — degradation at 7s
    transition_out: crossfade
    transition_duration: 0.8
    # Review: TRIM — good first 7s, crossfade into mood shift

  - path: clip_003.mp4
    trim_in_s: 0.5
    trim_out_s: 0.5
    transition_out: l_cut
    audio_lead_s: 1.0
    # Review: KEEP — strong close-up, L-cut into dialogue
```

---

## Common Mistakes

1. **Over-cutting**: Too many clips for the scene type. A dialogue scene with 15 clips is almost always wrong.
2. **Under-trimming**: Leaving AI artifacts at head/tail because "it's mostly fine."
3. **Monotonous rhythm**: Every clip the same duration. Vary it.
4. **Transition abuse**: Crossfading everything. Most cuts should be hard cuts.
5. **Ignoring audio**: Cutting on video beats only. Audio rhythm matters more than visual rhythm.
6. **Not comparing to reference**: If there's a reference cut, always run compare_clips.py before and after.
