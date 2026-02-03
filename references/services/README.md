# FAL.ai API References

**Last Updated**: 2026-02-02
**Purpose**: Centralized reference documentation for all FAL.ai services used in this project

---

## Directory Structure

```
references/services/
├── README.md (this file)
├── FAL_VIDEO_API_INDEX.md ⭐ Video generation API index
├── API_DISCREPANCIES.md ⚠️ CRITICAL discrepancies to review
│
├── grok/
│   └── grok-image-to-video.md (Official FAL spec)
│
├── kling/
│   └── kling-image-to-video.md (Official FAL spec - v2.5 Turbo Pro)
│
├── veo3/
│   └── veo3-1-image-to-video.md (Official FAL spec)
│
├── nano-banana-pro/
│   ├── LIMITATIONS.md
│   └── TECHNIQUES.md
│
└── [other services]/
    └── (flux, midjourney, runway-gen3, etc.)
```

---

## Quick Reference Links

### Video Generation (Primary Pipeline)

| Service | Spec File | Endpoint | Usage |
|---------|-----------|----------|-------|
| **Kling v2.5** | `kling/kling-image-to-video.md` | `fal-ai/kling-video/v2.5-turbo/pro/image-to-video` | General animation, 5-10s clips |
| **Grok Imagine** | `grok/grok-image-to-video.md` | `xai/grok-imagine-video/image-to-video` | Action sequences, 1-15s clips |
| **Veo 3.1** | `veo3/veo3-1-image-to-video.md` | `fal-ai/veo3.1/image-to-video` | Dialogue, 4-8s clips with audio |

### Image Generation (Final Frames)

| Service | Spec File | Endpoint | Usage |
|---------|-----------|----------|-------|
| **Nano Banana Pro** | `nano-banana-pro/` | `fal-ai/nano-banana-pro` | Final frames with image references |

---

## Important Documents

### 1. FAL_VIDEO_API_INDEX.md ⭐
**Purpose**: Central index for all video generation APIs
- Official endpoint specifications
- Parameter comparison matrix
- Update protocol

**When to use**: Reference for correct API parameters before coding

### 2. API_DISCREPANCIES.md ⚠️
**Purpose**: Critical discrepancies between official specs and working code
- Kling v1 vs v2.5 endpoint differences
- Parameter name variations
- Testing requirements

**When to use**: Before using any API, check for known discrepancies

---

## Official Spec Sources

All specifications downloaded from FAL.ai using `/llms.txt` format:

```
https://fal.ai/models/{model-path}/llms.txt
```

### Examples:
- Kling: https://fal.ai/models/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/llms.txt
- Grok: https://fal.ai/models/xai/grok-imagine-video/image-to-video/llms.txt
- Veo 3.1: https://fal.ai/models/fal-ai/veo3.1/image-to-video/llms.txt

---

## Usage Guidelines

### 1. Before Using an API
1. Check `FAL_VIDEO_API_INDEX.md` for official parameters
2. Check `API_DISCREPANCIES.md` for known issues
3. Verify your code matches recommended parameters
4. Test with a single generation before batch operations

### 2. When API Behavior Changes
1. Download latest spec from FAL.ai
2. Save to appropriate subdirectory
3. Update `FAL_VIDEO_API_INDEX.md`
4. Add discrepancies to `API_DISCREPANCIES.md` if needed
5. Update project documentation

### 3. Adding New Services
1. Download spec: `https://fal.ai/models/{model-path}/llms.txt`
2. Create subdirectory: `services/{service-name}/`
3. Save spec with descriptive name
4. Add entry to this README
5. Update relevant project documentation

---

## Current Status

### ✅ Verified and Working
- **Kling v1 Standard**: User-verified working with `start_image_url`
- **File uploads**: `fal_client.upload_file()` working correctly
- **Nano Banana Pro**: Final frame generation working

### ⚠️ Needs Validation
- **Kling v2.5 Turbo Pro**: Official spec, not yet tested
- **Grok duration type**: Spec says integer, needs validation
- **Veo 3.1 vs veo3**: Endpoint difference needs testing

### ❌ Known Issues
- Kling has multiple endpoints with different parameter names
- Previous Grok/Veo tests used text-to-video (incorrect workflow)

---

## Related Project Documentation

### Video Pipeline
- `VISUAL_PRODUCTION/VIDEO_PIPELINE.md` - Full workflow documentation
- `VISUAL_PRODUCTION/VIDEO_API_REFERENCE_CORRECTED.md` - API quick reference
- `VISUAL_PRODUCTION/VIDEO_PIPELINE_TEST_RESULTS.md` - Test results

### Image Pipeline
- `VISUAL_PRODUCTION/ANIMATION_PIPELINE_CORRECTED.md` - Final frame workflow
- `VISUAL_PRODUCTION/QUICKSTART_FINAL_FRAMES.md` - Quick start guide

---

## Maintenance

### Monthly
- [ ] Check FAL.ai blog for new model releases
- [ ] Download updated specs for any changed models
- [ ] Verify no breaking changes to current endpoints

### Per Release
- [ ] Test all APIs with sample generations
- [ ] Validate parameters match current specs
- [ ] Update documentation if changes found

### When Errors Occur
- [ ] Check if endpoint has been deprecated
- [ ] Download latest spec
- [ ] Compare with current usage
- [ ] Update code and docs as needed

---

## Contact / Issues

If you encounter:
- API errors not documented here
- Unexpected parameter behavior
- Spec/code mismatches

1. Document in `API_DISCREPANCIES.md`
2. Download fresh spec from FAL.ai
3. Test with official spec parameters
4. Update project documentation

---

## Version History

- **2026-02-02**: Initial organization with Kling, Grok, Veo 3.1 specs
  - Added FAL_VIDEO_API_INDEX.md
  - Added API_DISCREPANCIES.md
  - Documented Kling v1 vs v2.5 endpoint differences
