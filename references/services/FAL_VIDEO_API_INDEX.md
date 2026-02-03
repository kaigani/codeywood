# FAL Video API Reference Index

**Last Updated**: 2026-02-02
**Purpose**: Central index for all FAL.ai video generation API references

---

## Official API Specifications

All specifications downloaded from FAL.ai using `/llms.txt` format.

### Kling Video
- **Official Spec**: `kling/kling-image-to-video.md`
- **Model**: Kling 2.5 Turbo Pro
- **Endpoint**: `fal-ai/kling-video/v2.5-turbo/pro/image-to-video`
- **Parameter**: `image_url` (required)
- **Duration**: "5" or "10" (string)
- **Source**: https://fal.ai/models/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/llms.txt

### Grok Imagine Video
- **Official Spec**: `grok/grok-image-to-video.md`
- **Model**: Grok Imagine Video (xAI)
- **Endpoint**: `xai/grok-imagine-video/image-to-video`
- **Parameter**: `image_url` (required)
- **Duration**: 1-15 (integer)
- **Source**: https://fal.ai/models/xai/grok-imagine-video/image-to-video/llms.txt

### Veo 3.1
- **Official Spec**: `veo3/veo3-1-image-to-video.md`
- **Model**: Veo 3.1 (Google DeepMind)
- **Endpoint**: `fal-ai/veo3.1/image-to-video`
- **Parameter**: `image_url` (required)
- **Duration**: "4s", "6s", or "8s" (string)
- **Source**: https://fal.ai/models/fal-ai/veo3.1/image-to-video/llms.txt

---

## CRITICAL: Endpoint Discrepancies

### Kling - Multiple Endpoints Available

**Official Spec (v2.5 Turbo Pro)**:
```python
endpoint = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"
parameters = {
    "image_url": str,  # ✅ Standard parameter name
    "duration": "5" | "10",  # String
    "negative_prompt": "blur, distort, and low quality",
    "cfg_scale": 0.5
}
```

**User's Working Example (v1 Standard)**:
```python
endpoint = "fal-ai/kling-video/v1/standard/text-to-video"
parameters = {
    "start_image_url": str,  # ⚠️ Non-standard parameter name
    "duration": "5",  # String
    "negative_prompt": "blur, distort, and low quality",
    "generate_audio": True
}
```

**Status**: Both endpoints appear to work but use different parameter names.

**Recommendation**:
- Use v2.5 Turbo Pro endpoint (`image_to_video`) for consistency with Grok/Veo
- OR document both endpoints as valid options with different parameters
- REQUIRES TESTING to validate v2.5 Turbo Pro endpoint

---

## Parameter Comparison Matrix

| Model | Endpoint | Image Param | Duration Type | Duration Options | Audio Param |
|-------|----------|-------------|---------------|------------------|-------------|
| **Kling v2.5** | `fal-ai/kling-video/v2.5-turbo/pro/image-to-video` | `image_url` | String | "5", "10" | ❌ Not in spec |
| **Kling v1** | `fal-ai/kling-video/v1/standard/text-to-video` | `start_image_url` | String | "5", "6" | `generate_audio` (bool) |
| **Grok Imagine** | `xai/grok-imagine-video/image-to-video` | `image_url` | Integer | 1-15 | ✅ Native audio |
| **Veo 3.1** | `fal-ai/veo3.1/image-to-video` | `image_url` | String | "4s", "6s", "8s" | `generate_audio` (bool) |

---

## Recommended Production Parameters

### Kling v2.5 Turbo Pro (Official Spec)
```python
{
    "prompt": str,  # Motion description + Style DNA
    "image_url": str,  # Uploaded frame URL
    "duration": "5",  # "5" or "10"
    "negative_prompt": "blur, distort, and low quality",
    "cfg_scale": 0.5  # 0-1 range, default 0.5
}
```

### Kling v1 Standard (User-Verified)
```python
{
    "prompt": str,  # Motion description + Style DNA
    "start_image_url": str,  # Uploaded frame URL
    "duration": "5",  # "5" or "6"
    "negative_prompt": "blur, distort, and low quality",
    "generate_audio": True
}
```

### Grok Imagine Video
```python
{
    "prompt": str,  # Motion description + Style DNA
    "image_url": str,  # Uploaded frame URL
    "duration": 6,  # INTEGER 1-15, default 6
    "aspect_ratio": "16:9",  # or "auto"
    "resolution": "720p"  # "480p" or "720p"
}
```

### Veo 3.1
```python
{
    "prompt": str,  # Motion description + Style DNA
    "image_url": str,  # Uploaded frame URL
    "aspect_ratio": "16:9",  # "auto", "16:9", or "9:16"
    "duration": "8s",  # "4s", "6s", or "8s"
    "resolution": "720p",  # "720p", "1080p", or "4k"
    "generate_audio": True,  # Default true
    "negative_prompt": str  # Optional
}
```

---

## Action Items

### Immediate
- [x] Document official API specs in reference directory
- [ ] Test Kling v2.5 Turbo Pro endpoint to compare with v1 Standard
- [ ] Update VIDEO_API_REFERENCE_CORRECTED.md with official parameters
- [ ] Validate Grok duration parameter (integer vs string)
- [ ] Test Veo 3.1 endpoint (we've been using `veo3`, spec shows `veo3.1`)

### Testing Needed
1. **Kling v2.5 vs v1**: Compare quality, features, and audio support
2. **Grok duration**: Verify integer parameter works correctly
3. **Veo 3.1**: Test new endpoint and compare with veo3

### Documentation Updates
- [ ] Update VIDEO_PIPELINE.md with official endpoints
- [ ] Update VIDEO_API_REFERENCE_CORRECTED.md with parameter corrections
- [ ] Add reference links to official specs in all docs

---

## File Organization

```
references/services/
├── FAL_VIDEO_API_INDEX.md (this file)
├── kling/
│   └── kling-image-to-video.md (v2.5 Turbo Pro official spec)
├── grok/
│   └── grok-image-to-video.md (official spec)
└── veo3/
    └── veo3-1-image-to-video.md (official spec)
```

---

## Update Protocol

When FAL.ai releases new model versions or updates:

1. Download new spec: `https://fal.ai/models/[model-path]/llms.txt`
2. Save to appropriate subdirectory with descriptive name
3. Update this index with:
   - New endpoint path
   - Parameter changes
   - Any breaking changes
4. Test new endpoint before updating production code
5. Update all documentation referencing the changed API

---

## Related Documentation

- **Project Video Pipeline**: `VISUAL_PRODUCTION/VIDEO_PIPELINE.md`
- **Video API Reference**: `VISUAL_PRODUCTION/VIDEO_API_REFERENCE_CORRECTED.md`
- **Test Results**: `VISUAL_PRODUCTION/VIDEO_PIPELINE_TEST_RESULTS.md`
- **FAL General API**: `fal-api.json` (if exists in references/services/)
