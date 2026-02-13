"""
LTX-2 image-to-video prompt template.

Rich prompts — start frame anchors the visual, prompt directs motion.
Nearly identical to t2v but action describes what CHANGES FROM the start frame.
Setting anchors still needed (LTX-2 drifts without them).
"""

from ._types import PromptInputs, PromptResult

DEFAULT_NEGATIVE = (
    "blur, distort, low quality, cartoon, anime, deformed, extra limbs, "
    "text, watermark, modern clothing, contemporary architecture"
)

CHAR_LIMIT = 1500


def compose(inputs: PromptInputs) -> PromptResult:
    """Compose a rich i2v prompt from structured inputs.

    Same structure as t2v — the start frame provides visual anchor,
    but the prompt still needs full context for LTX-2 to maintain
    consistency throughout the clip.
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

    # 3. Action (motion FROM start frame) + body language
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
        warnings.append(f"i2v prompt is {char_count} chars (recommended <{CHAR_LIMIT})")

    return PromptResult(
        prompt=prompt,
        char_count=char_count,
        warnings=warnings,
        negative_prompt=DEFAULT_NEGATIVE,
    )
