# MiniMax H3 — Reference-to-Video (Local)

**Added**: 2026-08-06
**Status**: Pilot-validated 2026-08-06 (The Regular OTS reverse-pair, 3 variants — see Pilot findings below)
**Model**: [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) — near-frontier reference-to-video
**Local endpoint**: `http://192.168.1.181:8100/workflows/minimax-h3-r2v`

## Why it matters

H3 accepts **up to 9 reference images, 3 reference videos, and 3 standalone audio
clips in one generation** — all optional, any combination (none = pure t2v). This
collapses much of the old multi-stage identity pipeline (z-image refs →
qwen-image-edit composition → i2v) into a single reference-conditioned call:
character sheets, location refs, prop refs, a motion-reference video, and a
voice-timbre audio ref can all condition the same shot.

## Endpoint contract (verified against live server 2026-08-06)

| Input | Type | Default | Range | Notes |
|-------|------|---------|-------|-------|
| `prompt` | string | — | required | See prompt format below |
| `reference_image_1..9` | image | none | optional | Tagged `<Picture i>` by 1-based upload order |
| `reference_video_1..3` | video | none | optional | Tagged `<Video k>`; each video's soundtrack auto-becomes an audio reference for that slot |
| `reference_audio_1..3` | audio | none | optional | Tagged `<Audio j>`; standalone audio ordinals continue AFTER any reference-video soundtracks, in upload order |
| `width` | int | 832 | 256–1280 | |
| `height` | int | 480 | 256–1280 | |
| `duration` | float | 5 | **1–10 s** | Hard 10 s ceiling — plan shots accordingly (vs LTX-2.3's ~20 s) |
| `steps` | int | 20 | 1–50 | |
| `seed` | int | random | | Always pin for reproducibility |

Output: one video. Async job like other local workflows: POST returns 202 +
`{"job_id": ...}`, poll `GET /jobs/{id}` until `status == "completed"`, download
bytes from `GET /jobs/{id}/result`.

## Prompt format

Two levels. Start simple; escalate to the full format for dialogue/multi-ref shots.

### 1. Simple tagged prose (server-documented)

Plain prose that tags references by 1-based position within their type:

> "She wears the outfit from `<Picture 1>` while walking through the scene in
> `<Picture 2>`, moving like the dancer in `<Video 1>`."

Omit all tags and references for pure text-to-video.

### 2. Full structured format (MiniMax official guides — in this directory)

- **[prompt-guide-base.md](prompt-guide-base.md)** — T2VA / I2VA / FL2VA / L2VA
  (no-reference and keyframe modes). Core fields:
  `integrated_multimodal_description` (timeline of `[Shot N]` blocks) +
  `overall_soundscape` + `non_diegetic_music`.
- **[prompt-guide-full-reference.md](prompt-guide-full-reference.md)** — full-reference
  mode. Six sections in order: `subject_definitions`, `summary` (with
  `[reference generation]`-style task-type prefix), `retention_analysis`
  (`fully_preserved` / `partially_preserved` / `attribute_transfer` /
  `weak_reference`; audio: `fully_copy` / `partially_copy` / `reference`),
  `detailed_description` (350–500 words for generation tasks), soundscape, music.

Key conventions shared by both guides:

- **Shots**: `[Shot 1]` opens with no timestamp; later shots `[Shot 2] At 00:03.500, the camera cuts to...` with strictly increasing cut times.
- **Camera**: motion type + amplitude + speed written as natural prose — "The camera pushes in with small amplitude at slow speed toward..." Vocabulary: Zoom/Push/Pull, Pan, Truck, Tilt, Pedestal, Arc Shot, Tracking Shot, Static Shot, Shake Slightly/Strongly, POV, Roll.
- **Speakers**: stable `(S1)`, `(S2)` IDs in order of first vocal appearance; compound `(S1,S2)` for simultaneous speech. Describe voice (age, gender, pitch, timbre, pace) at first appearance, OUTSIDE the dialogue tag.
- **Dialogue**: `<d>[English] exact line.</d>` — language tag + verbatim words only inside the tag. Voiceover uses the exact phrase `says in an off-screen voiceover` and must be followed by "while his lips remain completely closed."
- **Cross-cut audio**: `<scenetrans>` at both connection points; `<cutoff>` for speech truncated by video end.
- **On-screen text**: double-quoted verbatim (renders as visible text — beware, same class of risk as LTX proper-noun leaks).
- **Subjects from multiple sources**: `<Subject 1> is the woman whose appearance comes from <Picture 1> and whose walking motion comes from <Video 1>.`
- Images that only define a character/style get cited inside a `<Subject N>` definition, NOT a standalone `<Picture N>` entry (standalone Picture = concrete frame anchor: first frame, keyframe, last frame, storyboard).

## Fit with existing pipeline (untested hypotheses to validate)

- **Identity stack**: Krea2 turnaround (one image per character, see
  `references/services/krea/`) + location ref + prop refs as `<Picture 1..N>`,
  defined as `<Subject N>`s — replaces the qwen-image-edit composition stage.
- **Voice**: qwen3-tts voiceclone output as `reference_audio_N` with
  `retention_analysis: reference` for timbre-guided dialogue delivery.
- **Motion/blocking**: a prior LTX clip or live-action reference as `<Video 1>`
  with `weak_reference` for rhythm/camera structure.
- **10 s ceiling** means dialogue-heavy shots need tighter line budgets than the
  LTX-2.3 audio-length-driven sizing rule (`max(clip_dur, audio_dur)` capped at 20 s).

## Pilot findings (2026-08-06 — The Regular, OTS reverse-pair, 3 Krea2 refs, seed 5411, 8s @ 832×480)

Artifacts: `projects/260226-the-regular/EXPERIMENTS/minimax_h3/` (run_pilot.py +
three clips + Whisper transcripts). Baseline comparison:
`ic_lora_ingredients/shots/reverse_turnaround_ls.mp4` (LTX-2.3 ingredients).

1. **AUDIO MUST ALWAYS BE SPECIFIED — the #1 prompting rule.** A prose prompt
   with no audio description produced **garbled invented dialogue** (Whisper:
   "I knew this is yet. Take you in like that."). The same shot with explicit
   `overall_soundscape:` + `non_diegetic_music: N/A` and no dialogue produced
   clean quiet room tone (mean −42.7 dB vs −29.1 dB). Never send a prompt
   without the two audio sections, even for "silent" shots.
2. **Dialogue in the official grammar works on the FIRST take.** Voice
   description outside the tag + `(S1) says: <d>[English] You okay, hon?</d>` +
   reverse-shot structure → Whisper transcribed both lines verbatim, correctly
   timed to their shots (line 1 in Shot 1 at 0–4s, line 2 after the cut at
   4–7s), correct per-speaker voices, in ONE generation spanning an internal
   cut. No single-character-closeup workaround needed (unlike LTX-2.3).
3. **Both prompt levels work for visuals; the full format buys precision.**
   Simple tagged prose delivered the OTS + internal hard cut + identity. The
   six-section format additionally honored fine blocking ("coffee pot lowered
   in one hand" rendered exactly). Use the full format for production; simple
   prose is fine for exploration — but per rule 1, always append the two audio
   sections even to simple prompts.
4. **Internal cuts**: "The shot cuts to the reverse..." in prose triggered a
   clean hard cut respecting the 180° line in 3/3 takes — more reliable than
   LTX ingredients' emergent reverse-pair behavior.
5. **Identity from separate refs — no sheet stitching.** Three separate Krea2
   images (2 character turnarounds + 1 location) as `<Picture 1-3>` held both
   identities and the location across shots. The ingredients-pipeline stitching
   step is unnecessary for H3.
6. **No caption/text burn-in** in any of the three takes (descriptive
   references only, no proper nouns in prompts — keep that discipline).
7. **Quality clearly above LTX-2.3 ingredients** on the same shot: film-grade
   light, sharper faces, no garbled background signage (the LTX baseline shows
   a gibberish window sign), correct two-character OTS coverage where LTX
   dropped the foreground character.
8. **Timing**: ~4.3 min warm per 8s clip @ 832×480 / 20 steps; first call after
   idle ~12 min (model load). Whisper-transcription QC of every dialogue clip
   is cheap and recommended (whisper-stt workflow on the same server).
