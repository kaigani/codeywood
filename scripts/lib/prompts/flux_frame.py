"""
Flux Klein/Dev frame generation prompt template.

Single frozen moment — no motion, no sound, no camera direction.
Uses frozen_moment field instead of action. Warns on transitional language.
"""

import re

from ._types import PromptInputs, PromptResult

DEFAULT_NEGATIVE = (
    "cartoon, anime, illustration, painting, sketch, multiple panels, "
    "triptych, split image, text overlay, watermark"
)

# Words that suggest motion/transition — shouldn't appear in frame prompts
TRANSITIONAL_PATTERNS = [
    r"\bbursts?\b",
    r"\brushes?\b",
    r"\bpulls?\b",
    r"\bdrops?\b",
    r"\bturns?\b",
    r"\bspins?\b",
    r"\bleaps?\b",
    r"\bruns?\b",
    r"\bclimbs?\b",
    r"\breaches?\b",
    r"\bmoving\b",
    r"\bslowly\b",
    r"\bbegins? to\b",
    r"\bstarts? to\b",
    r"\bthen\b",
    r"\bshe/he \w+s\b",
]


def compose(inputs: PromptInputs) -> PromptResult:
    """Compose a single-frame prompt for Flux image generation.

    Uses frozen_moment (required) instead of action.
    Omits: dialogue, camera, sound (irrelevant for static images).
    """
    parts = []
    warnings = []

    # 1. Shot type + setting
    if inputs.shot_type:
        parts.append(f"{inputs.shot_type}, {inputs.setting.description}")
    else:
        parts.append(inputs.setting.description)

    # 2. Characters — full inline descriptions
    for char in inputs.characters:
        parts.append(char.description)

    # 3. Frozen moment (required for frames) + body language
    moment = inputs.frozen_moment or inputs.action
    if not inputs.frozen_moment:
        warnings.append("No frozen_moment provided — using action field (may contain motion language)")

    parts.append(moment)
    if inputs.body_language:
        parts.append(inputs.body_language)

    # 4. Lighting
    if inputs.lighting:
        parts.append(inputs.lighting)

    # Omit: dialogue, sound, camera (not relevant for static frames)
    if inputs.dialogue:
        warnings.append("Dialogue was provided but omitted — not relevant for static frames")
    if inputs.sound:
        warnings.append("Sound was provided but omitted — not relevant for static frames")
    if inputs.camera:
        warnings.append("Camera was provided but omitted — not relevant for static frames")

    prompt = ". ".join(p.rstrip(". ") for p in parts if p) + "."

    # Check for transitional language
    for pattern in TRANSITIONAL_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            match = re.search(pattern, prompt, re.IGNORECASE).group()
            warnings.append(f"Transitional language detected: '{match}' — frame prompts should describe a single frozen moment")
            break  # One warning is enough

    char_count = len(prompt)

    return PromptResult(
        prompt=prompt,
        char_count=char_count,
        warnings=warnings,
        negative_prompt=DEFAULT_NEGATIVE,
    )
