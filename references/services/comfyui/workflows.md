# ComfyUI Workflows — Full Catalog

Source: `GET http://192.168.1.181:8100/workflows`
API: See `references/services/comfyui/async-api.md` for the async submit/poll/fetch pattern.

---

## Text-to-Video (T2V)

### ltx2-t2v — LTX-2 Text to Video

Generate video from text prompt using LTX-2 19B distilled.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `"blurry, low quality, still frame, frames, watermark, overlay, titles, has blurbox, has subtitles"` |
| `seed` | integer | no | 10 |
| `frame_count` | integer | no | 121 |
| `width` | integer | no | 1280 |
| `height` | integer | no | 720 |

### ltx2-i2v — LTX-2 Image to Video

Generate video from image + prompt using LTX-2 19B distilled.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `"blurry, low quality, still frame, frames, watermark, overlay, titles, has blurbox, has subtitles"` |
| `image` | image | yes | — |
| `width` | integer | no | 1280 |
| `height` | integer | no | 720 |
| `seed` | integer | no | 10 |
| `frame_count` | integer | no | 121 |

### ltx2-i2v-audio — LTX-2 Image+Audio to Video

Generate video from image + audio + prompt using LTX-2 19B distilled.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `"blurry, low quality, still frame, frames, watermark, overlay, titles, has blurbox, has subtitles"` |
| `image` | image | yes | — |
| `audio` | audio | yes | — |
| `width` | integer | no | 1280 |
| `height` | integer | no | 720 |
| `seed` | integer | no | 10 |
| `frame_count` | integer | no | 201 |
| `audio_duration` | integer | no | 10 |

### ltx2-i2v-audio-fl — LTX-2 Image+Audio to Video (First+Last Frame)

Generate video from first frame + last frame + audio + prompt using LTX-2 19B distilled.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `"blurry, low quality, still frame, frames, watermark, overlay, titles, has blurbox, has subtitles"` |
| `first_frame` | image | yes | — |
| `last_frame` | image | yes | — |
| `audio` | audio | yes | — |
| `width` | integer | no | 1920 |
| `height` | integer | no | 1088 |
| `seed` | integer | no | 10 |
| `frame_count` | integer | no | 121 |
| `audio_duration` | integer | no | 10 |
| `detailer` | float | no | 0 |

---

## Text-to-Image (T2I)

### flux2-t2i — Flux 2 Text to Image

Generate an image from text prompt using Flux 2 Dev.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `seed` | integer | no | 663030678474959 |
| `width` | integer | no | 1008 |
| `height` | integer | no | 1024 |
| `steps` | integer | no | 20 |

### flux2-klein-t2i — Flux 2 Klein Text to Image

Generate an image from text prompt using Flux 2 Klein 9B base.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `""` |
| `seed` | integer | no | 1115861580316969 |
| `width` | integer | no | 1024 |
| `height` | integer | no | 1024 |
| `steps` | integer | no | 20 |
| `cfg` | float | no | 5 |

### z-image-base-t2i — Z-Image Base Text to Image

Generate an image from text prompt using Z-Image Base (Lumina2 architecture).

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `""` |
| `seed` | integer | no | 536302980194797 |
| `width` | integer | no | 1024 |
| `height` | integer | no | 1024 |
| `steps` | integer | no | 25 |
| `cfg` | number | no | 4 |

See also: `references/services/z-image/z-image-base.md`

---

## Image-to-Image / Edit

### flux2-i2i — Flux 2 Image to Image

Transform an input image based on a text prompt using Flux 2 Dev.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `image` | image | yes | — |
| `seed` | integer | no | 937785883369698 |
| `steps` | integer | no | 20 |

### flux2-klein-edit — Flux 2 Klein Image Edit

Edit an image based on a text prompt using Flux 2 Klein 9B base.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `""` |
| `image` | image | yes | — |
| `seed` | integer | no | 281434942367487 |
| `steps` | integer | no | 20 |
| `cfg` | float | no | 5 |

### qwen-image-edit — Qwen Image Edit

Edit an image using a text prompt with Qwen Image Edit 2509.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `image` | image | yes | — |
| `image2` | image | no | — |
| `image3` | image | no | — |
| `seed` | integer | no | 0 |
| `steps` | integer | no | 4 |

See also: `references/services/qwen/qwen-image-edit.md`

---

## Multi-Reference

### flux2-dev-multiref — Flux 2 Dev Multi-Reference

Generate an image combining 1-4 reference images with a text prompt using Flux 2 Dev.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `image1` | image | yes | — |
| `image2` | image | no | — |
| `image3` | image | no | — |
| `image4` | image | no | — |
| `width` | integer | no | 1024 |
| `height` | integer | no | 1024 |
| `seed` | integer | no | 0 |
| `steps` | integer | no | 20 |
| `guidance` | float | no | 4 |

### flux2-klein-multiref — Flux 2 Klein Multi-Reference

Generate an image combining 1-4 reference images with a text prompt using Flux 2 Klein 9B.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `prompt` | string | yes | — |
| `negative_prompt` | string | no | `""` |
| `image1` | image | yes | — |
| `image2` | image | no | — |
| `image3` | image | no | — |
| `image4` | image | no | — |
| `width` | integer | no | 1344 |
| `height` | integer | no | 768 |
| `seed` | integer | no | 0 |
| `steps` | integer | no | 20 |
| `cfg` | float | no | 5 |

**Note**: Multi-ref workflows use `image1`, `image2`, etc. Qwen Edit uses `image`, `image2`, `image3` (no `1` suffix on first slot).

---

## Vision-Language

### qwen25-vl — Qwen2.5-VL Video Description

Describe and analyze a video using Qwen2.5-VL vision-language model.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `video` | video | yes | — |
| `prompt` | string | no | `"Describe this video and transcribe it with timecodes, write the dialogue.\nCritique this video from the perspective of an editor."` |
| `max_new_tokens` | integer | no | 1024 |
| `seed` | integer | no | 308300167471515 |

---

## Audio / Speech

### qwen3-tts-voiceclone — Qwen3 TTS Voice Clone

Clone a reference voice and generate new speech from a text prompt.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `voice` | audio | yes | — |
| `text` | string | yes | — |
| `seed` | integer | no | 555790508841396 |

### qwen3-tts-voicedesign — Qwen3 TTS Voice Design

Design a custom voice from a text description and generate a sample audio clip.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `instruct` | string | yes | — |
| `text` | string | no | `"Hello, this is voice designer. How did I do?"` |
| `seed` | integer | no | 893259380079916 |

### whisper-stt — Whisper STT Deluxe

Transcribe audio to text using Whisper, with plain text, SRT, JSON, and language detection.

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `audio` | audio | yes | — |
| `model_size` | string | no | `"base"` |
| `language` | string | no | `"auto"` |
| `task` | string | no | `"transcribe"` |
| `initial_prompt` | string | no | `""` |
| `temperature` | float | no | 0 |

---

## Quick Reference: Image Slot Naming

| Workflow Family | First Image | Additional Images |
|-----------------|-------------|-------------------|
| Qwen Edit | `image` | `image2`, `image3` |
| Flux Dev Multiref | `image1` | `image2`, `image3`, `image4` |
| Flux Klein Multiref | `image1` | `image2`, `image3`, `image4` |
| Flux I2I / Klein Edit | `image` | — |
| LTX-2 I2V | `image` | — |
| LTX-2 FL | `first_frame` | `last_frame` |

Common mistake: Using `image1` with Qwen or `image` with multiref workflows.
