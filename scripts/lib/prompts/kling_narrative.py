"""
Kling v3 narrative mode prompt template.

Uses @ElementN tags for character references instead of inline descriptions.
Hard 2500 char limit. Single prompt field with duration.
"""

from ._types import PromptInputs, PromptResult

DEFAULT_NEGATIVE = "blurry, distorted, low quality, artifacts, text, watermark"

CHAR_LIMIT = 2500


def compose(inputs: PromptInputs) -> PromptResult:
    """Compose a Kling narrative prompt with @ElementN character tags."""
    parts = []
    warnings = []

    # 1. Shot type + setting
    if inputs.shot_type:
        parts.append(f"{inputs.shot_type}, {inputs.setting.description}")
    else:
        parts.append(inputs.setting.description)

    # 2. Characters — @ElementN tags (not inline descriptions)
    for char in inputs.characters:
        tag = char.element_tag or ""
        if tag:
            parts.append(f"{tag} {char.id}")
        else:
            warnings.append(f"Character '{char.id}' has no element_tag — using inline description")
            parts.append(char.description)

    # 3. Action + body language
    parts.append(inputs.action)
    if inputs.body_language:
        parts.append(inputs.body_language)

    # 4. Dialogue as quoted text
    if inputs.dialogue:
        parts.append(inputs.dialogue)

    # 5. Lighting
    if inputs.lighting:
        parts.append(inputs.lighting)

    # 6. Sound direction
    if inputs.sound:
        parts.append(inputs.sound)

    # 7. Camera direction
    if inputs.camera:
        parts.append(inputs.camera)

    prompt = ". ".join(p.rstrip(". ") for p in parts if p) + "."
    char_count = len(prompt)

    if char_count > CHAR_LIMIT:
        warnings.append(f"Kling prompt is {char_count} chars — EXCEEDS {CHAR_LIMIT} char limit!")

    return PromptResult(
        prompt=prompt,
        char_count=char_count,
        warnings=warnings,
        negative_prompt=DEFAULT_NEGATIVE,
    )
