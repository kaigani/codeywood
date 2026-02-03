# Animation Modality: Visual Reference Approach

> Strategy for capturing style and building visual consistency for animated productions.

## Core Principle

Animation style is **designed**, not captured. Every visual element is a deliberate choice. Your reference process should focus on establishing and documenting those design decisions before generating character/location refs.

---

## Style Reference Strategy

### What to Capture

Unlike live action (which references real-world camera/film characteristics), animation style references should capture:

| Element | What to Define | Example |
|---------|---------------|---------|
| **Line Work** | Weight, consistency, taper, style | Clean vector vs. sketchy pencil vs. brush stroke |
| **Color Palette** | Primary, secondary, accent, shadow colors | Extract hex codes from key frames |
| **Shading Style** | Cel, soft gradient, ambient occlusion, flat | Hard 2-tone vs. soft falloff |
| **Shape Language** | Angular vs. rounded, proportions, silhouette | Chunky geometric vs. flowing organic |
| **Texture Treatment** | Clean vs. textured, paper grain, noise | Flat color vs. painted texture |
| **Background Style** | Detail level, atmosphere, perspective | Detailed paintings vs. minimal graphic |

### Reference Types to Generate

**Phase 1: Style Exploration**
1. **Mood frames** - Key emotional moments in target style
2. **Color keys** - Palette tests across different scenes (day/night/emotional)
3. **Lighting studies** - How light and shadow work in this style

**Phase 2: Hero Character Shots**
1. **Character key art** - Each main character in a defining moment
2. **Relationship shots** - Characters interacting (establishes relative scale, style interaction)
3. **Expression range** - Emotional extremes (tests how style handles expression)

**Phase 3: Character Identity Sheets**
1. **Multi-view reference** - The composite layout approach (see Nano Banana Pro techniques)
2. **Expression pack** - Full range of emotions
3. **Outfit variants** - If applicable

**Phase 4: Location References**
1. **Establishing shots** - Wide shots of key locations
2. **Key areas** - Important staging areas within locations
3. **Time/lighting variants** - Same location in different conditions

---

## Animation-Specific Vocabulary

### Line Art Descriptors
```
clean vector lines
consistent line weight
tapered brush strokes
sketchy pencil texture
thick outlines with thin details
no outlines / painterly edges
```

### Shading Descriptors
```
cel-shaded with hard shadow edge
two-tone shading
soft gradient shading
ambient occlusion on forms
flat color / no shading
cross-hatched shadows
```

### Color/Palette Descriptors
```
limited color palette
high saturation / vibrant colors
desaturated / muted tones
monochromatic with accent color
complementary color harmony
analogous warm palette
```

### Style References (Touchstones)
```
Castlevania (2017) - Dark, detailed, cinematic anime
Samurai Jack - Graphic, minimal, strong silhouettes
Spider-Verse - Textured, stylized, comic-influenced
Arcane - Painted, atmospheric, high detail
Primal - Rough, expressive, limited palette
```

---

## Prompt Pattern for Animation

```
[SCENE/CHARACTER DESCRIPTION]

[STYLE TOUCHSTONE] style. [LINE_WORK_DESCRIPTION]. [SHADING_STYLE]. [COLOR_DESCRIPTION].

[COMPOSITION/FRAMING]

[MOOD/ATMOSPHERE]

Color grading: [HEX_PALETTE]
```

**Example:**
```
A lone gunslinger standing at the edge of a corrupted frontier town at sunset.

Dark animated style inspired by Castlevania and Samurai Jack. Clean lines with
varied weight, thicker on silhouette edges. Cel-shaded with deep shadows,
minimal mid-tones. Desaturated earth tones with blood-red accent.

Wide shot, low angle, figure silhouetted against burning sky. Town buildings
frame the composition, leading eye to central figure.

Atmospheric, ominous, the calm before violence.

Color grading: ["#060910","#0b1220","#081f39","#15406a","#174f7c","#337eb2","#4ca9d2","#56b4d9","#b1cad4","#b9bfc8","#742d4b","#fe9f58"]
```

---

## Common Pitfalls

### Over-specifying
Animation styles are cohesive systems. Don't mix incompatible elements:
- Bad: "Pixar 3D rendering with anime speed lines and watercolor textures"
- Good: "Stylized 3D with soft lighting, inspired by Spider-Verse texture work"

### Ignoring Silhouette
Strong animation design reads in silhouette. Test your character designs as solid black shapes.

### Inconsistent Stylization
If faces are stylized but hands are realistic, it breaks the visual contract. Maintain consistent abstraction level.

---

## Pipeline Integration

1. Lock style with mood frames before any character work
2. Generate hero shots to test character-in-style
3. Extract working color palette from successful generations
4. Use locked style + extracted palette for all subsequent refs
5. Build character identity sheets informed by what worked in hero shots
