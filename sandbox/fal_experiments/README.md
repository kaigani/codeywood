# FAL.ai Experimentation Sandbox

**Project**: Hellmouth Cowboy
**Focus**: Style exploration and hero character shots
**Approach**: Style DNA template methodology

---

## Setup

### 1. Install Dependencies

```bash
pip install fal-client python-dotenv requests
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### 2. Configure API Key

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Get your FAL.ai API key from: https://fal.ai/dashboard/keys

3. Edit `.env` and add your key:
   ```
   FAL_KEY=your_actual_key_here
   ```

---

## Style DNA Approach

Rather than referencing IP names like "Castlevania" or "Samurai Jack" directly, we use a **Style DNA template** that deconstructs visual style into technical components:

**Format:**
```
[Subject], [Medium/Era], [Line-work/Texture], [Lighting/Rendering], [Color Palette]
```

### Current Templates

**gothic_western** - Primary Hellmouth Cowboy style
- Medium: Dark animated (Castlevania gothic + Sergio Leone western)
- Lines: Heavy ink outlines with weight variation, crisp silhouettes
- Lighting: Dramatic rim lighting, deep cel-shaded shadows, high contrast
- Palette: Desaturated dusty with deep blacks and blood-red accents

**samurai_jack_minimal** - Alternate exploration
- Medium: 2D animated, western noir
- Lines: Clean vector, thick consistent outlines, flat graphic forms
- Lighting: Stark silhouettes, two-tone shading, pure blacks
- Palette: Extremely limited (blacks, grays, single accent)

**base** - Generic starting point
- Medium: 1990s dark animated series, cel with digital compositing
- Lines: Clean vector with varied weight
- Lighting: Cel-shaded, harsh directional, minimal mid-tones
- Palette: Limited desaturated earth tones with blood-red

---

## Usage

### List Available Tests

```bash
python generate.py --list
```

### Run Individual Test

**Style exploration:**
```bash
python generate.py --test style_dna_1
python generate.py --test style_dna_2
python generate.py --test style_dna_3
```

**Hero shots:**
```bash
python generate.py --test hero_nameless_entrance
python generate.py --test hero_nameless_draw
python generate.py --test hero_nameless_quiet
```

### Run All Tests

```bash
python generate.py --test all_style    # All style exploration
python generate.py --test all_hero     # All hero shots
```

---

## Current Tests

### Style Exploration

| Test ID | Name | Style DNA | Subject |
|---------|------|-----------|---------|
| `style_dna_1` | Gothic Western - Lone Figure | gothic_western | Gunslinger silhouetted at dusk |
| `style_dna_2` | Minimal Noir - Town Aftermath | samurai_jack_minimal | Abandoned town, geometric shapes |
| `style_dna_3` | Base DNA - Gunfight Aftermath | base | Smoking revolvers, blood, aftermath |

### Hero Shots (Nameless)

| Test ID | Name | Type | Composition |
|---------|------|------|-------------|
| `hero_nameless_entrance` | The Entrance | Arrival/reveal | Wide, low angle, silhouette |
| `hero_nameless_draw` | Signature Action | Gun draw | Medium, motion blur, hands focus |
| `hero_nameless_quiet` | Quiet Moment | Vulnerability | Close-medium, firelight, isolation |

---

## Results

Generated images and metadata saved to `results/`:
- `{test_id}_{timestamp}.png` - Generated image
- `{test_id}_{timestamp}.json` - Metadata (prompt, settings, URL)

---

## Workflow

1. **Style Exploration Phase**
   - Run all style DNA tests
   - Review results
   - Identify which template produces best results
   - Refine winning template
   - Extract color palette from best result

2. **Hero Shot Phase**
   - Run hero shot tests with locked style DNA
   - Evaluate which captures character essence
   - Select winner for each character
   - Use as character reference (0.85-0.90 weight)

3. **Identity Sheet Phase**
   - Use locked style + hero shot as references
   - Generate composite identity sheets
   - Iterate based on learnings

---

## Adding New Tests

Edit `generate.py`:

**New style test:**
```python
STYLE_TESTS["my_test_id"] = {
    "name": "Test Name",
    "style_dna": "gothic_western",  # or other template
    "subject": "What to generate",
    "composition": "Framing and camera",
    "mood": "Emotional quality",
    "settings": {
        "image_size": {"width": 1536, "height": 864},
        "num_inference_steps": 35,
        "guidance_scale": 4.0,
    }
}
```

**New Style DNA template:**
```python
STYLE_DNA_TEMPLATES["my_style"] = {
    "medium_era": "...",
    "linework_texture": "...",
    "lighting_rendering": "...",
    "color_palette": "...",
}
```

---

## Next Steps

- [ ] Run initial style DNA tests
- [ ] Evaluate results against Hellmouth Cowboy aesthetic
- [ ] Refine winning style DNA template
- [ ] Extract hex palette from best style result
- [ ] Run hero shots with locked style
- [ ] Select winning hero shot per character
- [ ] Document findings in project STYLE_PROMPTS.md
