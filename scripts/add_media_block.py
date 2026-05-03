#!/usr/bin/env python3
"""Add media: block to every v5 persona YAML based on INTROS content."""
import re
from pathlib import Path

ROOT = Path("/Users/kaigani/Documents/PROJECTS/DEVELOPMENT/260125 codeywood")
PERSONAS = ROOT / "skills/writer/personas"
INTROS = ROOT / "projects/260414-writer-introductions/INTROS"
MEDIA_ROOT = PERSONAS / "media"


def parse_intro(md_path: Path) -> dict:
    text = md_path.read_text()
    out = {}
    current = None
    buf = []
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+)', line)
        if m:
            if current:
                out[current] = "\n".join(buf).strip()
                buf = []
            current = m.group(1).strip()
        else:
            if current:
                buf.append(line)
    if current:
        out[current] = "\n".join(buf).strip()
    return out


def main():
    updated = 0
    skipped = 0
    missing_intro = []

    for yaml_path in sorted(PERSONAS.glob("*.yaml")):
        if yaml_path.name.startswith("_"):
            continue
        yaml_id = yaml_path.stem
        # Skip legacy YAMLs with no media folder
        if not (MEDIA_ROOT / yaml_id).exists():
            missing_intro.append(yaml_id)
            continue

        intro_id = yaml_id.replace("_", "-", 1)  # first underscore after id stays
        # Actually: dashes only where INTROS uses them in name slug
        # INTROS uses dash everywhere after the numeric id: 05_oskar-brandt.md
        parts = yaml_id.split("_", 1)
        if len(parts) == 2:
            intro_id = f"{parts[0]}_{parts[1].replace('_', '-')}"
        md_path = INTROS / f"{intro_id}.md"
        if not md_path.exists():
            missing_intro.append(yaml_id)
            continue

        intro = parse_intro(md_path)
        dialogue = intro.get("Dialogue", "").strip().strip('"')
        # Tagline = everything after the "I'm {Name}." or "{Name}." prefix
        tagline = re.sub(r'^(?:I\'m |Hi — I\'m |Hi, I\'m |Call me )?[^.]+\.\s*', '', dialogue, count=1).strip()
        if not tagline:
            tagline = dialogue
        genre = intro.get("Genre", "").strip()
        medium = intro.get("Medium", "").strip()

        text = yaml_path.read_text()
        if "\nmedia:\n" in text or text.startswith("media:\n"):
            skipped += 1
            continue

        block = (
            "\nmedia:\n"
            f"  portrait: media/{yaml_id}/portrait.jpg\n"
            f"  intro_clip: media/{yaml_id}/intro.mp4\n"
            f"  voice_sample: media/{yaml_id}/voice.wav\n"
            f'  tagline: "{tagline}"\n'
            f'  genre: "{genre}"\n'
            f'  medium: "{medium}"\n'
        )
        # Append cleanly (ensure trailing newline first)
        if not text.endswith("\n"):
            text += "\n"
        yaml_path.write_text(text + block)
        updated += 1
        print(f"  +media: {yaml_id}  (tagline: \"{tagline[:50]}...\")")

    print(f"\nUpdated: {updated}  Skipped (already had media): {skipped}")
    if missing_intro:
        print(f"No intro/media dir (legacy, skipped): {missing_intro}")


if __name__ == "__main__":
    main()
