# Live Action Modality: Visual Reference Approach

> Strategy for capturing style and building visual consistency for live-action/photorealistic productions.

## Core Principle

Live action style references **real-world tools and techniques**. Your prompts should speak the language of cinematography, photography, and film production. The "style" is defined by camera, lens, film stock, lighting, and color grading choices.

---

## Style Reference Strategy

### What to Capture

| Element | What to Define | Example |
|---------|---------------|---------|
| **Camera/Format** | Sensor size, resolution, aspect ratio | ARRI Alexa, anamorphic 2.39:1 |
| **Lens Characteristics** | Focal length, aperture, bokeh, distortion | 50mm f/1.4, creamy bokeh, slight barrel distortion |
| **Film Stock/Look** | Grain, color science, dynamic range | Kodak Vision3 500T, pushed one stop |
| **Lighting Style** | Natural vs. motivated, contrast ratio, color temp | High contrast, warm practicals, cool fill |
| **Color Grade** | LUT reference, overall treatment | Teal and orange, crushed blacks, lifted highlights |
| **Movement** | Handheld, Steadicam, locked, crane | Documentary handheld with subtle drift |

### Reference Types to Generate

**Phase 1: Cinematography Tests**
1. **Look development frames** - Key scenes in target cinematography
2. **Lighting setups** - Day interior, night exterior, golden hour, etc.
3. **Color grade tests** - Same shot with different treatments

**Phase 2: Cast Visualization**
1. **Screen tests** - Characters in target lighting/framing
2. **Wardrobe tests** - Costume in context
3. **Key moments** - Signature dramatic beats

**Phase 3: Character References**
1. **Headshots** - Multiple angles, neutral lighting for consistency
2. **Full body** - Wardrobe reference
3. **In-scene** - Character in key location

**Phase 4: Location References**
1. **Scout shots** - Wide establishing, key angles
2. **Lighting studies** - Location at different times/conditions
3. **Production stills** - Detailed reference for set dressing

---

## Live Action Vocabulary

### Camera/Format
```
shot on ARRI Alexa 65
shot on RED Komodo 6K
shot on 35mm film
shot on 16mm film (grainier, more organic)
IMAX format
anamorphic widescreen
spherical lens
vintage lens flares
```

### Lens Language
```
50mm lens (natural perspective)
85mm portrait lens
35mm wide (slight distortion, environmental)
24mm wide angle
telephoto compression
shallow depth of field
deep focus (everything sharp)
soft focus
tilt-shift miniature effect
```

### Film Stock/Digital Look
```
Kodak Vision3 500T (tungsten, cinematic)
Kodak Portra 400 (warm skin tones)
Fujifilm Eterna (subtle, natural)
CineStill 800T (halation around lights)
digital cinema clean
film grain texture
pushed film (high contrast, more grain)
cross-processed
```

### Lighting
```
natural window light
golden hour backlight
harsh midday sun
overcast soft light
practical lighting (motivated by in-scene sources)
chiaroscuro (dramatic contrast)
three-point lighting
rim light / edge light
soft key, no fill
```

### Color Grade
```
teal and orange color grade
bleach bypass (desaturated, high contrast)
crushed blacks
lifted shadows
warm highlights, cool shadows
day-for-night
period-accurate color (70s, 80s, etc.)
```

---

## Prompt Pattern for Live Action

```
[SCENE/CHARACTER DESCRIPTION]

Cinematic still, [CAMERA/FORMAT]. [LENS_CHARACTERISTICS]. [LIGHTING_SETUP].

[FILM_STOCK or DIGITAL_LOOK]. [COLOR_GRADE].

[COMPOSITION/FRAMING]

[ATMOSPHERE/MOOD]
```

**Example:**
```
A weathered detective in a rain-soaked alley, cigarette smoke curling up past
neon signs.

Cinematic still, shot on ARRI Alexa with Cooke anamorphic lenses. 40mm,
f/2.8, shallow depth of field with oval bokeh. Practical lighting from neon
signs, harsh top light from fire escape, no fill.

Kodak Vision3 500T pushed one stop for grain and contrast. Teal and orange
grade, crushed blacks, halation around neon.

Medium shot, low angle, figure framed by alley walls. Neon reflections on
wet pavement.

Neo-noir atmosphere, humid, dangerous.
```

---

## Common Pitfalls

### Mixed Format Language
Don't combine incompatible technical specs:
- Bad: "IMAX shot on 16mm film" (impossible)
- Good: "Large format cinematography, clean digital with subtle film grain overlay"

### Lighting Contradictions
Be consistent about light sources:
- Bad: "Harsh noon sun and soft overcast light"
- Good: "Overcast day, soft diffused light, slightly cool"

### Over-Grading Descriptions
Keep color grade suggestions cohesive:
- Bad: "Teal shadows, orange highlights, desaturated, vibrant"
- Good: "Subtle teal in shadows, warm skin tones, slightly desaturated overall"

---

## Pipeline Integration

1. Establish cinematography bible with test frames
2. Lock camera/lens/lighting language before casting visualization
3. Generate cast visualization to test actors in target look
4. Build character reference sheets in consistent lighting
5. Location scouts maintain established look
6. All storyboards/shots reference the cinematography bible
