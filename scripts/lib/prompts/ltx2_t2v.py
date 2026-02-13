"""
LTX-2 text-to-video prompt template.

Richest prompts — no start frame, so prompt must carry all visual context.
Setting anchors, full character descriptions, dialogue as quoted text,
camera direction, and sound cues all included.
"""

from ._types import PromptInputs, PromptResult

DEFAULT_NEGATIVE = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, contemporary architecture"
)

CHAR_LIMIT = 1500


def compose(inputs: PromptInputs) -> PromptResult:
    """Compose a rich t2v prompt from structured inputs."""
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
        warnings.append(f"t2v prompt is {char_count} chars (recommended <{CHAR_LIMIT})")

    return PromptResult(
        prompt=prompt,
        char_count=char_count,
        warnings=warnings,
        negative_prompt=DEFAULT_NEGATIVE,
    )
