# Nano Banana Pro (Recraft v3) Best Practices

## Overview

Nano Banana Pro (accessed via fal.ai as recraft-v3) is our primary image generation model. This document captures best practices for achieving consistent, high-quality results.

## API Endpoint

```
fal-ai/recraft-v3
```

## Default Parameters

```json
{
  "image_size": {"width": 1024, "height": 1024},
  "num_inference_steps": 28,
  "guidance_scale": 3.5,
  "num_images": 1,
  "safety_tolerance": "2",
  "output_format": "png"
}
```

## Reference-Based Generation

The key to consistency is using reference images effectively.

### Reference Weight Guidelines

| Use Case | Weight | Notes |
|----------|--------|-------|
| Exact character reproduction | 0.95 | Minimal variation |
| Character with expression change | 0.90 | Allow subtle changes |
| Character with outfit change | 0.85-0.90 | Allow clothing variation |
| Character with pose change | 0.80-0.85 | Allow body position |
| Location consistency | 0.85 | Maintain key features |
| Style reference | 0.75-0.85 | Aesthetic consistency |

### Multiple References

When using multiple reference images:
- Character reference takes priority
- Location reference provides context
- Style reference sets aesthetic

## Prompt Structure

### Effective Order

1. Subject description (who/what)
2. Action/pose
3. Environment/location
4. Lighting
5. Camera/composition
6. Style keywords

### Example Structure

```
[CHARACTER DESCRIPTION], [ACTION/POSE], [OUTFIT],
in [LOCATION], [TIME OF DAY] lighting,
[SHOT TYPE], [COMPOSITION NOTES],
[STYLE KEYWORDS]
```

## Negative Prompts

### Always Include
```
deformed, distorted, disfigured, poorly drawn, bad anatomy,
wrong anatomy, extra limb, missing limb, floating limbs,
disconnected limbs, mutation, ugly, disgusting, blurry,
out of focus, bad art, beginner, amateur
```

### For Characters
```
multiple people, clone, duplicate, twins (unless intended),
wrong proportions, asymmetrical face (unless character trait)
```

### For Locations
```
people, figures, crowds (for empty location refs),
distorted architecture, impossible geometry
```

## Common Issues and Solutions

### Character Drift

**Problem**: Character looks different across generations

**Solutions**:
1. Increase reference weight to 0.95
2. Be more specific in character description
3. Use turnaround as reference for all generations
4. Include key distinguishing features in every prompt

### Location Inconsistency

**Problem**: Location features change between shots

**Solutions**:
1. Use establishing shot as reference for all angles
2. Describe key architectural features explicitly
3. Reference specific areas rather than full location
4. Maintain consistent lighting description

### Pose Distortion

**Problem**: Dynamic poses create anatomical issues

**Solutions**:
1. Lower reference weight to allow pose flexibility
2. Be explicit about limb positions
3. Describe weight distribution
4. Generate simpler poses first, build complexity

### Style Mismatch

**Problem**: Generated images don't match show aesthetic

**Solutions**:
1. Use consistent style keywords
2. Include lighting description
3. Reference color palette explicitly
4. Use style reference image

## Optimal Settings by Use Case

### Character Turnaround (No Reference)
```json
{
  "image_size": {"width": 1536, "height": 1024},
  "num_inference_steps": 30,
  "guidance_scale": 4.0
}
```

### Expression Pack (With Reference)
```json
{
  "image_size": {"width": 1024, "height": 1024},
  "num_inference_steps": 28,
  "guidance_scale": 3.5,
  "reference_weight": 0.95
}
```

### Dynamic Pose (With Reference)
```json
{
  "image_size": {"width": 1024, "height": 1024},
  "num_inference_steps": 28,
  "guidance_scale": 3.5,
  "reference_weight": 0.80
}
```

### Establishing Shot (No Reference)
```json
{
  "image_size": {"width": 1920, "height": 1080},
  "num_inference_steps": 28,
  "guidance_scale": 3.5
}
```

### Scene Shot (With References)
```json
{
  "image_size": {"width": 1920, "height": 1080},
  "num_inference_steps": 28,
  "guidance_scale": 3.5,
  "character_reference_weight": 0.90,
  "location_reference_weight": 0.85
}
```

## Iteration Strategy

### First Pass
- Generate with standard settings
- Review for major issues
- Note what works and what doesn't

### Refinement
- Adjust prompts based on results
- Fine-tune reference weights
- Add specificity where needed

### Regeneration
- If quality is low, don't just retry
- Adjust parameters or prompt
- Consider different reference angles

## Quality Checklist

Before accepting a generated image:

- [ ] Subject matches description
- [ ] Face matches reference (if character)
- [ ] Anatomy is correct
- [ ] Composition matches intent
- [ ] Style matches show aesthetic
- [ ] No obvious artifacts
- [ ] Lighting is appropriate

## Notes

- Results can vary between runs—this is normal
- Some concepts require multiple attempts
- Reference images are more reliable than prompt descriptions
- Build a library of successful prompts
- Document what works for reuse
