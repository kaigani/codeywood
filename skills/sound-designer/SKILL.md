---
skill: sound-designer
role: post-production
version: 1.0

description: |
  Sound design cognitive skill. Teaches Claude to think about audio as a
  storytelling layer — ambient beds, action sounds, dialogue, silence —
  and to use audio analysis tools for review and mixing decisions.

inputs:
  required:
    - name: scene_clips
      type: directory
      description: Video clips (may or may not contain audio)
  optional:
    - name: voice_refs
      type: directory
      path: REFERENCES/voice_refs/
      description: Character voice reference WAVs
    - name: dialogue_scripts
      type: file
      description: Dialogue lines per shot from shot_list.yaml
    - name: waveform
      type: file
      description: Pre-generated waveform PNG

outputs:
  - name: sound_design_notes
    type: file
    description: Per-clip audio direction and mixing instructions
  - name: dialogue_manifest
    type: file
    description: Dialogue generation manifest (character, line, timecode)

tools:
  - scripts/lib/audio_analysis.py (generate_waveform, detect_silence, transcribe_audio)
  - scripts/lib/ffmpeg.py (extract_audio, mix_audio_tracks, l_cut, j_cut)
---

# Sound Designer

## Purpose

Design and execute the audio layer of each scene. Sound is 50% of the audience's experience — a well-mixed audio bed transforms AI-generated video from "impressive tech demo" into "watchable film."

---

## The Three Audio Layers

Every scene needs all three layers, even if one is nearly silent.

### Layer 1: Ambient Bed (Always Present)

The constant background sound that tells the audience WHERE they are.

- **Caribbean port town**: Distant waves, seabirds, creaking wood, harbor bells, murmur of crowd
- **Ship interior**: Hull groaning, water against wood, distant chain rattle, muffled wind
- **Forest clearing**: Insects, rustling leaves, distant bird calls, wind through canopy
- **Office/modern**: HVAC hum, distant keyboard clicks, muffled conversation, elevator ding

**Rules**:
- The ambient bed NEVER stops. Total silence is disorienting.
- Volume: -20dB to -30dB below dialogue. Present but not competing.
- Ambient should be consistent across an entire scene (same location = same bed).
- Change in ambient = change in location or time.

### Layer 2: Action Sounds (Synced to Motion)

Sounds triggered by visible events in the video.

- Footsteps, door opens/closes, objects placed on surfaces
- Environmental interactions: wind gusting, waves crashing, fire crackling
- Impact sounds: punches, falls, collisions
- Mechanical: ships creaking under stress, ropes tightening, weapons drawn

**Rules**:
- Must be synced to visible action (within 0.1s tolerance).
- Better to omit than to be out of sync — bad sync is worse than no sound.
- Not every motion needs a sound. Pick the 2-3 most impactful per clip.

### Layer 3: Character Sounds (Dialogue, Breathing, Vocalizations)

The human audio layer.

- **Dialogue**: Spoken lines via TTS/voice clone
- **Breathing**: Heavy breathing for exertion, held breath for tension, sighs for emotion
- **Vocalizations**: Grunts, gasps, whispered exclamations, laughter, crying
- **Internal monologue**: V.O. with slight reverb/intimacy processing

**Rules**:
- Dialogue always sits on top of the mix (-6dB to -3dB relative to ambient).
- Breathing and vocalizations at -12dB — present but not dominant.
- V.O. should be slightly "closer" than scene dialogue (less room reverb).
- When a character speaks, duck the ambient bed by 3-6dB (auto-duck).

---

## Sound Palette Per Scene

Each location gets a consistent signature:

```yaml
location: "Harbor Square"
ambient_bed:
  base: "Caribbean harbor ambience"
  layers:
    - "gentle waves against stone pier"
    - "distant seabirds (gulls, terns)"
    - "wooden ship hulls creaking in current"
    - "murmur of market crowd at medium distance"
  volume_db: -24

action_sounds:
  - "boot steps on wet cobblestone"
  - "rope and canvas flapping in harbor wind"
  - "wooden cart wheels on stone"

character_signature:
  mars: "slightly raspy alto, Caribbean-accented English, guarded delivery"
  jonah: "warm tenor, careful phrasing, occasional humor underneath"
```

---

## Dynamic Range

### Quiet Does Not Mean Silent

| Scene State | Ambient Level | Action Level | Dialogue Level |
|------------|---------------|--------------|----------------|
| Calm | -24dB | -30dB (incidental) | -6dB |
| Tension building | -20dB | -18dB (emphasized) | -6dB |
| Action peak | -16dB | -10dB | -3dB (shouted) |
| Emotional beat | -28dB (ducked) | None | -6dB (intimate) |
| Silence moment | -36dB (nearly gone) | None | None |

### The Power of Near-Silence

The most impactful moments often use near-silence:
- Before a revelation: ambient drops to -36dB, then...
- The reveal: action sound at full volume, ambient surges back
- This dynamic range creates the "punch" that purely visual storytelling can't achieve.

### Trust Silence

Target 4-6 dramatic silences per 5 minutes at emotional turning points. Design silence as deliberately as sound — it's a free storytelling beat that most AI films completely miss.

The best moments in competitive AI films (e.g., Dead Enders' 4.5s, 4.6s, 5.9s silences) are structural beats placed at act boundaries. Plan them into the sound design, don't discover them in editing.

---

## Audio Analysis Workflow

### Before Mixing

```bash
# Generate waveform to visualize audio presence
python3 -c "from scripts.lib.audio_analysis import generate_waveform; ..."

# Detect silence regions (potential dialogue windows)
python3 -c "from scripts.lib.audio_analysis import detect_silence; ..."

# Transcribe existing audio (what did the AI generate?)
python3 scripts/analysis/analyze_clip.py CLIP --transcribe
```

### What to Look For

1. **Waveform shape**: Flat = no audio or static. Spiky = dialogue or action. Sustained = ambient.
2. **Silence regions**: Natural dialogue pauses? Or dead zones that need ambient fill?
3. **AI-generated audio**: The video model often generates ambient sounds. Assess quality — keep or replace?
4. **Dialogue overlap**: If AI generated speech, does it match the script? (Usually not — replace with TTS.)

---

## Mixing Decisions

### Keep AI Audio When:
- Ambient quality is good and matches the location
- Sound effects are well-synced to visible action
- No unwanted dialogue/speech was generated

### Replace AI Audio When:
- AI generated unwanted dialogue (common with face-forward shots)
- Ambient tone doesn't match location (e.g., AI generated indoor ambience for outdoor scene)
- Audio quality is poor (clicks, distortion, frequency artifacts)
- Need specific dialogue lines from the script

### Layer On Top When:
- AI ambient is acceptable but needs dialogue overlay
- Good base but missing specific action sounds
- Want to add music or V.O. on top of existing audio

### FFmpeg Mix Fallback
`mix_audio_tracks()` handles videos with or without existing audio tracks automatically. It detects whether the input video has audio and adjusts the ffmpeg filter graph accordingly — no need to check manually before calling.

---

## L-Cut and J-Cut Audio Strategy

### L-Cut (Audio Leads)
The next clip's audio starts 0.5-1.5s before the visual cut.

**Best for**:
- Dialogue scenes: hear the next speaker's first words while still seeing the listener's reaction
- Location transitions: hear the new location's ambient before seeing it (anticipation)
- Narration: V.O. continues from one visual to the next

### J-Cut (Video Leads)
The next clip's video starts 0.5-1.5s before the audio cut.

**Best for**:
- Reveals: see the new scene before hearing it (visual surprise, then audio context)
- Reaction shots: see a character's face before hearing what caused the reaction
- Time transitions: new visual, old audio creates a "memory" effect

### When to Use Neither
- Action sequences: hard cuts with hard audio cuts create energy
- Montage with music: audio is continuous music bed, visuals cut freely
- Comedy beats: precise timing requires exact audio/video sync

---

## Direction Narration as Audio Layer

Direction narration is a fourth audio layer used in paper cuts and early rough assemblies. It fills silence gaps with spoken description of what the audience would see and hear in the final production.

### Layer Placement

| Layer | Purpose | Volume | When |
|-------|---------|--------|------|
| Ambient bed | Environmental presence | -24dB | Always |
| Dialogue | Character speech (TTS) | -6dB | Per script |
| **Direction narration** | Camera/sound/blocking cues | **-8dB** | **Silence gaps only** |
| Action sounds | Synced to motion | -18dB | Per sound design |

Direction narration plays **only in gaps where no dialogue is scheduled**. It never overlaps with character speech. The paper cut script automatically finds the largest silence gap in each shot and places the narration there.

### Narrator Voice

Use a single consistent narrator voice across the production. Store the reference WAV at `REFERENCES/voice_refs/narrator_voice_ref.wav`. This voice should be:
- **Neutral and warm** — not dramatic or performative
- **Distinct from character voices** — the audience must instantly know this is narration, not dialogue
- **Clean recording** — minimal room tone, no background noise (the TTS clones whatever artifacts are in the reference)

### ComfyUI TTS: Sync vs. Async

The `qwen3-tts-voiceclone` workflow returns either:
- **HTTP 200 with audio bytes** (sync) — short texts, low queue load
- **HTTP 202 with `job_id`** (async) — longer texts or busy queue

The `generate_direction_audio()` function in `scripts/lib/audio_analysis.py` handles both. For batch generation, submit all jobs first, then poll — this parallelizes the GPU work and is 3-4x faster than sequential generation.

---

## Voice Design Reference

Characters need consistent vocal identities across the production:

```bash
# One-time: design character voices
python3 scripts/production/design_voices.py

# Per-scene: generate dialogue
python3 scripts/production/generate_dialogue.py --scene sc01
```

### Voice Design Tips
- Avoid delivery cues in TTS text — "whispered" gets read literally. The TTS model will speak "(whispering)" as actual text
- Delivery style must be baked into the voice reference via the design instruct
- Test with short phrases first, then generate full lines
- Use Whisper `model_size=large` for accurate transcription of generated dialogue (`base` misreads short words like "sea" → "C")
- **Voice iteration lesson**: Initial voice designs often come out too "bright/Disney." Design for the character's emotional register, not their surface personality. A guarded character needs a low, raspy voice — not a cheerful one that "sounds young"
- **Robot/AI characters**: Flat, synthesized TTS delivery is a natural strength for non-human characters. The emotion comes from context and script, not vocal inflection. Do not fight the TTS limitations here — they outperform human actors who would over-emote the role.

### Audio-Only Deterioration

When a character or machine is physically/emotionally deteriorating across a scene, audio layering can communicate this without regenerating video clips:
- Layer worsening mechanical sounds (grinding, stuttering servos, electrical crackle) that intensify across clips
- Degrade voice quality progressively (add subtle distortion, frequency roll-off, or dropout artifacts via ffmpeg filters)
- This is cheaper and more controllable than trying to achieve progressive visual deterioration across AI-generated clips
