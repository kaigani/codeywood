"""
Prompt template library — composable functions per modality.

Usage:
    from lib.prompts import ltx2_t2v, ltx2_i2v, kling_narrative, flux_frame
    from lib.prompts import PromptInputs, CharacterDesc, SettingAnchor, PromptResult

    result = ltx2_t2v.compose(inputs)
    print(result.prompt, result.char_count, result.warnings)
"""

from ._types import CharacterDesc, SettingAnchor, PromptInputs, PromptResult
from . import ltx2_t2v, ltx2_i2v, kling_narrative, flux_frame

__all__ = [
    "CharacterDesc",
    "SettingAnchor",
    "PromptInputs",
    "PromptResult",
    "ltx2_t2v",
    "ltx2_i2v",
    "kling_narrative",
    "flux_frame",
]
