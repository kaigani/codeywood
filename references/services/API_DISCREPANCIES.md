# FAL API Discrepancies - CRITICAL REVIEW NEEDED

**Date**: 2026-02-02
**Status**: REQUIRES VALIDATION

---

## Summary

After reviewing official FAL.ai API specifications, several discrepancies have been found between:
1. What we've been using in code
2. What the official specs document
3. What the user's working examples show

**CRITICAL**: These need validation before production use.

---

## 1. Kling Video - Multiple Endpoints

### Discrepancy

**Official Spec** shows: `fal-ai/kling-video/v2.5-turbo/pro/image-to-video`
**User's Working Example** uses: `fal-ai/kling-video/v1/standard/text-to-video`

### Parameter Differences

| Parameter | v2.5 Turbo Pro (Official) | v1 Standard (User's Example) |
|-----------|--------------------------|------------------------------|
| Image param | `image_url` | `start_image_url` ⚠️ |
| Duration | "5" or "10" (string) | "5" or "6" (string) |
| Audio | Not mentioned in spec | `generate_audio: true` ✅ |
| CFG scale | `cfg_scale: 0.5` (0-1) | Not used |
| Negative prompt | ✅ Supported | ✅ Supported |

### User's Verified Working Code
```python
result = fal_client.subscribe(
    "fal-ai/kling-video/v1/standard/text-to-video",
    arguments={
        "prompt": full_prompt,
        "start_image_url": uploaded_url,  # NOT image_url!
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "generate_audio": True
    }
)
```

### Official Spec Code
```python
result = fal_client.subscribe(
    "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
    arguments={
        "prompt": "description",
        "image_url": "https://...",  # NOT start_image_url!
        "duration": "5",  # "5" or "10" only
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5
    }
)
```

### Questions
1. ❓ Does v2.5 Turbo Pro support audio generation?
2. ❓ Is v2.5 Turbo Pro better quality than v1 Standard?
3. ❓ Why does v1 use `start_image_url` instead of standard `image_url`?
4. ❓ Are both endpoints actively supported?

### Recommendation
- **Test v2.5 Turbo Pro** with same frame to compare
- **Keep v1 Standard documented** as user-verified working
- **Document both** as valid options until tested

---

## 2. Grok Imagine Video - Duration Type

### Discrepancy

**Official Spec** shows: Duration is **integer** (1-15)
**Our Code** may have used: String

### Official Spec
```python
{
    "duration": 6,  # INTEGER, not "6"
    "aspect_ratio": "auto",
    "resolution": "720p"
}
```

### Impact
- Low - Type coercion likely handles this
- Should update to integer for correctness

### Recommendation
✅ **Use integer** for duration parameter as per spec

---

## 3. Veo - Endpoint Version

### Discrepancy

**Official Spec** shows: `fal-ai/veo3.1/image-to-video`
**Our Code** used: `fal-ai/veo3/image-to-video`

### Questions
1. ❓ Is `veo3` an alias for `veo3.1`?
2. ❓ Are they different models?
3. ❓ Does `veo3.1` have improvements over `veo3`?

### Official Veo 3.1 Parameters
```python
{
    "prompt": str,
    "image_url": str,
    "aspect_ratio": "16:9",  # Only "auto", "16:9", "9:16"
    "duration": "8s",  # "4s", "6s", or "8s" - STRING with 's'
    "resolution": "720p",  # "720p", "1080p", or "4k"
    "generate_audio": True,  # Default true
    "negative_prompt": str,  # Optional
    "seed": int,  # Optional
    "auto_fix": bool  # Optional - auto-rewrite prompts that fail
}
```

### Recommendation
✅ **Update to veo3.1** endpoint as per official spec
✅ **Use duration strings with 's' suffix**: "4s", "6s", "8s"

---

## 4. All Models - File Upload

### Status
✅ **VERIFIED CORRECT**

All our code uses `fal_client.upload_file()` which returns FAL storage URLs.

```python
# ✅ CORRECT - we're doing this
frame_url = fal_client.upload_file("path/to/frame.png")
# Returns: "https://v3b.fal.media/files/..."
```

This matches the official spec requirement for image URLs.

---

## Testing Requirements

### Priority 1 - CRITICAL
- [ ] **Test Kling v2.5 Turbo Pro** with image-to-video
  - Compare with v1 Standard for quality
  - Verify audio support (or lack thereof)
  - Test `image_url` vs `start_image_url` parameter names

- [ ] **Test Veo 3.1** endpoint
  - Compare with `veo3` endpoint
  - Verify it accepts same parameters
  - Check for quality/feature differences

### Priority 2 - Validation
- [ ] **Verify Grok duration** as integer (not string)
- [ ] **Test all parameter types** match official specs
- [ ] **Validate all optional parameters** work as documented

### Priority 3 - Documentation
- [ ] Update VIDEO_API_REFERENCE_CORRECTED.md
- [ ] Update VIDEO_PIPELINE.md
- [ ] Add test results to VIDEO_PIPELINE_TEST_RESULTS.md

---

## Corrected Parameter Summary

### Kling v2.5 Turbo Pro (Per Official Spec)
```python
fal_client.subscribe(
    "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
    arguments={
        "prompt": str,
        "image_url": str,  # Changed from start_image_url
        "duration": "5",  # "5" or "10"
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5
    }
)
```

### Kling v1 Standard (User-Verified Working)
```python
fal_client.subscribe(
    "fal-ai/kling-video/v1/standard/text-to-video",
    arguments={
        "prompt": str,
        "start_image_url": str,  # Unique to this endpoint
        "duration": "5",  # "5" or "6"
        "negative_prompt": "blur, distort, and low quality",
        "generate_audio": True
    }
)
```

### Grok Imagine (Per Official Spec)
```python
fal_client.subscribe(
    "xai/grok-imagine-video/image-to-video",
    arguments={
        "prompt": str,
        "image_url": str,
        "duration": 6,  # INTEGER 1-15, not string
        "aspect_ratio": "16:9",
        "resolution": "720p"  # "480p" or "720p"
    }
)
```

### Veo 3.1 (Per Official Spec)
```python
fal_client.subscribe(
    "fal-ai/veo3.1/image-to-video",  # Changed from veo3
    arguments={
        "prompt": str,
        "image_url": str,
        "aspect_ratio": "16:9",
        "duration": "8s",  # STRING with 's': "4s", "6s", or "8s"
        "resolution": "720p",  # "720p", "1080p", or "4k"
        "generate_audio": True
    }
)
```

---

## Decision Matrix

| Issue | Use Official Spec? | Use Working Code? | Action |
|-------|-------------------|-------------------|---------|
| **Kling endpoint** | ❓ Need to test | ✅ Verified working | Keep v1, test v2.5 |
| **Kling image param** | `image_url` | `start_image_url` | Keep working, note discrepancy |
| **Grok duration type** | Integer | Unknown | ✅ Update to integer |
| **Veo endpoint** | `veo3.1` | `veo3` | ✅ Update to veo3.1 |
| **Veo duration format** | "8s" with 's' | Unknown | ✅ Update to spec format |

---

## Next Steps

1. **Immediate**: Update Grok and Veo to match official specs
2. **Test**: Validate Kling v2.5 Turbo Pro endpoint
3. **Document**: Keep both Kling v1 and v2.5 documented with clear notes
4. **Monitor**: Watch for any API changes or deprecation notices

---

---

## 5. Image Generation APIs - CORRECTED (2026-02-03)

### Changes Made

#### image_size Parameter Format
**Status**: ✅ CORRECTED

Our code now converts dict-based sizes to fal literal strings where possible:

```python
# Map common sizes to fal literals
size_map = {
    (1024, 1024): "square_hd",
    (1536, 864): "landscape_16_9",
    (864, 1536): "portrait_16_9",
    (1024, 1536): "portrait_4_3",
    (1536, 1024): "landscape_4_3",
}
```

#### seed Parameter Support
**Status**: ✅ ADDED

All generation functions now support `--seed` parameter for reproducibility:
- `fal_generate.py --seed 12345`
- `generate_final_frame.py --seed 12345`
- `sandbox/fal_experiments/generate.py --seed 12345`

#### Nano Banana Pro Parameters
**Status**: ✅ DOCUMENTED

Two valid usage patterns:

1. **Text-to-Image** (identity sheets, style tests):
```python
arguments={
    "prompt": prompt,
    "image_size": "square_hd",  # or dict for custom sizes
    "negative_prompt": negative_prompt,
    "num_inference_steps": 40,
    "guidance_scale": 4.5,
    "seed": seed  # Optional
}
```

2. **Multi-Image Reference** (final frames):
```python
arguments={
    "prompt": prompt,
    "image_urls": [url1, url2],  # Reference images
    "aspect_ratio": "16:9",
    "resolution": "2K",
    "num_images": 1,
    "output_format": "png",
    "seed": seed  # Optional
}
```

---

## Related Files

- Official specs: `references/services/{kling,grok,veo3}/`
- API Index: `references/services/FAL_VIDEO_API_INDEX.md`
- Current code: `VISUAL_PRODUCTION/VIDEO_API_REFERENCE_CORRECTED.md`
- Image generation: `scripts/generate/fal_generate.py`, `scripts/generate/generate_final_frame.py`
