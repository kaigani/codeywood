"""
Dialogue parser for shot list YAML files.

Extracts dialogue lines from shot_list.yaml `dialogue:` fields into
structured DialogueLine objects. Classifies each line for routing:
  - text_tts: V.O., off-screen, whispered internal (Route A)
  - voice_to_voice: On-screen lip-synced dialogue (Route B)
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


# Character ID aliases — normalize to canonical IDs
CHARACTER_ALIASES = {
    "marlowe": "mars",
    "mars": "mars",
    "jonah": "jonah",
    "silas": "silas_human",
    "silas_human": "silas_human",
    "voice-taker": "silas_voicetaker",
    "voice_taker": "silas_voicetaker",
    "silas_voicetaker": "silas_voicetaker",
    "the voice-taker": "silas_voicetaker",
    "hannah": "hannah",
    "hannah_human": "hannah",
    "hannah_threshold": "hannah_threshold",
    "executioner": "executioner",
    "ledger": "narrator",
    "the ledger": "narrator",
    "narrator": "narrator",
}

# Delivery keywords that indicate visual-only (skip TTS)
VISUAL_ONLY_KEYWORDS = {"text on page", "text on screen", "written"}

# Non-speech dialogue values — produce no lines
NON_SPEECH_VALUES = {"none", "breathing", "reaction", "effort"}


@dataclass
class DialogueLine:
    """A single parsed dialogue line ready for TTS processing."""
    character_id: str       # Canonical ID: "mars", "jonah", "narrator", etc.
    text: str               # Actual spoken text
    delivery: str           # "normal", "whispered", "vo", "vo_whispered", "screamed", etc.
    shot_id: int            # Shot this belongs to
    line_index: int         # Order within shot (0-based)
    route: str              # "text_tts" or "voice_to_voice"

    @property
    def tts_text(self) -> str:
        """Text for TTS model. Returns raw text only — voice clone
        doesn't support delivery cues (it reads them as literal text).
        Delivery style should be baked into the voice ref via design_voices.py."""
        return self.text

    @property
    def filename_slug(self) -> str:
        """Short filename-safe slug from the text."""
        words = re.sub(r'[^a-z0-9\s]', '', self.text.lower()).split()
        slug = "_".join(words[:6])
        return slug[:40] if slug else "line"

    @property
    def output_filename(self) -> str:
        """Standard output filename for this line."""
        return f"shot{self.shot_id:02d}_{self.character_id}_{self.filename_slug}.wav"


def _normalize_character(raw_name: str) -> str:
    """Normalize a character name to canonical ID."""
    key = raw_name.strip().lower().replace("'", "").replace('"', '')
    return CHARACTER_ALIASES.get(key, key.replace(" ", "_"))


def _classify_delivery(raw_delivery: str) -> str:
    """Classify delivery from parenthetical text."""
    d = raw_delivery.lower().strip()
    if "v.o" in d and "whisper" in d:
        return "vo_whispered"
    if "v.o" in d or "voice over" in d or "voiceover" in d:
        return "vo"
    if "internal" in d or "monologue" in d:
        return "vo"
    if "whisper" in d:
        return "whispered"
    if "scream" in d or "shout" in d or "yell" in d:
        return "screamed"
    if "murmur" in d or "mutter" in d:
        return "whispered"
    return "normal"


def _is_visual_only(raw_delivery: str) -> bool:
    """Check if delivery indicates visual-only (no TTS needed)."""
    d = raw_delivery.lower()
    return any(kw in d for kw in VISUAL_ONLY_KEYWORDS)


def _determine_route(delivery: str) -> str:
    """Determine TTS route based on delivery type."""
    if delivery in ("vo", "vo_whispered"):
        return "text_tts"
    # On-screen dialogue defaults to voice_to_voice
    return "voice_to_voice"


def _extract_text(raw_text: str) -> str:
    """Extract clean text from quoted dialogue."""
    # Remove surrounding quotes (single or double)
    text = raw_text.strip()
    if (text.startswith("'") and text.endswith("'")) or \
       (text.startswith('"') and text.endswith('"')):
        text = text[1:-1]
    return text.strip()


def _split_on_pauses(text: str) -> List[str]:
    """Split text on [pause] markers into separate segments."""
    parts = re.split(r'\[pause\]', text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def parse_dialogue_value(
    dialogue_value: str,
    shot_id: int,
    shot_characters: List[str] = None,
) -> List[DialogueLine]:
    """
    Parse a single dialogue: field value into DialogueLine(s).

    Handles formats:
      - "none" / "breathing" / "reaction" / "effort" -> empty list
      - "Character: 'text'" -> normal delivery
      - "Character (V.O. whispered): 'text'" -> vo_whispered delivery
      - "Character (delivery): 'text'" -> classified delivery
      - "scripted: 'text'" -> infer character from shot_characters
      - "Ledger (text on page): 'text'" -> narrator, text_tts route
    """
    if not dialogue_value or not isinstance(dialogue_value, str):
        return []

    value = dialogue_value.strip()

    # Non-speech values
    if value.lower() in NON_SPEECH_VALUES:
        return []

    lines = []
    line_index = 0

    # Pattern: "Character (delivery): 'text'" or "Character: 'text'"
    # Also handles: "scripted: 'text'"
    pattern = re.compile(
        r"^([\w\s\-']+?)"           # Character name (lazy to avoid eating delivery)
        r"(?:\s*\(([^)]+)\))?"       # Optional (delivery) in parentheses
        r"\s*:\s*"                    # Colon separator
        r"['\"](.+?)['\"]"           # Quoted text (single or double quotes)
        r"\s*$",                      # End
        re.DOTALL
    )

    match = pattern.match(value)
    if match:
        raw_char = match.group(1).strip()
        raw_delivery = match.group(2) or ""
        raw_text = match.group(3).strip()

        # Handle "scripted" as character name
        if raw_char.lower() == "scripted":
            if shot_characters and len(shot_characters) > 0:
                character_id = _normalize_character(shot_characters[0])
            else:
                character_id = "unknown"
        else:
            character_id = _normalize_character(raw_char)

        # Check for visual-only delivery (e.g., "text on page")
        if _is_visual_only(raw_delivery):
            # Ledger text → read by narrator voice
            if character_id == "narrator" or raw_char.lower() in ("ledger", "the ledger"):
                character_id = "narrator"
            delivery = "vo"
            route = "text_tts"
        else:
            delivery = _classify_delivery(raw_delivery) if raw_delivery else "normal"
            route = _determine_route(delivery)

        # Split on [pause] markers
        text_segments = _split_on_pauses(raw_text)

        for segment in text_segments:
            text = _extract_text(segment)
            if text:
                lines.append(DialogueLine(
                    character_id=character_id,
                    text=text,
                    delivery=delivery,
                    shot_id=shot_id,
                    line_index=line_index,
                    route=route,
                ))
                line_index += 1

    return lines


def parse_shot_dialogue(shot: dict) -> List[DialogueLine]:
    """Parse dialogue from a single shot dict."""
    dialogue_value = shot.get("dialogue")
    if not dialogue_value:
        return []

    shot_id = shot.get("id", 0)
    shot_characters = shot.get("characters", [])

    return parse_dialogue_value(dialogue_value, shot_id, shot_characters)


def parse_scene_dialogue(shots: list) -> List[DialogueLine]:
    """Parse all dialogue lines from a list of shots."""
    all_lines = []
    for shot in shots:
        all_lines.extend(parse_shot_dialogue(shot))
    return all_lines


def get_speakable_lines(shots: list) -> List[DialogueLine]:
    """Get all lines that need audio generated (both routes)."""
    return parse_scene_dialogue(shots)


def get_text_tts_lines(shots: list) -> List[DialogueLine]:
    """Get only V.O./off-screen lines (Route A: text TTS)."""
    return [line for line in parse_scene_dialogue(shots) if line.route == "text_tts"]


def get_voice_to_voice_lines(shots: list) -> List[DialogueLine]:
    """Get only on-screen lip-synced lines (Route B: voice-to-voice)."""
    return [line for line in parse_scene_dialogue(shots) if line.route == "voice_to_voice"]
