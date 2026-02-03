# Nano Banana Pro (recraft-v3) Limitations

> Known issues and workarounds. Updated 2026-01.

## Layout Issues

### Multi-View Consistency
**Problem:** Even with detailed layout prompts, views may not perfectly match.
**Workaround:** Generate multiple candidates, select best. Use high character reference weight (0.90+) for subsequent generations.

### Complex Grid Layouts
**Problem:** More than 6-8 panels often results in confused composition.
**Workaround:** Split into multiple generations. Core identity sheet + separate expression pack.

---

## Style Limitations

### Text Rendering
**Problem:** Cannot reliably render readable text in images.
**Workaround:** Add text in post-processing. Leave space for text overlays.

### Exact Color Matching
**Problem:** Hex palettes influence but don't guarantee exact colors.
**Workaround:** Use color grading as constraint, accept variations. Post-process for exact brand colors.

### Extreme Stylization
**Problem:** Very abstract or experimental styles may be inconsistent.
**Workaround:** Use more literal style references. Break into simpler elements.

---

## Reference Limitations

### Reference Weight Ceiling
**Problem:** Very high reference weights (0.98+) can cause artifacts or over-fitting.
**Workaround:** Keep style refs at 0.85-0.90, character refs at 0.90-0.95 max.

### Conflicting References
**Problem:** Multiple references with different styles confuse the model.
**Workaround:** Ensure all references share consistent style. Use single style reference.

### Reference Resolution
**Problem:** Low-res references yield low-quality details.
**Workaround:** Use highest resolution references available. Upscale before using as reference.

---

## Content Limitations

### Hands and Fingers
**Problem:** Hands often have issues (extra fingers, awkward poses).
**Workaround:** Explicitly describe hand position. Reference specific hand gestures. Plan for manual touchup.

### Extreme Poses
**Problem:** Dynamic action poses may have anatomical issues.
**Workaround:** Use reference images for complex poses. Keep action poses simpler in reference sheets.

### Multiple Characters
**Problem:** Two+ characters in one image often have consistency issues.
**Workaround:** Generate characters separately. Composite in post if needed for relationship shots.

---

## Technical Limitations

### Aspect Ratio Constraints
**Problem:** Some aspect ratios perform better than others.
**Best:** 3:2, 16:9, 4:3
**Avoid:** Extreme ratios (1:4, 4:1)

### Generation Time
**Problem:** Higher step counts significantly increase generation time.
**Default:** 28 steps (good quality/speed balance)
**Hero shots:** 35 steps (slightly better but slower)

### Batch Consistency
**Problem:** Multiple generations from same prompt can vary significantly.
**Workaround:** Generate 3-5 candidates, select best. Lock style reference for subsequent batches.

---

## Platform-Specific Notes

### fal.ai Implementation
- Rate limits apply (check current tier)
- Async generation recommended for batches
- Results cached briefly; re-request may return same image

### Comparison to Other Services
| Issue | Nano Banana Pro | Midjourney | Flux |
|-------|-----------------|------------|------|
| Text in images | Poor | Fair | Good |
| Hands/fingers | Fair | Fair | Good |
| Style consistency | Excellent | Good | Fair |
| Layout control | Good | Poor | Fair |
| Color control | Excellent | Fair | Fair |
