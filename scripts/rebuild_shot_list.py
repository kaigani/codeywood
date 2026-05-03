#!/usr/bin/env python3
"""
Rebuild shot_list_t2v.yaml from current PITCHES/*.md files.
Preserves id, name, persona, seed, duration, concept.
Updates dialogue and video_prompt from pitch content.
Writes clean YAML with block literal for video_prompt.
"""

import re
import sys
from pathlib import Path
import yaml

PROJECT_DIR = Path("/Users/kaigani/Documents/PROJECTS/DEVELOPMENT/260125 codeywood/projects/260414-elevator-pitch-test")
PITCHES_DIR = PROJECT_DIR / "PITCHES"
SHOT_LIST_PATH = PROJECT_DIR / "PRODUCTION/EP01/sc01/shot_list_t2v.yaml"


def build_video_prompt(character, set_desc, lighting, direction, monologue, ambient):
    """Build video prompt, stripping trailing periods from fields to avoid double-dots."""
    def rstrip_dot(s):
        return s.strip().rstrip('.')
    parts = [
        "Medium shot, waist-up, subject looking directly into the lens, locked static camera.",
        rstrip_dot(character) + ".",
        rstrip_dot(set_desc) + ".",
        rstrip_dot(lighting) + ".",
        rstrip_dot(direction) + ".",
        f'The actor delivers the pitch: "{monologue}".',
        f"Ambient only — {ambient}, no music, no score.",
        "Static camera, no movement, no cuts, locked medium shot held for the full fifteen-second duration.",
    ]
    return " ".join(parts)


def extract_section(text, header):
    """Extract content under a ## Header section."""
    pattern = rf"## {re.escape(header)}\s*\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return None
    content = m.group(1).strip()
    # Remove single-line italic wrapping
    content = re.sub(r'^\*(.+)\*$', r'\1', content, flags=re.MULTILINE)
    return content


def derive_lighting(set_desc):
    s = set_desc.lower()
    if any(w in s for w in ['fluorescent', 'strip light', 'corridor', 'hospital', 'break room']):
        return "Practical cool fluorescent overhead, harsh flat light"
    elif any(w in s for w in ['night', 'evening', 'sodium', 'neon', 'street lamp']):
        return "Practical sodium street lamp or neon from outside, deep shadow fill"
    elif any(w in s for w in ['church', 'chapel', 'sanctuary', 'altar']):
        return "Practical warm afternoon window light from the left, soft diffuse shadow"
    elif any(w in s for w in ['construction', 'scaffold', 'demolish', 'winter sky', 'rebar']):
        return "Diffuse winter overcast daylight, flat grey key from above"
    elif any(w in s for w in ['grill', 'heat lamp', 'pass', 'ticket rail']):
        return "Practical warm orange heat-lamp key from the pass above, stainless steel backlight"
    elif any(w in s for w in ['warehouse', 'industrial', 'factory', 'workshop']):
        return "Practical tungsten work lamp key, cool ambient from high windows"
    elif any(w in s for w in ['bar', 'pub', 'tavern', 'club', 'lounge']):
        return "Practical warm bar back-lighting, low key ambience"
    elif any(w in s for w in ['studio', 'broadcast', 'monitor', 'control room', 'screen']):
        return "Practical monitor glow blue-white key, cool overhead fill"
    elif any(w in s for w in ['kitchen', 'domestic', 'home', 'living room', 'bedroom']):
        return "Practical warm overhead light, soft window fill"
    elif any(w in s for w in ['office', 'open plan', 'cubicle']):
        return "Practical cool overhead fluorescent, flat office light"
    elif any(w in s for w in ['classroom', 'lecture', 'school']):
        return "Practical fluorescent overhead, flat daylight from windows"
    elif any(w in s for w in ['afternoon', 'morning', 'daylight', 'sunlight', 'window']):
        return "Practical natural daylight from window, soft directional key"
    else:
        return "Practical available light, naturalistic exposure"


def derive_ambient(set_desc):
    s = set_desc.lower()
    # Commercial kitchen must match restaurant-specific cues, not generic "kitchen"
    if any(w in s for w in ['grill', 'ticket rail', 'heat lamp', 'three hundred covers', 'commercial kitchen']):
        return "grill hiss, ticket machine chatter, distant pan clatter"
    elif any(w in s for w in ['church', 'chapel', 'sanctuary']):
        return "faint hum in the walls, creak in the pews, distant street noise"
    elif any(w in s for w in ['hospital', 'break room', 'vending']):
        return "vending machine hum, distant hospital corridor, fluorescent ballast tick"
    elif any(w in s for w in ['construction', 'scaffold', 'demolish', 'rebar']):
        return "distant machinery, wind across open stonework, a structural creak"
    elif any(w in s for w in ['corridor', 'government', 'press office', 'evidence']):
        return "distant air conditioning, muffled corridor sounds, fluorescent hum"
    elif any(w in s for w in ['bar', 'pub', 'tavern', 'lounge']):
        return "low murmur of patrons, glass on wood, distant traffic"
    elif any(w in s for w in ['night', 'street', 'exterior', 'outdoor']):
        return "ambient city night noise, distant traffic, wind"
    elif any(w in s for w in ['domestic', 'home', 'living room', 'bedroom', 'kitchen at']):
        return "tap dripping, soft tick of a clock, faint outside traffic"
    elif any(w in s for w in ['warehouse', 'industrial', 'factory']):
        return "ventilation hum, distant industrial ambient, metal settling"
    elif any(w in s for w in ['studio', 'broadcast', 'control room']):
        return "monitor hum, ventilation fan, distant building HVAC"
    elif any(w in s for w in ['classroom', 'school', 'lecture']):
        return "empty corridor sounds, distant footsteps, fluorescent hum"
    elif any(w in s for w in ['office', 'open plan']):
        return "distant air conditioning, keyboard clicks, muffled phone"
    else:
        return "ambient room tone, subtle environmental noise"


def parse_pitch(md_path):
    """Parse a pitch markdown file."""
    text = md_path.read_text(encoding='utf-8')

    character = extract_section(text, "Character (visual context only)")
    set_desc = extract_section(text, "Set (visual context only)")
    direction = extract_section(text, "Direction")
    monologue_raw = extract_section(text, "Monologue")

    missing = []
    if not character: missing.append("Character")
    if not set_desc: missing.append("Set")
    if not direction: missing.append("Direction")
    if not monologue_raw: missing.append("Monologue")
    if missing:
        raise ValueError(f"Missing sections: {missing}")

    # Clean monologue
    monologue = monologue_raw.strip()
    if monologue.startswith('"') and monologue.endswith('"'):
        monologue = monologue[1:-1]
    monologue = re.sub(r'\*(.+?)\*', r'\1', monologue)

    lighting = derive_lighting(set_desc)
    ambient = derive_ambient(set_desc)
    video_prompt = build_video_prompt(character, set_desc, lighting, direction, monologue, ambient)

    return {'dialogue': monologue, 'video_prompt': video_prompt}


# ── Custom YAML writer ────────────────────────────────────────────────────────

def yaml_str(s):
    """Emit a YAML double-quoted scalar, escaping special chars."""
    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'

def yaml_block_literal(s, indent=4):
    """Emit a YAML block literal scalar (|) at given indent."""
    prefix = ' ' * indent
    lines = s.splitlines()
    body = '\n'.join(prefix + line for line in lines)
    return f'|\n{body}\n'

def write_shot_list(path, metadata, shots):
    """Write the shot list YAML manually for clean, readable output."""
    lines = []

    # Metadata block
    lines.append('t2v_metadata:')
    lines.append(f'  project: {metadata["project"]}')
    lines.append(f'  scene: {metadata["scene"]}')
    lines.append(f'  description: {yaml_str(metadata["description"])}')
    lines.append(f'  negative_prompt: {yaml_str(metadata["negative_prompt"])}')
    lines.append(f'  default_duration: {metadata["default_duration"]}')
    lines.append(f'  default_width: {metadata["default_width"]}')
    lines.append(f'  default_height: {metadata["default_height"]}')
    lines.append(f'  default_static_camera: {metadata["default_static_camera"]}')
    lines.append('')
    lines.append('shots:')

    for shot in shots:
        concept_val = 'null' if shot.get('concept') is None else yaml_str(str(shot['concept']))
        lines.append(f'  - id: {shot["id"]}')
        lines.append(f'    name: {yaml_str(shot["name"])}')
        lines.append(f'    persona: {yaml_str(shot["persona"])}')
        lines.append(f'    concept: {concept_val}')
        lines.append(f'    dialogue: {yaml_str(shot["dialogue"])}')
        lines.append(f'    duration: {shot["duration"]}')
        lines.append(f'    seed: {shot["seed"]}')

        # video_prompt as block literal
        prompt_block = yaml_block_literal(shot['video_prompt'], indent=6)
        lines.append(f'    video_prompt: {prompt_block}')

    content = '\n'.join(lines) + '\n'
    path.write_text(content, encoding='utf-8')


def main():
    # Load existing YAML (to read structure/metadata)
    with open(SHOT_LIST_PATH, 'r') as f:
        data = yaml.safe_load(f)

    meta = data['t2v_metadata']
    shots = data['shots']

    updated = 0
    errors = []

    for shot in shots:
        name = shot['name']
        pitch_path = PITCHES_DIR / f"{name}.md"

        if not pitch_path.exists():
            errors.append(f"MISSING: {pitch_path.name}")
            continue

        try:
            parsed = parse_pitch(pitch_path)
            shot['dialogue'] = parsed['dialogue']
            shot['video_prompt'] = parsed['video_prompt']
            updated += 1
        except Exception as e:
            errors.append(f"ERROR in {name}: {e}")

    print(f"Updated: {updated} / {len(shots)} shots")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  {e}")
        if any(e.startswith('ERROR') for e in errors):
            sys.exit(1)

    # Write clean YAML
    write_shot_list(SHOT_LIST_PATH, meta, shots)

    # Validate: re-parse
    with open(SHOT_LIST_PATH, 'r') as f:
        check = yaml.safe_load(f)

    assert len(check['shots']) == len(shots), f"Shot count mismatch: {len(check['shots'])} vs {len(shots)}"
    print(f"Validation OK — {len(check['shots'])} shots parsed cleanly.")

    # Spot-check shot 1
    s1 = check['shots'][0]
    print(f"\nSpot-check shot 1 ({s1['name']}):")
    print(f"  dialogue: {s1['dialogue'][:100]}")
    print(f"  prompt excerpt: {s1['video_prompt'][:150]}")


if __name__ == '__main__':
    main()
